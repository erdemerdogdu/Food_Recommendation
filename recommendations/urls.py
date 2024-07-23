from django.urls import path
from .views import RecommendView, LoadingView

urlpatterns = [
    path('', LoadingView.as_view(), name='loading'),
    path('getrecommendations/', RecommendView.as_view(), name='recommend'),
]
