from django.urls import path

from content.api.views import ActivateAccountView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate-account'),
]