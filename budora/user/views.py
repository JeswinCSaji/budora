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
from .models import Category,Product,Wishlist,Cart
from .models import ProductSummary  
from django.core.exceptions import ValidationError
from django.contrib.auth import password_validation
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash  # Add this import
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg
from textblob import TextBlob
from django.template.loader import get_template
from xhtml2pdf import pisa  # Import for PDF generation

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
                messages.info(request, "Email already taken")
                return redirect('register')
            elif User.objects.filter(email=email).exists():
                messages.info(request, "Email already taken")
                return redirect('register')
            
            else:
                user = User.objects.create_user(username=username, email=email,password=password)
                user_profile = UserProfile(user=user, email=email ,name=name)
                user_profile.save()


                subject = 'Welcome to Budora - Registration Successful'
                message = f'Dear {name},\n\n' \
                        'Congratulations! You have successfully registered on Budora. Welcome to our community.\n\n' \
                        'Thank you for choosing Budora as your platform.\n\n' \
                        'Best regards,\n' \
                        'The Budora Team'
                from_email = settings.EMAIL_HOST_USER  # Your sender email address
                recipient_list = [user.email]

                send_mail(subject, message, from_email, recipient_list)
                return redirect('loginu')
        else:
            messages.info(request, "Passwords do not match")
            return redirect('register')
    else:
        return render(request, 'register.html')
     
def loginu(request):
    login_error_message = None

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
        else:   
            login_error_message = "Invalid Credentials"

    return render(request, 'login.html', {'login_error_message': login_error_message})


@login_required   
def admin_index(request):
    return render(request, 'admin/dashadmin.html')


 
def product(request):
    return render(request, 'usertems/product.html')

def sample(request):
    return render(request, 'invoicesample.html')

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
def profile(request):
    user_profile = UserProfile.objects.get(user=request.user)

    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        profile_pic = request.FILES.get('profile_pic')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        reset_password = request.POST.get('reset_password')
        old_password = request.POST.get('old_password') 

        if 'profile_pic' in request.FILES:
            profile_pic = request.FILES['profile_pic']
            user_profile.profile_pic = profile_pic
            print('got')
        user_profile.name = name
        user_profile.phone_number = phone_number
        user_profile.address = address
        request.user.email = email

        # Check if all three password fields are not empty
        if old_password and reset_password and request.POST.get('cpass') == reset_password:
            if request.user.check_password(old_password):
                # The old password is correct, set the new password
                request.user.set_password(reset_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Update the session to prevent logging out
            else:
                messages.error(request, "Incorrect old password. Password not updated.")
        else:
            print("Please fill all three password fields correctly.")
        
        user_profile.reset_password = reset_password
        user_profile.save()
        request.user.save()
        return redirect('profile') 

    context = {
        'user_profile': user_profile
    }
    return render(request, 'userprofile/user_profile.html', context)


@login_required
def user_dashboard(request):
    return render(request,'userprofile/user_dashboard.html')



def saveproduct(request):
    return render(request,'usertems/save.html')

def seller_register(request):
    if request.method == 'POST':
        name = request.POST.get('username')
        username = request.POST['email']
        email = request.POST['email']
        landmark = request.POST['landmark']
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
                messages.info(request, "Email already registered")
                return redirect('seller_register')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)             
                contact = request.POST['contact']
                address = request.POST['address']
                landmark = request.POST['landmark']
                storename = request.POST['storename']
                seller = Seller.objects.create(user=user,email=email ,name=name, landmark=landmark, storename=storename, contact=contact, address=address)
                seller.save()
                # user_profile = UserProfile(user=user, email=email ,name=name)
                # user_profile.save()
               
                # Set the user as staff
                user.is_staff = True
                user.save()
                user_profile = UserProfile(user=user, email=email ,name=name)
                user_profile.save()
                
                # messages.success(request,"Seller request submitted. Please wait for approval.")
                # UserProfile.objects.create(user=user, name=name)
                subject = 'Welcome to Budora'
                message = 'We are thrilled to welcome you to Budora! Your account registration has been completed successfully, and you are now a valued member of our community.'
                from_email = settings.EMAIL_HOST_USER  # Your sender email address
                recipient_list = [seller.email]

                send_mail(subject, message, from_email, recipient_list)
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




