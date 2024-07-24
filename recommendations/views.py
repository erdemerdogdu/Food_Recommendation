from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.apps import apps
from datetime import timedelta
from django.utils import timezone
from django.db.models import Avg
import pandas as pd
import numpy as np
from textblob import TextBlob
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import euclidean
Restaurant = apps.get_model('restaurants', 'Restaurant')
Review = apps.get_model('reviews', 'Review')
Meal = apps.get_model('meals', 'Meal')
User = apps.get_model('customusers', 'MyUser')

class LoadingView(View):
    def get(self, request):
        return render(request, 'recommendations/loading.html')

class RecommendView(View):
    def get(self, request):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            df, cuisine_indexer = self.prepare_data(request)
            recommended_meals = []
            if df.empty:
                recommended_meals_ids = list(self.no_reviews())
                recommended_meals_ids.append(1)
            else:
                adventurousness = int(request.GET.get('adventurousness', 3))
                recommended_meals_ids = self.hybrid_recommendation(df, request.user.id, adventurousness)

            for meal_id in recommended_meals_ids:
                meal = Meal.objects.get(id=meal_id)
                recommended_meals.append({
                    "id": meal.id,
                    "name": meal.name,
                    "price": meal.price,
                    "cuisine": meal.cuisine_type,
                    "description": meal.description
                })
            return JsonResponse(recommended_meals, safe=False)


    def prepare_data(self, request):
        # User selection must be according to similarity level of the current user
        max_reviews_per_user = 100
        max_users = 10

        current_user_reviews = Review.objects.filter(user=request.user).order_by('-created_at')[:max_reviews_per_user]
        if not current_user_reviews.exists():
            df = pd.DataFrame()
            return df, 0

        other_users = User.objects.exclude(id=request.user.id).filter(review__isnull=False).distinct()[:max_users]

        all_reviews = list(current_user_reviews)
        for user in other_users:
            user_reviews = Review.objects.filter(user=user).order_by('-created_at')[:max_reviews_per_user]
            all_reviews.extend(user_reviews)

        unique_cuisine_types = Meal.objects.values_list('cuisine_type', flat=True).distinct()
        cuisine_indexer = {cuisine: idx for idx, cuisine in enumerate(unique_cuisine_types)}

        review_data = []
        for review in all_reviews:
            sentiment_score = TextBlob(review.comment).sentiment.polarity
            sentiment_rating = self.get_sentiment_rating(sentiment_score)

            review_data.append({
                'user_id': review.user.id,
                'meal_id': review.meal.id,
                'cuisine_type': cuisine_indexer[review.meal.cuisine_type],
                'restaurant_id': review.meal.restaurant.id,
                'service_rating': review.service_rating,
                'taste_rating': review.taste_rating,
                'delivery_rating': review.delivery_rating,
                'sentiment_rating': sentiment_rating,
                'created_at': review.created_at
            })

        df = pd.DataFrame(review_data)
        df['overall_rating'] = df[['service_rating', 'taste_rating', 'delivery_rating']].mean(axis=1)
        df['weighted_rating'] = df['overall_rating'] + 2 * df['sentiment_rating']
        df['time_weight'] = df['created_at'].apply(lambda x: self.calculate_time_weight(x, timezone.now()))
        df['weighted_sum'] = df['weighted_rating'] * df['time_weight']
        return df, cuisine_indexer

    def calculate_time_weight(self, date, current_date):
        if date >= current_date - timedelta(days=30):
            return 2
        elif date >= current_date - timedelta(days=365):
            return 1
        elif date >= current_date - timedelta(days=3 * 365):
            return 0.5
        else:
            return 0

    def get_sentiment_rating(self, sentiment_score):
        if sentiment_score > 0.6:
            return 5
        elif sentiment_score > 0.2:
            return 4
        elif sentiment_score > -0.2:
            return 3
        elif sentiment_score > -0.6:
            return 2
        else:
            return 1

    def euclidean_similarity(self, x, y):
        distance = euclidean(x, y)
        max_distance = 15
        euclidean_score = 1 - (distance / max_distance)
        return euclidean_score

    def no_reviews(self):
        top_ten_meals_ids = Meal.objects.annotate(
            average_rating=(Avg('review__delivery_rating') + Avg('review__service_rating') + Avg(
                'review__taste_rating')) / 3
        ).order_by('-average_rating').values_list('id', flat=True)[:10]

        return top_ten_meals_ids

    def collaborative_filtering(self, df):
        # One User may have multiple reviews for the same meal, so ı get average of weighted_rating
        df_grouped = df.groupby(['meal_id', 'user_id']).agg({
            'weighted_sum': 'sum',
            'time_weight': 'sum'
        }).reset_index()
        df_grouped['weighted_rating'] = df_grouped['weighted_sum'] / df_grouped['time_weight']

        user_item_matrix = df_grouped.pivot_table(index='meal_id', columns='user_id', values='weighted_rating')

        # İn order to fill Nan values with meaningful value, we first get mean of the that meal weighted rating
        # then replace Non values with that instead of 0 because 0 is not so meaningful
        meal_means = df_grouped.groupby('meal_id')['weighted_rating'].mean()
        user_item_matrix = user_item_matrix.apply(lambda meal_row: meal_row.fillna(meal_means[meal_row.name]), axis=1)

        # Other similarity models other than cosine, find the best match
        cosine_similarity_s = cosine_similarity(user_item_matrix)
        cosine_sim_df = pd.DataFrame(cosine_similarity_s, index=user_item_matrix.index, columns=user_item_matrix.index)

        meal_ids = user_item_matrix.index
        euclidean_sim = np.zeros((len(meal_ids), len(meal_ids)))

        for i, meal_id1 in enumerate(meal_ids):
            for j, meal_id2 in enumerate(meal_ids):
                if i != j:
                    euclidean_sim[i, j] = self.euclidean_similarity(user_item_matrix.loc[meal_id1],
                                                                    user_item_matrix.loc[meal_id2])
                else:
                    euclidean_sim[i, j] = 1.0


        euclidean_sim_df = pd.DataFrame(euclidean_sim, index=meal_ids, columns=meal_ids)
        hybrid_similarity = cosine_sim_df * euclidean_sim_df
        return hybrid_similarity

    def recommend_meals_cf(self, meal_similarity_df, user_id, df, adventurousness=5):
        user_meals = df[df['user_id'] == user_id]
        user_reviewed_meals = user_meals['meal_id'].unique()

        # most liked 10 meals has been selected to be compared to find ideal recommendation meals
        top_liked_meals = user_meals.nlargest(10, 'weighted_rating')['meal_id']

        non_reviewed_meals = meal_similarity_df.index.difference(user_reviewed_meals)
        similar_non_meals_scores = meal_similarity_df.loc[non_reviewed_meals, top_liked_meals].mean(axis=1)
        similar_meals_scores = meal_similarity_df.loc[user_reviewed_meals, top_liked_meals].mean(axis=1)
        recommended_non_meals = similar_non_meals_scores.sort_values(ascending=False).index
        recommended_meals = similar_meals_scores.sort_values(ascending=False).index
        total = recommended_meals[:(5-adventurousness)].append(recommended_non_meals[:adventurousness])
        return total

    def cb_recommendation(self, df, user_id, adventurousness):
        all_meals = df.drop_duplicates(subset='meal_id').set_index('meal_id')

        user_reviews = df[df['user_id'] == user_id]
        user_cuisine_preference = user_reviews['cuisine_type'].mode().iloc[0]
        user_restaurant_preference = user_reviews['restaurant_id'].mode().iloc[0]

        user_reviewed_meals = user_reviews['meal_id'].unique()
        non_reviewed_meals = all_meals.index.difference(user_reviewed_meals)

        filtered_non_meals = all_meals.loc[non_reviewed_meals]
        filtered_meals = all_meals.loc[user_reviewed_meals]

        filtered_non_meals = filtered_non_meals[
            (filtered_non_meals['cuisine_type'] == user_cuisine_preference) &
            (filtered_non_meals['restaurant_id'] == user_restaurant_preference)
            ]

        if len(filtered_non_meals) < 5:
            filtered_non_meals = all_meals.loc[non_reviewed_meals]
            filtered_non_meals = filtered_non_meals[
                (filtered_non_meals['cuisine_type'] == user_cuisine_preference)
            ]

        filtered_meals = filtered_meals[
            (filtered_meals['cuisine_type'] == user_cuisine_preference) &
            (filtered_meals['restaurant_id'] == user_restaurant_preference)
            ]

        if len(filtered_meals) < 5:
            filtered_meals = all_meals.loc[user_reviewed_meals]
            filtered_meals = filtered_meals[
                (filtered_meals['cuisine_type'] == user_cuisine_preference)
            ]

        recommended_meals = filtered_meals.sort_values(by='weighted_rating', ascending=False).head(5-adventurousness).index
        recommended_non_meals = filtered_non_meals.sort_values(by='weighted_rating', ascending=False).head(adventurousness).index
        total = recommended_meals.append(recommended_non_meals)
        return total

    def hybrid_recommendation(self, df, user_id, adventurousness):
        # REMAKE THE MEAL SELECTION CLUSTER ACCORDİNG TO AJAX REQUEST
        meal_similarity_df = self.collaborative_filtering(df)
        cf_recommendations = self.recommend_meals_cf(meal_similarity_df, user_id, df, adventurousness)
        cb_recommendations = self.cb_recommendation(df, user_id, adventurousness)
        common_meals = set(cf_recommendations).intersection(set(cb_recommendations))

        prioritized_recommendations = list(common_meals)

        prioritized_recommendations += [meal for meal in cf_recommendations if meal not in common_meals]
        prioritized_recommendations += [meal for meal in cb_recommendations if meal not in common_meals]
        return prioritized_recommendations
