from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Profile
from rest_framework.validators import UniqueValidator
import re


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("address", "phone")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2", "profile")
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"validators": [UniqueValidator(queryset=User.objects.all())]},
            "username": {"validators": [UniqueValidator(queryset=User.objects.all())]},
        }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})

        return data

    def create(self, validated_data):
        validated_data.pop("password2")

        profile_data = validated_data.pop("profile")

        user = User.objects.create_user(**validated_data)

        existing_profile = user.profile

        if existing_profile:
            existing_profile.address = profile_data.get(
                "address", existing_profile.address
            )
            existing_profile.phone = profile_data.get("phone", existing_profile.phone)
            existing_profile.save()
        else:
            Profile.objects.create(user=user, **profile_data)

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)

        if email and password:
            user = User.objects.filter(email=email).first()

            if user and user.check_password(password):
                refresh = RefreshToken.for_user(user)
                data["refresh"] = str(refresh)
                data["access"] = str(refresh.access_token)
                self.user = user
            else:
                raise serializers.ValidationError(
                    "Invalid credentials. Please try again."
                )
        else:
            raise serializers.ValidationError("Both email and password are required.")

        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    address = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "profile",
            "token",
            "address",
            "phone",
        )
        extra_kwargs = {
            "profile": {"read_only": True},
            "username": {"required": False},
            "email": {"required": False},
        }

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def validate(self, data):
        # Validate other fields as needed
        return data

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)

        # Update the profile fields (address and phone)
        profile_data = {
            "address": validated_data.get("address", instance.profile.address),
            "phone": validated_data.get("phone", instance.profile.phone),
        }
        instance.profile.address = profile_data["address"]
        instance.profile.phone = profile_data["phone"]
        instance.profile.save()

        instance.save()

        return instance


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)

    def validate(self, attrs):
        return attrs


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ["email"]


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True)

    def validate(self, data):
        if not data.get("new_password"):
            raise serializers.ValidationError("New password is required.")
        return data
