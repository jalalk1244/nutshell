from django.shortcuts import render
from .models import Product, Category, Subcategory


# Create your views here.
def products(request):
    '''View for the products page'''
    category = None

    if request.GET:
        if 'category' in request.GET:
            category = request.GET['category']
            products = Product.objects.filter(category__slug=category)
            print(products)
    else:
        products = Product.objects.all()

    subcategories = Subcategory.objects.filter(parent_category__slug=category)
    context = {
        'products': products,
        'category': category,
        'subcategories': subcategories,
    }
    return render(request, 'products/products.html', context)
