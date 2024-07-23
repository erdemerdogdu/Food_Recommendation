from django.db import models


class Meal(models.Model):
    # Using a string reference to the Restaurant model to avoid circular import issues
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    cuisine_type = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.name} from {self.restaurant.name}"
