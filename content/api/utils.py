from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def generate_activation_token(user):
    """Generate uid and token for account activation."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token

def get_user_from_uid(uid64, user_model):
    """Return user instance from encoded uid"""
    try:
        user_id = force_str(urlsafe_base64_decode(uid64))
        return user_model.objects.get(pk=user_id)
    except (TypeError, ValueError, OverflowError, user_model.DoesNotExist):
        return None
    
def generate_password_reset_token(user):
    """Generate uid and token for password reset."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token