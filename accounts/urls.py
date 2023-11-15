from django.urls import path
from .views import RegisterView, UserLoginView
from .views import UserProfileUpdateView, TokenObtainPairView
from .views import LogoutView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('update/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
