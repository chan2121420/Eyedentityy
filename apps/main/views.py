from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.conf import settings
import json


from .models import (
    Product, Category, Testimonial, CompanyInfo, 
    Newsletter, ContactMessage, Feature, AboutGlasses
)
from .forms import ProductForm
def add_product(request):
    """View to add a new product via form"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('shop')
    else:
        form = ProductForm()
    return render(request, 'main/add_product.html', {'form': form, 'company_info': get_company_info()})

def about_glasses(request):
    """View for the About Our Glasses page"""
    about = AboutGlasses.objects.order_by('-last_updated').first()
    return render(request, 'main/about_glasses.html', {
        'company_info': get_company_info(),
        'about': about,
    })

    def about_glasses(request):
        """View for the About Our Glasses page"""
        return render(request, 'main/about_glasses.html', {'company_info': get_company_info()})

def home(request):
    """Homepage view with featured products, categories, and testimonials"""
    def chunked(iterable, n):
        """Yield successive n-sized chunks from iterable."""
        for i in range(0, len(iterable), n):
            yield iterable[i:i + n]

    sale_products = list(Product.objects.filter(
        is_on_sale=True,
        is_active=True
    ).order_by('-created_at')[:6])
    sale_product_groups = list(chunked(sale_products, 3))

    context = {
        'sale_products': sale_products,
        'sale_product_groups': sale_product_groups,
        'featured_products': Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).order_by('-created_at')[:6],
        'categories': Category.objects.filter(is_active=True)[:6],
        'testimonials': Testimonial.objects.filter(
            is_active=True
        ).order_by('-is_featured', '-created_at')[:3],
        'company_info': get_company_info(),
        'about_glasses_cards': AboutGlasses.objects.all().order_by('id'),
    }
    return render(request, 'main/home.html', context)


def categories_list(request):
    """Categories page showing all product categories"""
    categories = Category.objects.filter(is_active=True).annotate(
        product_count=Count('products', filter=Q(products__is_active=True))
    ).order_by('order', 'name')
    about = AboutGlasses.objects.order_by('-last_updated').first()
    context = {
        'categories': categories,
        'company_info': get_company_info(),
        'about': about,
    }
    return render(request, 'main/categories.html', context)


def category_detail(request, slug):
    """Category detail page with products"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products_list = Product.objects.filter(
        category=category, 
        is_active=True
    ).order_by('-is_featured', '-created_at')
    
    # Pagination
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'products': products,
        'company_info': get_company_info(),
    }
    return render(request, 'main/category_detail.html', context)


def shop(request):
    """Shop page with filtering and pagination"""
    products_list = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True).order_by('order', 'name')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products_list = products_list.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filtering
    current_category = request.GET.get('category', '')
    if current_category:
        products_list = products_list.filter(category__slug=current_category)
    
    # Price filtering
    price_filter = request.GET.get('price', '')
    if price_filter == 'low':
        products_list = products_list.filter(price__lt=15)
    elif price_filter == 'mid':
        products_list = products_list.filter(price__gte=15, price__lte=25)
    elif price_filter == 'high':
        products_list = products_list.filter(price__gt=25)
    
    # Ordering
    order_by = request.GET.get('order', '-created_at')
    if order_by in ['price', '-price', 'name', '-name', '-created_at', '-is_featured']:
        products_list = products_list.order_by(order_by)
    
    # Pagination
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'current_category': current_category,
        'price_filter': price_filter,
        'order_by': order_by,
        'company_info': get_company_info(),
    }
    return render(request, 'main/shop.html', context)


