from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

# Import sitemaps
from apps.main.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap
from apps.blog.sitemaps import BlogPostSitemap, BlogCategorySitemap

# Sitemap configuration
sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog_posts': BlogPostSitemap,
    'blog_categories': BlogCategorySitemap,
}

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # CKEditor
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # Main app URLs
    path('', include('apps.main.urls')),
    
    # Blog app URLs
    path('blog/', include('apps.blog.urls')),
    
    # SEO URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    
    # Additional utility URLs
    path('.well-known/', include([
        # Add any .well-known routes here if needed
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Add debug toolbar if installed
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom error handlers
handler404 = 'apps.main.views.handler404'
handler500 = 'apps.main.views.handler500'