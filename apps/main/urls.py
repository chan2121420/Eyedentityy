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

    # Wishlist URLs
    path('wishlist/', views.view_wishlist, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/count/', views.get_wishlist_count, name='wishlist_count'),
    
    # WhatsApp Actions
    path('product/<int:product_id>/quick-quote/', views.quick_quote, name='quick_quote'),
    path('product/<int:product_id>/share/', views.share_product, name='share_product'),
    path('api/track-whatsapp-order/', views.track_whatsapp_order, name='track_whatsapp_order'),
]
