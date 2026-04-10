from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .tasks import send_otp_mail
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    ResgistrationSerializer,
    ResendOtpSerializer,
    ResetPasswordSerializer,
    VerifyOtpSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
)

from .models import CustomUser, OtpToken
from django.utils import timezone
from datetime import timedelta

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from django.conf import settings


@api_view(["POST"])
def register(request):
    serializers = ResgistrationSerializer(data=request.data)

    if serializers.is_valid():
        serializers.save()

        return Response(
            {
                "message": "Your account has been created successfully. An OTP has been sent to your email address for verification"
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def verify_otp(request):
    serializers = VerifyOtpSerializer(data=request.data)

    if serializers.is_valid():
        user = serializers.validated_data["user"]
        user.is_active = True
        user.save()
        # delete OTP
        OtpToken.objects.filter(user=user).delete()

        return Response(
            {"message": "Your account has been verified successfully"},
            status=status.HTTP_200_OK,
        )
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def resend_otp(request):
    serializers = ResendOtpSerializer(data=request.data)

    if serializers.is_valid():
        user = serializers.validated_data["user"]

        # deleting old otp
        OtpToken.objects.filter(user=user).delete()
        # Generate another otp
        otp = OtpToken.objects.create(
            user=user, otp_expires_at=timezone.now() + timedelta(minutes=10)
        )

        # send the otp to user
        send_otp_mail.delay(user.email, otp.otp_code)

        return Response(
            {"message": "A new OTP code has been sent to your email address"},
            status=status.HTTP_200_OK,
        )
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def login(request):
    serializers = LoginSerializer(data=request.data)

    if serializers.is_valid():
        data = serializers.validated_data

        return Response(
            {
                "message": "User login successfully",
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
            }
        )
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.validated_data["user"]

        # delete old otps
        OtpToken.objects.filter(user=user).delete()

        # create new otp
        otp = OtpToken.objects.create(
            user=user, otp_expires_at=timezone.now() + timedelta(minutes=10)
        )
        send_otp_mail.delay(user.email, otp.otp_code)

        return Response(
            {"message": "Password reset OTP has been sent to your email"},
            status=status.HTTP_200_OK,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def reset_password(request):
    serializers = ResetPasswordSerializer(data=request.data)
    if serializers.is_valid():
        user = serializers.validated_data["user"]
        new_password = serializers.validated_data["new_password"]

        user.set_password(new_password)
        user.save()

        # deleting otp after use
        OtpToken.objects.filter(user=user).delete()

        return Response(
            {"message": "Password reset successfully"}, status=status.HTTP_200_OK
        )
    return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)


# Google auth
@api_view(["POST"])
def google_auth(request):
    token = request.data.get("token")
    if not token:
        return Response(
            {"error": "Token not provided", "status": False},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        id_info = id_token.verify_oauth2_token(
            token, google_requests.Request(), settings.GOOGLE_OAUTH_CLIENT_ID
        )

        print(id_info)
        email = id_info["email"]

        user, created = CustomUser.objects.get_or_create(email=email)
        if created:
            user.set_unusable_password()
            user.registration_method = "google"
            user.save()

        else:
            if user.registration_method != "google":
                return Response(
                    {"error": "User needs to sign in through email", "status": False},
                    status=status.HTTP_403_FORBIDDEN,
                )

        user.is_active = True
        user.save()
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "status": True,
            },
            status=status.HTTP_200_OK,
        )

    except ValueError:
        return Response(
            {"error": "Invalid token", "status": False},
            status=status.HTTP_400_BAD_REQUEST,
        )
