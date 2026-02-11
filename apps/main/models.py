from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from PIL import Image
import urllib.parse


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
    product_code = models.CharField(max_length=50, unique=True, blank=True, null=True , help_text="Your physical product code (e.g., EYE-PHO-042, SKU-12345)")
    whatsapp_message = models.TextField(blank=True, help_text="Custom WhatsApp message for this product")
    whatsapp_share_message = models.TextField(blank=True, help_text="Custom WhatsApp share message (leave blank for auto-generated)")
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
        # Import inside method to avoid circular imports
        from django.db import ProgrammingError
        
        try:
            company_info = CompanyInfo.objects.first()
            # CRITICAL FIX: Remove all spaces from WhatsApp number
            whatsapp_number = company_info.whatsapp.replace(' ', '').replace('-', '') if company_info else '263784342632'
        except (ProgrammingError, Exception):
            whatsapp_number = '263784342632'
    
        # Use custom message if provided, otherwise use default
        if self.whatsapp_message:
            message = self.whatsapp_message
        else:
            # Build rich message with product details
            message_parts = [
                "🛒 *ORDER REQUEST*",
                "",
                f"📦 Product: {self.name}",
            ]
            
            # Add product code if available
            if self.product_code:
                message_parts.append(f"🔢 Code: {self.product_code}")
            
            message_parts.append(f"💰 Price: ${self.price}")
            
            # Add savings if on sale
            if self.old_price and self.old_price > self.price:
                savings = float(self.old_price) - float(self.price)
                message_parts.append(f"💸 You Save: ${savings:.2f}")
            
            # Add urgency if low stock
            if self.stock_quantity <= 5 and self.stock_quantity > 0:
                message_parts.append(f"⚠️ Only {self.stock_quantity} left in stock!")
            
            # Add product link
            message_parts.extend([
                "",
                f"📱 View product: {self.get_full_url()}",
                "",
                "Hi! I'd like to order this product. Please confirm availability and delivery options.",
            ])
            
            message = "\n".join(message_parts)
        
        encoded_message = urllib.parse.quote(message)
        
        return f"https://wa.me/{whatsapp_number}?text={encoded_message}"
    
    def get_full_url(self):
        """Get full absolute URL for product"""
        from django.contrib.sites.models import Site
        try:
            current_site = Site.objects.get_current()
            domain = current_site.domain
            protocol = 'https' if not domain.startswith('localhost') else 'http'
            return f"{protocol}://{domain}{self.get_absolute_url()}"
        except:
            # Fallback to hardcoded domain
            return f"https://eyedentity-gx20.onrender.com{self.get_absolute_url()}"
    
    @property
    def whatsapp_quick_quote(self):
        """Generate WhatsApp link for quote request"""
        from django.db import ProgrammingError
        
        try:
            company_info = CompanyInfo.objects.first()
            whatsapp_number = company_info.whatsapp.replace(' ', '').replace('-', '') if company_info else '263784342632'
        except (ProgrammingError, Exception):
            whatsapp_number = '263784342632'
        
        # Build message with product code if available
        message_parts = [f"Hi! I'd like a quote for {self.name}"]
        
        if self.product_code:
            message_parts[0] += f" (Code: {self.product_code})"
        
        message_parts.extend([
            ". Please provide:",
            "- Availability",
            "- Delivery cost to my location",
            "- Payment options",
            "- Total price"
        ])
        
        message = "\n".join(message_parts)
        
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{whatsapp_number}?text={encoded_message}"
    
    @property
    def whatsapp_share_link(self):
        """Generate WhatsApp share link with product image"""
        from django.db import ProgrammingError
        
        # Use custom share message if provided
        if self.whatsapp_share_message:
            message = self.whatsapp_share_message.format(
                product_name=self.name,
                product_code=self.product_code if self.product_code else 'N/A',
                price=self.price,
                url=self.get_full_url()
            )
        else:
            # Default share message with product details
            message_parts = [
                f"👓 Check out this eyewear! 👓",
                "",
                f"*{self.name}*",
            ]
            
            # Add product code if available
            if self.product_code:
                message_parts.append(f"Code: {self.product_code}")
            
            message_parts.append(f"Price: ${self.price}")
            
            # Add discount info if on sale
            if self.old_price and self.old_price > self.price:
                message_parts.append(f"🔥 Save {self.discount_percentage}% (Was ${self.old_price})")
            
            # Add features if available
            if self.features.exists():
                features_list = ", ".join([f.name for f in self.features.all()[:3]])
                message_parts.append(f"✨ Features: {features_list}")
            
            message_parts.extend([
                "",
                f"View details: {self.get_full_url()}",
                "",
                "🛒 Shop premium eyewear at Eyedentity!",
            ])
            
            message = "\n".join(message_parts)
        
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/?text={encoded_message}"
    
    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})


class Wishlist(models.Model):
    session_key = models.CharField(max_length=40, db_index=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Wishlist {self.session_key}"
    
    @property
    def total_price(self):
        """Calculate total price of all items"""
        return sum(float(item.product.price) for item in self.items.all())
    
    @property
    def whatsapp_order_link(self):
        """Generate WhatsApp message for all wishlist items"""
        from django.db import ProgrammingError
        
        try:
            company_info = CompanyInfo.objects.first()
            whatsapp_number = company_info.whatsapp.replace(' ', '').replace('-', '') if company_info else '263784342632'
        except (ProgrammingError, Exception):
            whatsapp_number = '263784342632'
        
        message_parts = [
            "🛒 *MULTIPLE ITEMS ORDER*",
            "",
            "I'm interested in ordering the following items:",
            "",
        ]
        
        for item in self.items.select_related('product__category').all():
            product = item.product
            message_parts.append(
                f"📦 {product.name}\n"
                f"   Code: {product.product_code}\n"
                f"   Price: ${product.price}"
            )
            message_parts.append("")
        
        message_parts.extend([
            f"💰 *Total: ${self.total_price:.2f}*",
            "",
            "Please confirm:",
            "- Availability of all items",
            "- Total delivery cost to my location",
            "- Payment options",
            "- Estimated delivery time",
        ])
        
        message = "\n".join(message_parts)
        encoded_message = urllib.parse.quote(message)
        
        return f"https://wa.me/{whatsapp_number}?text={encoded_message}"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['wishlist', 'product']
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.product.name} in wishlist"


class WhatsAppOrderClick(models.Model):
    product_id = models.CharField(max_length=50)
    product_name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    session_key = models.CharField(max_length=40, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-clicked_at']
        verbose_name = "WhatsApp Order Click"
        verbose_name_plural = "WhatsApp Order Clicks"
    
    def __str__(self):
        return f"{self.product_name} - {self.clicked_at.strftime('%Y-%m-%d %H:%M')}"


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
        from django.core.exceptions import ValidationError
        if self.product and self.product.additional_images.exists():
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
    whatsapp = models.CharField(max_length=20, help_text="WhatsApp number (e.g., 263784342632)")
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
        
        # Clean WhatsApp number
        if self.whatsapp:
            self.whatsapp = self.whatsapp.replace(' ', '').replace('-', '').replace('+', '')
        
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
                pass