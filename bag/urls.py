from django.urls import path
from . import views


urlpatterns = [
    path('', views.view_bag, name='bag'),
    path('add/', views.add_to_bag, name='add_to_bag'),
    path('remove/<int:product_id>/',
         views.remove_from_bag, name='remove_from_bag'),
    path('quantity/<int:product_id>/', views.quantity, name='quantity'),
]
