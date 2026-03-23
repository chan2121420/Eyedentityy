from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django_ckeditor_5.views import upload_file

from apps.main.sitemaps import ProductSitemap, CategorySitemap, StaticViewSitemap
from apps.blog.sitemaps import BlogPostSitemap, BlogCategorySitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
    'blog_posts': BlogPostSitemap,
    'blog_categories': BlogCategorySitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor5/image_upload/', login_required(upload_file), name='ck_editor_5_upload_file'),
    path('', include('apps.main.urls')),
    path('blog/', include('apps.blog.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('.well-known/', include([])),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

handler404 = 'apps.main.views.handler404'
handler500 = 'apps.main.views.handler500'