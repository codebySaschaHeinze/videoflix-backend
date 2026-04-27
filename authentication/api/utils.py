from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def generate_activation_token(user):
    """Generate uid and token for account activation."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token

def get_user_from_uid(uidb64, user_model):
    """Return user instance from encoded uid"""
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        return user_model.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        return None
    
def generate_password_reset_token(user):
    """Generate uid and token for password reset."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token

def send_password_reset_email(user):
    """Send password reset email with frontend reset link."""
    uid, token = generate_password_reset_token(user)
    reset_link = (
        f'{settings.FRONTEND_URL}/reset-password'
        f'?uid={uid}&token={token}'
    )

    send_mail(
        subject='Reset your Videoflix password',
        message=(
            'You requested a password reset.\n\n'
            f'Use this link to set a new password:\n{reset_link}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_activation_email(user):
    """Send account activation email with frontend activation link."""
    uid, token = generate_activation_token(user)
    activation_link = (
        f'{settings.FRONTEND_URL}/activate'
        f'?uid={uid}&token={token}'
    )

    send_mail(
        subject='Activate your Videoflix account.',
        message=(
            'Welcome to Videoflix.\n\n'
            f'Activate your account with this link:\n{activation_link}'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

    return uid, token