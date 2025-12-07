from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField

class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Blog Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_category', kwargs={'slug': self.slug})


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['name']


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    category = models.ForeignKey(BlogCategory, on_delete=models.CASCADE, related_name='posts')
    content = RichTextUploadingField()
    excerpt = models.TextField(max_length=300, help_text="Brief description for listings")
    featured_image = models.ImageField(upload_to='blog/')
    image_caption = models.CharField(max_length=200, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    
    # SEO fields
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Status and visibility
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    read_time = models.PositiveIntegerField(default=5, help_text="Estimated read time in minutes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at when first published
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
            
        # Auto-generate meta description from excerpt if not provided
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
            
        # Auto-calculate read time based on content length
        if self.content:
            import re
            # Remove HTML tags for word count
            clean_content = re.sub('<.*?>', '', self.content)
            word_count = len(clean_content.split())
            # Average reading speed is 200 words per minute
            self.read_time = max(1, round(word_count / 200))
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

    def increment_views(self):
        """Increment view count"""
        self.views += 1
        self.save(update_fields=['views'])

    def get_related_posts(self, count=3):
        """Get related posts based on category and tags"""
        related_posts = BlogPost.objects.filter(
            category=self.category,
            is_published=True
        ).exclude(id=self.id)
        
        # If we have tags, prioritize posts with similar tags
        if self.tags.exists():
            tag_ids = list(self.tags.values_list('id', flat=True))
            related_posts = related_posts.filter(tags__in=tag_ids).distinct()
        
        return related_posts.order_by('-published_at', '-created_at')[:count]

    @property
    def reading_time_display(self):
        """Display reading time in a user-friendly format"""
        if self.read_time == 1:
            return "1 min read"
        return f"{self.read_time} min read"

    @property
    def word_count(self):
        """Calculate approximate word count"""
        if self.content:
            import re
            clean_content = re.sub('<.*?>', '', self.content)
            return len(clean_content.split())
        return 0


class BlogComment(models.Model):
    """Model for blog post comments (optional feature)"""
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField(blank=True)
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # For nested comments (replies)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.name} on {self.post.title}'

    @property
    def is_reply(self):
        return self.parent is not None