import datetime
from .models import UserProfile
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login, logout, get_user_model
from django.contrib import messages
from django.http import JsonResponse
from .models import Seller
from .models import Certification
from django.shortcuts import get_object_or_404
from django.db import IntegrityError  
from django.contrib.auth.decorators import login_required 
from .models import Category,Product,Wishlist
from .models import ProductSummary  
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation

def register(request):
     
    if request.method == 'POST':
        name = request.POST.get('username')
        username = request.POST.get('email')
        email = request.POST.get('email')
        password = request.POST.get('pwd')
        Cpassword = request.POST.get('cpwd')

        try:
            password_validation.validate_password(password, User)
        except ValidationError as e:
            for error in e.error_list:
                messages.error(request, error)
            return redirect('register')
        
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
            
            if user.is_superuser:
                request.session['user_id'] = user.id
                request.session['username'] = user.email
                return redirect('admin_index') 
            elif user.is_staff:
                request.session['user_id'] = user.id
                request.session['username'] = user.email
                return redirect('seller_index')
            else:
                request.session['user_id'] = user.id
                request.session['username'] = user.email
                return redirect('index.html')  # Redirect other users to index.html
        else :   
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect('loginu')
            
    else:
        return render(request, 'login.html') 

@login_required   
def admin_index(request):
    return render(request, 'admin/dashadmin.html')


 
def product(request):
    return render(request, 'usertems/product.html')

def index(request):
    product_summaries = ProductSummary.objects.all()
    list1=[]
    for summary in product_summaries:
        if request.user.is_authenticated:
            in_wishlist = is_in_wishlist(request,summary)
        else:
            in_wishlist=False
        book_data = {
            'product_summaries': summary,
            'in_wishlist': in_wishlist,
        }
        list1.append(book_data)  
    return render(request, 'index.html',{'product_summaries':list1})

def loggout(request):
    print('Logged Out')
    logout(request)
    if 'username' in request.session:
        del request.session['username']
        request.session.clear()
    return redirect('index')

@login_required
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        profile_pic = request.FILES.get('profile_pic')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            user_profile.profile_pic = profile_pic
            print('got')
        user_profile.name = name
        user_profile.phone_number = phone_number
        user_profile.address = address
        request.user.email = email

        user_profile.save()
        request.user.save()
        messages.success(request, "Profile updated successfully")
        return redirect('profile') 


    context = {
        'user_profile': user_profile
    }
    return render(request, 'userprofile/user_profile.html', context)

@login_required
def user_dashboard(request):
    return render(request,'userprofile/user_dashboard.html')

def plant_recommendation(request):
    return render(request,'recommendation/plantrecommendation.html')

def saveproduct(request):
    return render(request,'usertems/save.html')

