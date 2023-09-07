from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User


# Create your models here.


class User(AbstractUser):
    is_admin= models.BooleanField('Is admin', default=False)
    is_customer = models.BooleanField('Is customer', default=False)
    is_seller = models.BooleanField('Is seller', default=False)
    is_legaladvisor= models.BooleanField('Is advisor', default=False)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='user_groups',
        related_query_name='user_group'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='user_permissions',
        related_query_name='user_permission'
    )

class UserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    # Add other fields related to the user profile
    
    def __str__(self):
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