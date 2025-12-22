from django.contrib import admin
from .models import Brand, Shop, ShopOutlet, ProductDetails

# Register your models here.

admin.site.register(Brand)
admin.site.register(Shop)
admin.site.register(ShopOutlet)
admin.site.register(ProductDetails)