from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    ChangePasswordView,
    get_user_profile_by_id,
)

app_name = "users_api"

urlpatterns = [
    # Authentication endpoints
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("login/", UserLoginView.as_view(), name="user-login"),
    path("logout/", UserLogoutView.as_view(), name="user-logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    # User profile endpoints
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("profile/<int:user_id>/", get_user_profile_by_id, name="user-profile-by-id"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
