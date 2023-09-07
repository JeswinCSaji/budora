from django.shortcuts import render, redirect
from .forms import SignUpForm, LoginForm
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import User
from .forms import SignUpForm, LoginForm
from .forms import CertificationForm
from django.contrib.auth import authenticate, login
from ecohiveapp.models import User 
from .models import Certification,Application, ApplicationStatus
from django.shortcuts import get_object_or_404
from .models import Application, ApplicationStatus
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from .models import Category,Product
# Make sure the import path is correct

# Create your views here.


def index(request):
    return render(request, 'index.html')


def register(request):
    msg = None
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            msg = 'user created'
            return redirect('login')
        else:
            msg = 'form is not valid'
    else:
        form = SignUpForm()
    return render(request,'register.html', {'form': form, 'msg': msg})




def user_login(request):
    form = LoginForm(request.POST or None)
    msg = None

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_customer:
                    login(request, user)
                    return redirect('index')
                elif user.is_seller:
                    login(request, user)
                    return redirect('dashseller')
                elif user.is_legaladvisor:
                    print("Redirecting to dashlegal")
                    return redirect('dashlegal')
                elif user.is_admin:
                    print("Redirecting to dashlegal")
                    return redirect('admin')
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating form'

    return render(request, 'login.html', {'form': form, 'msg': msg})

# def dashseller(request):
#     if request.method == 'POST':
#         form = CertificationForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('successseller')  # Redirect to a success page
#     else:
#         form = CertificationForm()
    
#     return render(request, 'dashseller.html', {'form': form})
@login_required
def dashseller(request):
    # Get the user's applications
    user_applications = Application.objects.filter(user=request.user)

    # Check the approval status for each application
    approval_statuses = ApplicationStatus.objects.filter(application__in=user_applications)
    existing_certification = Certification.objects.filter(user=request.user)

    categories = Category.objects.all()
    products = Product.objects.all()

    if existing_certification:
        return render(request, 'dashseller.html', {'existing_certification': existing_certification})

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
    return render(request, 'dashseller.html', {
    'form': form,
    'approval_statuses': approval_statuses,
    'existing_certification': existing_certification,
    'categories': categories,
    'products': products,
})

# views.py

# @login_required
# def approve_application(request, application_id):
#     # Logic to approve the application
#     application = get_object_or_404(Application, id=application_id)
#     application_status, created = ApplicationStatus.objects.get_or_create(application=application)
#     application_status.is_approved = True
#     application_status.save()

#     # Return a success response
#     return JsonResponse({"status": "success"})

# @login_required
# def reject_application(request, application_id):
#     # Logic to reject the application
#     application = get_object_or_404(Application, id=application_id)
#     application_status, created = ApplicationStatus.objects.get_or_create(application=application)
#     application_status.is_approved = False
#     application_status.save()

#     # Return a success response
#     return JsonResponse({"status": "success"})


def dashlegal(request):
    # Retrieve Certification objects
    seller_applications = Certification.objects.all()

    # Retrieve User roles for each Certification applicant
    user_roles = {}
    for application in seller_applications:
        # Ensure the user associated with the Certification exists
        user = get_object_or_404(User, id=application.user_id)

        # Retrieve user roles
        user_roles[application.id] = {
            'is_admin': user.is_admin,
            'is_customer': user.is_customer,
            'is_seller': user.is_seller,
            'is_legaladvisor': user.is_legaladvisor,
        }

    context = {
        'seller_applications': seller_applications,
        'user_roles': user_roles,  # Include user roles in the context
    }
    return render(request, 'dashlegal.html', context)

def index(request):
    return render(request, 'index.html')
def loggout(request):
    print('Logged Out')
    logout(request)
    if 'username' in request.session:
        del request.session['username']
        request.session.clear()
    return redirect('index')

def check_email(request):
    email = request.GET.get('email')
    exists = User.objects.filter(email=email).exists()
    return JsonResponse({'exists': exists})

def check_username(request):
    username = request.GET.get('username')
    exists = User.objects.filter(username=username).exists()
    return JsonResponse({'exists': exists})

def seller_register(request):
    return render(request, 'seller_register.html')
def successseller(request):
    return render(request, 'successseller.html')
def successaddcategory(request):
    return render(request, 'successaddcategory.html')
def successaddproduct(request):
    return render(request, 'successaddproduct.html')

def admin(request):
    if request.method == 'POST':
        # Retrieve form data directly from the request
        category_name = request.POST.get('category_name')
        category_description = request.POST.get('category_description')
        default_product_price = request.POST.get('default_product_price')

        # Create a new Category instance with the form data
        category = Category(
            category_name=category_name,
            category_description=category_description,
            default_product_price=default_product_price,
        )
        category.save()
        # Optionally, you can display a success message
        messages.success(request, 'Category created successfully.')
        return redirect('successaddcategory')  # Redirect back to the admin page

    return render(request, 'admin.html')

#CODE FOR updated views button approval and reject

# def dashseller(request):
#     existing_certification = Certification.objects.filter(user=request.user).first()

#     if existing_certification:
#         # Check for approval message in messages
#         approval_message = None
#         for message in messages.get_messages(request):
#             if "approved" in message.message:
#                 approval_message = message.message
#                 break

#         return render(request, 'dashseller.html', {'existing_certification': existing_certification, 'approval_message': approval_message})

#     if request.method == 'POST':
#         form = CertificationForm(request.POST, request.FILES)
#         if form.is_valid():
#             certification = form.save(commit=False)
#             certification.user = request.user
#             certification.save()

#             return redirect('successseller')
#     else:
#         form = CertificationForm()

#     return render(request, 'dashseller.html', {'form': form})

