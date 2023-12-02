from rest_framework import serializers, validators
from rest_framework_simplejwt.tokens import RefreshToken
from .models import ContactUsModel, User, Profile


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["image"]


class ProfileSerializerView(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("address", "phone")


class ProfileSerializerUp(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    username = serializers.CharField(source="user.username")

    class Meta:
        model = Profile
        fields = ("email", "username", "address", "phone", "image")


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    username = serializers.CharField(source="user.username")
    verification_code = serializers.CharField(write_only=True)

    class Meta:
        model = Profile
        fields = ("email", "username", "address", "phone", "image", "verification_code")


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializerView()
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "password2", "profile")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        profile_data = validated_data.pop("profile")
        verification_code = profile_data.pop("verification_code", None)

        user = User.objects.create_user(**validated_data)
        existing_profile = user.profile

        if existing_profile:
            existing_profile.address = profile_data.get(
                "address", existing_profile.address
            )
            existing_profile.phone = profile_data.get("phone", existing_profile.phone)
            existing_profile.verification_code = verification_code
            existing_profile.save()
        else:
            Profile.objects.create(user=user, **profile_data)

        return user


class EmailVerificationSerializer(serializers.Serializer):
    verification_code = serializers.CharField()
    email = serializers.EmailField()

    def validate(self, data):
        verification_code = data.get("verification_code")
        email = data.get("email")

        if not verification_code or not email:
            raise serializers.ValidationError(
                "Email and verification code are required."
            )

        try:
            user = User.objects.get(email=email)
            if verification_code != user.profile.verification_code:
                raise serializers.ValidationError("Invalid verification code")
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")

        return data


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email", None)
        password = data.get("password", None)

        if email and password:
            user = User.objects.filter(email=email).first()

            if user and user.check_password(password):
                if user.profile.is_verified or user.is_staff:
                    refresh = RefreshToken.for_user(user)
                    data["refresh"] = str(refresh)
                    data["access"] = str(refresh.access_token)
                    self.user = user
                else:
                    raise serializers.ValidationError(
                        "Account not verified. Please verify your account."
                    )

            else:
                raise serializers.ValidationError(
                    "Invalid credentials. Please try again."
                )
        else:
            raise serializers.ValidationError("Both email and password are required.")

        return data


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, required=False)
    password = serializers.CharField(write_only=True, required=False)
    profile = ProfileSerializerUp(required=False)
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "confirm_password",
            "profile",
            "token",
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
        if "password" in data and "confirm_password" in data:
            if data["password"] != data["confirm_password"]:
                raise serializers.ValidationError("Passwords do not match.")
        return data

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)

        password = validated_data.get("password")
        if password:
            instance.set_password(password)

        instance.save()

        profile_data = validated_data.get("profile", {})
        profile_instance = instance.profile

        if profile_instance:
            profile_instance.address = profile_data.get(
                "address", profile_instance.address
            )
            profile_instance.phone = profile_data.get("phone", profile_instance.phone)
            profile_instance.save()
        elif profile_data:
            Profile.objects.create(user=instance, **profile_data)

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


class ContactUsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactUsModel
        fields = "__all__"

    def create(self, validated_data):
        return ContactUsModel.objects.create(**validated_data)
