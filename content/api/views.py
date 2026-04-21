from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from content.api.serializers import RegisterSerializer
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