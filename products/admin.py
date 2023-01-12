from django.contrib import admin
from .models import Category, Subcategory, Product

# Register your models here.
admin.site.register(Product)
admin.site.register(Subcategory)
admin.site.register(Category)
