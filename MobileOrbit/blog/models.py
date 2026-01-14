from django.db import models
from django.conf import settings # Use settings to reference the User model

# -------------------------
# Simple Wishlist Model
# (Allows duplicate products per user)
# -------------------------
class Wishlist(models.Model):
    """
    Represents a single entry in a user's wishlist.
    A product can be added multiple times by the same user.
    """
    # Links to the User model
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist_items'
    )
    
    # Links to the Product model
    product = models.ForeignKey(
        'Product', 
        on_delete=models.CASCADE,
        related_name='in_wishlists'
    )
    
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # NOTE: We have intentionally removed 'unique_together'
        # to allow a user to add the same product multiple times.
        ordering = ['-added_at'] # Shows the newest additions first

    def __str__(self):
        # We assume the User model has a 'username' attribute
        return f"{self.user.username} wished for {self.product.name}"

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
    shop_logo = models.URLField(max_length=500, blank=True, help_text="Shop logo URL")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.shop_name


# -------------------------
# ShopOutlet Model
# -------------------------
class ShopOutlet(models.Model):
    outlet_name = models.CharField(max_length=255)
    outlet_address = models.TextField()
    phone_number = models.CharField(max_length=15, null=True, blank=True) 

    off_day = models.CharField(
        max_length=10,
        choices=[
            ('Saturday', 'Saturday'),
            ('Sunday', 'Sunday'),
            ('Monday', 'Monday'),
            ('Tuesday', 'Tuesday'),
            ('Wednesday', 'Wednesday'),
            ('Thursday', 'Thursday'),
            ('Friday', 'Friday'),
        ],
        null=True,
        blank=True
    )

    # closing_time = models.TimeField(null=True, blank=True)

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="outlets"
    )
    opening_time = models.TimeField(null=True, blank=True)
    closing_time = models.TimeField(null=True, blank=True)

    shop = models.ForeignKey(
        Shop,
        on_delete=models.CASCADE,
        related_name="outlets"
    )

    def __str__(self):
        return f"{self.outlet_name} ({self.shop.shop_name})"

    def get_operating_hours(self):
        if self.opening_time and self.closing_time:
            return f"{self.opening_time.strftime('%I:%M %p')} - {self.closing_time.strftime('%I:%M %p')}"
        return "Hours not specified"
    
# -------------------------
# ProductDetails Model
# -------------------------
class Product(models.Model):
    name = models.CharField(max_length=500)
    brand = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(max_length=1000, blank=True, null=True)
    regular_price = models.IntegerField(default=0)
    discount_price = models.IntegerField(default=0)
    discount_percentage = models.CharField(max_length=10, blank=True, null=True)
    link = models.URLField(max_length=1000, unique=True) # Unique link prevents duplicates
    store_name = models.CharField(max_length=50) # To know if it's from KRY, Dazzle, etc.
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class ProductListing(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='listings')
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    link = models.URLField(max_length=500)
    in_stock = models.BooleanField(default=True)
    
    def discount_percent(self):
        if self.old_price and self.old_price > self.price:
            return int(100 - (self.price / self.old_price * 100))
        return 0

    def __str__(self):
        return f"{self.product.name} - {self.shop.shop_name}"
    