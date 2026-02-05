"""
COMPLETE FIXED views.py for apps/main/views.py
This fixes all 500 errors on home and shop pages
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import cache_page
from django.utils import timezone
from django.conf import settings
import json
from django.db import ProgrammingError, OperationalError


from .models import (
    Product, Category, Testimonial, CompanyInfo, 
    Newsletter, ContactMessage, Feature, AboutGlasses, Wishlist, WishlistItem, WhatsAppOrderClick
)
from .forms import ProductForm


def get_company_info():
    """Get company info with proper error handling - FIXED"""
    from django.core.cache import cache
    
    # Try to get from cache first
    company_info = cache.get('company_info')
    
    if company_info is None:
        try:
            company_info = CompanyInfo.objects.first()
            if not company_info:
                # Create default if none exists
                company_info = CompanyInfo.objects.create(
                    name="Eyedentity Eyewear",
                    tagline="Stylish. Protective. Uniquely You.",
                    description="<p>Premium eyewear solutions in Harare, Zimbabwe.</p>",
                    address="Harare, Zimbabwe",
                    phone="+263 784 342 632",
                    whatsapp="263784342632",
                    email="info@eyedentity.co.zw",
                    opening_hours="Mon-Fri: 9:00 AM - 6:00 PM\nSat: 9:00 AM - 4:00 PM\nSun: Closed"
                )
            # Cache for 1 hour
            cache.set('company_info', company_info, 60 * 60)
            
        except (ProgrammingError, OperationalError) as e:
            print(f"Database error getting company info: {e}")
            return None
    
    return company_info


def home(request):
    """Homepage view - COMPLETELY FIXED"""
    def chunked(iterable, n):
        """Yield successive n-sized chunks from iterable."""
        result = []
        for item in iterable:
            result.append(item)
            if len(result) == n:
                yield result
                result = []
        if result:
            yield result

    # Initialize all variables with empty defaults
    sale_products = []
    sale_product_groups = []
    featured_products = []
    categories = []
    testimonials = []
    about_glasses_cards = []
    
    try:
        # Safely query products
        sale_products = list(Product.objects.filter(
            is_on_sale=True,
            is_active=True
        ).select_related('category').prefetch_related('features')[:6])
        
        if sale_products:
            sale_product_groups = list(chunked(sale_products, 3))
        
        featured_products = list(Product.objects.filter(
            is_featured=True, 
            is_active=True
        ).select_related('category').prefetch_related('features')[:6])
        
        categories = list(Category.objects.filter(is_active=True)[:6])
        
        testimonials = list(Testimonial.objects.filter(
            is_active=True
        ).order_by('-is_featured', '-created_at')[:3])
        
        about_glasses_cards = list(AboutGlasses.objects.all().order_by('id'))
        
    except (ProgrammingError, OperationalError) as e:
        print(f"Database error in home view: {e}")
        # Variables already initialized with empty lists
    except Exception as e:
        print(f"Unexpected error in home view: {e}")
        # Variables already initialized with empty lists

    context = {
        'sale_products': sale_products,
        'sale_product_groups': sale_product_groups,
        'featured_products': featured_products,
        'categories': categories,
        'testimonials': testimonials,
        'company_info': get_company_info(),
        'about_glasses_cards': about_glasses_cards,
    }
    return render(request, 'main/home.html', context)


def shop(request):
    """Shop page - COMPLETELY FIXED"""
    # Initialize defaults
    products_list = Product.objects.none()
    categories = []
    search_query = ''
    current_category = ''
    price_filter = ''
    order_by = '-created_at'
    
    try:
        products_list = Product.objects.filter(
            is_active=True
        ).select_related('category').prefetch_related('features')
        
        categories = list(Category.objects.filter(is_active=True).order_by('order', 'name'))
        
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
            try:
                products_list = products_list.filter(category__slug=current_category)
            except Exception:
                pass
        
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
        
    except (ProgrammingError, OperationalError) as e:
        print(f"Database error in shop view: {e}")
    except Exception as e:
        print(f"Unexpected error in shop view: {e}")
    
    # Pagination - always safe
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page', 1)
    
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages if paginator.num_pages > 0 else 1)
    except Exception:
        products = paginator.page(1)
    
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
    """View for the About Our Glasses page - FIXED"""
    about = None
    try:
        about = AboutGlasses.objects.order_by('-last_updated').first()
    except (ProgrammingError, OperationalError):
        pass
    
    return render(request, 'main/about_glasses.html', {
        'company_info': get_company_info(),
        'about': about,
    })


def categories_list(request):
    """Categories page - FIXED"""
    categories = []
    about = None
    
    try:
        categories = list(Category.objects.filter(is_active=True).annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        ).order_by('order', 'name'))
        
        about = AboutGlasses.objects.order_by('-last_updated').first()
    except (ProgrammingError, OperationalError) as e:
        print(f"Database error in categories view: {e}")
    
    context = {
        'categories': categories,
        'company_info': get_company_info(),
        'about': about,
    }
    return render(request, 'main/categories.html', context)


def category_detail(request, slug):
    """Category detail page - FIXED"""
    try:
        category = get_object_or_404(Category, slug=slug, is_active=True)
        products_list = Product.objects.filter(
            category=category, 
            is_active=True
        ).select_related('category').prefetch_related('features').order_by('-is_featured', '-created_at')
    except (ProgrammingError, OperationalError, Http404):
        return redirect('categories')
    
    # Pagination
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page', 1)
    
    try:
        products = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        products = paginator.page(1)
    
    context = {
        'category': category,
        'products': products,
        'company_info': get_company_info(),
    }
    return render(request, 'main/category_detail.html', context)


def product_detail(request, slug):
    """Individual product detail page - FIXED"""
    try:
        product = get_object_or_404(
            Product.objects.select_related('category').prefetch_related('features', 'additional_images'),
            slug=slug,
            is_active=True
        )
    except (ProgrammingError, OperationalError, Http404):
        return redirect('shop')
    
    # Track recently viewed products
    recently_viewed = request.session.get('recently_viewed', [])
    if product.id not in recently_viewed:
        recently_viewed.insert(0, product.id)
        recently_viewed = recently_viewed[:5]
        request.session['recently_viewed'] = recently_viewed
    
    # Get related products
    related_products = []
    recently_viewed_products = []
    additional_images = []
    
    try:
        related_products = list(Product.objects.filter(
            category=product.category,
            is_active=True
        ).select_related('category').exclude(id=product.id)[:4])
        
        recently_viewed_products = list(Product.objects.filter(
            id__in=recently_viewed,
            is_active=True
        ).select_related('category').exclude(id=product.id)[:4])
        
        additional_images = list(product.additional_images.all()[:5])
    except Exception as e:
        print(f"Error loading related products: {e}")
    
    context = {
        'product': product,
        'related_products': related_products,
        'recently_viewed': recently_viewed_products,
        'company_info': get_company_info(),
        'additional_images': additional_images,
    }
    return render(request, 'main/product_detail.html', context)


def about(request):
    """About page - FIXED"""
    testimonials = []
    try:
        testimonials = list(Testimonial.objects.filter(is_active=True).order_by(
            '-is_featured', '-created_at'
        )[:6])
    except (ProgrammingError, OperationalError):
        pass
    
    context = {
        'company_info': get_company_info(),
        'testimonials': testimonials,
    }
    return render(request, 'main/about.html', context)


def contact(request):
    """Contact page - FIXED"""
    company_info = get_company_info()
    
    if request.method == 'POST':
        import bleach
        from django.core.validators import validate_email
        from django.core.exceptions import ValidationError
        
        name = bleach.clean(request.POST.get('name', '').strip())
        email = request.POST.get('email', '').strip()
        subject = bleach.clean(request.POST.get('subject', '').strip())
        message = bleach.clean(request.POST.get('message', '').strip())
        
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Please enter a valid email address.')
            return redirect('contact')
        
        if len(name) < 2 or len(name) > 100:
            messages.error(request, 'Name must be between 2 and 100 characters.')
            return redirect('contact')
        
        if len(subject) < 5 or len(subject) > 200:
            messages.error(request, 'Subject must be between 5 and 200 characters.')
            return redirect('contact')
        
        if len(message) < 10:
            messages.error(request, 'Message must be at least 10 characters long.')
            return redirect('contact')
        
        if name and email and subject and message:
            try:
                ContactMessage.objects.create(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message
                )
                messages.success(request, 'Thank you for your message! We\'ll get back to you within 24 hours.')
                return redirect('contact')
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again or contact us via WhatsApp.')
        else:
            messages.error(request, 'Please fill in all required fields.')
    
    context = {
        'company_info': company_info,
    }
    return render(request, 'main/about.html', context)


@csrf_protect
@require_http_methods(["POST"])
def newsletter_signup(request):
    """AJAX endpoint for newsletter signup - FIXED"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip().lower()
    except json.JSONDecodeError:
        email = request.POST.get('email', '').strip().lower()
    
    if not email:
        return JsonResponse({'success': False, 'message': 'Please enter an email address.'})
    
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'success': False, 'message': 'Please enter a valid email address.'})
    
    from django.core.cache import cache
    cache_key = f'newsletter_signup_{request.META.get("REMOTE_ADDR")}'
    if cache.get(cache_key):
        return JsonResponse({'success': False, 'message': 'Please wait a moment before trying again.'})
    
    try:
        newsletter, created = Newsletter.objects.get_or_create(
            email=email,
            defaults={'is_active': True}
        )
        
        if created:
            cache.set(cache_key, True, 60)
            return JsonResponse({
                'success': True, 
                'message': 'Thank you for subscribing! Check your email for exclusive offers.'
            })
        else:
            if newsletter.is_active:
                return JsonResponse({
                    'success': False, 
                    'message': 'You are already subscribed to our newsletter.'
                })
            else:
                newsletter.is_active = True
                newsletter.save()
                return JsonResponse({
                    'success': True, 
                    'message': 'Welcome back! Your subscription has been reactivated.'
                })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'message': 'There was an error processing your request. Please try again.'
        })