def seller_register(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        username = request.POST['email']
        email = request.POST['email']
        password = request.POST['pwd']
        Cpassword = request.POST.get('cpwd')
        
        # Validate password strength
        try:
            password_validation.validate_password(password, User)
        except ValidationError as e:
            for error in e.error_list:
                messages.error(request, error)
            return redirect('seller_register')
        
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
                seller = Seller.objects.create(user=user,email=email ,name=name, storename=storename, contact=contact, address=address)
                seller.save()
               
                # Set the user as staff
                user.is_staff = True
                user.save()
                
                # messages.success(request,"Seller request submitted. Please wait for approval.")
                UserProfile.objects.create(user=user, name=name)
                return redirect('loginu')
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


@login_required
def approvalpending(request):
    return render(request,'seller/approvalpending.html')


def seller_loggout(request):
    print('Logged Out')
    logout(request)
    if 'username' in request.session:
        del request.session['username']
        request.session.clear()
    return redirect(loginu)


def admin_loggout(request):
    print('Logged Out')
    logout(request)
    if 'username' in request.session:
        del request.session['username']
        request.session.clear()
    return redirect(loginu)

@login_required
def seller_index(request):
    existing_certification = Certification.objects.filter(user=request.user).first()

    if existing_certification:
        return render(request, 'seller/dashseller.html', {'existing_certification': existing_certification})

    if request.method == 'POST':
        # Handle form submission
        certification_image = request.FILES.get('certification_image')
        owner_name = request.POST.get('owner_name')
        store_name = request.POST.get('store_name')
        expiry_date_from = request.POST.get('expiry_date_from')
        expiry_date_to = request.POST.get('expiry_date_to')

        # Perform client-side validation here using JavaScript if needed

        # Perform server-side validation if needed
        # if not certification_image or not owner_name or not store_name or not expiry_date_from or not expiry_date_to:
        #     messages.error(request, 'Please fill in all required fields.')
        # else:
            # Create and save the Certification instance
        certification = Certification(
            user=request.user,
            certification_image=certification_image,
            owner_name=owner_name,
            store_name=store_name,
            expiry_date_from=expiry_date_from,
            expiry_date_to=expiry_date_to,
        )
        certification.save()
        return redirect('successseller')  # Redirect to a success page

    return render(request, 'seller/dashseller.html', {
        'existing_certification': existing_certification,
    })

@login_required
def successseller(request):
    return render(request, 'seller/successseller.html')

@login_required
def successaddcategory(request):
    return render(request, 'admin/successaddcategory.html')

@login_required
def successaddproduct(request):
    return render(request, 'seller/successaddproduct.html')

@login_required
def viewcategory(request):
    categories = Category.objects.all()
    return render(request, 'admin/viewcategory.html', {'categories': categories})

@login_required
def viewaddproduct(request):
    existing_certification = Certification.objects.filter(user=request.user).first()

    if not existing_certification:
        return redirect('seller_index')

    try:
        seller = request.user.seller  # Assuming the Seller profile is associated with the User model
        user_products = Product.objects.filter(seller=seller)
    except Seller.DoesNotExist:
        user_products = []

    return render(request, 'seller/viewaddproduct.html', {'user_products': user_products})

@login_required
def viewproducts(request):
    # Retrieve all products
    all_products = Product.objects.all()

    context = {
        'all_products': all_products,
    }
    return render(request, 'admin/viewproducts.html', context)



@login_required
def addproducts(request):
    
    existing_certification = Certification.objects.filter(user=request.user).first()

    if existing_certification:
        certification_status = existing_certification.is_approved
    else:
        certification_status = 'pending'  # Set a default value if no certification exists

    if certification_status == 'approved':
        if request.method == 'POST':
        # Extract data from the POST request
            product_name = request.POST.get('product_name')
            product_description = request.POST.get('product_description')
            select_category_id = request.POST.get('select_category')
            product_price = request.POST.get('product_price')
            product_stock = request.POST.get('product_stock')
            product_image = request.FILES.get('product_image')

        # Retrieve the selected category
            category = Category.objects.get(id=select_category_id)

        # Check if a product with the same name already exists in the selected category
        # Check if the current user has already added a product with the same name in this category
            existing_product = Product.objects.filter(
                product_name=product_name,
                category=category,
                seller__user=request.user  # Filter by the current user
            )

            if existing_product.exists():
                error_message = "You have already added a product with this name in the selected category."
                return render(request, 'seller/addproducts.html', {'error_message': error_message})

        # Retrieve the seller associated with the currently logged-in user
            seller = Seller.objects.get(user=request.user)
        # Create and save the Product instance
            product = Product(
                product_name=product_name,
                product_description=product_description,
                category=category,
                product_price=product_price,
                product_stock=product_stock,
                product_image=product_image,
                seller=seller  # Associate the seller with the product

            )
            product.save()

            return redirect('successaddproduct')  # Redirect to a success page after saving the product

        categories = Category.objects.all()  # Retrieve all Category objects from the database

        context = {
            'categories': categories,
            'certification_status': certification_status,
          # Pass the categories queryset to the template context
            }
        
        return render(request, 'seller/addproducts.html', context)
    else:
        return render(request, 'seller/addproducts.html', {'certification_status': certification_status})

@login_required
def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.delete()
    except Product.DoesNotExist:
        # Handle the case where the product with the given ID does not exist.
        pass

    # Redirect back to the viewproducts page or wherever you want to go after deletion.
    return redirect('viewproducts')

@login_required
def dashlegal(request):
    # Retrieve Certification objects including their IDs
    seller_applications = Certification.objects.all()

    # Retrieve User roles for each Certification applicant
    user_roles = {}
    for application in seller_applications:
        # Ensure the user associated with the Certification exists
        user = get_object_or_404(User, id=application.user_id)

        # Retrieve user roles
        user_roles[application.id] = {
            'is_admin': user.is_superuser,
            'is_customer': user,
            'is_seller': user.is_staff
        }

    context = {
        'seller_applications': seller_applications,
        'user_roles': user_roles,  # Include user roles in the context
    }
    return render(request, 'admin/dashlegal.html', context)

def logoutmessage(request):
    return render(request,'logoutmessage.html')

@login_required
def addcategory(request):
    if request.method == 'POST':
        try:
            # Retrieve form data directly from the request
            category_name = request.POST.get('category_name')
            formatted_category_name = category_name.capitalize()
            category_description = request.POST.get('category_description')
           

            # Create a new Category instance with the form data
            category, created = Category.objects.get_or_create(
                category_name=formatted_category_name,
                defaults={'category_description': category_description}
            )
            if created:
                # The category was created
                messages.success(request, 'Category created successfully.')
            else:
                # The category already exists
                messages.error(request, 'Category already exists.')

            return redirect('successaddcategory')

            # Display a success message
            # messages.success(request, 'Category created successfully.')
              # Redirect back to the admin page

        except IntegrityError as e:
            # Handle database integrity error (e.g., unique constraint violation)
            messages.error(request, 'Error creating category: {}'.format(str(e)))

    return render(request, 'admin/addcategory.html')

@login_required
def delete_category(request, category_id):
    # Get the category object to delete
    category = get_object_or_404(Category, pk=category_id)

    associated_products = Product.objects.filter(category=category)

    if request.method == 'POST':
        # Delete all associated products
        associated_products.delete()
        
        # Delete the category
        category.delete()
        
        return redirect('viewcategory')  # Redirect to the category list page

    return render(request, 'admin/delete_category.html', {'category': category, 'associated_products': associated_products})

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)

    if request.method == 'POST':
        new_category_name = request.POST['category_name']
          # Check if a category with the same name already exists
        if Category.objects.filter(category_name=new_category_name).exclude(id=category.id).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            # Update the category if no duplicate name found
        
            category.category_name = request.POST['category_name']
            category.category_description = request.POST['category_description']
            category.save()
            return redirect('viewcategory')  # Replace 'category_list' with your category list URL name

    return render(request, 'admin/edit_category.html', {'category': category})

