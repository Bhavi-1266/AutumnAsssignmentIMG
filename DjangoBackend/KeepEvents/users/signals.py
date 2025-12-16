# users/signals.py
from allauth.account.signals import user_signed_up
from django.dispatch import receiver

@receiver(user_signed_up)
def handle_social_signup(request, user, **kwargs):
    """
    Social (Google) signup:
    - Trust Google's email verification
    - Do NOT send OTP
    - Keep user active
    """
    user.is_active = True
    user.save()
