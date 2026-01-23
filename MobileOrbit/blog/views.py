from django.shortcuts import render
from django.http import JsonResponse
from .scraper import run_all_scrapers
from django.db.models import Q
from .models import Wishlist
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductListing, Wishlist, Shop, Product, ProductListing, Payment
import uuid  #unic identifier
from django.contrib import messages
import requests
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest

@login_required
# def sslcommerz_payment(request, product_id):
#     # 1️⃣ Get product safely
#     product = get_object_or_404(Product, id=product_id)

#     # 2️⃣ Create payment record (pending)
#     payment = Payment.objects.create(
#         user=request.user,
#         product=product,
#         transaction_id=f"TXN{product.id}{request.user.id}",
#         amount=product.discount_price if product.discount_price > 0 else product.regular_price,
#         status="Pending",
#     )

#     # 3️⃣ Prepare SSLCommerz payload its a stracture to create oboject of ssl commerce api
#     payload = {
#         "store_id": settings.SSLCOMMERZ_STORE_ID,
#         "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
#         "total_amount": payment.amount,
#         "currency": "BDT",
#         "tran_id": payment.transaction_id,
#         "success_url": request.build_absolute_uri("/payment/success/"),
#         "fail_url": request.build_absolute_uri("/payment/fail/"),
#         "cancel_url": request.build_absolute_uri("/payment/cancel/"),
#         "cus_name": request.user.get_full_name() or request.user.username,
#         "cus_email": request.user.email or "test@example.com",
#         "cus_add1": "Dhaka",
#         "cus_city": "Dhaka",
#         "cus_country": "Bangladesh",
#         "cus_phone": "01748196522",
#         "shipping_method": "NO",
#         "product_name": product.name,
#         "product_category": "Mobile",
#         "product_profile": "general",
#     }

#     # 4️⃣ Call SSLCommerz API
#     response = requests.post(
#         settings.SSLCOMMERZ_INIT_URL,
#         data=payload
#     )

#     data = response.json()

#     # 5️⃣ Redirect to payment gateway
#     if data.get("status") == "SUCCESS":
#         return HttpResponseRedirect(data["GatewayPageURL"])

#     # 6️⃣ Fallback if gateway fails
#     payment.status = "Failed"
#     payment.save()
#     return HttpResponseRedirect("/")

@login_required
def sslcommerz_payment(request, product_id):
    #  Get product safely
    product = get_object_or_404(Product, id=product_id)

    # Create unique transaction ID
    transaction_id =str(uuid.uuid4())

    # Create payment record (Pending)
    payment = Payment.objects.create(
        user=request.user,
        product=product,
        transaction_id=transaction_id,
        amount=product.discount_price if product.discount_price > 0 else product.regular_price,
        status="Pending",
    )

    #  Prepare SSLCommerz payload
    payload = {
        "store_id": settings.SSLCOMMERZ_STORE_ID,
        "store_passwd": settings.SSLCOMMERZ_STORE_PASSWORD,
        "total_amount": payment.amount,
        "currency": "BDT",
        "tran_id": payment.transaction_id,
        "success_url": request.build_absolute_uri("/payment/success/"),
        "fail_url": request.build_absolute_uri("/payment/fail/"),
        "cancel_url": request.build_absolute_uri("/payment/cancel/"),
        "cus_name": request.user.get_full_name() or request.user.username,
        "cus_email": request.user.email or "test@example.com",
        "cus_phone": "01748196522",
        "cus_add1": "Dhaka",
        "cus_city": "Dhaka",
        "cus_country": "Bangladesh",
        "shipping_method": "NO",
        "product_name": product.name,
        "product_category": "Mobile",
        "product_profile": "general",
    }

    #  Call SSLCommerz API
    response = requests.post(settings.SSLCOMMERZ_INIT_URL, data=payload)
    data = response.json()

    # If gateway created successfully → show processing page
    if data.get("status") == "SUCCESS":
        return render(
            request,
            "processing.html",
            {
                "transaction_id": payment.transaction_id,
                "amount": payment.amount,
                "gateway_url": data["GatewayPageURL"],
            }
        )

    # If gateway fails
    payment.status = "Failed"
    payment.save()
    return HttpResponseRedirect("/")

@csrf_exempt #post api for success
def payment_success(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")

    tran_id = request.POST.get("tran_id")

    if not tran_id:
        return HttpResponseBadRequest("Transaction ID not found")

    try:
        payment = Payment.objects.get(transaction_id=tran_id)
    except Payment.DoesNotExist:
        return HttpResponseBadRequest("Payment record does not exist")

    # Update payment status safely
    payment.status = "Success"
    payment.save(update_fields=["status"])

    return render(request, "payment_success.html", {
        "payment": payment
    })


# def payment_success(request):
#     tran_id = request.POST.get("tran_id")
#     payment = Payment.objects.get(transaction_id=tran_id)  #get transection id from database
#     payment.status = "Success" #status cheance
#     payment.save()
    # return redirect("download_invoice", tran_id=tran_id)

@csrf_exempt
def payment_fail(request):
    tran_id = request.POST.get("tran_id") 
    Payment.objects.filter(transaction_id=tran_id).update(status="Failed")
    return HttpResponse("Payment Failed")

@csrf_exempt
def payment_cancel(request):
    return HttpResponse("Payment Cancelled")

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )

    return redirect(request.META.get('HTTP_REFERER', 'product_page'))


