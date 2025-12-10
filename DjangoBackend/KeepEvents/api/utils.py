# events/utils.py
from guardian.shortcuts import assign_perm, remove_perm
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

def set_event_perms(event, visibility, extra_user_ids=None):
    """
    visibility: "admin" | "img" | "public"
    extra_user_ids: optional list of user IDs with direct access
    """
    admin_group = Group.objects.get(name="Admin")
    img_group = Group.objects.get(name="IMG Member")
    public_group = Group.objects.get(name="Public")

    # Clear old group perms on this event
    for g in [admin_group, img_group, public_group]:
        remove_perm("view_event_obj", g, event)
        remove_perm("change_event_obj", g, event)
        remove_perm("delete_event_obj", g, event)

    # Base: Admin can always view/change/delete
    assign_perm("view_event_obj", admin_group, event)
    assign_perm("change_event_obj", admin_group, event)
    assign_perm("delete_event_obj", admin_group, event)

    if visibility == "img":
        assign_perm("view_event_obj", img_group, event)

    if visibility == "public":
        assign_perm("view_event_obj", img_group, event)
        assign_perm("view_event_obj", public_group, event)

    # Optional per-user direct view perms
    if extra_user_ids:
        for uid in extra_user_ids:
            try:
                u = User.objects.get(pk=uid)
            except User.DoesNotExist:
                continue
            assign_perm("view_event_obj", u, event)


import random
from datetime import timedelta
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from users.models import EmailOTP

def generate_otp(length=6):
    return "".join(random.choice("0123456789") for _ in range(length))

def create_and_send_email_otp(user):
    # Invalidate previous unused OTPs
    EmailOTP.objects.filter(user=user, used=False).update(used=True)

    code = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=5)

    EmailOTP.objects.create(
        user=user,
        code=code,
        expires_at=expires_at,
    )

    subject = "KeepEvents email verification OTP"
    message = f"Your OTP is {code}. It is valid for 5 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = [user.email]

    send_mail(subject, message, from_email, to_email)