@login_required
def seller_index(request):
    allreviews = Review.objects.filter(seller=request.user.seller)    
    avg_rating = allreviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    existing_certification = Certification.objects.filter(user=request.user).first()

    if existing_certification:
        return render(request, 'seller/dashseller.html', {'existing_certification': existing_certification, 'allreviews':allreviews,'avg_rating':avg_rating})

    if request.method == 'POST':
        # Handle form submission
        certification_image = request.FILES.get('certification_image')
        owner_name = request.POST.get('owner_name')
        store_name = request.POST.get('store_name')
        expiry_date_from = request.POST.get('expiry_date_from')
        expiry_date_to = request.POST.get('expiry_date_to')
        opening_time = request.POST.get('opening_time')
        closing_time = request.POST.get('closing_time')
        opening_days = request.POST.getlist('opening_days')  # Get a list of selected opening days
        store_image = request.FILES.get('store_image') 

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
            opening_time=opening_time,
            closing_time=closing_time,
            opening_days=','.join(opening_days),  # Save selected days as a comma-separated string
            store_image=store_image,
        )
        certification.save()

        seller = Seller.objects.get_or_create(user=request.user)[0]  # Get or create Seller instance for the user
        seller.name = owner_name
        seller.email = request.user.email
        seller.storename = store_name
        seller.opening_time = opening_time
        seller.closing_time = closing_time
        seller.opening_days = ','.join(opening_days)  # Save selected days as a comma-separated string
        seller.save()

        subject = 'Your Certification Request Has Been Submitted'
        message = ' your certification request has been successfully received by our team. Your dedication to contributing to our community of plant enthusiasts is greatly appreciated. Our team will now begin the verification process, ensuring that all details are accurate and complete. Once this step is completed, you will be granted access to add your plants to our platform. Thank you for choosing our platform to share your love for plants. We are excited to have you as part of our community and look forward to seeing your contributions flourish.'
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [seller.email]

        send_mail(subject, message, from_email, recipient_list)       
        return redirect('successseller')  # Redirect to a success page

    return render(request, 'seller/dashseller.html', {
        'existing_certification': existing_certification,
        'allreviews':allreviews,
        'avg_rating':avg_rating,
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
            formatted_product_name = product_name.capitalize()
            select_category_id = request.POST.get('select_category')
            product_price = request.POST.get('product_price')
            product_stock = request.POST.get('product_stock')
            product_image = request.FILES.get('product_image')

        # Retrieve the selected category
            category = Category.objects.get(id=select_category_id)

        # Check if a product with the same name already exists in the selected category
        # Check if the current user has already added a product with the same name in this category
            existing_product = Product.objects.filter(
                product_name=formatted_product_name,
                category=category,
                seller__user=request.user # Filter by the current user
            )

            if existing_product.exists():
                error_message = "You have already added a product with this name in the selected category."
                return render(request, 'seller/addproducts.html', {'error_message': error_message})

        # Retrieve the seller associated with the currently logged-in user
            seller = Seller.objects.get(user=request.user)
        # Create and save the Product instance
            product = Product(
                product_name=product_name,
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
    today = timezone.now().date()

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
        'today': today,
    }
    return render(request, 'admin/dashlegal.html', context)



@login_required
def addcategory(request):
    form_error_message = None  # Initialize form_error_message as None

    if request.method == 'POST':
        try:
            # Retrieve form data directly from the request
            category_name = request.POST.get('category_name')
            formatted_category_name = category_name.title()  # Use title() to capitalize all words
            category_description = request.POST.get('category_description')

            # Check if the category with the given name already exists
            existing_category = Category.objects.filter(category_name=formatted_category_name).first()

            if existing_category:
                # The category already exists
                form_error_message = 'Category already exists.'
            else:
                # Create a new Category instance with the form data
                category = Category(category_name=formatted_category_name, category_description=category_description)
                category.save()
                messages.success(request, 'Category created successfully.')
                return redirect('successaddcategory')

        except IntegrityError as e:
            # Handle database integrity error (e.g., unique constraint violation)
            form_error_message = 'Error creating category: {}'.format(str(e))

    return render(request, 'admin/addcategory.html', {'form_error_message': form_error_message})





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
    editcategory_error_message = None  # Initialize form_error_message as None

    if request.method == 'POST':
        new_category_name = request.POST['category_name']
        # Check if a category with the same name already exists
        if Category.objects.filter(category_name=new_category_name).exclude(id=category.id).exists():
            editcategory_error_message = 'Category with this name already exists.'
        else:
            # Update the category if no duplicate name found
            category.category_name = request.POST['category_name']
            category.category_description = request.POST['category_description']
            category.save()
            return redirect('viewcategory')  # Replace 'category_list' with your category list URL name

    return render(request, 'admin/edit_category.html', {'category': category, 'editcategory_error_message': editcategory_error_message})

@login_required
def seller_approve_order(request, order_id):
    order = get_object_or_404(OrderItem, id=order_id)
    if request.method == 'POST':
        order.seller_is_approved = OrderItem.APPROVED  # Set it to 'approved'
        order.save()
        # subject = 'Congratulations! Your License Has Been Approved'
        # message = 'We are delighted to inform you that your license application has been successfully approved. Your dedication and compliance with the necessary requirements have made this approval possible. We appreciate your patience throughout the process. With your approved license, you are now officially recognized and authorized to add your plants. '
        # from_email = settings.EMAIL_HOST_USER  # Your sender email address
        # recipient_list = [order.seller.email]
        # send_mail(subject, message, from_email, recipient_list)
    return redirect('sellerorder')
    
@login_required
def approve_certification(request, certification_id):
    certification = get_object_or_404(Certification, id=certification_id)
    if request.method == 'POST':
        certification.is_approved = Certification.APPROVED  # Set it to 'approved'
        certification.save()
        subject = 'Congratulations! Your License Has Been Approved'
        message = 'We are delighted to inform you that your license application has been successfully approved. Your dedication and compliance with the necessary requirements have made this approval possible. We appreciate your patience throughout the process. With your approved license, you are now officially recognized and authorized to add your plants. '
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [certification.user.email]
        send_mail(subject, message, from_email, recipient_list)
    return redirect('dashlegal')
    

@login_required
def reject_certification(request, certification_id):
    certification = get_object_or_404(Certification, id=certification_id)
    if request.method == 'POST':
        certification.is_approved = Certification.REJECTED  # Set it to 'rejected'
        certification.save()
        subject = 'Important Notice: Your License Application Has Been Declined'
        message = 'We regret to inform you that your recent license application has been declined, and as a result, you will not be able to add your plants on our platform. '
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [certification.user.email]
        send_mail(subject, message, from_email, recipient_list)
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
        subject = 'Important Notice: Your Account Is Now Active'
        message = 'We are pleased to inform you that your account has been successfully activated. Welcome to our platform! Your account is now ready for you to explore and enjoy all the features and benefits it offers. Whether you are here for information, services, or interactions, we are excited to have you as part of our community.'
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)
    return redirect('user_list')

@login_required
def deactivate_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.is_active = False
        user.save()
        subject = 'Important Notice: Account Deactivation'
        message = 'We regret to inform you that your user account has been deactivated. This action has been taken based on certain circumstances or violations of our policies that have come to our attention.As a result, you will no longer have access to your account and its associated services. If you believe this deactivation is in error or have any questions regarding this decision, please contact our support team by replying to this mail.'
        from_email = settings.EMAIL_HOST_USER  # Your sender email address
        recipient_list = [user.email]
        send_mail(subject, message, from_email, recipient_list)
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
def stock_approve(request, product_summary_id):
    order = get_object_or_404(ProductSummary, id=product_summary_id)
    if request.method == 'POST':
        order.stock_is_approved = ProductSummary.APPROVED  # Set it to 'approved'
        order.save()
    return redirect('viewstock')

@login_required 
def edit_product_stock(request, pk):
    product_summary = get_object_or_404(ProductSummary, pk=pk)

    if request.method == 'POST':
        product_summary.product_sci_name = request.POST['product_sci_name']
        product_summary.product_description = request.POST['product_description']
        product_summary.product_image = request.FILES.get('product_image')
        product_summary.light_requirements = request.POST['light_requirements']
        product_summary.water_requirements = request.POST['water_requirements']
        product_summary.humidity_requirements = request.POST['humidity_requirements']
        product_summary.soil_type = request.POST['soil_type']
        product_summary.toxicity_information = request.POST['toxicity_information']
        product_summary.maintenance_instructions = request.POST['maintenance_instructions']
        
        # Get the corresponding Product object based on product_name
        product = Product.objects.get(product_name=product_summary.product_name)
        product_summary.product = product
        product_summary.category = product.category
        
        product_summary.save()
        return redirect('viewstock')

    return render(request, 'admin/editstock.html', {'product_summary': product_summary})


@login_required 
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # categories = Category.objects.all()  # Assuming you have a 'Category' model

    if request.method == 'POST':
        # Update the product fields based on form input
        product.product_name = request.POST['product_name']
        
        # Get the category instance based on the selected ID
        # category_id = request.POST.get('select_category')
        # if category_id:
        #     category = get_object_or_404(Category, id=category_id)
        #     product.category = category
        
        product.product_price = request.POST['product_price']
        product.product_stock = request.POST['product_stock']
        
        # Handle product image upload or update
        # if 'product_image' in request.FILES:
        #     product.product_image = request.FILES['product_image']

        # Save the updated product
        product.save()
        return redirect('viewaddproduct')  # Redirect to the product list page

    return render(request, 'seller/edit_product.html', {'product': product})

@login_required
def delete_add_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        # Handle form submission for deleting the product
        product.delete()
        return redirect('viewaddproduct')  # Redirect to the product list page

    return render(request, 'seller/delete_add_product.html', {'product': product})


@login_required
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

@login_required
def product_single(request, product_id):
    product = get_object_or_404(ProductSummary, pk=product_id)
    product_name = product.product.product_name
    products=Product.objects.filter(product_name=product_name)
    product_details=Product.objects.filter(product_name=product.product_name)

    sellers = []
    for i in products:
        sellers.append(i.seller)

    all_average_ratings = {}
    for seller in sellers:
        allreviews = Review.objects.filter(seller=seller)
        avg_rating = allreviews.aggregate(Avg('rating'))['rating__avg'] or 0
        all_average_ratings[seller] = avg_rating

    print(all_average_ratings)
    

    # print(f"sellers_with_product: {sellers_with_product}")
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
    
    # print(sellers_with_product)
    return render(request, 'usertems/product.html', {'product': product,'is_in_wishlist': is_in_wishlist,'sellers_with_product':sellers,'product_details':product_details,
                                                     'allreviews':allreviews,'avg_rating':avg_rating
                                                     })

# def product_stores(request, product_id):
#     try:
#         product_summary = ProductSummary.objects.get(pk=product_id)
        
#         print(product_summary.product.seller.storename)
#     except ProductSummary.DoesNotExist:
#         # Handle the case where the specified product_summary_id does not exist.
#         # You can return an error response or render an appropriate template.
#         return HttpResponse("Product Summary not found", status=404)

#     # Query sellers related to products associated with this product summary
#     sellers_with_product = Seller.objects.filter(products__product_summary=product_summary)
#     print(f"product_id: {product_id}")
#     print(f"product_summary: {product_summary}")
#     print(f"sellers_with_product: {sellers_with_product}")


#     return render(request, 'usertems/product_stores.html', {'product_summary': product_summary, 'sellers_with_product': sellers_with_product})


@login_required
def wishlist_view(request):
    # Assuming you have user authentication and each user has a unique cart
    user = request.user

    # Retrieve the user's cart items
    wishlist_items = Wishlist.objects.filter(user=user)
    total_items = len(wishlist_items)

    context = {
        'wishlist_items': wishlist_items,
        'total_items': total_items
    }

    return render(request, 'usertems/wishlist.html', context)

def remove_all_from_wishlist(request):
    user = request.user
    # Get all wishlist items for the current user
    wishlist_items = Wishlist.objects.filter(user=user)

    # Delete all wishlist items
    wishlist_items.delete()

    return render(request, 'usertems/wishlist.html')

def remove_from_wishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)

    if request.method == 'POST':
        wishlist_item.delete()

    return redirect('wishlist')  

