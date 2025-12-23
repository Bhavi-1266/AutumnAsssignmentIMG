from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authtoken.models import Token

from users.models import EmailOTP
from .utils import create_and_send_email_otp
from .serializers import RequestOTPSerializer, VerifyOTPSerializer

User = get_user_model()

@api_view(["POST"])
@permission_classes([AllowAny])
def request_email_otp(request):
    serializer = RequestOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"].strip().lower()

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    create_and_send_email_otp(user)
    return Response({"detail": "OTP sent"}, status=status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_email_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data["email"].strip().lower()
    code = serializer.validated_data["code"]

    try:
        user = User.objects.get(email__iexact=email)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    otp_qs = EmailOTP.objects.filter(user=user, code=code, used=False).order_by("-created_at")
    otp_obj = otp_qs.first()
    if not otp_obj or not otp_obj.is_valid():
        return Response({"detail": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

    otp_obj.used = True
    otp_obj.save()

    user.is_active = True
    user.save()

    # optional: return token directly after verification
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"detail": "Email verified", "token": token.key , "user_id": user.id}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_token(request):
    if not request.user.is_active:
        return Response({"detail": "Email not verified"}, status=status.HTTP_403_FORBIDDEN)
    token, _ = Token.objects.get_or_create(user=request.user)
    return Response({"token": token.key})
