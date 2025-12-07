from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.views.generic import ListView, DetailView
from django.utils import timezone
from django.contrib import messages

from .models import BlogPost, BlogCategory, Tag, BlogComment


def blog_list(request):
    """Blog listing page with category filtering and search"""
    posts_list = BlogPost.objects.filter(is_published=True)
    categories = BlogCategory.objects.filter(is_active=True).annotate(
        post_count=Count('posts', filter=Q(posts__is_published=True))
    ).order_by('name')

    print('posts', posts_list)
    
    # Category filtering
    current_category = request.GET.get('category', '')
    if current_category:
        try:
            category = BlogCategory.objects.get(slug=current_category, is_active=True)
            posts_list = posts_list.filter(category=category)
        except BlogCategory.DoesNotExist:
            # If category doesn't exist, show all posts
            current_category = ''
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        posts_list = posts_list.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Order by featured first, then by published date
    posts_list = posts_list.order_by('-is_featured', '-published_at', '-created_at')
    
    # Pagination
    paginator = Paginator(posts_list, 9)  # 9 posts per page
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/blog_list.html', context)


def blog_detail(request, slug):
    """Blog post detail page with related posts"""
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    
    # Increment view count
    post.increment_views()
    
    # Get related posts
    related_posts = post.get_related_posts(3)
    
    # Get company info for contact details
    from apps.main.views import get_company_info
    company_info = get_company_info()
    
    # Handle comment submission
    if request.method == 'POST' and 'submit_comment' in request.POST:
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        website = request.POST.get('website', '').strip()
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')

        if name and email and content:
            try:
                parent_comment = None
                if parent_id:
                    parent_comment = BlogComment.objects.get(id=parent_id, post=post)

                comment = BlogComment.objects.create(
                    post=post,
                    name=name,
                    email=email,
                    website=website,
                    content=content,
                    parent=parent_comment,
                    is_approved=True  # Instantly approve
                )
                messages.success(request, 'Your comment has been posted.')
                return redirect('blog_detail', slug=post.slug)
            except Exception as e:
                messages.error(request, 'There was an error submitting your comment. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')

    # Get all comments (newest first)
    comments = BlogComment.objects.filter(
        post=post,
        is_approved=True,
        parent=None
    ).order_by('-created_at')
    print('commeent', comments)
    
    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
        'company_info': company_info,
    }
    return render(request, 'blog/blog_detail.html', context)


def blog_category(request, slug):
    """Blog category page showing all posts in a category"""
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    posts_list = BlogPost.objects.filter(
        category=category,
        is_published=True
    ).order_by('-is_featured', '-published_at', '-created_at')
    
    # Pagination
    paginator = Paginator(posts_list, 9)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'posts': posts,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/blog_category.html', context)


def blog_tag(request, slug):
    """Blog tag page showing all posts with a specific tag"""
    tag = get_object_or_404(Tag, slug=slug, is_active=True)
    posts_list = BlogPost.objects.filter(
        tags=tag,
        is_published=True
    ).order_by('-published_at', '-created_at')
    
    # Pagination
    paginator = Paginator(posts_list, 9)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'tag': tag,
        'posts': posts,
        'total_posts': paginator.count,
    }
    return render(request, 'blog/blog_tag.html', context)


def blog_search(request):
    """Dedicated blog search page"""
    query = request.GET.get('q', '').strip()
    posts_list = BlogPost.objects.filter(is_published=True)
    
    if query:
        posts_list = posts_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(category__name__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    else:
        posts_list = posts_list.none()  # Empty queryset if no query
    
    posts_list = posts_list.order_by('-published_at', '-created_at')
    
    # Pagination
    paginator = Paginator(posts_list, 9)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'query': query,
        'posts': posts,
        'total_results': paginator.count,
    }
    return render(request, 'blog/blog_search.html', context)


# AJAX Views
def get_popular_posts(request):
    """Get popular blog posts for AJAX requests"""
    posts = BlogPost.objects.filter(
        is_published=True
    ).order_by('-views', '-published_at')[:5]
    
    posts_data = []
    for post in posts:
        posts_data.append({
            'title': post.title,
            'url': post.get_absolute_url(),
            'views': post.views,
            'published_at': post.published_at.strftime('%B %d, %Y') if post.published_at else '',
            'category': post.category.name,
            'read_time': post.reading_time_display,
        })
    
    return JsonResponse({'posts': posts_data})


def get_recent_posts(request):
    """Get recent blog posts for AJAX requests"""
    posts = BlogPost.objects.filter(
        is_published=True
    ).order_by('-published_at', '-created_at')[:5]
    
    posts_data = []
    for post in posts:
        posts_data.append({
            'title': post.title,
            'url': post.get_absolute_url(),
            'excerpt': post.excerpt,
            'published_at': post.published_at.strftime('%B %d, %Y') if post.published_at else '',
            'category': post.category.name,
            'featured_image': post.featured_image.url if post.featured_image else '',
        })
    
    return JsonResponse({'posts': posts_data})


# Class-based views (alternative implementations)
class BlogListView(ListView):
    """Class-based view for blog listing"""
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(is_published=True)
        
        # Category filtering
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query)
            )
        
        return queryset.order_by('-is_featured', '-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = BlogCategory.objects.filter(is_active=True)
        context['current_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class BlogDetailView(DetailView):
    """Class-based view for blog post detail"""
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)
    
    def get_object(self):
        obj = super().get_object()
        # Increment views
        obj.increment_views()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_posts'] = self.object.get_related_posts(3)
        
        # Get company info
        from apps.main.views import get_company_info
        context['company_info'] = get_company_info()
        
        return context