from django.urls import path
from .views import user_registration, user_login, user_logout

urlpatterns = [
    path('register/', user_registration, name='user-registration'),
    path('login/', user_login, name='user-login'),
    path('logout/', user_logout, name='user-logout'),
]