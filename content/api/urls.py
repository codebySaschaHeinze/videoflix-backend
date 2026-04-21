from django.urls import path

from content.api.views import (
    ActivateAccountView,
    LoginView,
    LogoutView,
    RegisterView,
    TokenRefreshView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate-account'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]