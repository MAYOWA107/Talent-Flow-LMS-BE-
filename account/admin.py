from django.contrib import admin
from core.models import Profile
from .models import CustomUser, OtpToken


admin.site.register(CustomUser)
admin.site.register(OtpToken)
admin.site.register(Profile)
