from django.shortcuts import render


# # Create your views here.
# from django.shortcuts import render, get_object_or_404
# from .models import ProductDetails, Brand, Shop, ShopOutlet
# from django.http import JsonResponse
# from django.core.management import call_command

# # ------------------------
# # Home / List all products
# # ------------------------
# def product_list(request):
#     products = ProductDetails.objects.all()  # fetch all products
#     return render(request, "products/product_list.html", {"products": products})

# # ------------------------
# # Product detail page
# # ------------------------
# def product_detail(request, product_id):
#     product = get_object_or_404(ProductDetails, id=product_id)
#     return render(request, "products/product_detail.html", {"product": product})

# # ------------------------
# # Brand list
# # ------------------------
# def brand_list(request):
#     brands = Brand.objects.all()
#     return render(request, "products/brand_list.html", {"brands": brands})

# # ------------------------
# # Shop list
# # ------------------------
# def shop_list(request):
#     shops = Shop.objects.all()
#     return render(request, "products/shop_list.html", {"shops": shops})

# # ------------------------
# # ShopOutlet list for a specific shop
# # ------------------------
# def shop_outlets(request, shop_id):
#     shop = get_object_or_404(Shop, id=shop_id)
#     outlets = shop.outlets.all()  # using related_name='outlets'
#     return render(request, "products/shop_outlets.html", {"shop": shop, "outlets": outlets})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Brand, Shop, ProductDetails
from .scraper import scrape_dazzle, scrape_pickaboo, scrape_rio, scrape_mobileclub


# -------------------------------
# PRICE CLEANER
# -------------------------------
def clean_price(price_str):
    """
    Converts: "৳ 25,500" → 25500.0
    """
    try:
        p = price_str.replace("৳", "").replace(",", "").replace("Tk", "").strip()
        return float(p)
    except:
        return 0.0


# -------------------------------
# MAIN SCRAPE & SAVE VIEW
# -------------------------------
@csrf_exempt
def run_all_scrapers(request):

    # Create shop entries (only once)
    dazzle_shop, _ = Shop.objects.get_or_create(
        shop_name="Dazzle",
        defaults={"shop_fb_link": "", "shop_url": "https://dazzle.com.bd"}
    )

    pickaboo_shop, _ = Shop.objects.get_or_create(
        shop_name="Pickaboo",
        defaults={"shop_fb_link": "", "shop_url": "https://pickaboo.com"}
    )

    rio_shop, _ = Shop.objects.get_or_create(
        shop_name="Rio International",
        defaults={"shop_fb_link": "", "shop_url": "https://riointernational.com.bd"}
    )

    mobileclub_shop, _ = Shop.objects.get_or_create(
        shop_name="Mobile Club",
        defaults={"shop_url": "https://www.mobileclub.com.bd"}
    )
    saved_count = 0

    # -------------------------------
    # 1. SCRAPE DAZZLE
    # -------------------------------
    dazzle_data = scrape_dazzle()

    for item in dazzle_data:
        brand_name = detect_brand(item["name"])
        brand, _ = Brand.objects.get_or_create(name=brand_name)

        ProductDetails.objects.create(
            product_name=item["name"],
            brand=brand,
            shop_id=dazzle_shop,
            price=clean_price(item["price"]),
            product_link=item["link"],
            rating=None,
            product_info="",
            stock=""
        )
        saved_count += 1

    # -------------------------------
    # 2. SCRAPE PICKABOO
    # -------------------------------
    pickaboo_data = scrape_pickaboo()
    

    for item in pickaboo_data:
        brand_name = detect_brand(item["name"])
        brand, _ = Brand.objects.get_or_create(name=brand_name)

        ProductDetails.objects.create(
            product_name=item["name"],
            brand=brand,
            shop_id=pickaboo_shop,
            price=clean_price(item["price"]),
            product_link=item["link"],
            rating=None,
            product_info="",
            stock=""
        )
        saved_count += 1
        
        
      # -------------------------------
    # 4. SCRAPE MOBILE CLUB (API)
    # -------------------------------
    mobileclub_data = scrape_mobileclub()

    for item in mobileclub_data:
        brand, _ = Brand.objects.get_or_create(name=item["brand"])

        ProductDetails.objects.create(
            product_name=item["name"],
            brand=brand,
            shop_id=mobileclub_shop,
            price=clean_price(item["price"]),
            product_link=item.get("link", ""),
            rating=None,
            product_info="",
            stock=item.get("stock", "")
        )
        saved_count += 1

    # -------------------------------
    # 3. SCRAPE RIO INTERNATIONAL
    # -------------------------------
    rio_data = scrape_rio()

    for item in rio_data:
        brand_name = detect_brand(item["name"])
        brand, _ = Brand.objects.get_or_create(name=brand_name)

        ProductDetails.objects.create(
            product_name=item["name"],
            brand=brand,
            shop_id=rio_shop,
            price=clean_price(item["price"]),
            product_link=item["link"],
            rating=None,
            product_info="",
            stock=""
        )
        saved_count += 1

    # -------------------------------
    # RESPONSE
    # -------------------------------
    return JsonResponse({
        "status": "success",
        "message": "All scrapers completed successfully!",
        "total_data_saved": saved_count,
    })



def home(request):
    products = ProductDetails.objects.all() 
    return render(request, 'base.html', {'products': products})

def product(request):
    products = ProductDetails.objects.select_related("brand", "shop_id").all()

    context = {
        "products": products
    }
    return render(request, "product.html", context)

from .models import Brand

def detect_brand(product_name):
    product_name = product_name.lower()

    for brand in Brand.objects.values_list("name", flat=True):
        if brand.lower() in product_name:
            return brand

    return "Unknown"

def clean_price(price_str):
    try:
        return float(
            price_str.replace("৳", "")
                     .replace(",", "")
                     .replace("Tk", "")
                     .strip()
        )
    except:
        return 0.0