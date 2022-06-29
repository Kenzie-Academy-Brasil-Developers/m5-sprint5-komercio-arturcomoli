from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def _create_user(
        self, email, password, is_seller, is_superuser, **extra_fields
    ):
        now = timezone.now()

        if not email:
            raise ValueError("Email is a required field")

        email = self.normalize_email(email)

        user = self.model(
            email=email,
            is_seller=is_seller,
            is_superuser=is_superuser,
            date_joined=now,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, is_seller, **extra_fields):
        return self._create_user(
            email, password, is_seller, False, **extra_fields
        )

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, False, True, **extra_fields)
