from os.path import basename

from django.contrib.auth.hashers import check_password
from django.core.signing import BadSignature, TimestampSigner
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .serializers import ImageSerializer


class ImageUploadView(APIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        filename = basename(request.data["image"].name)

        # Add the filename to the validated data
        serializer.validated_data["filename"] = filename
        serializer.save(user_id=request.user.id)
        response_data = serializer.data

        return Response(response_data, status=status.HTTP_201_CREATED)

    def get_serializer(self, *args, **kwargs):
        return ImageSerializer(*args, **kwargs)


class ImageListView(ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)


class ExpiringLinkView(APIView):
    def get(self, request, *args, **kwargs):
        image_id = kwargs.get("image_id")
        image = get_object_or_404(Image, id=image_id)

        # Check if the user has the right to generate an expiring link
        if not image.user.account_tier.expiring_links:
            return Response(
                {"message": "You do not have the right to generate an expiring link."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the expiration time from the request parameters
        expire_seconds = request.query_params.get("expire_seconds", 300)
        expire_seconds = max(300, min(int(expire_seconds), 30000))

        # Generate the signed URL
        signer = TimestampSigner()
        value = signer.sign(str(image_id))
        expiring_link = reverse("serve_image", args=[value])

        return JsonResponse(
            {
                "image_id": image_id,
                "expiring_link": request.build_absolute_uri(expiring_link),
                "expire_seconds": expire_seconds,
            }
        )


class ImageView(RetrieveAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        filename = self.kwargs.get("filename")

        filter_kwargs = {"image": filename}

        obj = get_object_or_404(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        image_data = open(instance.image.path, "rb").read()
        return HttpResponse(image_data, content_type="image/jpeg")


def serve_image(request, signed_value):
    signer = TimestampSigner()

    try:
        # Unsign the value to get the image ID
        image_id = signer.unsign(signed_value, max_age=300)
    except BadSignature:
        raise NotFound("No such image")

    image = get_object_or_404(Image, id=image_id)

    # Serve the image
    return FileResponse(image.image.file)
