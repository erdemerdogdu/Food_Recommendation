from django.contrib.auth import authenticate, login, update_session_auth_hash
from .forms import MyUserCreationForm, MyAuthenticationForm, UserProfileForm, PasswordChangeCustomForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import Group
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.views import View


class NormalUserRegisterView(View):
    def get(self, request):
        form = MyUserCreationForm()
        return render(request, 'customusers/register_normal_user.html', {'form': form})

    def post(self, request):
        form = MyUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            normal_user_group = Group.objects.get(name='Normal User')
            user.groups.add(normal_user_group)
            return redirect('login')
        return render(request, 'customusers/register_normal_user.html', {'form': form})


class RestaurantUserRegisterView(View):
    def get(self, request):
        form = MyUserCreationForm()
        return render(request, 'customusers/register_restaurant_user.html', {'form': form})

    def post(self, request):
        form = MyUserCreationForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            restaurant_user_group = Group.objects.get(name='Restaurant User')
            user.groups.add(restaurant_user_group)
            return redirect('login')
        return render(request, 'customusers/register_restaurant_user.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/home')
        form = MyAuthenticationForm()
        return render(request, 'customusers/login.html', {'form': form})

    def post(self, request):
        form = MyAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if form.cleaned_data.get('remember_me'):
                    request.session.set_expiry(604800)  # 1 week in seconds
                else:
                    request.session.set_expiry(0)
                return redirect('/home')
        return render(request, 'customusers/login.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(View):
    template_name = 'customusers/profile.html'
    success_url = reverse_lazy('profile')

    def get(self, request):
        form = UserProfileForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect(self.success_url)
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class PasswordChangeView(View):
    def get(self, request):
        form = PasswordChangeCustomForm(user=request.user)
        return render(request, 'customusers/password_change.html', {'form': form})

    def post(self, request):
        form = PasswordChangeCustomForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect("/home")
        return render(request, 'customusers/password_change.html', {'form': form})
