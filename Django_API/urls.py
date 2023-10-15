from django.urls import path

# from django.contrib.auth.views import LoginView
from .views import LoginView
from .views import ImageUploadView, ImageListView

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("image/upload/", ImageUploadView.as_view(), name="image_upload"),
    path("image/list/", ImageListView.as_view(), name="image_list"),
]
