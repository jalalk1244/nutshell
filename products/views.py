from django.shortcuts import render
from .models import Product, Category, Subcategory


# Create your views here.
def products(request):
    '''View for the products page'''
    products = Product.objects.all()
    category = None
    sort = None
    sort_by = 'sku'
    subcategories = []

    if request.GET:
        if 'sort' in request.GET:
            sort_key = request.GET['sort']
            if sort_key == 'l2h':
                sort_by = 'price'
            else:
                sort_by = '-price'
        products = Product.objects.all().order_by(sort_by)

        if 'category' in request.GET:
            category = request.GET['category']
            products = Product.objects.filter(
                category__slug=category).order_by(sort_by)
            subcategories = Subcategory.objects.filter(
                parent_category__slug=category)
            if 'subcategory' in request.GET:
                subcategory = request.GET['subcategory']
                products = Product.objects.filter(
                    sub_category__slug=subcategory).order_by(sort_by)

    context = {
        'products': products,
        'category': category,
        'subcategories': subcategories,
    }
    return render(request, 'products/products.html', context)
