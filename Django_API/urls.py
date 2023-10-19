from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (
    ExpiringLinkView,
    ImageListView,
    ImageUploadView,
    ImageView,
    serve_image,
)

urlpatterns = [
    path("image/upload/", ImageUploadView.as_view(), name="image_upload"),
    path("image/list/", ImageListView.as_view(), name="image_list"),
    path("media/<str:filename>/", ImageView.as_view(), name="image_view"),
    path(
        "images/<int:image_id>/expiring_link/",
        ExpiringLinkView.as_view(),
        name="expiring_link",
    ),
    path("images/<str:signed_value>/", serve_image, name="serve_image"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
