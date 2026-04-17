from django.db.models.signals import post_save
from django.conf import settings
from .models import OtpToken
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .tasks import send_otp_mail
from core.models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_superuser and instance.is_staff:
            pass
        else:
            OtpToken.objects.create(
                user=instance, otp_expires_at=timezone.now() + timedelta(minutes=10)
            )

        # email credentials
        otp = OtpToken.objects.filter(user=instance).last()
        send_otp_mail.delay(instance.email, otp.otp_code)

        Profile.objects.create(user=instance)
