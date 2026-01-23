from django.urls import path
from .views import register_view, login_view, logout_view, profile_view
from django.conf import settings
from django.conf.urls.static import static
from blog import views

urlpatterns = [
    path('singup/', register_view, name='singup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path("pay/<int:product_id>/", views.sslcommerz_payment, name="pay"),
    path("invoice/<str:tran_id>/", views.download_invoice, name="download_invoice"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)