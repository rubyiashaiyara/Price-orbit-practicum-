from django.urls import path
from . import views
from .views import run_all_scrapers, home, product

urlpatterns = [
    path("scrape/run/", run_all_scrapers, name="run_all_scrapers"),
    path('home/', home, name="home_page"),
    path("product/", product, name="product_page"),
    
]
