from django.urls import path
from django.contrib import admin
from .views import LoginView, ProfileUpdateView, PasswordChangeView, NormalUserRegisterView, RestaurantUserRegisterView


urlpatterns = [
    path('register/normal/', NormalUserRegisterView.as_view(), name='register_normal_user'),
    path('register/restaurant/', RestaurantUserRegisterView.as_view(), name='register_restaurant_user'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', ProfileUpdateView.as_view(), name='profile'),
    path('profile/password_change/', PasswordChangeView.as_view(), name='password_change'),
    path('admin/', admin.site.urls),

]