@login_required
def wishlist_page(request):
    wishlist_items = Wishlist.objects.select_related('product').filter(user=request.user)

    return render(request, 'blog/wishlist.html', {
        'wishlist_items': wishlist_items
    })

@login_required
def shop_list(request):
    # Fetch all shops
    shops = Shop.objects.prefetch_related('outlets').all()

    selected_shop = request.GET.get('shop')

    context = {
        "shops": shops,
        "selected_shop": selected_shop,
    }

    return render(request, "blog/Shop.html", context)

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

@login_required
def download_invoice(request, tran_id):
    payment = get_object_or_404(Payment, transaction_id=tran_id, user=request.user)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="invoice_{tran_id}.pdf"'

    doc = SimpleDocTemplate(response)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("<b>PriceFinder Invoice</b>", styles["Title"]),
        Paragraph(f"Username: {payment.user}", styles["Normal"]),
        Paragraph(f"Transaction ID: {payment.transaction_id}", styles["Normal"]),
        Paragraph(f"Product: {payment.product.name}", styles["Normal"]),
        Paragraph(f"Amount Paid: ৳{payment.amount}", styles["Normal"]),
        Paragraph(f"Status: {payment.status}", styles["Normal"]),
    ]

    doc.build(content)
    return response

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

@login_required
def deal_page(request, product_id):
    product = Product.objects.get(id=product_id)
    
    # You must query ALL listings for this product
    listings = ProductListing.objects.filter(product=product) 
    
    context = {
        'product': product,
        'listings': listings, # This is what populates the table
    }
    return render(request, 'Deal.html', context)


# def deal_page(request, product_id):
#     product = get_object_or_404(Product, id=product_id)

#     listings = ProductListing.objects.select_related("shop").filter(product=product)

#     deals = []
#     for listing in listings:
#         deals.append({
#             "shop": listing.shop.shop_name,
#             "shop_logo_url": listing.shop.logo.url if hasattr(listing.shop, "logo") and listing.shop.logo else None,
#             "price": listing.price,
#             "regular_price": listing.old_price,
#             "discount_percentage": listing.discount_percent(),
#             "in_stock": listing.in_stock,
#             "rating": getattr(listing.shop, "rating", None),
#             "link": listing.link,
#         })
#     print("deals: ", deals)
#     in_stock_deals = [d for d in deals if d["in_stock"]]
#     best_deal = min(in_stock_deals, key=lambda x: x["price"], default=None)

#     return render(request, "Deal.html", {
#         "product": product,
#         "deals": deals,
#         "best_deal": best_deal,
#     })


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

# def deal_search_view(request):
#     query = request.GET.get('q')
#     context = {
#         'query': query,
#         'product': None,
#         'listings': [],
#         'best_deal': None
#     }
    
#     # Only run logic if there is a query
#     if query:
#         found_products = Product.objects.filter(name__icontains=query)
#         if found_products.exists():
#             target_product = found_products.first()
#             listings = ProductListing.objects.filter(product=target_product).order_by('price')
#             context['product'] = target_product
#             context['listings'] = listings
#             if listings.exists():
#                 context['best_deal'] = listings.first()
#     return render(request, 'deal.html', context)

@login_required
def deal_search_view(request):
    query = request.GET.get('q', '').strip()

    context = {
        'query': query,
        'product': None,
        'deals': [],
        'best_deal': None,
    }

    if not query:
        return render(request, 'Deal.html', context)

    # Find all similar products
    products = Product.objects.filter(name__icontains=query) #---------filter for name

    if not products.exists():
        return render(request, 'Deal.html', context)

    # Use first product as main reference
    main_product = products.first()
    context['product'] = main_product

    deals = []
    for product in products:
        deals.append({
            "shop": product.store_name,
            "shop_logo_url": None,  # optional
            "price": product.discount_price if product.discount_price > 0 else product.regular_price,
            "regular_price": product.regular_price,
            "discount_percentage": product.discount_percentage,
            "in_stock": True,  # static
            "link": product.link,
        })

    # Sort by lowest price
    deals = sorted(deals, key=lambda x: x["price"])
    context['deals'] = deals
    context['best_deal'] = deals[0] if deals else None

    return render(request, 'Deal.html', context)

def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        # Filter the products based on the query (you can adjust this as needed)
        suggestions = Product.objects.filter(name__icontains=query)[:5]
        suggestions_list = [{'name': product.name} for product in suggestions]
        return JsonResponse(suggestions_list, safe=False)
    return JsonResponse([], safe=False)

def deals_admin(request):
    return render(request, 'deals_admin.html')

