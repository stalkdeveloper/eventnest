from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View
from .forms import RegisterForm, LoginForm, AdminLoginForm, ProfileUpdateForm
from .models import CustomUser


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, 'accounts/register.html', {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome to EventNest, {user.username}!')
            return redirect('core:dashboard')
        return render(request, 'accounts/register.html', {'form': form})


class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, 'accounts/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'core:dashboard')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        return render(request, 'accounts/login.html', {'form': form})


class AdminLoginView(View):
    def get(self, request):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return redirect('core:admin_dashboard')
        return render(request, 'accounts/admin_login.html', {'form': AdminLoginForm()})

    def post(self, request):
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_staff or user.is_superuser:
                login(request, user)
                messages.success(request, f'Admin login successful.')
                return redirect('core:admin_dashboard')
            else:
                messages.error(request, 'You do not have admin privileges.')
        return render(request, 'accounts/admin_login.html', {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('accounts:login')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    profile_pic = request.user.get_profile_picture()
    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile_pic': profile_pic,
    })


def password_reset_view(request):
    return render(request, 'accounts/password_reset.html')