def product_detail(request, slug):
    """Individual product detail page"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'company_info': get_company_info(),
        'additional_images': product.additional_images.all()[:5],
    }
    return render(request, 'main/product_detail.html', context)


def about(request):
    """About page with company info and testimonials"""
    company_info = get_company_info()
    testimonials = Testimonial.objects.filter(is_active=True).order_by(
        '-is_featured', '-created_at'
    )[:6]
    
    context = {
        'company_info': company_info,
        'testimonials': testimonials,
    }
    return render(request, 'main/about.html', context)


def contact(request):
    """Contact page with form handling"""
    company_info = get_company_info()
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if name and email and subject and message:
            try:
                ContactMessage.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                messages.success(request, 'Thank you for your message! We\'ll get back to you soon.')
                return redirect('contact')
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'company_info': company_info,
    }
    return render(request, 'main/about.html', context)


@require_http_methods(["POST"])
@csrf_exempt
def newsletter_signup(request):
    """AJAX endpoint for newsletter signup"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except json.JSONDecodeError:
        email = request.POST.get('email', '').strip().lower()
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Please enter an email address.'})
    
    # Basic email validation
    if '@' not in email or '.' not in email.split('@')[1]:
        return JsonResponse({'success': False, 'message': 'Please enter a valid email address.'})
    
    try:
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            return JsonResponse({'success': True, 'message': 'Thank you for subscribing to our newsletter!'})
        else:
            if newsletter.is_active:
                return JsonResponse({'success': False, 'message': 'You are already subscribed to our newsletter.'})
            else:
                newsletter.is_active = True
                newsletter.save()
                return JsonResponse({'success': True, 'message': 'Welcome back! Your subscription has been reactivated.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': 'There was an error processing your request.'})


def search(request):
    """Search across products"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('home')
    
    # Search products
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(category__name__icontains=query),
        is_active=True
    ).order_by('-is_featured', '-created_at')
    
    # Pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    context = {
        'query': query,
        'products': products,
        'total_results': paginator.count,
        'company_info': get_company_info(),
    }
    return render(request, 'main/shop.html', context)


# API Views for AJAX requests
def get_product_variants(request, product_id):
    """Get product variants for AJAX requests"""
    try:
        product = Product.objects.get(id=product_id, is_active=True)
        variants = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product_id)[:4]
        
        variants_data = []
        for variant in variants:
            variants_data.append({
                'id': variant.id,
                'name': variant.name,
                'price': str(variant.price),
                'image': variant.image.url if variant.image else '',
                'url': variant.get_absolute_url(),
            })
        
        return JsonResponse({'variants': variants_data})
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


def get_category_products(request, category_slug):
    """Get products for a category via AJAX"""
    try:
        category = Category.objects.get(slug=category_slug, is_active=True)
        products = Product.objects.filter(
            category=category,
            is_active=True
        )[:8]
        
        products_data = []
        for product in products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'old_price': str(product.old_price) if product.old_price else None,
                'image': product.image.url if product.image else '',
                'url': product.get_absolute_url(),
                'is_on_sale': product.is_on_sale,
                'discount_percentage': product.discount_percentage,
            })
        
        return JsonResponse({
            'category': category.name,
            'products': products_data
        })
    except Category.DoesNotExist:
        return JsonResponse({'error': 'Category not found'}, status=404)


# Utility functions
def get_company_info():
    """Get company information, create default if doesn't exist"""
    company_info, created = CompanyInfo.objects.get_or_create(
        defaults={
            'name': "Eyedentity Eyewear",
            'tagline': "Stylish. Protective. Uniquely You.",
            'description': "<p>Premium eyewear solutions in Harare, Zimbabwe.</p>",
            'address': "Harare, Zimbabwe",
            'phone': "+263123456789",
            'whatsapp': "263123456789",
                'email': "info@Eyedentity.co.zw",
            'opening_hours': "Mon-Fri: 9:00 AM - 6:00 PM\nSat: 9:00 AM - 4:00 PM\nSun: Closed"
        }
    )
    return company_info


# Context processors (to be added to settings.py)
def site_context(request):
    """Global context processor for site-wide data"""
    return {
        'company_info': get_company_info(),
        'main_categories': Category.objects.filter(is_active=True)[:5],
    }


# Error handlers
def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', {
        'company_info': get_company_info(),
    }, status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', {
        'company_info': get_company_info(),
    }, status=500)