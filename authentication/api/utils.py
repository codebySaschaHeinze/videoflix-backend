from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


def generate_activation_token(user):
    """Generate uid and token for account activation."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return uid, token

def send_html_email(subject, text_content, html_content, recipient):
    """Send email with plain text fallback and HTML content."""
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send(fail_silently=False)

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

    subject = 'Reset your password'
    text_content = (
        'Hello,\n\n'
        'We recently received a request to reset your password. '
        f'If you made this request, please use this link:\n{reset_link}\n\n'
        'Please note that for security reasons, this link is only valid for 24 hours.\n\n'
        'If you did not request a password reset, please ignore this email.\n\n'
        'Best regards,\n'
        'Your Videoflix team!'
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <body style="margin:0; padding:0; background-color:#ffffff; font-family:Arial, Helvetica, sans-serif; color:#333333;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:40px 24px;">
            <tr>
                <td style="max-width:1100px; margin:0 auto; font-size:18px; line-height:1.5;">
                    <p style="margin:0 0 32px 0;">
                        Hello,
                    </p>

                    <p style="margin:0 0 32px 0;">
                        We recently received a request to reset your password. If you made this request,
                        please click on the following link to reset your password:
                    </p>

                    <p style="margin:0 0 32px 0;">
                        <a href="{reset_link}"
                           style="display:inline-block; background-color:#1825e8; color:#ffffff; text-decoration:none; padding:16px 32px; border-radius:40px; font-size:20px; font-weight:700;">
                            Reset password
                        </a>
                    </p>

                    <p style="margin:0 0 32px 0;">
                        Please note that for security reasons, this link is only valid for 24 hours.
                    </p>

                    <p style="margin:0 0 32px 0;">
                        If you did not request a password reset, please ignore this email.
                    </p>

                    <p style="margin:0 0 32px 0;">
                        Best regards,
                    </p>

                    <p style="margin:0 0 32px 0;">
                        Your Videoflix team!
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    send_html_email(subject, text_content, html_content, user.email)


def send_activation_email(user):
    """Send account activation email with frontend activation link."""
    uid, token = generate_activation_token(user)
    activation_link = (
        f'{settings.FRONTEND_URL}/activate'
        f'?uid={uid}&token={token}'
    )

    subject = 'Confirm your email'
    text_content = (
        'Dear user,\n\n'
        'Thank you for registering with Videoflix. '
        'To complete your registration and verify your email address, '
        f'please use this link:\n{activation_link}\n\n'
        'If you did not create an account with us, please disregard this email.\n\n'
        'Best regards,\n'
        'Your Videoflix Team.'
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <body style="margin:0; padding:0; background-color:#ffffff; font-family:Arial, Helvetica, sans-serif; color:#333333;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:40px 24px;">
            <tr>
                <td style="max-width:900px; margin:0 auto; font-size:18px; line-height:1.5;">
                    <p style="margin:0 0 8px 0;">
                        Dear user,
                    </p>

                    <p style="margin:0 0 32px 0;">
                        Thank you for registering with <span style="color:#1f22e8;">Videoflix</span>.
                        To complete your registration and verify your email address, please click the link below:
                    </p>

                    <p style="margin:0 0 32px 0;">
                        <a href="{activation_link}"
                           style="display:inline-block; background-color:#1825e8; color:#ffffff; text-decoration:none; padding:16px 32px; border-radius:40px; font-size:20px; font-weight:700;">
                            Activate account
                        </a>
                    </p>

                    <p style="margin:0 0 32px 0;">
                        If you did not create an account with us, please disregard this email.
                    </p>

                    <p style="margin:0 0 32px 0;">
                        Best regards,
                    </p>

                    <p style="margin:0;">
                        Your Videoflix Team.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    send_html_email(subject, text_content, html_content, user.email)

    return uid, token