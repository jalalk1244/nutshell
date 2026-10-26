from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseBadRequest
from django.views.decorators.http import require_POST
from products.models import Product

MAX_QUANTITY = 99

def money(value):
    return Decimal(value).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def delivery_for(total):
    return Decimal('3.00') if 0 < total < Decimal('25.00') else Decimal('0.00')

def get_cart_info(request):
    items, count, total = [], 0, Decimal('0.00')
    bag = request.session.get('bag', {})
    if not isinstance(bag, dict):
        raise ValueError('Invalid cart')
    for product_id, qty in bag.items():
        if not str(product_id).isascii() or not str(product_id).isdigit() or len(str(product_id)) > 19 or type(qty) is not int or not 1 <= qty <= MAX_QUANTITY:
            raise ValueError('Invalid cart quantity')
        product = get_object_or_404(Product, pk=product_id)
        if product.price <= 0:
            raise ValueError('Product price is invalid')
        total += money(product.price * qty)
        count += qty
        items.append({'product_id': str(product_id), 'quantity': qty, 'product': product})
    delivery = delivery_for(total)
    return dict(bag_products=items, product_count=count, total=total, delivery=delivery,
                grand_total=money(total + delivery), number_of_items=len(items))

def view_bag(request):
    try:
        context = get_cart_info(request)
    except ValueError:
        return HttpResponseBadRequest('Invalid cart. Remove invalid items and try again.')
    return render(request, 'bag/bag.html', context)

def save_bag(request, bag):
    request.session['bag'] = bag
    request.session.pop('checkout_key', None)
    request.session.pop('checkout_quote', None)

@require_POST
def add_to_bag(request):
    product_id = request.POST.get('product_id', '')
    if not product_id.isascii() or not product_id.isdigit() or len(product_id) > 19:
        return HttpResponseBadRequest('Invalid product')
    product = get_object_or_404(Product, pk=product_id)
    raw = request.POST.get('quantity', '')
    if not raw.isascii() or not raw.isdigit() or len(raw) > 2 or not 1 <= int(raw) <= MAX_QUANTITY:
        return HttpResponseBadRequest('Quantity must be between 1 and 99.')
    bag = request.session.get('bag', {}).copy()
    qty = bag.get(str(product.id), 0) + int(raw)
    if qty > MAX_QUANTITY:
        return HttpResponseBadRequest('Maximum quantity is 99.')
    bag[str(product.id)] = qty
    save_bag(request, bag)
    return redirect('product_detail', product_id=product.id)

@require_POST
def quantity(request, product_id):
    get_object_or_404(Product, pk=product_id)
    bag = request.session.get('bag', {}).copy()
    current = bag.get(str(product_id))
    action = request.POST.get('action')
    if type(current) is not int or action not in ('plus', 'minus'):
        return HttpResponseBadRequest('Invalid quantity change')
    qty = current + (1 if action == 'plus' else -1)
    if not 0 <= qty <= MAX_QUANTITY:
        return HttpResponseBadRequest('Maximum quantity is 99.')
    if qty == 0:
        bag.pop(str(product_id), None)
    else:
        bag[str(product_id)] = qty
    save_bag(request, bag)
    return redirect('bag')

@require_POST
def remove_from_bag(request, product_id):
    bag = request.session.get('bag', {}).copy()
    bag.pop(str(product_id), None)
    save_bag(request, bag)
    return redirect('bag')
