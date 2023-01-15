from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg
from .models import Product, Category, Subcategory, ProductRating, WishList
from .forms import ReviewForm, ProductForm


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
    product_review = ProductRating.objects.filter(product=product).order_by('-comment')
    product_ratings = ProductRating.objects.filter(product=product)
    avg = None

    if request.user.is_authenticated:
        is_wished_product = len(WishList.objects.filter(Q(user=request.user) & Q(wished_product=product)))
    else:
        is_wished_product = 0

    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        product_rating_form = ReviewForm(request.POST)
        if product_rating_form.is_valid():
            product_rating_form.instance.user = request.user
            product_rating_form.instance.product = product
            product_rating_form.save()
            messages.success(request, 'Product review added Successfuly')
            return redirect(reverse('product_detail', args=[product_id]))
        else:
            messages.error(request, 'Somthing went wrong, please try again!')
    else:
        product_rating_form = ReviewForm()

    average_rating = product_review.aggregate(Avg('rating'))['rating__avg']
    if avg is not None:
        avg = round(average_rating)
    else:
        avg = 0

    context = {
        'product': product,
        'related_products': related_products,
        'product_rating_form': product_rating_form,
        'product_ratings': product_ratings,
        'avg': avg,
        'star_range': range(avg),
        'is_wished_product': is_wished_product,
    }

    return render(request, 'products/product_detail.html', context)


@login_required
def view_wishlist(request):
    '''A view to view products of the wishlist'''
    wishlist_of_user = WishList.objects.filter(user=request.user)

    context = {
        'wishlist_of_user': wishlist_of_user,
    }

    return render(request, 'products/wishlist.html', context)


def add_to_wishlist(request, product_id):
    '''A view to add products to the wishlist'''

    product = get_object_or_404(Product, pk=product_id)
    if product:
        if request.user.is_authenticated:
            wished_item, created = WishList.objects.get_or_create(
                wished_product=product,
                user=request.user,)
            messages.success(request, 'Product added to your wishlist')
        else:
            messages.error(request, 'Login to add products to your wishlist')

    return redirect('product_detail', product_id=product.id)


@login_required
def remove_from_wishlist(request, product_id):
    '''A view to remove products from the wishlist'''

    product = get_object_or_404(Product, pk=product_id)
    if product:
        wished_item, created = WishList.objects.get_or_create(
            wished_product=product,
            user=request.user,)
        wished_item.delete()
        messages.success(request, 'Product removed from your wishlist')

    return redirect('product_detail', product_id=product.id)


@login_required
def add_new_product(request):
    '''A view to add new products to the store'''
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully added product')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to add product. Please ensure the form is valid.')
    else:
        form = ProductForm()

    context = {
        'form': form
    }

    return render(request, 'products/add_product.html', context)


@login_required
def edit_product(request, product_id):
    '''A view to edit products of the store'''
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Successfully edited product')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            messages.error(request, 'Failed to edit product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
    }

    return render(request, 'products/edit_product.html', context)


@login_required
def delete_product(request, product_id):
    '''A view to delete products of the store'''
    if not request.user.is_superuser:
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)
    product.delete()
    messages.success(request, 'Product successfuly deleted')

    return render(request, 'products')