from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets
import string

User = get_user_model()

class LoginView(APIView):
    """
    Login with email and password
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response({
                'detail': 'Email and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find user by email
            user = User.objects.filter(email=email).first()
            if not user:
                return Response({
                    'detail': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check password
            if not user.check_password(password):
                return Response({
                    'detail': 'Invalid email or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Check if user is active
            if not user.is_active:
                return Response({
                    'detail': 'Account is deactivated'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': {
                        'id': user.role.id,
                        'name': user.role.name,
                        'display_name': user.role.display_name
                    } if user.role else None
                }
            })
            
        except Exception as e:
            return Response({
                'detail': f'Login error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetRequestView(APIView):
    """
    Request password reset - sends reset token to user's email
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'detail': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find user by email
            user = User.objects.filter(email=email).first()
            if not user:
                # For security, don't reveal if email exists or not
                return Response({
                    'detail': 'If the email exists, a password reset link has been sent.'
                }, status=status.HTTP_200_OK)
            
            # Check if user is active
            if not user.is_active:
                return Response({
                    'detail': 'Account is deactivated'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Generate secure reset token
            reset_token = self._generate_reset_token()
            
            # Save token and timestamp
            user.password_reset_token = reset_token
            user.password_reset_token_created_at = timezone.now()
            user.save(update_fields=['password_reset_token', 'password_reset_token_created_at'])
            
            # Send email with reset link
            self._send_password_reset_email(user, reset_token)
            
            return Response({
                'detail': 'If the email exists, a password reset link has been sent.',
                'message': 'Check your email for password reset instructions.'
            })
            
        except Exception as e:
            return Response({
                'detail': f'Password reset request error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _generate_reset_token(self):
        """Generate a secure random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def _send_password_reset_email(self, user, reset_token):
        """Send password reset email"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        subject = 'Password Reset Request - Farm Management System'
        message = f"""
Hello {user.first_name or user.username},

You have requested to reset your password for the Farm Management System.

Click the link below to reset your password:
{reset_url}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email.

Best regards,
Farm Management System Team
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send password reset email: {e}")


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset with token and new password
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        
        if not token or not new_password:
            return Response({
                'detail': 'Token and new password are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({
                'detail': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Find user with valid token
            user = User.objects.filter(
                password_reset_token=token,
                password_reset_token_created_at__isnull=False
            ).first()
            
            if not user:
                return Response({
                    'detail': 'Invalid or expired reset token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if token is expired (1 hour)
            token_age = timezone.now() - user.password_reset_token_created_at
            if token_age > timedelta(hours=1):
                # Clear expired token
                user.password_reset_token = None
                user.password_reset_token_created_at = None
                user.save(update_fields=['password_reset_token', 'password_reset_token_created_at'])
                
                return Response({
                    'detail': 'Reset token has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if user is active
            if not user.is_active:
                return Response({
                    'detail': 'Account is deactivated'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(new_password)
            
            # Clear reset token
            user.password_reset_token = None
            user.password_reset_token_created_at = None
            
            user.save(update_fields=['password', 'password_reset_token', 'password_reset_token_created_at'])
            
            return Response({
                'detail': 'Password has been reset successfully',
                'message': 'You can now login with your new password.'
            })
            
        except Exception as e:
            return Response({
                'detail': f'Password reset error: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