@login_required
def approve_certification(request, certification_id):
    certification = get_object_or_404(Certification, id=certification_id)
    if request.method == 'POST':
        certification.is_approved = Certification.APPROVED  # Set it to 'approved'
        certification.save()
    return redirect('dashlegal')

@login_required
def reject_certification(request, certification_id):
    certification = get_object_or_404(Certification, id=certification_id)
    if request.method == 'POST':
        certification.is_approved = Certification.REJECTED  # Set it to 'rejected'
        certification.save()
    return redirect('dashlegal')

@login_required
def user_list(request):
    users = User.objects.all()
    return render(request, 'admin/userlist.html', {'users': users})

@login_required
def activate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = True
        user.save()
    return redirect('user_list')

@login_required
def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = False
        user.save()
    return redirect('user_list')

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt  # Use csrf_exempt for simplicity; consider using a csrf token for security in production
def delete_user(request, user_id):
    # Check if the request method is POST (for safety, you might want to use a confirmation modal before sending the request)
    if request.method == 'POST':
        # Get the user object to delete
        user = get_object_or_404(User, id=user_id)

        # Check if the user can be deleted (e.g., you might want to add custom logic here)
        if not user.is_superuser:
            user.delete()
            return JsonResponse({'message': 'User deleted successfully.'})

    return JsonResponse({'error': 'Unable to delete user.'}, status=400)

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Handle form submission and update user details
        user.username = request.POST['username']
        user.email = request.POST['email']

        # Update user role based on the selected role option
        role = request.POST.get('role')
        if role == 'customer':
            user.is_staff = False
            user.is_superuser = False
        elif role == 'staff':
            user.is_staff = True
            user.is_superuser = False
        elif role == 'superuser':
            user.is_staff = True
            user.is_superuser = True

        user.save()
        return redirect('user_list')  # Redirect back to the user list page

    return render(request, 'admin/edituser.html', {'user': user})

