from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
import os
from PIL import Image as PilImage
from io import BytesIO
from django.core.signing import TimestampSigner
from django.core.files.base import ContentFile
from django.utils.translation import gettext as _

THUMBNAIL_SIZE_200 = (200, 200)
THUMBNAIL_SIZE_400 = (400, 400)


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


class Thumbnail(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/")
    parent_image = models.ForeignKey(
        "Image", related_name="thumbnails", on_delete=models.CASCADE
    )


class Image(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/")

    def save(self, *args, **kwargs):
        super().save(
            *args, **kwargs
        )  # Save the instance before creating the thumbnails
        if self.image:
            # open image
            image = PilImage.open(self.image)

            # create thumbnails
            for size_name, size_str in self.user.account_tier.thumbnail_sizes.items():
                width, height = map(
                    int, size_str.split("x")
                )  # split the string and convert to integers
                image.thumbnail((width, height), PilImage.LANCZOS)
                thumb_name, thumb_extension = os.path.splitext(self.image.name)
                thumb_extension = thumb_extension.lower()
                thumb_filename = (
                    thumb_name + f"_{size_name}_thumb_{size_str}" + thumb_extension
                )
                temp_thumb = BytesIO()
                image.save(temp_thumb, format="JPEG")
                temp_thumb.seek(0)

                # Save the thumbnail image to a new ImageField
                thumb_file = ContentFile(temp_thumb.read(), name=thumb_filename)
                Thumbnail.objects.create(
                    image=thumb_file, user=self.user, parent_image=self
                )

                temp_thumb.close()

    def get_expiring_link(self, expire_seconds):
        if self.user.account_tier == CustomUser.ENTERPRISE:
            signer = TimestampSigner()
            value = signer.sign(self.image.url)
            return {"signed_value": value, "expire_seconds": expire_seconds}
        else:
            return None
