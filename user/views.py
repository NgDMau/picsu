from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm, LoginForm
from .models import UserProfile


def signin(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not UserProfile.objects.filter(user=user).exists():
                user_profile=UserProfile.objects.create(user=user)
            return redirect('home')  # Redirect to 'home' or another appropriate page
    else:
        form = LoginForm()

    return render(request, 'registration/login.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            if not UserProfile.objects.filter(user=user).exists():
                user_profile=UserProfile.objects.create(user=user)
            login(request, user)
            return redirect('home')  # Redirect to a home page or dashboard
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})