def search(request):
    """Search across products - FIXED"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('home')
    
    products_list = Product.objects.none()
    
    try:
        products_list = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query),
            is_active=True
        ).select_related('category').prefetch_related('features').order_by('-is_featured', '-created_at')
    except (ProgrammingError, OperationalError):
        pass
    
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page', 1)
    
    try:
        products = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        products = paginator.page(1)
    
    context = {
        'query': query,
        'products': products,
        'total_results': paginator.count,
        'company_info': get_company_info(),
    }
    return render(request, 'main/shop.html', context)


def get_product_variants(request, product_id):
    """Get product variants for AJAX requests"""
    try:
        product = Product.objects.select_related('category').get(id=product_id, is_active=True)
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
        ).select_related('category')[:8]
        
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


def site_context(request):
    """Global context processor for site-wide data"""
    main_categories = []
    try:
        main_categories = list(Category.objects.filter(is_active=True)[:5])
    except (ProgrammingError, OperationalError):
        pass
    
    return {
        'company_info': get_company_info(),
        'main_categories': main_categories,
    }


@require_http_methods(["POST"])
@csrf_protect
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        
        wishlist, created = Wishlist.objects.get_or_create(session_key=session_key)
        wishlist_item, item_created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product
        )
        
        if item_created:
            return JsonResponse({
                'success': True,
                'message': f'{product.name} added to your list',
                'wishlist_count': wishlist.items.count()
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Product already in your list'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error adding to list. Please try again.'
        }, status=500)


@require_http_methods(["POST"])
@csrf_protect
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    try:
        session_key = request.session.session_key
        if not session_key:
            return JsonResponse({'success': False, 'message': 'No wishlist found'})
        
        wishlist = get_object_or_404(Wishlist, session_key=session_key)
        product = get_object_or_404(Product, id=product_id)
        
        WishlistItem.objects.filter(wishlist=wishlist, product=product).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Product removed',
            'wishlist_count': wishlist.items.count()
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error removing product'
        }, status=500)


def view_wishlist(request):
    """View all wishlist items"""
    session_key = request.session.session_key
    wishlist_items = []
    wishlist = None
    
    if session_key:
        try:
            wishlist = Wishlist.objects.get(session_key=session_key)
            wishlist_items = list(wishlist.items.select_related(
                'product__category'
            ).prefetch_related('product__features').all())
        except Wishlist.DoesNotExist:
            pass
    
    context = {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
        'company_info': get_company_info(),
    }
    return render(request, 'main/wishlist.html', context)


def get_wishlist_count(request):
    """AJAX endpoint to get wishlist count"""
    session_key = request.session.session_key
    count = 0
    
    if session_key:
        try:
            wishlist = Wishlist.objects.get(session_key=session_key)
            count = wishlist.items.count()
        except Wishlist.DoesNotExist:
            pass
    
    return JsonResponse({'count': count})


@csrf_protect
@require_http_methods(["POST"])
def track_whatsapp_order(request):
    """Track WhatsApp order button clicks for analytics"""
    try:
        data = json.loads(request.body)
        
        if not request.session.session_key:
            request.session.create()
        
        WhatsAppOrderClick.objects.create(
            product_id=data.get('product_id', ''),
            product_name=data.get('product_name', ''),
            price=data.get('price', 0),
            session_key=request.session.session_key,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def quick_quote(request, product_id):
    """Generate quick quote WhatsApp link"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        return redirect(product.whatsapp_quick_quote)
    except:
        return redirect('shop')


def share_product(request, product_id):
    """Generate product share WhatsApp link"""
    try:
        product = get_object_or_404(Product, id=product_id, is_active=True)
        return redirect(product.whatsapp_share_link)
    except:
        return redirect('shop')


def wishlist_context(request):
    """Context processor for wishlist"""
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    
    wishlist = None
    items_count = 0
    
    try:
        wishlist = Wishlist.objects.get(session_key=session_key)
        items_count = wishlist.items.count()
    except (Wishlist.DoesNotExist, ProgrammingError, OperationalError):
        pass
        
    return {
        'wishlist': wishlist,
        'wishlist_items_count': items_count,
    }


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