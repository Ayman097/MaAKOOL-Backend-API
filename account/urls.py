# from django.urls import path
# from . import views
# from .views import UserDetailsView
# from rest_framework_simplejwt.views import TokenRefreshView

# urlpatterns = [
#     path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('register/', views.RegisterView.as_view(), name='auth_register'),
#     path('test/', views.testEndPoint, name='test'),
#     path('users/<int:pk>/', UserDetailsView.as_view(), name='user-detail'),
#     path('', views.getRoutes),
# ]


from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView, UpdateUserView

urlpatterns = [
    path('register', RegisterView.as_view()),
    path('login', LoginView.as_view()),
    path('user', UserView.as_view()),
    path('update-user', UpdateUserView.as_view()),
    path('logout', LogoutView.as_view()),
]
