import datetime
from .models import UserProfile
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib import messages

from .models import Seller
from .forms import CertificationForm
from .models import Certification,Application, ApplicationStatus
from django.shortcuts import get_object_or_404
from .models import Application, ApplicationStatus

from django.contrib.auth.decorators import login_required 
from .models import Category,Product

def register(request):
     
    if request.method == 'POST':
        name = request.POST.get('username')
        username = request.POST.get('email')
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
                user_profile = UserProfile(user=user, email=email ,name=name)
                user_profile.save()
                messages.info(request, "Registered")
                return redirect('loginu')
        else:
            messages.info(request, "Passwords do not match")
            return redirect('register')
    else:
        return render(request, 'register.html')
     
def loginu(request):
    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.email
            if user.is_staff:
                return redirect('seller_index')
            else:
                return redirect('index.html')  # Redirect other users to index.html
        else :   
            messages.error(request, "Invalid credentials")
            return redirect('loginu')
            
    else:
        return render(request, 'login.html') 



def index(request):
    return render(request, 'index.html')

def loggout(request):
    print('Logged Out')
    logout(request)
    if 'username' in request.session:
        del request.session['username']
        request.session.clear()
    return redirect('index')

def edit_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        profile_pic = request.FILES.get('profile_picture')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_picture']
            user_profile.profile_pic = profile_pic

        user_profile.name = name
        user_profile.phone_number = phone_number
        user_profile.address = address
        request.user.email = email

        user_profile.save()
        request.user.save()
        # messages.success(request, "Profile updated successfully")
        return redirect('profile') 


    context = {
        'user_profile': user_profile
    }
    return render(request, 'userprofile/edit-profile.html', context)

def profile(request):
    return render(request, 'userprofile/user_profile.html')

def user_dashboard(request):
    return render(request,'userprofile/user_dashboard.html')

def plant_recommendation(request):
    return render(request,'recommendation/plantrecommendation.html')


def seller_register(request):
    if request.method == 'POST':
        
        username = request.POST['email']
        email = request.POST['email']
        password = request.POST['pwd']
        Cpassword = request.POST.get('cpwd')
        if password == Cpassword:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already taken")
                return redirect('seller_register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already taken")
                return redirect('seller_register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                contact = request.POST['contact']
                address = request.POST['address']
                storename = request.POST['storename']
                seller = Seller.objects.create(user=user, storename=storename, contact=contact, address=address)
                user.save()
                messages.success(request,"Seller request submitted. Please wait for approval.")
                UserProfile.objects.create(user=user, address="")
                return redirect('approvalpending')
        else:
            messages.info(request, "Passwords do not match")
            return redirect('seller_register')
    return render(request, 'seller/seller_register.html')

def seller_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            # Redirect to the seller's dashboard
            return redirect('seller_dashboard')
        else:
            # Handle authentication error
            return render(request, 'seller/seller_login.html', {'error_message': 'Invalid login credentials'})
    return render(request, 'seller/seller_login.html')

# def seller_index(request):
#     return render(request,'seller/base.html')


def approvalpending(request):
    return render(request,'seller/approvalpending.html')

def seller_loggout(request):
    print('Logged Out')
    logout(request)
    if 'username' in request.session:
        del request.session['username']
        request.session.clear()
    return redirect('loginu')

@login_required
def seller_index(request):
    # Get the user's applications
    user_applications = Application.objects.filter(user=request.user)

    # Check the approval status for each application
    approval_statuses = ApplicationStatus.objects.filter(application__in=user_applications)
    existing_certification = Certification.objects.filter(user=request.user)

    categories = Category.objects.all()
    products = Product.objects.all()

    if existing_certification:
        return render(request, 'seller/base.html', {'existing_certification': existing_certification})

    form = CertificationForm()

    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            print("Form is valid")  # Debug statement
            certification = form.save(commit=False)
            certification.user = request.user
            certification.save()
            print("Certification saved successfully")  # Debug statement
            return redirect('successseller')  # Redirect to a success page
        else:
            messages.error(request, 'Please fill in all required fields.')
            print("Form is not valid")  # Debug statement

        if 'product_form' in request.POST:
                # Product form submission
            print("Product form submitted")  # Debug statement
            product_name = request.POST.get('product_name')
            product_description = request.POST.get('product_description')
            select_category_id = request.POST.get('select_category')
            product_image = request.FILES.get('product_image')

                # Ensure all required fields are provided
            if product_name and product_description and select_category_id:
                try:
                        # Retrieve the selected category
                    selected_category = Category.objects.get(id=select_category_id)

                        # Calculate the product price based on the selected category
                    product_price = selected_category.default_product_price

                        # Create a new product instance with the calculated price
                    product = Product(
                        product_name=product_name,
                        product_description=product_description,
                        category=selected_category,
                        product_price=product_price,
                        product_image=product_image,
                    )
                    product.save()
                    messages.success(request, 'Product added successfully.')
                    return redirect('successaddproduct')
                except Category.DoesNotExist:
                    messages.error(request, 'Selected category does not exist.')
            else:
                messages.error(request, 'Please fill in all required fields.')
    print(categories)
    return render(request, 'seller/base.html', {
    'form': form,
    'approval_statuses': approval_statuses,
    'existing_certification': existing_certification,
    'categories': categories,
    'products': products,
})

def successseller(request):
    return render(request, 'seller/successseller.html')
def successaddcategory(request):
    return render(request, 'seller/successaddcategory.html')
def successaddproduct(request):
    return render(request, 'seller/successaddproduct.html')
