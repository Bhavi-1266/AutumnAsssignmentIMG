from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from api.utils import create_and_send_email_otp

@receiver(user_signed_up)
def handle_social_signup(request, user, **kwargs):
    user.is_active = False
    user.save()
    create_and_send_email_otp(user)
