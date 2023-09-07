
from django.db import models
from django.contrib.auth.models import User

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # approved = models.BooleanField(default=False)
    storename = models.CharField(max_length=100)
    contact = models.CharField(max_length=15)
    address = models.TextField()

    def str(self):
        return self.user.username

class Certification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    certification_image = models.ImageField(upload_to='certification_image/', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    expiry_date_from = models.DateField()
    expiry_date_to = models.DateField()
    certification_authority = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class ApplicationStatus(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)

class Category(models.Model):
    category_name = models.CharField(max_length=100)
    category_description = models.TextField()
    default_product_price = models.DecimalField(max_digits=10, decimal_places=2)
    # category_image = models.ImageField(upload_to='category_images/', null=True, blank=True)  # Default product price for this category
    # Other fields for the category...

    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_name = models.CharField(max_length=100)  # Product name selected by the seller
    product_description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)  # Reference to the category
    product_price = models.DecimalField(max_digits=10, decimal_places=2, editable=False)  # Product price inherited from the category
    product_image = models.ImageField(upload_to='category_images/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Inherit the default price from the associated category
        self.product_price = self.category.default_product_price
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.product_name
    
    
    @property
    def is_staff(self):
        return self.is_admin
    
