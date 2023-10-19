from io import BytesIO

import django
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Image, Tier


class ImageUploadTest(APITestCase):
    def setUp(self):
        tier = Tier.objects.create(
            name="Test Tier",
            thumbnail_sizes={"small": "200x200", "large": "400x400"},
            link_to_original=False,
            expiring_links=False,
        )
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123", account_tier=tier
        )
        self.client.force_authenticate(user=self.user)

    def test_image_upload(self):
        response = requests.get("https://picsum.photos/500/500")
        image_content = BytesIO(response.content)
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=image_content.read(),
            content_type="image/jpeg",
        )
        data = {"image": image}
        response = self.client.post(reverse("image_upload"), data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class APIEndpointTest(APITestCase):
    def setUp(self):
        tier = Tier.objects.create(
            name="Test Tier",
            thumbnail_sizes={"small": "200x200", "large": "400x400"},
            link_to_original=True,
            expiring_links=False,
        )
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpass123", account_tier=tier
        )
        self.client.force_authenticate(user=self.user)

    def test_image_upload(self):
        response = requests.get("https://picsum.photos/500/500")
        image_content = BytesIO(response.content)
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=image_content.read(),
            content_type="image/jpeg",
        )
        data = {"image": image}
        response = self.client.post(reverse("image_upload"), data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_images(self):
        response = self.client.get(reverse("image_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_image_detail(self):
        response = requests.get("https://picsum.photos/500/500")
        image_content = BytesIO(response.content)
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=image_content.read(),
            content_type="image/jpeg",
        )
        data = {"image": image}
        response = self.client.post(reverse("image_upload"), data, format="multipart")

        # Get the filename of the Image object from the response
        image_url = response.data["image"]
        print(image_url)
        filename = image_url.split("/")[-1]
        print(filename)

        response = self.client.get(reverse("image_view", kwargs={"filename": filename}))
        print(response, "response")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