@login_required 
def view_products(request):
    product_summaries = ProductSummary.objects.all()
    return render(request, 'admin/viewstock.html', {'product_summaries': product_summaries})

@login_required 
def edit_product_stock(request, pk):
    product_summary = get_object_or_404(ProductSummary, pk=pk)

    if request.method == 'POST':
        # Update the product details based on the form submission
        product_summary.product_sci_name = request.POST['product_sci_name']
        product_summary.product_description = request.POST['product_description']
        product_summary.product_price = request.POST['product_price']
        product_summary.product_image = request.FILES.get('product_image')  # Use get to handle optional file upload
        product_summary.light_requirements = request.POST['light_requirements']
        product_summary.water_requirements = request.POST['water_requirements']
        product_summary.humidity_requirements = request.POST['humidity_requirements']
        product_summary.soil_type = request.POST['soil_type']
        product_summary.toxicity_information = request.POST['toxicity_information']
        product_summary.maintenance_instructions = request.POST['maintenance_instructions']
        product_summary.save()
        return redirect('viewstock')  # Redirect to the product summary page after editing

    return render(request, 'admin/editstock.html', {'product_summary': product_summary})

@login_required 
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()  # Assuming you have a 'Category' model

    if request.method == 'POST':
        # Update the product fields based on form input
        product.product_name = request.POST['product_name']
        product.product_description = request.POST['product_description']
        
        # Get the category instance based on the selected ID
        category_id = request.POST.get('select_category')
        if category_id:
            category = get_object_or_404(Category, id=category_id)
            product.category = category
        
        product.product_price = request.POST['product_price']
        product.product_stock = request.POST['product_stock']
        
        # Handle product image upload or update
        if 'product_image' in request.FILES:
            product.product_image = request.FILES['product_image']

        # Save the updated product
        product.save()
        return redirect('viewaddproduct')  # Redirect to the product list page

    return render(request, 'seller/edit_product.html', {'product': product, 'categories': categories})

@login_required
def delete_add_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Handle form submission for deleting the product
        product.delete()
        return redirect('viewaddproduct')  # Redirect to the product list page

    return render(request, 'seller/delete_add_product.html', {'product': product})


def store(request): 
    product_summaries = ProductSummary.objects.all() 
    list1=[]
    for summary in product_summaries:
        if request.user.is_authenticated:
            in_wishlist = is_in_wishlist(request,summary)
        else:
            in_wishlist=False
        book_data = {
                'product_summaries': summary,
                'in_wishlist': in_wishlist,
            }
        list1.append(book_data)  
    return render(request, 'usertems/store.html', {'product_summaries':list1})


def is_in_wishlist(request,summary):
    user = request.user
    is_in_wishlist=Wishlist.objects.filter(user=user, product=summary).first()
    if is_in_wishlist:
        return True
    else:
        False

