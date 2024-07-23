from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.


class Restaurant(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    opening_hours = models.CharField(max_length=255, null=True, blank=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='restaurants_added')

    def __str__(self):
        return f"{self.name} by {self.owner.first_name}"
