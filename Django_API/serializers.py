from rest_framework import serializers
from .models import Image, Thumbnail


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ["image"]


class ImageSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailSerializer(many=True, read_only=True)

    class Meta:
        model = Image
        fields = ("id", "user", "image", "thumbnails")
