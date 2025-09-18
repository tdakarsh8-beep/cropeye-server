from django.contrib.auth.models import AbstractUser
from django.db import models

class Role(models.Model):
    """
    A database-backed Role. You can assign any number of Django Permissions to it.
    """
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.display_name or self.name

class User(AbstractUser):
    # Temporary: reuse the old 'role' varchar column for the FK
    role = models.ForeignKey(
        Role,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='users',
        db_column='role',
    )

    # Track who created this user (for manager -> field officer hierarchy)
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        help_text="Manager who created this user"
    )

    phone_number    = models.CharField(
        max_length=15, 
        blank=True,
        help_text="Phone number with country code (e.g., +1234567890)"
    )
    otp             = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at  = models.DateTimeField(null=True, blank=True)
    otp_delivery_method = models.CharField(
        max_length=20,
        choices=[
            ('whatsapp', 'WhatsApp'),
            ('email', 'Email'),
        ],
        null=True,
        blank=True,
        help_text="Method used to deliver the last OTP"
    )
    
    # Password reset fields
    password_reset_token = models.CharField(max_length=100, null=True, blank=True)
    password_reset_token_created_at = models.DateTimeField(null=True, blank=True)
    address         = models.TextField(blank=True)
    village         = models.CharField(max_length=100, blank=True)
    state           = models.CharField(max_length=100, blank=True)
    district        = models.CharField(max_length=100, blank=True)
    taluka          = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_joined']

    def __str__(self):
        role = self.role.name if self.role else "NoRole"
        return f"{self.username} ({role})"

    def has_role(self, role_name: str) -> bool:
        return bool(self.role and self.role.name == role_name)

    def has_any_role(self, role_names: list[str]) -> bool:
        return bool(self.role and self.role.name in role_names)

