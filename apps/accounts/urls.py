from django.urls import path
from .views import GoogleLoginCustom, GetAccountShowView, SendVerificationCode, VerifyCodeAndRegister, CompleteOnboardingView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token-verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('send-verification-code/', SendVerificationCode.as_view(), name='verification-code'),
    path('verify-code-register/', VerifyCodeAndRegister.as_view(), name='verify-register'),
    path('complete-onboarding/', CompleteOnboardingView.as_view(), name='complete-onboarding'),
    path('user/', GetAccountShowView.as_view(), name='user-data'),
    path('social-login/google/', GoogleLoginCustom.as_view(), name='google_login'),
]

# urlpatterns = [
#     path('user/', GetAccountShowView.as_view(), name='user-data'),
#     path('send-verification-code/', SendVerificationCode.as_view(), name='verification-code'),
#     path('verify-code-register/', VerifyCodeAndRegister.as_view(), name='user-register'),
#     path('login/', LoginView.as_view(), name='login'),
#     path('logout/', LogoutView.as_view(), name='logout'),
#     path('password/change/', PasswordChangeView.as_view(), name='password_change'),
#     path('social-login/google/', GoogleLoginCustom.as_view(), name='google_login'),
# ]
