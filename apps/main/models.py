from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from PIL import Image


# AboutGlasses model for dynamic about page content
class AboutGlasses(models.Model):
    title = models.CharField(max_length=200, default="About Our Glasses")
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "About Our Glasses"
        verbose_name_plural = "About Our Glasses"

    def __str__(self):
        return self.title
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from PIL import Image


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True)
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('category_detail', kwargs={'slug': self.slug})


class Feature(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, blank=True, help_text="Bootstrap icon class (e.g., 'bi-shield-check')")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Product(models.Model):
    LENS_TYPES = [
        ('prescription', 'Prescription'),
        ('reading', 'Reading'),
        ('sunglasses', 'Sunglasses'),
        ('blue_light', 'Blue Light Blocking'),
        ('photochromic', 'Photochromic'),
        ('polarized', 'Polarized'),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    lens_type = models.CharField(max_length=20, choices=LENS_TYPES, blank=True)
    features = models.ManyToManyField(Feature, blank=True)
    
    # Product specifications
    frame_material = models.CharField(max_length=100, blank=True)
    lens_material = models.CharField(max_length=100, blank=True)
    uv_protection = models.CharField(max_length=50, blank=True)
    
    # Business fields
    stock_quantity = models.PositiveIntegerField(default=0)
    whatsapp_message = models.TextField(blank=True, help_text="Custom WhatsApp message for this product")
    is_featured = models.BooleanField(default=False)
    is_on_sale = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto-set is_on_sale if old_price exists
        if self.old_price and self.old_price > self.price:
            self.is_on_sale = True
        else:
            self.is_on_sale = False
            
        super().save(*args, **kwargs)

    @property
    def discount_percentage(self):
        if self.old_price and self.old_price > self.price:
            discount = ((self.old_price - self.price) / self.old_price) * 100
            return round(discount)
        return 0

    @property
    def whatsapp_link(self):
        from .models import CompanyInfo
        company_info = CompanyInfo.objects.first()
        whatsapp_number = company_info.whatsapp if company_info else '263784342632'
        
        if self.whatsapp_message:
            message = self.whatsapp_message
        else:
            message = f"Hi! I'm interested in the {self.name} priced at ${self.price}. Can you tell me more?"
        
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{whatsapp_number}?text={encoded_message}"

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.product.name} - Image"

    def clean(self):
        # Ensure a product has at most 5 additional images (plus the main image = 6 max)
        from django.core.exceptions import ValidationError
        if self.product and self.product.additional_images.exists():
            # If this instance is new (no pk yet) count existing ones
            existing_count = self.product.additional_images.count()
            if not self.pk and existing_count >= 5:
                raise ValidationError('A product can have at most 5 additional images.')
        return super().clean()


class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-created_at']

    def __str__(self):
        return f"{self.name} - {self.rating} stars"


class CompanyInfo(models.Model):
    name = models.CharField(max_length=200, default="Eyedentity Eyewear")
    tagline = models.CharField(max_length=200, default="Stylish. Protective. Uniquely You.")
    description = RichTextUploadingField()
    address = models.TextField()
    phone = models.CharField(max_length=20)
    whatsapp = models.CharField(max_length=20, help_text="WhatsApp number without + sign")
    email = models.EmailField(blank=True)
    opening_hours = models.TextField()
    map_embed = models.TextField(blank=True, help_text="Google Maps embed code")
    logo = models.ImageField(upload_to='company/', blank=True)
    
    # Social media
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Company Information"
        verbose_name_plural = "Company Information"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one CompanyInfo instance exists
        if not self.pk and CompanyInfo.objects.exists():
            raise ValueError("Only one CompanyInfo instance is allowed")
        super().save(*args, **kwargs)


class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['-subscribed_at']


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


# User Profile Extension
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize avatar if it exists
        if self.avatar:
            try:
                img = Image.open(self.avatar.path)
                if img.height > 300 or img.width > 300:
                    output_size = (300, 300)
                    img.thumbnail(output_size)
                    img.save(self.avatar.path)
            except Exception:
                pass  # Handle any image processing errors gracefully


# Signal to create user profile
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)