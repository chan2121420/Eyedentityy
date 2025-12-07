from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost, BlogCategory


class BlogPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class BlogCategorySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return BlogCategory.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at