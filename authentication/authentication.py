from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate users with JWT access token from HttpOnly cookie."""

    def authenticate(self, request):
        access_token = request.COOKIES.get(settings.AUTH_COOKIE_ACCESS)

        if not access_token:
            return None

        validated_token = self.get_validated_token(access_token)
        return self.get_user(validated_token), validated_token