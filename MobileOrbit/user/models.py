from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    # Standard fields (first_name, last_name, username, password) are already in AbstractUser
    
    # We override email to make it unique and required
    email = models.EmailField(_('email address'), unique=True)
    
    # New Custom Fields
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    
    # Requires 'pip install Pillow'
    image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    # LOGIN CONFIGURATION
    # We still want to log in with Email, even though we have a username
    USERNAME_FIELD = 'email'
    
    # Fields required when creating a superuser via command line
    # (Email and Password are required by default)
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return self.email
    
    