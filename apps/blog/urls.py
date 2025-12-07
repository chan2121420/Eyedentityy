from django.urls import path
from . import views

urlpatterns = [
    # Main blog pages
    path('', views.blog_list, name='blog_list'),
    path('search/', views.blog_search, name='blog_search'),
    
    # Blog post detail
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    
    # Category and tag pages
    path('category/<slug:slug>/', views.blog_category, name='blog_category'),
    path('tag/<slug:slug>/', views.blog_tag, name='blog_tag'),
    
    # AJAX endpoints
    path('api/popular/', views.get_popular_posts, name='api_popular_posts'),
    path('api/recent/', views.get_recent_posts, name='api_recent_posts'),
]