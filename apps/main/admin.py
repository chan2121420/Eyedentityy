from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, Product, ProductImage, Feature, Testimonial, 
    CompanyInfo, Newsletter, ContactMessage, UserProfile, AboutGlasses, Wishlist, WhatsAppOrderClick
)

# Register AboutGlasses for admin editing
@admin.register(AboutGlasses)
class AboutGlassesAdmin(admin.ModelAdmin):
    list_display = ["title", "last_updated"]
    search_fields = ["title", "content"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'order', 'product_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active', 'order']
    ordering = ['order', 'name']
    
    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    product_count.short_description = 'Active Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 5
    fields = ['image', 'alt_text', 'is_primary']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'price', 'old_price', 'discount_display', 
        'is_featured', 'is_on_sale', 'is_active', 'stock_quantity', 'created_at'
    ]
    list_filter = [
        'category', 'lens_type', 'is_featured', 'is_on_sale', 
        'is_active', 'created_at'
    ]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured', 'is_active', 'stock_quantity']
    filter_horizontal = ['features']
    inlines = [ProductImageInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'old_price')
        }),
        ('Product Details', {
            'fields': (
                'lens_type', 'features', 'frame_material', 
                'lens_material', 'uv_protection'
            )
        }),
        ('Business Settings', {
            'fields': (
                'stock_quantity', 'whatsapp_message', 'is_featured', 
                'is_on_sale', 'is_active'
            )
        }),
    )
    
    def discount_display(self, obj):
        if obj.discount_percentage > 0:
            return format_html(
                '<span style="color: green; font-weight: bold;">{}%</span>',
                obj.discount_percentage
            )
        return '-'
    discount_display.short_description = 'Discount'
    
    def save_model(self, request, obj, form, change):
        # Auto-set is_on_sale based on pricing
        if obj.old_price and obj.old_price > obj.price:
            obj.is_on_sale = True
        else:
            obj.is_on_sale = False
        super().save_model(request, obj, form, change)


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon_class', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    list_editable = ['is_active']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'rating', 'is_featured', 'is_active', 'created_at']
    list_filter = ['rating', 'is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'text']
    list_editable = ['is_featured', 'is_active']
    ordering = ['-is_featured', '-created_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['created_at']
        return []


@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'tagline', 'description', 'logo')
        }),
        ('Contact Details', {
            'fields': ('address', 'phone', 'whatsapp', 'email', 'opening_hours')
        }),
        ('Online Presence', {
            'fields': ('facebook_url', 'instagram_url', 'twitter_url')
        }),
        ('Technical', {
            'fields': ('map_embed',),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one CompanyInfo instance
        if CompanyInfo.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of CompanyInfo
        return False


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']
    ordering = ['-subscribed_at']
    readonly_fields = ['subscribed_at']
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} subscriptions activated.')
    activate_subscriptions.short_description = 'Activate selected subscriptions'
    
    def deactivate_subscriptions(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} subscriptions deactivated.')
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    list_editable = ['is_read']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = 'Mark selected messages as read'
    
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} messages marked as unread.')
    mark_as_unread.short_description = 'Mark selected messages as unread'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'date_of_birth', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email', 'phone']
    readonly_fields = ['created_at']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return ['user', 'created_at']
        return ['created_at']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'email', 'item_count', 'total_price', 'created_at']
    search_fields = ['session_key', 'email']
    readonly_fields = ['created_at', 'updated_at']
    
    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = 'Items'


@admin.register(WhatsAppOrderClick)
class WhatsAppOrderClickAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'price', 'ip_address', 'clicked_at']
    list_filter = ['clicked_at']
    search_fields = ['product_name', 'product_id', 'ip_address']
    readonly_fields = ['clicked_at']
    date_hierarchy = 'clicked_at'
    
    def has_add_permission(self, request):
        return False  

# Admin site customization
admin.site.site_header = "Eyedentity Eyewear Admin"
admin.site.site_title = "Eyedentity Admin"
admin.site.index_title = "Welcome to Eyedentity Administration"