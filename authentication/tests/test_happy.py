from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APIClient


User = get_user_model()


class AuthenticationHappyTests(TestCase):
    """Test successful authentication flows."""

    def setUp(self):
        """Set up test client."""
        self.client = APIClient()

    def test_register_user(self):
        """Test user registration succeeds."""
        response = self.client.post(
            reverse('register'),
            {
                'email': 'user@example.com',
                'password': 'Test12345!',
                'confirmed_password': 'Test12345!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['email'], 'user@example.com')
        self.assertIn('token', response.data)

    def test_activate_user(self):
        """Test user activation succeeds."""
        user = User.objects.create_user(
            email='user@example.com',
            password='Test12345!',
            is_active=False,
        )
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            reverse(
                'activate-account',
                kwargs={'uidb64': uid, 'token': token},
            )
        )

        user.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.is_active)
        self.assertEqual(
            response.data['message'],
            'Account successfully activated.',
        )

    def test_login_user(self):
        """Test active user login succeeds."""
        User.objects.create_user(
            email='user@example.com',
            password='Test12345!',
            is_active=True,
        )

        response = self.client.post(
            reverse('login'),
            {
                'email': 'user@example.com',
                'password': 'Test12345!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Login successful')
        self.assertIn('access_token', response.cookies)
        self.assertIn('refresh_token', response.cookies)