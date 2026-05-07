from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import View
from .forms import RegisterForm, LoginForm, ProfileUpdateForm
from .models import CustomUser


class LoginView(View):
    """Single login for ALL users. Redirects by account_type after auth."""
    def get(self, request):
        if request.user.is_authenticated:
            return self._redirect(request.user)
        return render(request, 'accounts/login.html', {'form': LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            nxt = request.GET.get('next', '')
            if nxt and nxt.startswith('/') and not nxt.startswith('//'):
                return redirect(nxt)
            return self._redirect(user)
        return render(request, 'accounts/login.html', {'form': form})

    @staticmethod
    def _redirect(user):
        if user.is_system_user:
            return redirect('admin_dashboard:dashboard')
        return redirect('web_dashboard:dashboard')


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('accounts:login')


class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('web_dashboard:dashboard')
        return render(request, 'accounts/register.html', {'form': RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.account_type = CustomUser.AccountType.PLATFORM
            user.save()
            login(request, user)
            messages.success(request, f'Welcome to EventNest, {user.username}!')
            return redirect('web_dashboard:dashboard')
        return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('accounts:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile_pic': request.user.get_profile_picture(),
    })
