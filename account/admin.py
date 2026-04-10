from django.contrib import admin

from .models import CustomUser, OtpToken


admin.site.register(CustomUser)
admin.site.register(OtpToken)
