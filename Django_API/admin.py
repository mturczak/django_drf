from django.contrib import admin
from .models import CustomUser, Tier, Image


class TierAdmin(admin.ModelAdmin):
    list_display = ("name", "thumbnail_sizes", "link_to_original", "expiring_links")


class ImageAdmin(admin.ModelAdmin):
    list_display = ("id", "image", "user")  # Adjust this to your Image model fields


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
        "is_staff",
    ]
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
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
        (("Custom Fields"), {"fields": ("account_tier",)}),
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
