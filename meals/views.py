
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Meal
from .forms import MealForm
from django.utils.decorators import method_decorator
from .decorators import restaurant_user_required
from django.contrib import messages
from django.apps import apps
Restaurant = apps.get_model('restaurants', 'Restaurant')


class MealListView(View):
    def get(self, request):
        meals = Meal.objects.All()
        return render(request, 'meals/meal_list.html', {'meals': meals})


class MealsByRestaurantView(View):
    def get(self, request, restaurant_id):
        meals = Meal.objects.filter(restaurant_id=restaurant_id)
        restaurant_name = meals.first().restaurant.name if meals else None
        return render(request, 'meals/meal_list.html', {'meals': meals, 'restaurant_name': restaurant_name})


class MealsByCuisinesView(View):
    def get(self, request):
        meals = Meal.objects.all().select_related('restaurant')
        cuisines = {}

        for meal in meals:
            cuisine = meal.cuisine_type
            if cuisine not in cuisines:
                cuisines[cuisine] = []
            cuisines[cuisine].append(meal)

        return render(request, 'meals/meals_by_cuisines.html', {'cuisines': cuisines})


@method_decorator(restaurant_user_required, name='dispatch')
class AddMealView(View):
    def get(self, request, restaurant_id):
        restaurant = Restaurant.objects.get(id=restaurant_id, owner_id= request.user.id)
        form = MealForm(initial={'restaurant': restaurant})
        return render(request, 'meals/add_meal.html', {'form': form})

    def post(self, request, restaurant_id):
        form = MealForm(request.POST)
        if form.is_valid():
            meal = form.save(commit=False)
            meal.restaurant_id = restaurant_id
            meal.save()
            messages.success(request, f'Meal named {meal.name} added successfully!')
            return redirect(f'/meals/mymeals/{meal.restaurant.id}')
        return render(request, 'meals/add_meal.html', {'form': form})


@method_decorator(restaurant_user_required, name='dispatch')
class MyMealsView(View):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner_id= request.user.id)
        meals = Meal.objects.filter(restaurant=restaurant)

        return render(request, 'meals/mymeals.html', {
            'restaurant': restaurant,
            'meals': meals,
        })


@method_decorator(restaurant_user_required, name='dispatch')
class MealEditView(View):
    def get(self, request, meal_id):
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner_id=request.user.id)
        form = MealForm(instance=meal)
        return render(request, 'meals/edit_meal.html', {'form': form})

    def post(self, request, meal_id):
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner_id=request.user.id)
        form = MealForm(request.POST, instance=meal)
        if form.is_valid():
            form.save()
            messages.success(request, f'Meal named {meal.name} edited successfully!')
            return redirect(f'/meals/mymeals/{meal.restaurant.id}/')  # Redirect to meal detail page or another page
        return render(request, 'meals/edit_meal.html', {'form': form})


@method_decorator(restaurant_user_required, name='dispatch')
class DeleteMealView(View):
    def get(self, request, meal_id):
        meal = get_object_or_404(Meal, id=meal_id, restaurant__owner_id=request.user.id)
        meal.delete()
        messages.success(request, f'Meal named {meal.name} deleted successfully!')
        return redirect(f'/meals/mymeals/{meal.restaurant.id}')
