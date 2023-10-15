from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.generics import ListAPIView
from .models import CustomUser, Image
from .serializers import ImageSerializer
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.permissions import IsAuthenticated


from django.core import signing
from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.views import APIView


from django.contrib.auth.hashers import check_password
from .models import CustomUser


class LoginView(APIView):
    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return Response({"error": "Invalid Credentials"}, status=400)

        if user and check_password(password, user.password):
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "passwords": f"{password, user.password, check_password(password, user.password)}",
                }
            )
        else:
            return Response(
                {
                    "error": f"Invalid Credentials{password, user.password, check_password(password, user.password)}"
                },
                status=400,
            )


class ImageUploadView(APIView):
    parser_classes = (
        MultiPartParser,
        FormParser,
    )
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        image_serializer = ImageSerializer(data=request.data)

        if image_serializer.is_valid():
            image_serializer.save(user=request.user)
            image = Image.objects.get(id=image_serializer.data["id"])
            response_data = image_serializer.data

            # Add links to the thumbnails and original image based on the user's account tier
            if request.user.account_tier.name == "Basic":
                response_data["thumbnail_200_link"] = image.thumbnails["200"]
            elif request.user.account_tier.name == "Premium":
                response_data["thumbnail_200_link"] = image.thumbnails["200"]
                response_data["thumbnail_400_link"] = image.thumbnails["400"]
                response_data["original_image_link"] = image.image.url
            elif request.user.account_tier.name == "Enterprise":
                response_data["thumbnail_200_link"] = image.thumbnails["200"]
                response_data["thumbnail_400_link"] = image.thumbnails["400"]
                response_data["original_image_link"] = image.image.url
                response_data["expiring_link"] = image.get_expiring_link(
                    300
                )  # Default expiration time is 300 seconds

            return Response(response_data, status=status.HTTP_201_CREATED)

        else:
            return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImageListView(ListAPIView):
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)


class ExpiringLinkView(APIView):
    def get(self, request, *args, **kwargs):
        image_id = kwargs.get("image_id")
        image = Image.objects.get(id=image_id)

        # Check if the user has the right to generate an expiring link
        if request.user.account_tier != "Enterprise":
            return Response(
                {"message": "You do not have the right to generate an expiring link."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the expiration time from the request parameters
        expire_seconds = request.query_params.get("expire_seconds", 300)
        expire_seconds = max(300, min(int(expire_seconds), 30000))

        # Generate the signed URL
        signer = signing.TimestampSigner()
        value = signer.sign(str(image_id))
        expiring_link = {
            "image_id": image_id,
            "signed_value": value,
            "expire_seconds": expire_seconds,
        }

        return JsonResponse(expiring_link)
