# backend/accounts/models.py
import random

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    USER_TYPE_USER          = "user"
    USER_TYPE_COACH         = "coach"
    USER_TYPE_ACADEMY_OWNER = "academy_owner"

    USER_TYPES = (
        (USER_TYPE_USER,          "User"),
        (USER_TYPE_COACH,         "Coach"),
        (USER_TYPE_ACADEMY_OWNER, "Academy owner"),
    )

    user_type = models.CharField(
        max_length=20, choices=USER_TYPES, default=USER_TYPE_USER
    )
    phone   = models.CharField(max_length=20, blank=True)
    picture = models.ImageField(upload_to='users/', blank=True, null=True)

    @property
    def is_user(self):
        return self.user_type == self.USER_TYPE_USER

    @property
    def is_coach(self):
        return self.user_type == self.USER_TYPE_COACH

    @property
    def is_academy_owner(self):
        return self.user_type == self.USER_TYPE_ACADEMY_OWNER


class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="password_reset_otps"
    )
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def generate_otp():
        return str(random.randint(100000, 999999))

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
