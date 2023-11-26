from django.urls import path
from .views import RegisterView, UserLoginView
from .views import *


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", UserLoginView.as_view(), name="login"),
    path("staff_login/", StaffLoginView.as_view(), name="staff_login"),
    path("update/", UserProfileUpdateView.as_view(), name="user-profile-update"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("profile/<int:user_id>/", UserProfileView.as_view(), name="user-profile"),
    path("reset-password/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "reset-password/confirm/<str:uidb64>/<str:token>/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "profile/image/update/",
        ProfileImageUpdateView.as_view(),
        name="profile-image-update",
    ),
    path("verify-email/", EmailVerificationView.as_view(), name="verify_email"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("contact_us/", ContactUsListView.as_view(), name="contact_us"),
    path(
        "contact_us/<int:pk>/delete/",
        ContactUsDetailView.as_view(),
        name="contact_us_delete",
    ),
]
