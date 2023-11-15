from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer
from .serializers import UserLoginSerializer
from .serializers import UserProfileUpdateSerializer
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LogoutSerializer
from rest_framework_simplejwt.tokens import OutstandingToken, BlacklistedToken
from .models import RevokedToken





class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(data)

class UserLoginView(TokenObtainPairView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        response = super().post(request, *args, **kwargs)
        user = serializer.user
        refresh = response.data['refresh']
        access = response.data['access']
        user_data = {
                        'email': user.email,
                        'username': user.username,
                        'address': user.profile.address,
                        'phone': user.profile.phone,
                        'id': user.id
                    }

        response.data.update({'user': user_data})
        return response




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

            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        except OutstandingToken.DoesNotExist:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

