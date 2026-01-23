from django.contrib import admin
from .models import Brand, Shop, ShopOutlet, Product, Wishlist, Payment

# Register your models here.

admin.site.register(Brand)
admin.site.register(Shop)
admin.site.register(ShopOutlet)
admin.site.register(Product)
admin.site.register(Wishlist)
admin.site.register(Payment)