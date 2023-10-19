from django.contrib import admin
from django.utils.html import format_html

from .models import CustomUser, Image, Tier


class TierAdmin(admin.ModelAdmin):
    list_display = ("name", "thumbnail_sizes", "link_to_original", "expiring_links")


class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image_preview", "thumbnail_preview", "user")

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" width="100" height="100" />'.format(obj.image.url)
        )

    image_preview.short_description = "Image Preview"

    def thumbnail_preview(self, obj):
        if obj.thumbnails.exists():
            thumbnails_html = "".join(
                [
                    '<img src="{}" width="50" height="50" />'.format(
                        thumbnail.image.url
                    )
                    for thumbnail in obj.thumbnails.all()
                ]
            )
            return format_html(thumbnails_html)
        else:
            return "No thumbnails"

    thumbnail_preview.short_description = "Thumbnail Preview"


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    model = CustomUser
    list_display = [
        "username",
        "email",
        "account_tier",
        "is_staff",
    ]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (("Tier"), {"fields": ("account_tier",)}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "email",
                    "is_staff",
                    "is_active",
                    "groups",
                    "user_permissions",
                    "account_tier",
                ),
            },
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Image, ImageAdmin)


admin.site.register(Tier, TierAdmin)
