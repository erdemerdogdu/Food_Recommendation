from django.urls import path
from .views import (RestaurantListView, MyRestaurantsView, AddRestaurantView, EditRestaurantView, DeleteRestaurantView,
                    RestaurantInfoView, RestaurantsMapView, ReviewsStatisticsView)

urlpatterns = [
    path('', RestaurantListView.as_view(), name='restaurant_list'),
    path('ajax/reviews_statistics/<int:restaurant_id>/', ReviewsStatisticsView.as_view(), name='reviews_statistics'),
    path('myrestaurants/', MyRestaurantsView.as_view(), name='my_restaurants'),
    path('add/', AddRestaurantView.as_view(), name='add_restaurant'),
    path('info/<int:restaurant_id>', RestaurantInfoView.as_view(), name='map_restaurant'),
    path('map', RestaurantsMapView.as_view(), name='map_restaurant'),
    path('<int:restaurant_id>/edit/', EditRestaurantView.as_view(), name='edit_restaurant'),
    path('<int:restaurant_id>/delete/', DeleteRestaurantView.as_view(), name='delete_restaurant'),
]
