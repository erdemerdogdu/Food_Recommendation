from django.urls import path
from .views import HomePageView, LogoutView,  UnauthorizedView, AboutUsView

urlpatterns = [
    path('', HomePageView.as_view(), name='home_page'),
    path('logout', LogoutView.as_view(), name='log_out'),
    path('unauthorized',  UnauthorizedView.as_view(), name='unauthorized'),
    path('aboutus', AboutUsView.as_view(), name='unauthorized'),

]