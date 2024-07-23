from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('restaurants/', include('restaurants.urls')),
    path('meals/', include('meals.urls')),
    path('customusers/', include('customusers.urls')),
    path('reviews/', include('reviews.urls')),
    path('recommendations/', include('recommendations.urls')),
    path('home/', include('home.urls'))
]
