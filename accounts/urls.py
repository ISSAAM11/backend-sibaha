from django.urls import path

from .views import (
    ChangePasswordView,
    CoachDetailView,
    CoachListView,
    ForgotPasswordView,
    LoginView,
    ProfileView,
    RefreshTokenView,
    RegisterView,
    ResetPasswordView,
    VerifyOTPView,
)

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot_password"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("coaches/", CoachListView.as_view(), name="coach_list"),
    path("coaches/<int:pk>/", CoachDetailView.as_view(), name="coach_detail"),
]
