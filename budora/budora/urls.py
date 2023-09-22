"""budora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from user import views
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('register.html',views.register, name='register'),
    path('login.html',views.loginu,  name='loginu'),
    path('index.html', views.index, name='index'),
    path('logoutmessage/', views.logoutmessage, name='logoutmessage'),
    path('logout/', views.loggout, name='loggout'),
    path('accounts/', include('allauth.urls')),
    
    path('dashlegal', views.dashlegal, name='dashlegal'),
    path('admin_index', views.admin_index, name='admin_index'),
    path('addcategory', views.addcategory, name='addcategory'),
    path('viewcategory', views.viewcategory, name='viewcategory'),
    path('viewaddproduct', views.viewaddproduct, name='viewaddproduct'),
    path('addproducts', views.addproducts, name='addproducts'),
    path('viewproducts', views.viewproducts, name='viewproducts'),
    path('store', views.store, name='store'),
    path('product', views.product, name='product'),

    path('saveproduct', views.saveproduct, name='saveproduct'),


    # path('update_product', views.update_product, name='update_product'),

    path('category/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('edit_category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('approve_certification/<int:certification_id>/', views.approve_certification, name='approve_certification'),
    path('reject_certification/<int:certification_id>/', views.reject_certification, name='reject_certification'),

    path('seller_login.html', views.seller_login, name='seller_login.html'),
    path('seller_register', views.seller_register, name='seller_register'),
    path('approvalpending', views.approvalpending, name='approvalpending'),
    path('seller_index', views.seller_index, name='seller_index'),
    path('seller_logout/', views.seller_loggout, name='seller_loggout'),
    path('admin_logout/', views.admin_loggout, name='admin_loggout'),

    path('successseller.html', views.successseller, name='successseller'),
    path('successaddcategory.html', views.successaddcategory, name='successaddcategory'),
    path('successaddproduct.html', views.successaddproduct, name='successaddproduct'),
    path('delete_add_product/<int:product_id>/', views.delete_add_product, name='delete_add_product'),

    # path('approve_seller/<int:application_id>/', views.approve_seller, name='approve_seller'),
    # path('reject_seller/<int:application_id>/', views.reject_seller, name='reject_seller'),
    
    path('profile', views.profile, name='profile'),

    path('user_dashboard/', views.user_dashboard, name='user_dashboard'),
    path('plant_recommendation/', views.plant_recommendation, name='plant_recommendation'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('viewstock', views.view_products, name='viewstock'),
    path('product-summary/<int:pk>/edit/', views.edit_product_stock, name='edit_product_stock'),
    path('product_single/<int:product_id>/', views.product_single, name='product_single'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('remove_from_wishlist/<int:wishlist_item_id>/',views.remove_from_wishlist, name='remove_from_wishlist'),
    # path('remove_storewishlist/<int:wishlist_item_id>/',views.remove_storewishlist, name='remove_storewishlist'),
    path('remove_productwishlist/<int:wishlist_item_id>/',views.remove_productwishlist, name='remove_productwishlist'),
    # path('remove_indexwishlist/<int:wishlist_item_id>/',views.remove_indexwishlist, name='remove_indexwishlist'),
    path('add_productwishlist/<int:product_id>/', views.add_productwishlist, name='add_productwishlist'),
    # path('add_indexwishlist/<int:product_id>/', views.add_indexwishlist, name='add_indexwishlist'),
    # path('add_storewishlist/<int:product_id>/', views.add_indexwishlist, name='add_storewishlist'),
    #userlist
    path('user_list', views.user_list, name='user_list'),
    path('activate_user/<int:user_id>/', views.activate_user, name='activate_user'),
    path('deactivate_user/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('edit_user/<int:user_id>/', views.edit_user, name='edit_user'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