@login_required
def remove_productwishlist(request, product_id):
    product = get_object_or_404(ProductSummary, pk=product_id)

    wishlist_item = Wishlist.objects.filter(product=product)
    if request.method == 'POST':
        wishlist_item.delete()
    return redirect('product_single',product_id=product_id) 

def remove_storewishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)

    if request.method == 'POST':
        wishlist_item.delete()

    return redirect('store') 

def remove_indexwishlist(request, wishlist_item_id):
    wishlist_item = get_object_or_404(Wishlist, id=wishlist_item_id)

    if request.method == 'POST':
        wishlist_item.delete()

    return redirect('index.html') 

@login_required
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

@login_required
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

@login_required
def submit_review_productpage(request, seller_id, product_id):
    if request.method == 'POST':
        description = request.POST.get('description')
        rating = int(request.POST.get('rating', 0))
        review_id = request.POST.get('review_id')  # Get the review_id from the form

        seller = get_object_or_404(Seller, pk=seller_id)
        print(review_id)

        # Sentiment Analysis using TextBlob
        sentiment_score = analyze_sentiment(description)

        # Calculate the rating based on sentiment score
        star_rating = map_sentiment_to_rating(sentiment_score)

        if review_id:
            # If review_id is available, it's an edit action
            review = Review.objects.get(pk=review_id)
            review.rating = star_rating  # Update the rating based on sentiment
            review.description = description
            review.save()
        else:
            # It's an add action
            review = Review.objects.create(
                user=request.user,
                rating=star_rating,  # Use calculated rating
                description=description,
                seller=seller,
                review_status='REVIEWED',
            )
        send_review_notification_email(request.user, seller, review)

        # Redirect back to the product page or another appropriate page
        return redirect('seller_detail', seller_id=seller_id, product_id=product_id)

