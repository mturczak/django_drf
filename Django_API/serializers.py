from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers

from .models import Image, Thumbnail


class ThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thumbnail
        fields = ["id", "image", "user", "parent_image"]


class ImageSerializer(serializers.ModelSerializer):
    thumbnails = ThumbnailSerializer(many=True, read_only=True)
    image = serializers.ImageField(write_only=True)
    expiring_link_example = serializers.SerializerMethodField()

    class Meta:
        model = Image
        fields = (
            "id",
            "user",
            "image",
            "thumbnails",
            "filename",
            "expiring_link_example",
        )

    def get_expiring_link_example(self, obj):
        if obj.user.account_tier.expiring_links:
            request = self.context.get("request")
            site_url = get_current_site(request).domain
            return (
                f"http://{site_url}/images/{obj.id}/expiring_link/?expire_seconds=600"
            )
        else:
            return None

    def get_expiring_link(self, obj):
        if obj.user.account_tier.expiring_links:
            expire_seconds = self.context["request"].query_params.get(
                "expire_seconds", 300
            )
            expire_seconds = max(300, min(int(expire_seconds), 30000))
            return obj.get_expiring_link(expire_seconds)
        else:
            return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image and instance.image.file:
            representation["image"] = instance.image.url
            if "thumbnails" in representation:
                representation["thumbnails"] = [
                    {"id": thumbnail["id"], "image": thumbnail["image"]}
                    for thumbnail in representation["thumbnails"]
                ]
        if (
            not instance.user.account_tier.link_to_original
            and "image" in representation
        ):
            del representation["image"]
        return representation
