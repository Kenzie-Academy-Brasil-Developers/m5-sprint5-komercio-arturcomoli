from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.utils import CustomUserManager


# Create your models here.
class Account(AbstractUser):
    username = None
    last_login = None
    is_staff = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_seller = models.BooleanField()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]
    objects = CustomUserManager()
