from django.urls import path
from .views import (
    register,
    verify_otp,
    resend_otp,
    reset_password,
    login,
    forgot_password,
    google_auth,
)


urlpatterns = [
    path("register/", register, name="register"),
    path("verify-otp/", verify_otp, name="verify_otp"),
    path("resend-otp/", resend_otp, name="resend_otp"),
    path("forgot-password/", forgot_password, name="forgot-password"),
    path("reset-password/", reset_password, name="reset_password"),
    path("login/", login, name="login"),
    # google signup/login
    path("google/", google_auth, name="google"),
]
