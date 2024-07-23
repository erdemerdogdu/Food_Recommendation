from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    username = models.CharField(max_length=150, unique=False, blank=True, null=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["username", 'first_name', 'last_name']

    def __str__(self):
        return f"{self.email} by {self.first_name} {self.last_name}"
