from django.urls import path
from .views import RegisterView, UserLoginView
from .views import UserProfileUpdateView, TokenObtainPairView
from .views import LogoutView
from .views import UserProfileView
from .views import PasswordResetView, PasswordResetConfirmView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path(
        "update/<user_id>", UserProfileUpdateView.as_view(), name="user-profile-update"
    ),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("profile/<user_id>", UserProfileView.as_view(), name="user-profile"),
    path("reset-password/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "reset-password/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("logout/", LogoutView.as_view(), name="logout"),
]
