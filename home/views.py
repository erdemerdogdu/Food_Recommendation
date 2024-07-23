from django.shortcuts import render
from django.views import View
from django.shortcuts import redirect
from django.contrib.auth import logout


class HomePageView(View):
    def get(self, request):
        return render(request, 'home/home.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/customusers/login')


class UnauthorizedView(View):
    def get(self, request):
        return render(request, 'home/unauthorized.html')


class AboutUsView(View):
    def get(self, request):
        return render(request, 'home/aboutus.html')
