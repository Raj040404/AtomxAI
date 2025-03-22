from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

def login_signup_view(request):
    if request.method == 'POST':
        # Determine if the form is for login or signup
        if 'login' in request.POST:  # Check if it's a login form
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Corrected to use auth_login
                messages.success(request, 'Login successful!')  # Add success message
                return redirect('dashboard')  # Redirect to dashboard after login
            else:
                messages.error(request, 'Invalid username or password')
        
        elif 'signup' in request.POST:  # Check if it's a signup form
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            # Check if the username already exists
            if User.objects.filter(username=username).exists():
                messages.warning(request, 'Username already taken')
            else:
                # Create a new user
                user = User.objects.create_user(username=username, password=password)
                user.save()
                messages.success(request, 'Account created successfully. Please log in.')  # Success message
                return redirect('login_signup_view')  # Redirect to login page after signup

    return render(request, 'layout.html')  # Render the same template for both


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')  # Success message on logout
    return redirect('login_signup_view')  # Redirect to login page after logout
    
def home(request):
    return render(request, 'website/home.html')

def about(request):
    return render(request, 'website/about.html')