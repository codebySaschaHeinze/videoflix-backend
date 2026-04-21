from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.views import APIView

from content.api.serializers import LoginSerializer, RegisterSerializer
from content.api.utils import generate_activation_token, get_user_from_uid


User = get_user_model()


class RegisterView(APIView):
    """Handle user registration."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Register a new inactive user."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        uid, token = generate_activation_token(user)

        return Response(
            {
                'user': {
                    'id': user.id,
                    'email': user.email,
                },
                'token': token,
                'uid': uid,
            },
            status=status.HTTP_201_CREATED
        )
    

class ActivateAccountView(APIView):
    """Activate user account with uid and token."""

    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Activate an inactive user account."""
        user = get_user_from_uid(uidb64, User)

        if not user or not default_token_generator.check_token(user, token):
            return Response(
                {'message': 'Activation failed.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        user.is_active = True
        user.save(update_fields=['is_active'])

        return Response(
            {'message': 'Account successfully activated.'},
            status=status.HTTP_200_OK,
        )
    

class LoginView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        """Log in in user and set JWT cookies."""
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                'detail': 'Login successful.',
                'user': {
                    'id': user.id,
                    'username': user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key=settings.AUTH_COOKIE_ACCESS,
            value=access_token,
            httponly=settings.AUTH_COOKIE_HTTP_ONLY,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
        )
        response.set_cookie(
            key=settings.AUTH_COOKIE_REFRESH,
            value=refresh_token,
            httponly=settings.AUTH_COOKIE_HTTP_ONLY,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
        )

        return response
    

class TokenRefreshView(APIView):
    """Refresh access token from refresh cookie."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Create a new access token from refresh token cookie."""
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except TokenError:
            return Response(
                {'detail': 'invalid refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        response = Response(
            {
                'detail': 'Token refreshed.',
                'access': access_token,
            },
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key=settings.AUTH_COOKIE_ACCESS,
            value=access_token,
            httponly=settings.AUTH_COOKIE_HTTP_ONLY,
            secure=settings.AUTH_COOKIE_SECURE,
            samesite=settings.AUTH_COOKIE_SAMESITE,
        )

        return response
    

class LogoutView(APIView):
    """Log out user and invalidate refresh token."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Blacklist refresh token and clear auth cookies."""
        refresh_token = request.COOKIES.get(settings.AUTH_COOKIE_REFRESH)

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token missing.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response(
                {'detail': 'Invalid refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        
        response = Response(
            {
                'detail': (
                    'Logout successful! All tokens will be deleted'
                    'Refresh token is now invalid.'
                )
            },
            status=status.HTTP_200_OK,
        )

        response.delete_cookie(settings.AUTH_COOKIE_ACCESS)
        response.delete_cookie(settings.AUTH_COOKIE_REFRESH)

        return response