def send_review_notification_email(user, seller, review):
    # Email to the user
    user_subject = 'Review Submitted Successfully'
    user_message = f'Dear {user.userprofile.name},\n\n' \
                   'Thank you for submitting your review on our platform. ' \
                   'Your feedback is valuable to us.\n\n' \
                   'Best regards,\n' \
                   'The Budora Team'
    user_from_email = settings.EMAIL_HOST_USER
    user_recipient_list = [user.email]

    # Email to the seller
    seller_subject = 'New Review Posted for Your Product'
    seller_message = f'{seller.storename},\n\n' \
                     f'A new review has been posted for your product by {user.userprofile.name}. ' \
                     'You can log in to your seller account to view the review.\n\n' \
                     'Best regards,\n' \
                     'The Budora Team'
    seller_from_email = settings.EMAIL_HOST_USER
    seller_recipient_list = [seller.email]

    # Send emails
    send_mail(user_subject, user_message, user_from_email, user_recipient_list, fail_silently=False)
    send_mail(seller_subject, seller_message, seller_from_email, seller_recipient_list, fail_silently=False)
#cart
@login_required
def seller_detail(request, seller_id, product_id):
    
    seller = get_object_or_404(Seller, pk=seller_id)
    product = get_object_or_404(Product, pk=product_id)
    user_orders = Order.objects.filter(user=request.user)
    if user_orders:
        orders = OrderItem.objects.filter(seller=seller).first()
    else:
        orders = None
    print(orders)
    # user_orders = Order.objects.filter(user=request.user,seller=seller).first()
    review = Review.objects.filter(user=request.user, seller=seller).first()
    allreviews = Review.objects.filter(seller=seller)
    
    if review:
        review_status = review.review_status
        review_id = review.pk  # Add the review_id to the order
        review_desc=review.description
    else:
        review_status = 'Pending'  # Default to "Pending" if no review found
        review_id = None  # Set review_id to None if no review found
        review_desc = None
    user = request.user
   
    avg_rating = allreviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # Check if the product is already in the user's cart
    existing_cart_item = Cart.objects.filter(user=user, product=product).first()
    is_in_cart = existing_cart_item is not None

    # Fetch all products related to this seller
    seller_products = seller.products.all()

    # Calculate the total stock from those products
    total_stock = sum(product.product_stock for product in seller_products)
    
    # Include the product stock and cart information in the context
    context = {
        'seller': seller,
        'total_stock': total_stock,
        'seller_products': seller_products,
        'product': product,
        'is_in_cart': is_in_cart,
        'review_status' : review_status,
        'review_id' : review_id,
        'avg_rating': avg_rating,
        'orders': orders,
        'review_desc':review_desc,
    }
    if len(allreviews)>0:
        context['allreviews']=allreviews
        print(len(allreviews))


    if request.method == 'POST':
        # If it's a POST request, get the quantity from the form
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not provided
        image = product.product_image
        seller = product.seller

        if not is_in_cart:
            # If the product is not in the cart, add it to the cart with the specified quantity
            Cart.objects.create(user=user, product=product, quantity=quantity, image=image,seller=seller)
        else:
            # If the product is already in the cart, update the quantity
            existing_cart_item.quantity += quantity
            existing_cart_item.save()

        return redirect('cart')

    return render(request, 'usertems/storeproduct.html', context)

