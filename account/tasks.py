from celery import shared_task
from django.core.mail import send_mail


@shared_task
def send_otp_mail(email, otp_code):
    subject = "Verify your Talent Flow Account"
    message = f""" 
                    Hi, Welcomwe to Talent Flow!!
                    We are excited to have you on board! To get started, Please verify your email address by using the code below
                    Verification Code: {otp_code}
                    This code will expire in 10 minutes

                    If you didn't create an account with Talent Flow, you can safely ignore this email.
                    Once verified, you will be able to access your dashboard and manage the app effectively.

                    
                    Best regards, 
                    Talent Flow Team
                """
    from_email = "ogunkoyamayowa77@gmail.com"

    send_mail(subject, message, from_email, [email], fail_silently=False)
