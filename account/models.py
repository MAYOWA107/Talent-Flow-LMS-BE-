from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import uuid, secrets
from django.conf import settings


REGISTRATION_CHOICES = [
    ("email", "Email"),
    ("google", "Google"),
]


class CustomUserManager(BaseUserManager):

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("User must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("is_staff must be set to True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("is_superuser must be set to True")

        if extra_fields.get("is_active") is not True:
            raise ValueError("is_active must be set to True")

        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    CHOICES = (
        ("admin", "Admin"),
        ("student", "Student"),
        ("instructor", "Instructor"),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=CHOICES, default="student")
    registration_method = models.CharField(max_length=20, choices=REGISTRATION_CHOICES)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


def generate_otp():
    return str(secrets.randbelow(900000) + 100000)


class OtpToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otp_tokens"
    )
    otp_code = models.CharField(max_length=6, default=generate_otp)
    otp_created = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField()

    def __str__(self):
        return self.user.email
