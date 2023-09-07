from django.contrib import admin
from .models import Seller
from .models import Certification
from .models import Category, Product, UserProfile
# Register your models here.
admin.site.register(Seller)

@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'certification_authority', 'expiry_date_from', 'expiry_date_to', 'certification_authority','certification_image', 'timestamp')
    list_filter = ('certification_authority', 'expiry_date_from', 'expiry_date_to')
    search_fields = ('first_name', 'last_name', 'certification_authority')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_name', 'default_product_price')  # Customize the fields to display
    list_filter = ('default_product_price',)  # Add filters if needed
    search_fields = ('category_name', 'category_description')  # Add search fields if needed

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'category', 'product_price','product_image')  # Customize the fields to display
    list_filter = ('category', 'product_price')  # Add filters if needed
    search_fields = ('product_name', 'product_description')  # Add search fields if needed

# Register your models here.
admin.site.register(UserProfile)