def load_reviews(request, seller_id):
    seller = get_object_or_404(Seller, pk=seller_id)
    reviews = Review.objects.filter(seller=seller)

    # You can format the reviews as needed before sending them to the template
    # For example, you can serialize them to JSON
    reviews_data = [{'user': review.user.username, 'comment': review.comment} for review in reviews]
    if len(reviews_data)>0:
    # Send the reviews data as JSON response
        return JsonResponse({'reviews': reviews_data})
    else:
        return JsonResponse()


@login_required
def cart_view(request):
    # Assuming you have user authentication and each user has a unique cart
    user = request.user

    # Retrieve the user's cart items
    cart_items = Cart.objects.filter(user=user)

    # Calculate the total price of items in the cart
    total_price = sum(cart_item.product.product_price * cart_item.quantity for cart_item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'usertems/cart.html', context)

def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id)

    if request.method == 'POST':
        cart_item.delete()

    return redirect('cart')

def update_cart_item(request, cart_item_id):
    if request.method == 'POST':
        # Retrieve the cart item
        cart_item = Cart.objects.get(id=cart_item_id)

        # Get the new quantity from the form
        new_quantity = int(request.POST.get('quantity'))

        # Update the cart item's quantity
        cart_item.quantity = new_quantity
        cart_item.save()

    # Redirect back to the cart view
    return redirect('cart')

from .models import BillingDetails, Cart, Order, OrderItem  # Import your models here
from django.shortcuts import render, redirect
from decimal import Decimal

from django.db import transaction

@login_required
@transaction.atomic
def checkout(request):
    total_price = 0  # Initialize total_price outside the if block
    cart_items = Cart.objects.filter(user=request.user)  # Define cart_items here
    billing_details = None  # Initialize billing_details to None

    # Check if billing details exist for the user
    if BillingDetails.objects.filter(user=request.user).exists():
        billing_details = BillingDetails.objects.get(user=request.user)

    if request.method == 'POST' and 'place_order' in request.POST:
        # If billing details already exist, you can skip processing the form and just calculate the total price
        if not billing_details:
            # Retrieve and process the form data for billing details
            first_name = request.POST.get('firstname')
            last_name = request.POST.get('lastname')
            state = request.POST.get('state')
            street_address = request.POST.get('streetaddress')
            apartment_suite_unit = request.POST.get('apartmentsuiteunit')
            town_city = request.POST.get('towncity')
            postcode_zip = request.POST.get('postcodezip')
            phone = request.POST.get('phone')
            email = request.POST.get('emailaddress')

            # Create BillingDetails object (assuming BillingDetails is a separate model)
            billing_details = BillingDetails(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                state=state,
                street_address=street_address,
                apartment_suite_unit=apartment_suite_unit,
                town_city=town_city,
                postcode_zip=postcode_zip,
                phone=phone,
                email=email,
            )
            billing_details.save()

        total_price = sum(item.product.product_price * item.quantity for item in cart_items)

        # Convert total_price to a float before storing it in the session
        request.session['order_total'] = float(total_price)

        # Redirect to the payment page to complete the order
        return redirect('payment')

    # If it's not a POST request or not a place order request, continue displaying the cart items
    total_price = sum(item.product.product_price * item.quantity for item in cart_items)

    # Convert total_price to a float before passing it to the template
    context = {
        'cart_items': cart_items,
        'total_price': float(total_price),
        'billing_details': billing_details,  # Pass billing_details to the template
    }

    return render(request, 'usertems/checkout.html', context)


