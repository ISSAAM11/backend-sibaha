# backend/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


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
    phone = models.CharField(max_length=20, blank=True)

    @property
    def is_user(self):
        return self.user_type == self.USER_TYPE_USER

    @property
    def is_coach(self):
        return self.user_type == self.USER_TYPE_COACH

    @property
    def is_academy_owner(self):
        return self.user_type == self.USER_TYPE_ACADEMY_OWNER
