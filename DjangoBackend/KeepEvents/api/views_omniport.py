from django.shortcuts import redirect
from urllib.parse import urlencode
from django.conf import settings
import requests

from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer

def omniport_login(request):
    request.session["oauth_state"] = "img_oauth_login"

    params = {
        "client_id": settings.OMNIPORT_CLIENT_ID,
        "redirect_uri": settings.OMNIPORT_REDIRECT_URI,
        "state": request.session["oauth_state"],
    }

    return redirect(
        f"{settings.OMNIPORT_BASE_URL}/oauth/authorise/?{urlencode(params)}"
    )



def get_or_create_user_from_omniport(user_data):
    from users.models import users  # your custom user model

    person = user_data.get("person", {})
    student = user_data.get("student", {})
    contact = user_data.get("contactInformation", {})

    # 1️⃣ Pick email (prefer institute webmail)
    email = contact.get("instituteWebmailAddress") or contact.get("emailAddress")
    if not email:
        raise ValueError("No email found in Omniport response")

    # 2️⃣ Extract fields
    full_name = person.get("fullName", "")
    short_name = person.get("shortName", "")
    enrollment_number = student.get("enrolmentNumber", "")

    # 3️⃣ Find or create user by email
    user, created = users.objects.get_or_create(
        email=email,
        defaults={
            "username": email,              # if username is required
            "full_name": full_name,
            "short_name": short_name,
            "enrollment_number": enrollment_number,
        },
    )

    return user



def omniport_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    if not code:
        return Response(
            {"error": "Authorization code missing"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if state != request.session.get("oauth_state"):
        return Response(
            {"error": "Invalid OAuth state"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token_response = requests.post(
        f"{settings.OMNIPORT_BASE_URL}/open_auth/token/",
        data={
            "client_id": settings.OMNIPORT_CLIENT_ID,
            "client_secret": settings.OMNIPORT_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "redirect_uri": settings.OMNIPORT_REDIRECT_URI,
            "code": code,
        },
        timeout=10,
    )

    if token_response.status_code != 200:
        return Response(
            token_response.json(),
            status=status.HTTP_400_BAD_REQUEST,
        )

    access_token = token_response.json()["access_token"]

    user_response = requests.get(
        f"{settings.OMNIPORT_BASE_URL}/open_auth/get_user_data/",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=10,
    )

    if user_response.status_code != 200:
        return Response(
            user_response.json(),
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = get_or_create_user_from_omniport(user_response.json())

    refresh = RefreshToken.for_user(user)

    response = Response(
        {
            "user": UserSerializer(user, context={"request": request}).data
        },
        status=status.HTTP_200_OK,
    )

    response.set_cookie(
        key="access",
        value=str(refresh.access_token),
        httponly=True,
        secure=False,      # True in production
        samesite="Lax",
        max_age=15 * 60,
    )

    response.set_cookie(
        key="refresh",
        value=str(refresh),
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=7 * 24 * 60 * 60,
    )

    return response

        