#payment
from django.shortcuts import render
import razorpay
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

razorpay_client = razorpay.Client(
    auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

@login_required
def payment(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = Decimal(sum(cart_item.product.product_price * cart_item.quantity for cart_item in cart_items))
    currency = 'INR'
    amount = int(total_price * 100)
    
    # Create a Razorpay Order
    razorpay_order = razorpay_client.order.create(dict(
        amount=amount,
        currency=currency,
        payment_capture='0'
    ))

    # Order id of the newly created order
    razorpay_order_id = razorpay_order['id']
    callback_url = '/paymenthandler/'

    # Create an Order outside the loop
    order = Order.objects.create(
        user=request.user,
        total_price=total_price,
        razorpay_order_id=razorpay_order_id,
        payment_status=Order.PaymentStatusChoices.PENDING,
    )

    # Loop through cart items and create OrderItem for each product
    for cart_item in cart_items:
        product = cart_item.product
        price = product.product_price
        quantity = cart_item.quantity
        total_item_price = price * quantity

        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            seller=product.seller,
            quantity=quantity,
            price=price,
            total_price=total_item_price,
        )

    # Save the order to generate an order ID
    order.save()

    # Create a context dictionary with all the variables you want to pass to the template
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
        'callback_url': callback_url,
        'order_item': order_item,
    }

    return render(request, 'usertems/payment.html', context=context)




@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')

        # Verify the payment signature.
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        result = razorpay_client.utility.verify_payment_signature(params_dict)

        if not result:
            # Signature verification failed.
            return render(request, 'paymentfail.html')

        # Signature verification succeeded.
        # Retrieve the order from the database
        try:
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
        except Order.DoesNotExist:
            return HttpResponseBadRequest("Order not found")

        if order.payment_status == Order.PaymentStatusChoices.SUCCESSFUL:
            # Payment is already marked as successful, ignore this request.
            return HttpResponse("Payment is already successful")

        if order.payment_status != Order.PaymentStatusChoices.PENDING:
            # Order is not in a pending state, do not proceed with stock update.
            return HttpResponseBadRequest("Invalid order status")

        # Capture the payment amount
        amount = int(order.total_price * 100)  # Convert Decimal to paise
        razorpay_client.payment.capture(payment_id, amount)

        # Update the order with payment ID and change status to "Successful"
        order.payment_id = payment_id
        order.payment_status = Order.PaymentStatusChoices.SUCCESSFUL
        order.save()

        # Remove the products from the cart and update stock
        cart_items = Cart.objects.filter(user=request.user)
        for cart_item in cart_items:
            product = cart_item.product
            if product.product_stock >= cart_item.quantity:
                # Decrease the product stock and update ProductSummary
                product.product_stock -= cart_item.quantity
                product.save()
                summary, created = ProductSummary.objects.get_or_create(product_name=product.product_name)
                summary.update_total_stock()
                # Remove the item from the cart
                cart_item.delete()
            else:
                # Handle insufficient stock, you can redirect or show an error message
                return HttpResponseBadRequest("Insufficient stock for some items")

        # # Redirect to a payment success page
        # subject = 'Order Confirmation: Your Reservation Was Successful'
        # message = 'We are delighted to confirm that your reservation has been successfully processed. Your choice in our selection is greatly appreciated! Your selected indoor plants are now reserved for you at our store. To complete your purchase and secure your chosen plants, kindly visit our store location at your earliest convenience.'
        # from_email = settings.EMAIL_HOST_USER  # Your sender email address
        # recipient_list = [order.user.email]
        # send_mail(subject, message, from_email, recipient_list)

        # subject = 'Order Confirmation: Reservation for Indoor Plants'
        # message = f'This is to inform you that the following reservation has been confirmed:\n\n'
        # message += 'Customer Name: [order.user.userprofile.name]\n'  # Replace [Customer Name] with the actual customer's name
        # message += 'Email: [order.user.email]\n'  # Replace [Customer Email] with the actual customer's email
        # message += 'Reserved Indoor Plant:\n'
        # message += '- Plant 1\n'  # Replace with the actual plant names and details
        # message += '- Plant 2\n'
        # # Add more plant details as needed
        # message += '\n'
        # message += 'The customer will be visiting your shop to complete the purchase and pick up the reserved plants.'
        # message += '\n\nThank you for using our reservation service.'
        # from_email = settings.EMAIL_HOST_USER  # Your sender email address
        # recipient_list = [order.seller.email]
        # send_mail(subject, message, from_email, recipient_list)
        return redirect('orders')

    return HttpResponseBadRequest("Invalid request method")

