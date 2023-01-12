from django.contrib import admin
from .models import Category, Subcategory, Product


# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'sku',
        'name',
        'category',
        'sub_category',
        'price',
        'image',
    )

    prepopulated_fields = {"slug": ("name",)}

    ordering = ('id',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
    )
    prepopulated_fields = {"slug": ("name",)}


class SubcategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'parent_category',
    )
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
