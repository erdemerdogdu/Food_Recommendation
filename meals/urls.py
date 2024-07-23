from django.urls import path
from .views import MealsByRestaurantView,MealsByCuisinesView,AddMealView,MyMealsView,MealEditView,DeleteMealView

urlpatterns = [
    path('<int:restaurant_id>/', MealsByRestaurantView.as_view(), name='meal_list'),
    path('', MealsByCuisinesView.as_view(), name='meal_cuisinelist'),
    path('add/<int:restaurant_id>', AddMealView.as_view(), name='addmeal'),
    path('mymeals/<int:restaurant_id>/', MyMealsView.as_view(), name='my_meals'),
    path('edit/<int:meal_id>', MealEditView.as_view(), name='editmeal'),
    path('delete/<int:meal_id>', DeleteMealView.as_view(), name='deletemeal'),
]