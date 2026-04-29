from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


User = get_user_model()


class AuthenticationUnhappyTests(APITestCase):
    """Tests failed authentication flows."""

    def setUp(self):
        """Set up test client and reusable user."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@user.de',
            password='test123!',
            is_active=True,
        )

    def test_register_with_existing_email(self):
        """Test registration fails when email already exists."""
        response = self.client.post(
            reverse('register'),
            {
                'email': 'test@user.de',
                'password': 'test123!',
                'confirmed_password': 'test123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_password(self):
        """Test login fails with wrong password."""
        response = self.client.post(
            reverse('login'),
            {
                'email': 'test@user.de',
                'password': 'WRONG123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_inactive_user(self):
        """Test inactive user cannot log in."""
        inactive_user = User.objects.create_user(
            email='inactive@user.de',
            password='test123!',
            is_active=False, 
        )

        response = self.client.post(
            reverse('login'),
            {
                'email': inactive_user.email,
                'password': 'test123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_with_invalid_token(self):
        """Test activation fails with invalid token."""
        inactive_user = User.objects.create_user(
            email='inactive@user.de',
            password='test123!',
            is_active=False,
        )

        response = self.client.get(
            reverse(
                'activate-account',
                kwargs={
                    'uidb64': 'invalid-uid',
                    'token': 'invalid-token',
                },
            )
        )

        inactive_user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(inactive_user.is_active)

    def test_refresh_without_cookie(self):
        """Test token refresh fails without refresh cookie."""
        response = self.client.post(reverse('token-refresh'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_without_cookie(self):
        """Test logout fails without refresh cookie."""
        response = self.client.post(reverse('logout'))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)