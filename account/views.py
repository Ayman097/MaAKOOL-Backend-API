from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .serializer import UserSerializer
from .models import User
import jwt
import datetime


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class LoginView(APIView):
    def post(self, request):
        email = request.data["email"]
        password = request.data["password"]

        user = User.objects.filter(email=email).first()

        if user is None or not user.check_password(password):
            raise AuthenticationFailed("Invalid credentials.")

        payload = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "exp": datetime.datetime.utcnow()
            + datetime.timedelta(minutes=15),  # Shortened expiry time
            "iat": datetime.datetime.utcnow(),
        }

        token = jwt.encode(payload, "your_secret_key", algorithm="HS256")

        response = Response()
        response.set_cookie(key="jwt", value=token, httponly=False)

        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated.")

        try:
            payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
            user = User.objects.filter(id=payload["id"]).first()

            if not user:
                raise AuthenticationFailed("User not found.")

            serializer = UserSerializer(user)
            return Response(serializer.data)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")


class UpdateUserView(APIView):
    def put(self, request):
        token = request.COOKIES.get("jwt")

        if not token:
            raise AuthenticationFailed("Unauthenticated.")

        try:
            payload = jwt.decode(token, "your_secret_key", algorithm="HS256")
            user = User.objects.filter(id=payload["id"]).first()

            if not user:
                raise AuthenticationFailed("User not found.")

            serializer = UserSerializer(instance=user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Unauthenticated.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie("jwt")
        response.data = {"message": "Goodbye"}
        return response
