from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from .models import PasswordResetOTP
from .serializers import (
    ForgotPasswordSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    VerifyOTPSerializer,
    get_tokens_for_user,
)

User = get_user_model()


def build_user_payload(user: User):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "user_type": user.user_type,
    }


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        tokens = get_tokens_for_user(user)
        data = {
            "user": build_user_payload(user),
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        tokens = get_tokens_for_user(user)

        data = {
            "user": build_user_payload(user),
            "access": tokens["access"],
            "refresh": tokens["refresh"],
        }
        return Response(data, status=status.HTTP_200_OK)


class RefreshTokenView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response(
                {"detail": "No refresh token provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
            user = User.objects.get(id=access_token["user_id"])
        except Exception:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        data = {
            "user": build_user_payload(user),
            "access": str(access_token),
            "refresh": str(refresh),
        }
        return Response(data, status=status.HTTP_200_OK)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "No account found with this email address."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Invalidate any previous unused OTPs for this user
        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)

        otp_code = PasswordResetOTP.generate_otp()
        PasswordResetOTP.objects.create(
            user=user,
            otp_code=otp_code,
            expires_at=timezone.now() + timedelta(minutes=10),
        )

        import resend
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send({
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [user.email],
            "subject": "Your Shibaha password reset code",
            "text": f"Your verification code is: {otp_code}\n\nThis code expires in 10 minutes.",
        })

        return Response(
            {"message": "If this email is registered, a code has been sent."},
            status=status.HTTP_200_OK,
        )


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid request."}, status=status.HTTP_404_NOT_FOUND)

        otp_record = (
            PasswordResetOTP.objects.filter(user=user, otp_code=otp, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if otp_record is None or not otp_record.is_valid():
            return Response(
                {"detail": "le code de vérification est incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"message": "Code verified."}, status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]
        new_password = serializer.validated_data["new_password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"detail": "Invalid request."}, status=status.HTTP_404_NOT_FOUND)

        otp_record = (
            PasswordResetOTP.objects.filter(user=user, otp_code=otp, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if otp_record is None or not otp_record.is_valid():
            return Response(
                {"detail": "le code de vérification est incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save()
        otp_record.is_used = True
        otp_record.save()

        return Response({"message": "Password reset successful."}, status=status.HTTP_200_OK)

