from django.urls import path
from . import views


urlpatterns = [
    path('', views.products, name='products'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('wishlist/', views.view_wishlist, name='wishlist'),
]
