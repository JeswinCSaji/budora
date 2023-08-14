from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages


def register(request):
    if request.method == 'POST':
        # first_name = request.POST.get('fname')
        # last_name = request.POST.get('sname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('pwd')
        Cpassword = request.POST.get('cpwd')

        if password == Cpassword:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already taken")
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already taken")
                return redirect('register')
            else:
                user = User.objects.create_user(username=username, email=email,password=password)
                user.save()
                messages.info(request, "Registered")
                return redirect('login')  # Redirect to login page
        else:
            messages.info(request, "Passwords do not match")
            return redirect('register')
    return render(request, 'register.html')

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('index.html')  # Replace with your desired URL
        else:
            messages.error(request, "Invalid Credentials")
            return redirect('login')
    else:
        return render(request, 'login.html')

# def forgot(request):
#     return render(request, '#')

def index(request):
    return render(request, 'index.html')