@login_required
def orders(request):
    # Retrieve orders for the currently logged-in user
    user_orders = Order.objects.filter(user=request.user)

    # Create a list of tuples containing order, item, and review_status
    order_items = []

    for order in user_orders:
        for item in order.orderitem_set.all():
            review = Review.objects.filter(user=request.user, seller=item.product.seller).first()
            if review:
                review_status = review.review_status
                item.review_id = review.pk  # Add the review_id to the item
                item.review_desc = review.description
            else:
                review_status = 'Pending'  # Default to "Pending" if no review found
                item.review_id = None  # Set review_id to None if no review found
                item.review_desc = None
            order_items.append((order, item, review_status))

    context = {
        'order_items': order_items,
    }

    return render(request, 'usertems/orders.html', context)

# ... Your other imports and view functions ...

def generate_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # Create a Django HTML template for the PDF content
    template = get_template('pdf_order.html')
    context = {'order': order}
    html = template.render(context)

    # Create a PDF file using the HTML content
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice{order_id}.pdf"'

    # Generate PDF from HTML using xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)

    return response

def analyze_sentiment(text):
    analysis = TextBlob(text)
    sentiment_score = analysis.sentiment.polarity
    return sentiment_score

def map_sentiment_to_rating(sentiment_score):
    if sentiment_score >= 0.5:
        return 5
    elif sentiment_score >= 0.2:
        return 4
    elif sentiment_score >= -0.2:
        return 3
    elif sentiment_score >= -0.5:
        return 2
    else:
        return 1
   
@login_required
def submit_review(request):
    if request.method == 'POST':
        seller_id = request.POST.get('seller_id')
        seller = Seller.objects.get(id=seller_id)
        description = request.POST.get('description')
        review_id = request.POST.get('review_id')  # Get the review_id from the form

        # Sentiment Analysis using TextBlob
        sentiment_score = analyze_sentiment(description)

        # Calculate the rating based on sentiment score
        star_rating = map_sentiment_to_rating(sentiment_score)

        if review_id:
            # If review_id is available, it's an edit action
            review = Review.objects.get(review_id=review_id)
            review.description = description
            review.rating = star_rating  # Update the rating based on sentiment
            review.save()
        else:
            # It's an add action
            review = Review.objects.create(
                user=request.user,
                rating=star_rating,  # Use calculated rating
                description=description,
                seller=seller,
                review_status='REVIEWED',
            )
        print(review_id)
        send_review_notification_email(request.user, seller, review)
        # Redirect to a success page or the product detail page
        return redirect('orders')


    
@login_required
def view_orders(request):
    all_orders = Order.objects.all()
    return render(request, 'admin/view_orders.html', {'all_orders': all_orders})

@login_required
def sellerorder(request):
    user = request.user

    # Check if the current user is a seller
    if user.is_staff:
        # If the user is a seller, retrieve the seller profile
        current_seller = user.seller

        # Retrieve the orders for the current seller
        seller_orders = OrderItem.objects.filter(seller=current_seller)

        context = {
            'seller': current_seller,
            'seller_orders': seller_orders,
        }

    return render(request, 'seller/sellerorder.html', context)

@login_required
def seller_approve_order(request, order_id):
    order = get_object_or_404(OrderItem, id=order_id)
    if request.method == 'POST':
        order.seller_is_approved = OrderItem.APPROVED  # Set it to 'approved'
        order.save()
        # subject = 'Congratulations! Your License Has Been Approved'
        # message = 'We are delighted to inform you that your license application has been successfully approved. Your dedication and compliance with the necessary requirements have made this approval possible. We appreciate your patience throughout the process. With your approved license, you are now officially recognized and authorized to add your plants. '
        # from_email = settings.EMAIL_HOST_USER  # Your sender email address
        # recipient_list = [order.seller.email]
        # send_mail(subject, message, from_email, recipient_list)
    return redirect('sellerorder')

@login_required
def customer_approve_order(request, order_id):
    order = get_object_or_404(OrderItem, id=order_id)
    if request.method == 'POST':
        order.customer_is_approved = OrderItem.COLLECTED  # Set it to 'approved'
        order.save()
        # subject = 'Congratulations! Your License Has Been Approved'
        # message = 'We are delighted to inform you that your license application has been successfully approved. Your dedication and compliance with the necessary requirements have made this approval possible. We appreciate your patience throughout the process. With your approved license, you are now officially recognized and authorized to add your plants. '
        # from_email = settings.EMAIL_HOST_USER  # Your sender email address
        # recipient_list = [order.seller.email]
        # send_mail(subject, message, from_email, recipient_list)
    return redirect('orders')




from django.shortcuts import render
from django.http import JsonResponse
from .models import ProductSummary,Recommend
from .models import Review  # Import your Review model


def live_search(request):
    if request.method == 'GET':
        search_query = request.GET.get('query', '')
        results = ProductSummary.objects.filter(product_name__icontains=search_query)
        product_data = []

        for product in results:
            # You can add more fields from the ProductSummary model as needed
            product_info = {
                'name': product.product_name,
                'prod_id': product.id,

                 # Include img1 URL
            }
            product_data.append(product_info)

        return JsonResponse({'products': product_data})
    


# myapp/views.py
from django.shortcuts import render
from django.http import JsonResponse
import joblib
import numpy as np
import pandas as pd

