from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Subcategory



# Create your views here.
def products(request):
    '''View for rendering the products'''
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

        if 'q' in request.GET:
            q = request.GET['q']
            products = Product.objects.filter(
                Q(name__icontains=q) | Q(description__icontains=q))

    context = {
        'products': products,
        'category': category,
        'subcategories': subcategories,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    '''View the product details'''
    product = get_object_or_404(Product, pk=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]

    context = {
        'product': product,
        'related_products': related_products,
    }

    return render(request, 'products/product_detail.html', context)
