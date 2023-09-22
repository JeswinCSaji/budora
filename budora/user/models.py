
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True, blank=True)
    email = models.EmailField(max_length=255,null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    # gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # approved = models.BooleanField(default=False)
    name = models.CharField(max_length=100,null=True, blank=True)
    email = models.EmailField(max_length=255,null=True, blank=True)
    storename = models.CharField(max_length=100)
    contact = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(blank=True, null=True)

    def str(self):
        return self.user.username

class Certification(models.Model):
    APPROVED = 'approved'
    REJECTED = 'rejected'
    PENDING = 'pending'
    
    APPROVAL_CHOICES = [
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (PENDING, 'Pending'),
    ]
    # seller = models.ForeignKey(Seller, on_delete=models.CASCADE, default=Seller)

    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    certification_image = models.ImageField(upload_to='certification_image/', null=True, blank=True)
    owner_name = models.CharField(max_length=100)  # Change 'first_name' to 'owner_name'
    store_name = models.CharField(max_length=100)  # Add 'store_name' field
    expiry_date_from = models.DateField()
    expiry_date_to = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_approved = models.CharField(
        max_length=10,
        choices=APPROVAL_CHOICES,
        default=PENDING,
    )
    
class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_description = models.TextField()
    # default_product_price = models.DecimalField(max_digits=10, decimal_places=2)
    # category_image = models.ImageField(upload_to='category_images/', null=True, blank=True)  # Default product price for this category
    # Other fields for the category...

    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=100)  # Product name selected by the seller
    product_description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Reference to the category
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Product price inherited from the category
    product_image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    product_stock = models.IntegerField(default=0, null=True, blank=True)  # Add the default value here

    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, default=1)

    
    def __str__(self):
        return self.product_name

    def save(self, *args, **kwargs):
        super(Product, self).save(*args, **kwargs)
        # After saving the product, update the ProductSummary
        summary, created = ProductSummary.objects.get_or_create(product_name=self.product_name)
        summary.update_total_stock()
        
class ProductSummary(models.Model):
    product_name = models.CharField(max_length=100, unique=True)
    product_sci_name = models.CharField(max_length=100, blank=True, null=True)
    total_stock = models.IntegerField(default=0, null=True, blank=True)
    product_image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    product_description = models.TextField(blank=True, null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Additional fields
    light_requirements = models.CharField(max_length=100, blank=True, null=True)
    water_requirements = models.CharField(max_length=100, blank=True, null=True)
    humidity_requirements = models.CharField(max_length=100, blank=True, null=True)
    soil_type = models.CharField(max_length=100, blank=True, null=True)
    toxicity_information = models.TextField( blank=True, null=True)
    maintenance_instructions = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.product_name

    def update_total_stock(self):
        # Calculate the total stock for this product name from the Product model
        total_stock = Product.objects.filter(product_name=self.product_name).aggregate(total_stock=Sum('product_stock'))['total_stock']
        self.total_stock = total_stock or 0
        self.save()
    @receiver(post_save, sender=Product)
    @receiver(post_delete, sender=Product)
    def update_product_summary(sender, instance, **kwargs):
        product_name = instance.product_name

        # Calculate the total stock for the given product name
        total_stock = Product.objects.filter(product_name=product_name).aggregate(total_stock=Sum('product_stock'))['total_stock']

        # Update or create the corresponding ProductSummary instance
        product_summary, created = ProductSummary.objects.get_or_create(product_name=product_name)
        product_summary.total_stock = total_stock or 0
        product_summary.save()

    @property
    def is_staff(self):
        return self.is_admin

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductSummary, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='Wishlist_item_images/', blank=True, null=True)  # Add image field

    def __str__(self):
        return f"{self.user.username}'s Wishlist Item - {self.product.product_name}"