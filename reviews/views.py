from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import ReviewForm
from .models import Review
from django.db.models import Avg, F, Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.decorators import method_decorator
from .decorators import normal_user_required
from django.contrib import messages
from django.apps import apps

MealModel = apps.get_model('meals', 'Meal')
Restaurant = apps.get_model('restaurants', 'Restaurant')


@method_decorator(normal_user_required, name='dispatch')
class AddReviewView(View):
    def get(self, request, meal_id):
        meal = get_object_or_404(MealModel, id=meal_id)
        form = ReviewForm(initial={'meal': meal})
        return render(request, 'reviews/add_review.html', {'form': form, 'meal': meal})

    def post(self, request, meal_id):
        meal = get_object_or_404(MealModel, id=meal_id)
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.meal = meal
            review.save()
            messages.success(request, f'Review added successfully!')
            return redirect(f'/reviews/myreviews')
        return render(request, 'reviews/add_review.html', {'form': form, 'meal': meal})


class RestaurantReviewView(View):
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        meals = MealModel.objects.filter(restaurant=restaurant)
        reviews = Review.objects.filter(meal__in=meals).order_by('-created_at')
        summaries = []
        if reviews.exists():

            avg_delivery = reviews.aggregate(Avg('delivery_rating'))['delivery_rating__avg']
            avg_taste = reviews.aggregate(Avg('taste_rating'))['taste_rating__avg']
            avg_service = reviews.aggregate(Avg('service_rating'))['service_rating__avg']
            total_avg = (avg_delivery + avg_taste + avg_service) / 3
            review_count = reviews.count()

            meals_with_reviews = meals.annotate(
                avg_delivery=Avg('review__delivery_rating'),
                avg_taste=Avg('review__taste_rating'),
                avg_service=Avg('review__service_rating'),
                total_avg_rating=(F('avg_delivery') + F('avg_taste') + F('avg_service')) / 3,
                review_count=Count('review')  # Count total number of reviews for each meal
            ).filter(
                review_count__gt=0  # Only include meals with at least one review
            ).order_by('-total_avg_rating')

            # Find the best meal based on highest average rating among meals with reviews
            best_meal = meals_with_reviews.first()

            summaries.append({
                'restaurant': restaurant,
                'avg_delivery': avg_delivery,
                'avg_taste': avg_taste,
                'avg_service': avg_service,
                'total_avg': total_avg,
                'review_count': review_count,
                'best_meal': best_meal,
            })
        else:
            # Handle case where there are no reviews
            summaries.append({
                'restaurant': restaurant,
                'avg_delivery': 0,
                'avg_taste': 0,
                'avg_service': 0,
                'total_avg': 0,
                'review_count': 0,
                'best_meal': None,
            })

        paginator = Paginator(reviews, 10)  # Show 20 reviews per page

        page_number = request.GET.get('page')
        try:
            reviews = paginator.page(page_number)
        except PageNotAnInteger:
            reviews = paginator.page(1)
        except EmptyPage:
            reviews = paginator.page(paginator.num_pages)

        return render(request, 'reviews/restaurant_reviews.html', {
            'reviews': reviews,
            'restaurant': restaurant,
            "summaries": summaries,
        })


@method_decorator(normal_user_required, name='dispatch')
class MyReviewsView(View):
    def get(self, request):
        search_query = request.GET.get('search', '')
        reviews = Review.objects.filter(user=request.user).order_by("-created_at")

        if search_query:
            reviews = reviews.filter(
                Q(comment__icontains=search_query) |
                Q(meal__name__icontains=search_query)
            )

        paginator = Paginator(reviews, 10)  # Show 10 reviews per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'reviews': page_obj,
            'search_query': search_query
        }

        return render(request, 'reviews/my_reviews.html', context)


class MealReviewView(View):
    def get(self, request, meal_id):
        meal = get_object_or_404(MealModel, id=meal_id)
        reviews = Review.objects.filter(meal=meal).order_by('-created_at')

        paginator = Paginator(reviews, 10)  # Show 20 reviews per page

        page_number = request.GET.get('page')
        try:
            reviews = paginator.page(page_number)
        except PageNotAnInteger:
            reviews = paginator.page(1)
        except EmptyPage:
            reviews = paginator.page(paginator.num_pages)

        return render(request, 'reviews/meal_reviews.html', {
            'reviews': reviews,
            'meal': meal,
        })


@method_decorator(normal_user_required, name='dispatch')
class EditReviewView(View):
    def get(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        form = ReviewForm(instance=review)
        return render(request, 'reviews/edit_review.html', {'form': form, 'review': review})

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save(commit=False)
            review.created_at = timezone.now()
            review.save()
            messages.success(request, f'Review edited successfully!')
            return redirect('/reviews/myreviews')
        return render(request, 'reviews/edit_review.html', {'form': form, 'review': review})


@method_decorator(normal_user_required, name='dispatch')
class ReviewDeleteView(View):
    def get(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, user=request.user)
        review.delete()
        messages.success(request, f'Review deleted successfully!')
        return redirect('/reviews/myreviews')
