from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .models import Restaurant
from django.db.models import Avg
from .decorators import restaurant_user_required
from django.utils.decorators import method_decorator
from .forms import RestaurantForm
from django.contrib import messages
from django.apps import apps
Review = apps.get_model('reviews', 'Review')


class RestaurantListView(View):
    def get(self, request):
        restaurants = Restaurant.objects.all()
        restaurant_data = []

        for restaurant in restaurants:
            reviews = Review.objects.filter(meal__restaurant=restaurant)

            total_reviews = reviews.count()
            avg_service_rating = reviews.aggregate(Avg('service_rating'))['service_rating__avg']  or 0
            avg_taste_rating = reviews.aggregate(Avg('taste_rating'))['taste_rating__avg']  or 0
            avg_delivery_rating = reviews.aggregate(Avg('delivery_rating'))['delivery_rating__avg']  or 0
            avg_total_rating = (avg_service_rating + avg_taste_rating + avg_delivery_rating) / 3

            restaurant_data.append({
                'restaurant': restaurant,
                'total_reviews': total_reviews,
                'avg_total_rating': avg_total_rating,
            })

        context = {
            'restaurant_data': restaurant_data,
        }
        return render(request, 'restaurants/restaurant_list.html', context)


class ReviewsStatisticsView(View):
    def get(self, request, restaurant_id):
        restaurant = Restaurant.objects.get(pk=restaurant_id)
        reviews = Review.objects.filter(meal__restaurant=restaurant)

        # Calculate statistics
        total_reviews = reviews.count()
        avg_service_rating = reviews.aggregate(Avg('service_rating'))['service_rating__avg']
        avg_taste_rating = reviews.aggregate(Avg('taste_rating'))['taste_rating__avg']
        avg_delivery_rating = reviews.aggregate(Avg('delivery_rating'))['delivery_rating__avg']

        context = {
            'total_reviews': total_reviews,
            'avg_service_rating': avg_service_rating,
            'avg_taste_rating': avg_taste_rating,
            'avg_delivery_rating': avg_delivery_rating,
        }

        return render(request, 'restaurants/reviews_statistics.html', context)


@method_decorator(restaurant_user_required, name='dispatch')
class MyRestaurantsView(View):
    def get(self, request):
        user = request.user
        restaurants = Restaurant.objects.filter(owner=user)
        return render(request, 'restaurants/my_restaurants.html', {'restaurants': restaurants})


@method_decorator(restaurant_user_required, name='dispatch')
class AddRestaurantView(View):
    def get(self, request):
        form = RestaurantForm()
        return render(request, 'restaurants/add_restaurant.html', {'form': form})

    def post(self, request):
        form = RestaurantForm(request.POST)
        if form.is_valid():
            restaurant = form.save(commit=False)
            restaurant.owner = request.user
            restaurant.save()
            messages.success(request, f'Restaurant named {restaurant.name} added successfully!')
            return redirect('my_restaurants')
        return render(request, 'restaurants/add_restaurant.html', {'form': form})


@method_decorator(restaurant_user_required, name='dispatch')
class EditRestaurantView(View):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner_id=request.user.id)
        form = RestaurantForm(instance=restaurant)
        return render(request, 'restaurants/edit_restaurant.html', {'form': form, 'restaurant': restaurant})

    def post(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner_id=request.user.id)
        form = RestaurantForm(request.POST, instance=restaurant)
        if form.is_valid():
            form.save()
            messages.success(request, f'Restaurant named {restaurant.name} edited successfully!')
            return redirect('/restaurants/myrestaurants',)
        return render(request, 'restaurants/edit_restaurant.html', {'form': form, 'restaurant': restaurant})


@method_decorator(restaurant_user_required, name='dispatch')
class DeleteRestaurantView(View):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id, owner_id=request.user.id)
        restaurant.delete()
        messages.success(request, f'Restaurant named {restaurant.name} deleted successfully!')
        return redirect('/restaurants/myrestaurants')  # Redirect to the 'my_restaurants' page


class RestaurantInfoView(View):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        return render(request, 'restaurants/restaurant_map.html', {'restaurant': restaurant})


class RestaurantsMapView(View):
    def get(self, request,):
        restaurants = Restaurant.objects.filter(owner=request.user)
        return render(request, 'restaurants/myrestaurants_map.html', {'restaurants': restaurants})
