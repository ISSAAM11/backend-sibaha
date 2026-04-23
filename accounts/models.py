# backend/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_ADMIN  = "admin"
    USER_TYPE_COACH  = "coach"
    USER_TYPE_USER   = "user"

    USER_TYPES = (
        (USER_TYPE_ADMIN, "Admin"),
        (USER_TYPE_COACH, "Coach"),
        (USER_TYPE_USER, "User"),
    )

    user_type = models.CharField(
        max_length=10, choices=USER_TYPES, default=USER_TYPE_USER
    )

    @property
    def is_coach(self):
        return self.user_type == self.USER_TYPE_COACH

    @property
    def is_admin(self):
        # you can also rely on is_superuser/is_staff if you like
        return self.user_type == self.USER_TYPE_ADMIN
