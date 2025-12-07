from django.urls import path

from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('about-glasses/', views.about_glasses, name='about_glasses'),
    path('contact/', views.contact, name='contact'),
    
    # Categories
    path('categories/', views.categories_list, name='categories'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Products
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('product/add/', views.add_product, name='add_product'),
    
    # AJAX endpoints
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('api/product/<int:product_id>/variants/', views.get_product_variants, name='product_variants'),
    path('api/category/<slug:category_slug>/products/', views.get_category_products, name='category_products'),
]