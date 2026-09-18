import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm

security_logger = logging.getLogger('accounts.security')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            security_logger.info("New user registered: '%s' from IP %s", user.username, request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Welcome to ShopNow, {user.first_name or user.username}!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            security_logger.info("Successful login for user '%s' from IP %s", username, request.META.get('REMOTE_ADDR'))
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                return redirect(next_url)
            return redirect('home')
        else:
            security_logger.warning("Failed login attempt for username '%s' from IP %s", username, request.META.get('REMOTE_ADDR'))
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def profile_view(request):
    user = request.user
    profile = user.profile
    orders = user.orders.all()[:5]
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'orders': orders,
        'user_form': UserUpdateForm(instance=user),
        'profile_form': ProfileUpdateForm(instance=profile),
        'password_form': CustomPasswordChangeForm(user),
    })


@login_required
def profile_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
        else:
            for form in [user_form, profile_form]:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'{field}: {error}')
    return redirect('profile')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            security_logger.info("Password changed for user '%s'", user.username)
            messages.success(request, 'Password changed successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    return redirect('profile')


@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = request.user
        if user.check_password(password):
            username = user.username
            logout(request)
            user.delete()
            security_logger.warning("User '%s' deleted their account", username)
            messages.success(request, 'Your account has been permanently deleted.')
            return redirect('home')
        else:
            security_logger.warning("Failed account deletion attempt for user '%s' (wrong password)", user.username)
            messages.error(request, 'Incorrect password. Account deletion failed.')
    return redirect('profile')
