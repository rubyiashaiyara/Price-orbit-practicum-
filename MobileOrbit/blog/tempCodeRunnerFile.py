from django.shortcuts import render
from django.http import JsonResponse
from .scraper import run_all_scrapers
from .models import Product, ProductListing
from django.db.models import Q

def product_autocomplete(request):
    """
    API View: Returns a list of product names for the search bar autocomplete.
    """
    if 'term' in request.GET:
        term = request.GET.get('term')
        # Filter products containing the term (case-insensitive)
        # We assume you want to suggest product names
        qs = Product.objects.filter(name__icontains=term)
        # Limit to 8 results for performance
        titles = list(qs.values_list('name', flat=True)[:8])
        return JsonResponse(titles, safe=False)
    return JsonResponse([], safe=False)

def product_page(request):
    """
    Main Product Page: Handles listing, searching, and filtering.
    """
    # Start with all products sorted by newest
    products = Product.objects.all().order_by('-created_at')
    
    # 1. Main Search Query 'q' (from the search bar)
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query) |
            Q(store_name__icontains=query)
        )

    # 2. Filter by Price Range
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        try:
            products = products.filter(discount_price__gte=int(min_price))
        except ValueError:
            pass # Ignore invalid input
            
    if max_price:
        try:
            # Note: Assuming you want to filter based on the selling price (discount_price)
            products = products.filter(discount_price__lte=int(max_price))
        except ValueError:
            pass

    # 3. Filter by Brands (Checkbox list)
    # request.GET.getlist allows retrieving multiple selected checkboxes
    selected_brands = request.GET.getlist('brand')
    if selected_brands:
        products = products.filter(brand__in=selected_brands)

    # 4. Get a list of all unique brands for the sidebar
    all_brands = Product.objects.values_list('brand', flat=True).distinct().order_by('brand')

    context = {
        'products': products,
        'brands': all_brands,
        'selected_brands': selected_brands, # To keep checkboxes checked after reload
    }
    
    return render(request, 'blog/product_page.html', context)

def home(request):
    return render(request, 'base.html')

def blog_page(request):
    return render(request, 'blog.html')

def deal_page(request):
    return render(request, 'Deal.html')

def trigger_scraping(request):
    """
    Runs scrapers and returns JSON status.
    """
    try:
        run_all_scrapers()
        return JsonResponse({
            "status": "success", 
            "message": "All scraping completed successfully! Data saved to database."
        })
    except Exception as e:
        return JsonResponse({
            "status": "error", 
            "message": str(e)
        }, status=500)

def home_search_view(request):
    # This seems redundant now that logic is in product_page, 
    # but keeping it if you use it on the homepage separately.
    products = Product.objects.all().order_by('-created_at')
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(brand__icontains=query) |
            Q(store_name__icontains=query)
        )
    return render(request, 'base.html', {'products': products})

def deal_search_view(request):
    query = request.GET.get('q')
    context = {
        'query': query,
        'product': None,
        'listings': [],
        'best_deal': None
    }
    
    # Only run logic if there is a query
    if query:
        found_products = Product.objects.filter(name__icontains=query)
        if found_products.exists():
            target_product = found_products.first()
            listings = ProductListing.objects.filter(product=target_product).order_by('price')
            context['product'] = target_product
            context['listings'] = listings
            if listings.exists():
                context['best_deal'] = listings.first()

    return render(request, 'deal.html', context)

def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        # Filter the products based on the query (you can adjust this as needed)
        suggestions = Product.objects.filter(name__icontains=query)[:5]
        suggestions_list = [{'name': product.name} for product in suggestions]
        return JsonResponse(suggestions_list, safe=False)
    return JsonResponse([], safe=False)