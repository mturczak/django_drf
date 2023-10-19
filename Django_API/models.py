import os
from io import BytesIO

from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.files.base import ContentFile
from django.core.signing import TimestampSigner
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from PIL import Image as PilImage


class Tier(models.Model):
    name = models.CharField(max_length=200)
    thumbnail_sizes = models.JSONField()  # Store sizes as a JSON field
    link_to_original = models.BooleanField(default=False)
    expiring_links = models.BooleanField(default=False)


class CustomUser(AbstractUser):
    account_tier = models.ForeignKey(
        Tier, on_delete=models.CASCADE, null=True, blank=True
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="customuser_set",  # new
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="customuser_set",  # new
        related_query_name="user",
    )


class Image(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    image = models.ImageField(upload_to="")
    original_image_link = models.URLField(blank=True, null=True)
    filename = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Flag to check if the image is being saved for the first time
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.image:
            # open image
            original_image = PilImage.open(self.image)

            # create thumbnails
            for (
                size_name,
                size_str,
            ) in self.user.account_tier.thumbnail_sizes.items():
                with BytesIO() as temp_thumb:
                    # Create a copy of the original image for each thumbnail
                    image = original_image.copy()
                    width, height = map(
                        int, size_str.split("x")
                    )  # split the string and convert to integers
                    image.thumbnail((width, height), PilImage.LANCZOS)
                    thumb_name, thumb_extension = os.path.splitext(self.image.name)
                    thumb_extension = thumb_extension.lower()
                    thumb_filename = (
                        thumb_name + f"_{size_name}_thumb_{size_str}" + thumb_extension
                    )
                    image.save(temp_thumb, format="JPEG")
                    temp_thumb.seek(0)

                    # Save the thumbnail image to a new ImageField
                    thumb_file = ContentFile(temp_thumb.read(), name=thumb_filename)
                    thumbnail = Thumbnail.objects.create(
                        image=thumb_file, user=self.user, parent_image=self
                    )

            # Save the original image link in the Image model
            self.original_image_link = self.image.url

            # Save the model without creating the thumbnails again
            super().save(update_fields=["original_image_link"])

    def get_expiring_link(self, expire_seconds):
        if self.user.account_tier == getattr(CustomUser, "ENTERPRISE", None):
            signer = TimestampSigner()
            value = signer.sign(self.image.url)
            return {"signed_value": value, "expire_seconds": expire_seconds}
        else:
            return None


class Thumbnail(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="thumbnails/")
    parent_image = models.ForeignKey(
        Image, related_name="thumbnails", on_delete=models.CASCADE
    )


@receiver(post_save, sender=Image)
def create_thumbnails(sender, instance, created, **kwargs):
    if created:
        instance.save()
