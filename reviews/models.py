from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meal = models.ForeignKey('meals.Meal', on_delete=models.CASCADE)
    comment = models.TextField()
    service_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    taste_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    delivery_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.meal.name} Review by  {self.user.first_name}"
