from django.shortcuts import render
from .models import Product, Category, Subcategory


# Create your views here.
def products(request):
    '''View for the products page'''
    category = None
    sort = None
    sort_by = 'sku'

    if request.GET:
        if 'sort' in request.GET:
            sort_key = request.GET['sort']
            if sort_key == 'l2h':
                sort_by = 'price'
            else:
                sort_by = '-price'

        if 'category' in request.GET:
            category = request.GET['category']
            products = Product.objects.filter(category__slug=category).order_by(sort_by)
        else:
            products = Product.objects.all().order_by(sort_by)

    subcategories = Subcategory.objects.filter(parent_category__slug=category)
    context = {
        'products': products,
        'category': category,
        'subcategories': subcategories,
    }
    return render(request, 'products/products.html', context)
