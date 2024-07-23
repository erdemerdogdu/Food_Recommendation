from django.db import migrations

def move_cuisine_type(apps, schema_editor):
    Restaurant = apps.get_model('restaurants', 'Restaurant')
    MealModel = apps.get_model('meals', 'Meal')

    for meal in MealModel.objects.all():
        meal.cuisine_type = meal.restaurant.cuisine_type
        meal.save()

class Migration(migrations.Migration):

    dependencies = [
        ('meals', '0002_meal_cuisine_type'), # Add dependency to the latest migration of restaurants app
    ]

    operations = [
        migrations.RunPython(move_cuisine_type),
    ]