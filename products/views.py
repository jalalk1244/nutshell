from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.db.models import Q
from .models import Product, Category, Subcategory, ProductRating
from .forms import ReviewForm


# Create your views here.
def products(request):
    '''View for rendering the products'''
    products = Product.objects.all()
    category = None
    subcategory = None
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
            if 'category' not in request.GET:
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
        'subcategory': subcategory,
        'subcategories': subcategories,
    }
    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    '''View the product details'''
    product = get_object_or_404(Product, pk=product_id)
    related_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:4]
    product_ratings = ProductRating.objects.all()

    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        product_rating_form = ReviewForm(request.POST)
        if product_rating_form.is_valid():
            product_rating_form.instance.user = request.user
            product_rating_form.instance.product = product
            product_rating_form.save()
            return redirect(reverse('product_detail', args=[product_id]))
        else:
            pass  # add messages here
    else:
        product_rating_form = ReviewForm()

    context = {
        'product': product,
        'related_products': related_products,
        'product_rating_form': product_rating_form,
        'product_ratings': product_ratings,
        'range': range(5),
    }

    return render(request, 'products/product_detail.html', context)


def view_wishlist(request):
    '''A view to add products to the wishlist'''

    return render(request, 'products/wishlist.html')