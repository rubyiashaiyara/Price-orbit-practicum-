from django.db import models

# Create your models here.
from django.db import models

# -------------------------
# Brand Model
# -------------------------
class Brand(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True,  unique=True)

    def __str__(self):
        return self.name


# -------------------------
# Shop Model
# -------------------------
class Shop(models.Model):
    shop_name = models.CharField(max_length=255)
    shop_fb_link = models.URLField(max_length=500)
    shop_url = models.URLField(max_length=500)

    def __str__(self):
        return self.shop_name


# -------------------------
# ShopOutlet Model
# -------------------------
class ShopOutlet(models.Model):
    outlet_name = models.CharField(max_length=255)
    outlet_address = models.TextField()
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="outlets")

    def __str__(self):
        return f"{self.outlet_name} ({self.shop.shop_name})"


# -------------------------
# ProductDetails Model
# -------------------------
class ProductDetails(models.Model):
    product_name = models.CharField(max_length=255)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name="shop")
    price = models.FloatField()
    product_link = models.URLField(max_length=500, default=None)
    rating = models.FloatField(null=True, blank=True)
    product_info = models.TextField(blank=True)
    stock = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    

    def __str__(self):
        return f"{self.product_name} ({self.shop.shop_name})"
