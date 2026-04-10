from rest_framework import serializers
from .models import CustomUser, OtpToken
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import authenticate
from rest_framework.validators import ValidationError

from rest_framework_simplejwt.tokens import RefreshToken


class ResgistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )

    class Meta:
        model = CustomUser
        fields = ["email", "password", "confirm_password", "full_name", "role"]

    def validate(self, attrs):
        email_exist = get_user_model().objects.filter(email=attrs["email"]).exists()

        if email_exist:
            raise ValidationError("Error occured!! This email already exist.")

        elif attrs["password"] != attrs["confirm_password"]:
            raise ValidationError("Error occured!! Your passwords don't match")

        elif attrs["role"] not in ["student", "instructor"]:
            raise ValidationError("Invalid role selected")

        return attrs

    def create(self, validated_data):
        user = get_user_model().objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            full_name=validated_data["full_name"],
            role=validated_data["role"],
        )

        return user


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        email = attrs["email"]
        otp_code = attrs["otp_code"]

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise ValidationError("Incorrect email address!! This user does not exist.")

        if user.is_active:
            raise ValidationError("Account already verified.")

        try:
            otp = OtpToken.objects.filter(user=user).latest("otp_created")
        except OtpToken.DoesNotExist:
            raise ValidationError("No OTP found. Please request a new one.")

        if otp.otp_code != otp_code:
            raise ValidationError(
                "Error occured!! Invalid code provided. Please enter valid OTP"
            )

        if not otp.otp_code:
            raise ValidationError("No OTP found!!")

        if timezone.now() > otp.otp_expires_at:
            raise ValidationError("otp code has expired.")

        attrs["user"] = user
        return attrs


class ResendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"]

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise ValidationError("Error!! This user does not exist")

        if user.is_active:
            raise ValidationError("This account has been verified")

        last_otp = OtpToken.objects.filter(user=user).order_by("-otp_created").first()

        if last_otp:
            if timezone.now() < last_otp.otp_created + timedelta(minutes=2):
                raise ValidationError("Please wait before requesting another OTP")

        attrs["user"] = user
        return attrs


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        user = authenticate(username=email, password=password)

        if not user:
            raise ValidationError("Invalid email or password!!!!")

        if not user.is_active:
            raise ValidationError(
                "Your account is not verified. Please verify using the OTP provided in your email after signing up"
            )

        # creating a token for the user
        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs["email"]

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise ValidationError(
                "This email does not exist. Please provide a valid email"
            )

        if not user.is_active:
            raise ValidationError(
                "This accout is not a verified account. Please go and create an account"
            )

        attrs["user"] = user
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        error_messages={"min_length": "Password must be at least 8 characters long"},
    )

    def validate(self, attrs):
        email = attrs["email"]
        otp_code = attrs["otp_code"]
        new_password = attrs["new_password"]

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            raise ValidationError(
                "This user does not exist. Please provide a valid email"
            )

        try:
            otp = OtpToken.objects.filter(user=user).latest("otp_created")
        except OtpToken.DoesNotExist:
            raise ValidationError("Incorrect OTP code")

        if otp.otp_code != otp_code:
            raise ValidationError("Incorrect OTP provided")

        if timezone.now() > otp.otp_expires_at:
            raise ValidationError("OTP code has expired!!")

        if user.check_password(new_password):
            raise ValidationError("new password cannot be the same as old password")

        attrs["user"] = user
        return attrs
