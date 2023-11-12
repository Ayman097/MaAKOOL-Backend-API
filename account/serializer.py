# from account.models import User, Profile
# from django.contrib.auth.password_validation import validate_password
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
# from rest_framework import serializers
# from rest_framework.validators import UniqueValidator
# from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'


# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['full_name'] = user.profile.full_name
#         token['username'] = user.username
#         token['email'] = user.email
#         token['bio'] = user.profile.bio
#         token['image'] = str(user.profile.image)
#         token['verified'] = user.profile.verified

#         return token

#     def validate(self, attrs):
#         data = super().validate(attrs)
#         user = self.user
#         data['id'] = user.id
#         data['full_name'] = user.profile.full_name
#         data['username'] = user.username
#         data['email'] = user.email
#         data['bio'] = user.profile.bio
#         data['image'] = str(user.profile.image)
#         data['verified'] = user.profile.verified

#         return data


# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     password2 = serializers.CharField(write_only=True, required=True)

#     class Meta:
#         model = User
#         fields = ('id', 'email', 'username', 'password', 'password2')

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError({"password": "Password fields didn't match."})

#         return attrs

#     def create(self, validated_data):
#         user = User.objects.create(
#             username=validated_data['username'],
#             email=validated_data['email']
#         )

#         user.set_password(validated_data['password'])
#         user.save()

#         response_data = {
#             'id': user.id,
#             'email': user.email,
#             'username': user.username,
#             'bio': user.bio,
#             'image': user.image
#         }

#         return response_data



#     def update(self, instance, validated_data):
#         profile_data = validated_data.pop('profile', {})
#         profile = instance.profile

#         instance.username = validated_data.get('username', instance.username)
#         instance.email = validated_data.get('email', instance.email)
#         instance.save()

#         profile.full_name = profile_data.get('full_name', profile.full_name)
#         profile.bio = profile_data.get('bio', profile.bio)
#         profile.image = profile_data.get('image', profile.image)
#         profile.verified = profile_data.get('verified', profile.verified)
#         profile.save()

#         return instance




# class UpdateUserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = '__all__'

#     def update(self, instance, validated_data):
#         instance.username = validated_data.get('username', instance.username)
#         instance.email = validated_data.get('email', instance.email)
#         instance.save()
#         return instance


from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
