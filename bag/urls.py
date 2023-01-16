from django.urls import path
from . import views


urlpatterns = [
    path('', views.view_bag, name='bag'),
    path('add/', views.add_to_bag, name='add_to_bag'),
]
