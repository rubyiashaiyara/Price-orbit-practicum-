from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home_page'),

    path('product/', views.product_page, name='product_page'),
    path('product/autocomplete/', views.product_autocomplete, name='product_autocomplete'),

    path('blog/', views.blog_page, name='blog'),

    # ✅ DEALS URL (THIS IS IMPORTANT)
    path('deals/', views.deal_search_view, name='deal_page'),

    path('search-suggestions/', views.search_suggestions, name='search_suggestions'),
    path('scrape/run/', views.trigger_scraping, name='run_all_scrapers'),

    path("shop/", views.shop_list, name="shop_detail"),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
]
