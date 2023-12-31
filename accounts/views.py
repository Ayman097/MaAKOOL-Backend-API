from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView, DestroyAPIView

from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from rest_framework.exceptions import ParseError
from .models import ContactUsModel, User, RevokedToken, Profile
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    ContactUsSerializer,
    UserSerializer,
    UserLoginSerializer,
    UserProfileUpdateSerializer,
    LogoutSerializer,
    ProfileSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    ProfileImageSerializer,
    EmailVerificationSerializer,
)
from django.conf import settings
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
import secrets


class ProfileImageUpdateView(generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileImageSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def perform_update(self, serializer):
        instance = self.get_object()
        serializer.save(user=instance.user)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        verification_code = secrets.token_urlsafe(16)
        user.profile.verification_code = verification_code
        user.profile.save()
        send_mail(
            "Verification Code",
            f"Your verification code is: {verification_code}",
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

        return Response(
            {"message": "Verification code sent"}, status=status.HTTP_200_OK
        )


class EmailVerificationView(generics.GenericAPIView):
    serializer_class = EmailVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        email = validated_data.get("email")

        user = User.objects.get(email=email)
        user.profile.is_verified = True
        user.profile.save()

        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)


class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        if not user.profile.is_verified:
            return Response(
                {"detail": "Account not verified. Please verify your account."},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = super().post(request, *args, **kwargs)

        refresh = response.data["refresh"]
        access = response.data["access"]
        user_data = {
            "email": user.email,
            "username": user.username,
            "address": user.profile.address,
            "phone": user.profile.phone,
            "id": user.id,
        }

        response.data.update({"user": user_data})
        return response


class StaffLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.user

        if not user.is_staff:
            return Response(
                {"detail": "You do not have permission to log in."},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = super().post(request, *args, **kwargs)

        refresh = response.data["refresh"]
        access = response.data["access"]
        user_data = {
            "email": user.email,
            "username": user.username,
            "address": user.profile.address,
            "phone": user.profile.phone,
            "id": user.id,
        }

        response.data.update({"user": user_data})
        return response


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id, format=None):
        if request.user.id != user_id:
            return Response(
                {"error": "You don't have permission to view this profile"},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(id=user_id)
            profile = user.profile
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token = serializer.validated_data["refresh_token"]
        try:
            token = OutstandingToken.objects.get(token=refresh_token)

            RevokedToken.add(token)

            access_token = request.data.get("access_token")
            if access_token:
                access_token = OutstandingToken.objects.get(token=access_token)
                RevokedToken.add(access_token)

            return Response(
                {"message": "Successfully logged out."}, status=status.HTTP_200_OK
            )
        except OutstandingToken.DoesNotExist:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetView(APIView):
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        try:
            user = User.objects.get(email=email)
            refresh = RefreshToken.for_user(user)

            current_site = get_current_site(request)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            relative_link = reverse(
                "password-reset-confirm", kwargs={"uidb64": uidb64, "token": token}
            )
            abs_url = f"http://localhost:5173/ForgetPasswordConfirm/{uidb64}/{token}/"

            send_mail(
                "Password Reset",
                f"Please follow this link to reset your password: {abs_url}",
                "a7med74yaso@gmail.com",
                [email],
                fail_silently=False,
            )

            return Response(
                {"message": "Password reset link sent successfully."},
                status=status.HTTP_200_OK,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class PasswordResetConfirmView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]
        uidb64 = kwargs["uidb64"]
        token = kwargs["token"]

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)

            if default_token_generator.check_token(user, token):
                user.set_password(new_password)
                user.save()
                return Response(
                    {"message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid user ID"}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ContactUsListView(ListCreateAPIView):
    serializer_class = ContactUsSerializer
    pagination_class = PageNumberPagination
    queryset = ContactUsModel.objects.all()


class ContactUsDetailView(DestroyAPIView):
    serializer_class = ContactUsSerializer
    queryset = ContactUsModel.objects.all()
