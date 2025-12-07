from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import BlogCategory, BlogPost, Tag, BlogComment


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'post_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    ordering = ['name']
    
    def post_count(self, obj):
        return obj.posts.filter(is_published=True).count()
    post_count.short_description = 'Published Posts'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'post_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_active']
    ordering = ['name']
    
    def post_count(self, obj):
        return obj.blogpost_set.filter(is_published=True).count()
    post_count.short_description = 'Posts Using Tag'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'category', 'is_published', 'is_featured',
        'views', 'read_time', 'published_status', 'created_at'
    ]
    list_filter = [
        'category', 'is_published', 'is_featured', 'author',
        'created_at', 'published_at'
    ]
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ['is_published', 'is_featured']
    filter_horizontal = ['tags']
    readonly_fields = ['views', 'word_count_display', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'category', 'content', 'excerpt')
        }),
        ('Media', {
            'fields': ('featured_image', 'image_caption')
        }),
        ('Classification', {
            'fields': ('tags',)
        }),
        ('SEO', {
            'fields': ('meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'read_time')
        }),
        ('Statistics', {
            'fields': ('views', 'word_count_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def published_status(self, obj):
        if obj.is_published:
            if obj.published_at:
                return format_html(
                    '<span style="color: green;">Published on {}</span>',
                    obj.published_at.strftime('%b %d, %Y')
                )
            else:
                return format_html('<span style="color: orange;">Published (date not set)</span>')
        else:
            return format_html('<span style="color: red;">Draft</span>')
    published_status.short_description = 'Publication Status'
    
    def word_count_display(self, obj):
        return f"{obj.word_count:,} words"
    word_count_display.short_description = 'Word Count'
    
    def save_model(self, request, obj, form, change):
        # Auto-set author to current user if creating new post
        if not change:
            obj.author = request.user
        
        # Set published_at when first published
        if obj.is_published and not obj.published_at:
            obj.published_at = timezone.now()
            
        super().save_model(request, obj, form, change)
    
    actions = ['make_published', 'make_draft', 'make_featured', 'remove_featured']
    
    def make_published(self, request, queryset):
        updated = 0
        for obj in queryset:
            if not obj.is_published:
                obj.is_published = True
                if not obj.published_at:
                    obj.published_at = timezone.now()
                obj.save()
                updated += 1
        self.message_user(request, f'{updated} posts published.')
    make_published.short_description = 'Publish selected posts'
    
    def make_draft(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f'{updated} posts marked as draft.')
    make_draft.short_description = 'Mark selected posts as draft'
    
    def make_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts marked as featured.')
    make_featured.short_description = 'Mark selected posts as featured'
    
    def remove_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} posts removed from featured.')
    remove_featured.short_description = 'Remove featured status from selected posts'


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'post_title', 'content_preview', 'is_approved', 
        'is_reply', 'created_at'
    ]
    list_filter = ['is_approved', 'created_at', 'post__category']
    search_fields = ['name', 'email', 'content', 'post__title']
    list_editable = ['is_approved']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Comment Details', {
            'fields': ('post', 'parent', 'name', 'email', 'website')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Moderation', {
            'fields': ('is_approved', 'created_at')
        }),
    )
    
    def post_title(self, obj):
        return obj.post.title
    post_title.short_description = 'Post'
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment Preview'
    
    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'
    
    actions = ['approve_comments', 'unapprove_comments']
    
    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} comments approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def unapprove_comments(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} comments unapproved.')
    unapprove_comments.short_description = 'Unapprove selected comments'


# Customize admin interface
admin.site.site_header = "Eyedentity Blog Admin"
admin.site.site_title = "Blog Admin"
admin.site.index_title = "Blog Administration"