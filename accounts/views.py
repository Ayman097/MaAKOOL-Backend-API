from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User, RevokedToken, Profile
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
)
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.http import HttpResponseBadRequest
from django.utils.encoding import force_bytes
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from app.models import Product
from django.db.models import Avg
from .models import Review


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

        refresh = RefreshToken.for_user(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response(data)


class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = super().post(request, *args, **kwargs)
        user = serializer.user

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


class ContactUsView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = ContactUsSerializer(data=request.data)
        if serializer.is_valid():
            subject = "Contact Us Form Submission"
            message = f"""
            Name: {serializer.validated_data["name"]}
            Email: {serializer.validated_data["email"]}
            Phone: {serializer.validated_data["phone"]}
            
            Feedback:
            {serializer.validated_data["feedback"]}
            """
            from_email = "a7med74yaso@gmail.com"
            recipient_list = ["a7med74yaso@gmail.com", "imamahdi22@gmail.com"]

            send_mail(subject, message, from_email, recipient_list, fail_silently=False)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# Rview Products

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review(request, id):
    user = request.user
    product = get_object_or_404(Product, pk=id) 
    data = request.data
    review = product.reviews.filter(user=user)
    
    # To Ensure user give rate between 1 : 5
    if data['rating'] <= 0 or data['rating'] >= 6:
        return Response({'Error': "Please Rate between 1 to 5"}, status=status.HTTP_400_BAD_REQUEST)
    elif review.exists():
        new_review = {'rating': data['rating'], 'comment': data['comment']}
        review.update(**new_review)

        # Calculate Avg Rating for product
        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        product.rateings = rating['avg_ratings']
        product.save()
        return Response({'details': 'Review Updated Successfully'}, status=status.HTTP_200_OK)
    else:
        Review.objects.create(
            product = product,
            user = user,
            comment = data['comment'],
            rating = data['rating']   
        )
        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        product.rateings = rating['avg_ratings']
        product.save()
        return Response({'details': 'Review Created Successfully'}, status=status.HTTP_200_OK)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delate_review(request, id):
    user = request.user
    product = get_object_or_404(Product, pk=id) 
    review = product.reviews.filter(user=user)

    if review.exists():
        review.delete()
        rating = product.reviews.aggregate(avg_ratings = Avg('rating'))
        if rating['avg_ratings'] is None:
            rating['avg_ratings'] = 0
            product.rateings = rating['avg_ratings']
            product.save()
            return Response({'details': 'Review Deleted'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'you are not authrized to delete this review'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'error': 'Review Not found'}, status=status.HTTP_400_BAD_REQUEST)