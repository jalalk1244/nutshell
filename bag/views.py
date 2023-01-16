from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib import messages
from products.models import Product

# Create your views here.


def view_bag(request):
    '''A view to render bag items'''
    bag_products = []
    total = 0
    product_count = 0
    bag = request.session.get('bag', {})

    for product_id, product_data in bag.items():
        product = get_object_or_404(Product, pk=product_id)
        total += product_data * product.price
        product_count += product_data
        bag_products.append({
            'product_id': product_id,
            'quantity': product_data,
            'product': product,
        })
    
    if total < 25:
        delivery = 3
    else:
        delivery = 0
    
    grand_total = total + delivery

    context = {
        'bag_products': bag_products,
        'total': total,
        'product_count': product_count,
        'delivery': delivery,
        'grand_total': grand_total,
        'number_of_items': len(bag_products),
    }

    return render(request, 'bag/bag.html', context)


def add_to_bag(request):
    '''A view to add items to the bag'''

    if request.method == 'POST':
        bag = request.session.get('bag', {})
        product_id = request.POST['product_id']
        quantity = int(request.POST['quantity'])
        product = get_object_or_404(Product, pk=product_id)

        if product_id in bag.keys():
            bag[product_id] += quantity
            messages.success(request, f'Updated {product.name} quantity to {bag[product_id]}')
        else:
            bag[product_id] = quantity
            messages.success(request, f'Added {product.name} the cart')

    request.session['bag'] = bag
    return redirect(reverse('product_detail', args=[product.id]))
