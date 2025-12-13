from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from .forms import RegisterForm, LoginForm
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.errors:
            # Print errors to console for debugging if needed
            print(form.errors) 
        if form.is_valid():
            user = form.save()
            login(request, user) # Auto-login after register
            return redirect('home') # Change 'home' to your landing page URL name
    else:
        form = RegisterForm()

    return render(request, 'sign_up.html', {'form': form})

def login(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.errors:
            # Print errors to console for debugging if needed
            print(form.errors)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('home') # Change 'home' to your landing page URL name
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout(request):
    auth_logout(request)
    return redirect('landing') # Change 'landing' to your landing page URL name

def landing(request):
    return render(request, 'landing.html')

@login_required
def home(request):
    if not request.user.is_authenticated:
        return redirect('landing')   # logged-in home
    return render(request, 'home.html')