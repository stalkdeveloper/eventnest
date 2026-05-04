from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import CustomUser


class LoginView(View):
    """
    Single login page for ALL users.
    After authentication, redirect based on account_type:
      system   → /dashboard/admin/
      platform → /dashboard/  (organiser or guest)
    """
    def get(self, request):
        if request.user.is_authenticated:
            return self._redirect_by_type(request.user)
        return render(request, 'accounts/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            # honour ?next= but only if it is a safe path
            next_url = request.GET.get('next', '')
            if next_url and next_url.startswith('/') and not next_url.startswith('//'):
                return redirect(next_url)
            return self._redirect_by_type(user)
        return render(request, 'accounts/login.html', {'form': form})

    @staticmethod
    def _redirect_by_type(user):
        if user.is_system_user:
            return redirect('core:admin_dashboard')
        return redirect('core:dashboard')


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('accounts:login')


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return render(request, 'accounts/register.html', {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.account_type = CustomUser.AccountType.PLATFORM  # new registrants = platform
            user.save()
            login(request, user)
            messages.success(request, f'Welcome to EventNest, {user.username}!')
            return redirect('core:dashboard')
        return render(request, 'accounts/register.html', {'form': form})


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