def plant_recommendation(request):
    symptoms = ['Light Requirements', 'Watering Frequency', 'Humidity Tolerance', 'Temperature Range','Maintenance Difficulty', 'Toxicity to Pets', 'Aesthetic Appeal', 'Air-Purifying','Indoor Space', 'Price Range', 'Recommended For']
    symptoms = sorted(symptoms)
    context = {'symptoms':symptoms, 'status':'1'}
    return render(request,'recommendation/plantrecommendation.html', context)


nb_model = joblib.load('models/naive_bayes.pkl')

list_a = ['Light Requirements', 'Watering Frequency', 'Humidity Tolerance', 'Temperature Range',
          'Maintenance Difficulty', 'Toxicity to Pets', 'Aesthetic Appeal', 'Air-Purifying',
          'Indoor Space', 'Price Range', 'Recommended For']


@csrf_exempt
def MakePrediction(request):
    s1 = request.POST.get('s1')
    s2 = request.POST.get('s2')
    s3 = request.POST.get('s3')
    s4 = request.POST.get('s4')
    s5 = request.POST.get('s5')
    id = request.POST.get('id')

    list_b = [s1, s2, s3, s4, s5]
    list_c = [0] * len(list_a)
    for symptom in list_b:
        if symptom in list_a:
            list_c[list_a.index(symptom)] = 1
    test = np.array(list_c).reshape(1, -1)
    prediction = nb_model.predict(test)
    result = prediction[0]
    a = Recommend(s1=s1, s2=s2, s3=s3, s4=s4, s5=s5, plant=result, user_id=id)
    a.save()

    return JsonResponse({'status': result})



def predict_result(request):
    userid = request.user.id
    plant = Recommend.objects.all().filter(user_id=userid)
    context = {'plant':plant,'status':'1'}
    return render(request,'recommendation/predict_form.html',context)

    

from django.http import JsonResponse
from django.shortcuts import render
import joblib
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def plant_recommendation(request):
    return render(request,'recommendation/plantrecommendation.html')

def recommendation(request):
    model = joblib.load('models/random_forest_model.pkl')
    user = request.user

    if request.method == 'POST':
        # Get the input data from the form
        air_purification = request.POST.get('air_purification_level')
        humidity_increase = request.POST.get('humidity_increase_level')
        stress_reduction = request.POST.get('stress_reduction_level')
        mental_health = request.POST.get('mental_health_level')
        productivity = request.POST.get('productivity_level')
        sleep_improvement = request.POST.get('sleep_improvement_level')
        aesthetic_pleasure = request.POST.get('aesthetic_pleasure_level')
        aromatherapy_level = request.POST.get('aroma_benefit_level')

        input_data = pd.DataFrame({
            'Air Purification': [float(air_purification) if air_purification else 0.0],
            'Humidity Increase': [float(humidity_increase) if humidity_increase else 0.0],
            'Stress Reduction': [float(stress_reduction) if stress_reduction else 0.0],
            'Mental Health': [float(mental_health) if mental_health else 0.0],
            'Productivity': [float(productivity) if productivity else 0.0],
            'Sleep Improvement': [float(sleep_improvement) if sleep_improvement else 0.0],
            'Aromatherapy': [float(aromatherapy_level) if aromatherapy_level else 0.0],
            'Aesthetic Pleasure': [float(aesthetic_pleasure) if aesthetic_pleasure else 0.0],
        })

        

        N = 30
        predicted_probabilities = model.predict_proba(input_data)[0]
        sorted_plants = sorted(zip(model.classes_, predicted_probabilities), key=lambda x: -x[1])
        top_n_recommendations = [plant for plant, _ in sorted_plants[:N]]

        recommended_plants_formatted = [plant.lower().replace(' ', '') for plant in top_n_recommendations]

        recommended_plants = []  # Create an empty list to store matching plants

        for plant_name in recommended_plants_formatted:
            matching_plants = ProductSummary.objects.filter(product_name__icontains=plant_name)
            recommended_plants.extend(matching_plants)

        X_test = pd.read_csv('models/plantsample.csv')  # Load your test data
        y_test = X_test['Plant Name']
        X_test = X_test[['Air Purification', 'Humidity Increase', 'Stress Reduction', 'Mental Health', 'Productivity', 'Sleep Improvement', 'Aromatherapy', 'Aesthetic Pleasure']]
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy of the Random Forest model: {accuracy:.2f}")
        # Now, recommended_plants contains all matching plants
        response_data = {'recommended_plants': top_n_recommendations, 'accuracy': accuracy, 'matching_plants': recommended_plants}
        


    return render(request, 'recommendation/result.html',response_data )



@login_required
def add_recommwishlist(request, product_id):
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

@login_required
def remove_recommwishlist(request, product_id):
    product = get_object_or_404(ProductSummary, pk=product_id)

    wishlist_item = Wishlist.objects.filter(product=product)
    if request.method == 'POST':
        wishlist_item.delete()
    return redirect('product_single',product_id=product_id) 