def storewishlist(request):
    product_summaries = ProductSummary.objects.all()   
    return render(request, 'usertems/store.html', {'product_summaries': product_summaries})

def product_single(request, product_id):
    product = get_object_or_404(ProductSummary, pk=product_id)
    user = request.user


    if request.user.is_authenticated:
    # Check if the product is already in the user's cart
        existing_wishlist_item = Wishlist.objects.filter(user=user, product=product).first()
        is_in_wishlist = existing_wishlist_item is not None

    else:
        is_in_wishlist=False
    if request.method == 'POST':
        image = product.product_image

        if not is_in_wishlist:
            # If the product is not in the cart, add it to the cart with the specified quantity
            Wishlist.objects.create(user=user, product=product, image=image)
        else:
            print("Already in Cart")

        return redirect('product_single',product_id=product_id)
    
    return render(request, 'usertems/product.html', {'product': product,'is_in_wishlist': is_in_wishlist})

# def saveproduct(request):
#     return render(request,'usertems/save.html')

def wishlist_view(request):
    # Assuming you have user authentication and each user has a unique cart
    user = request.user

    # Retrieve the user's cart items
    wishlist_items = Wishlist.objects.filter(user=user)

    context = {
        'wishlist_items': wishlist_items,
    }

    return render(request, 'usertems/wishlist.html', context)

def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)

    if request.method == 'POST':
        wishlist_item.delete()

    return redirect('wishlist')  

def remove_storewishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)

    if request.method == 'POST':
        wishlist_item.delete()

    return redirect('store') 

def remove_productwishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)

    if request.method == 'POST':
        wishlist_item.delete()

    return redirect('product_single') 

def remove_indexwishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)

    if request.method == 'POST':
        wishlist_item.delete()

    return redirect('index.html') 

def add_productwishlist(request, product_id):
    product = get_object_or_404(ProductSummary, pk=product_id)
    user = request.user

    # Check if the product is already in the user's cart
    existing_wishlist_item = Wishlist.objects.filter(user=user, product=product).first()
    is_in_wishlist = existing_wishlist_item is not None

    if request.method == 'POST':
        image = product.product_image

        if not is_in_wishlist:
            # If the product is not in the cart, add it to the cart with the specified quantity
            Wishlist.objects.create(user=user, product=product, image=image)
        else:
            print("Already in Cart")

        return redirect('product_single',product_id=product_id)
    return render(request, 'usertems/product.html', {'product': product,'is_in_wishlist': is_in_wishlist})

def add_storewishlist(request, product_id):
    product = get_object_or_404(ProductSummary, pk=product_id)
    user = request.user

    # Check if the product is already in the user's cart
    existing_wishlist_item = Wishlist.objects.filter(user=user, product=product).first()
    is_in_wishlist = existing_wishlist_item is not None

    if request.method == 'POST':
        image = product.product_image

        if not is_in_wishlist:
            # If the product is not in the cart, add it to the cart with the specified quantity
            Wishlist.objects.create(user=user, product=product, image=image)
        else:
            print("Already in Cart")

        return redirect('store')
    return render(request, 'usertems/store.html', {'product': product,'is_in_wishlist': is_in_wishlist})

def add_indexwishlist(request, product_id):
    product = get_object_or_404(ProductSummary, pk=product_id)
    user = request.user

    # Check if the product is already in the user's cart
    existing_wishlist_item = Wishlist.objects.filter(user=user, product=product).first()
    is_in_wishlist = existing_wishlist_item is not None

    if request.method == 'POST':
        image = product.product_image

        if not is_in_wishlist:
            # If the product is not in the cart, add it to the cart with the specified quantity
            Wishlist.objects.create(user=user, product=product, image=image)
        else:
            print("Already in Cart")

        return redirect('index.html')
    return render(request, 'index.html', {'product': product,'is_in_wishlist': is_in_wishlist})
