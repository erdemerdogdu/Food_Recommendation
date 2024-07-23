from django.urls import path
from .views import AddReviewView, RestaurantReviewView, MyReviewsView, MealReviewView, EditReviewView, ReviewDeleteView

urlpatterns = [
    path('add_review/<int:meal_id>/', AddReviewView.as_view(), name='add_review'),
    path('<int:restaurant_id>/', RestaurantReviewView.as_view(), name='restaurant_review'),
    path('myreviews/', MyReviewsView.as_view(), name='my_reviews'),
    path('mealreviews/<int:meal_id>', MealReviewView.as_view(), name='my_reviews'),
    path('myreviews/edit/<int:review_id>', EditReviewView.as_view(), name='edit_reviews'),
    path('myreviews/delete/<int:review_id>/', ReviewDeleteView.as_view(), name='delete_review'),
]
