from django.db import models
from django.conf import settings


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to="profile_img/", blank=True, null=True)
    linkedIn_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.user.full_name
