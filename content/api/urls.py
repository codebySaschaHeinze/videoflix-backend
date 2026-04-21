from django.urls import path

from content.api.views import RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
]