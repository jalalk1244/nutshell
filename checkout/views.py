import json
import uuid
from decimal import Decimal
import stripe
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST, require_http_methods
from bag.views import get_cart_info
from profiles.forms import UserProfileForm
from .forms import OrderForm
from .models import Order, OrderLineItem
from .access import authorized_order

def checkout_key(request):
    key = request.session.get('checkout_key')
    if not key:
        key = str(uuid.uuid4())
        request.session['checkout_key'] = key
    return key

def cart_quote(cart):
    return json.dumps([(item['product_id'], item['quantity'], str(item['product'].price))
                       for item in cart['bag_products']], sort_keys=True)

@require_POST
def cache_checkout_data(request):
    # Persist and authorize the intended order BEFORE allowing Stripe confirmation.
    key = request.session.get('checkout_key')
    if not key or request.POST.get('checkout_key') != key:
        return JsonResponse({'error': 'Checkout expired. Reload checkout.'}, status=409)
    form = OrderForm(request.POST)
    if not form.is_valid():
        return JsonResponse({'error': 'Please correct your delivery details.', 'fields': form.errors}, status=400)
    try:
        cart = get_cart_info(request)
    except ValueError:
        return JsonResponse({'error': 'Invalid cart.'}, status=400)
    if not cart['bag_products']:
        return JsonResponse({'error': 'Your bag is empty.'}, status=400)
    if request.session.get('checkout_quote') != cart_quote(cart):
        return JsonResponse({'error': 'Prices changed. Reload checkout to review the new total.'}, status=409)
    if cart['grand_total'] > Decimal('999999.99'):
        return JsonResponse({'error': 'Order exceeds the supported payment limit.'}, status=400)
    bag = json.dumps(request.session['bag'], sort_keys=True)
    with transaction.atomic():
        order, created = Order.objects.get_or_create(checkout_key=key, defaults={
            **form.cleaned_data, 'payment_status': 'pending', 'original_bag': bag,
            'currency': settings.STRIPE_CURRENCY,
            'user_profile': request.user.userprofile if request.user.is_authenticated else None,
            'order_total': cart['total'], 'delivery_cost': cart['delivery'],
            'grand_total': cart['grand_total'],
        })
        if created:
            OrderLineItem.objects.bulk_create([
                OrderLineItem(order=order, product=item['product'], quantity=item['quantity'],
                              unit_price=item['product'].price,
                              lineitem_total=item['product'].price * item['quantity'])
                for item in cart['bag_products']])
    if order.user_profile_id and (not request.user.is_authenticated or order.user_profile.user_id != request.user.id):
        return JsonResponse({'error': 'Checkout identity changed. Adjust bag and retry.'}, status=409)
    if not order.user_profile_id:
        keys = request.session.get('guest_orders', [])
        if str(order.checkout_key) not in keys:
            request.session['guest_orders'] = keys + [str(order.checkout_key)]
    if order.payment_status == 'paid':
        return JsonResponse({'redirect': reverse('checkout_success', args=[order.order_number])})
    if order.original_bag != bag or any(str(getattr(order, f)) != str(value) for f, value in form.cleaned_data.items()):
        return JsonResponse({'error': 'Checkout details changed. Adjust your bag to start a new checkout.'}, status=409)
    if request.user.is_authenticated and 'save-info' in request.POST:
        data = {'default_' + f: value for f, value in form.cleaned_data.items() if f not in ('full_name', 'email')}
        profile_form = UserProfileForm(data, instance=request.user.userprofile)
        if profile_form.is_valid():
            profile_form.save()
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        # Stripe idempotency also recovers a timeout between intent creation and DB save.
        if order.stripe_pid:
            intent = stripe.PaymentIntent.retrieve(order.stripe_pid)
        else:
            intent = stripe.PaymentIntent.create(
                amount=int(order.grand_total * 100), currency=order.currency,
                metadata={'order_key': str(order.checkout_key)},
                idempotency_key='nutshell-' + str(order.checkout_key),
            )
        Order.objects.filter(pk=order.pk, stripe_pid='').update(stripe_pid=intent.id)
        order.refresh_from_db()
        if order.stripe_pid != intent.id:
            return JsonResponse({'error': 'Payment binding failed.'}, status=409)
    except stripe.StripeError:
        return JsonResponse({'error': 'Payment service unavailable. Retry safely.'}, status=503)
    return JsonResponse({'client_secret': intent.client_secret,
                         'redirect': reverse('checkout_success', args=[order.order_number])})

@require_http_methods(['GET', 'POST'])
def checkout(request):
    if request.method == 'POST':
        if request.POST.get('finish_order'):
            order = authorized_order(request, request.POST['finish_order'])
            if order.payment_status != 'paid':
                return HttpResponseBadRequest('Payment confirmation is still pending.')
            if str(order.checkout_key) == request.session.get('checkout_key'):
                if json.dumps(request.session.get('bag', {}), sort_keys=True) == order.original_bag:
                    request.session['bag'] = {}
                request.session.pop('checkout_key', None)
            return redirect('checkout_success', order_number=order.order_number)
        order = Order.objects.filter(checkout_key=request.session.get('checkout_key')).first()
        if not order:
            return HttpResponseBadRequest('Start checkout before confirming.')
        authorized_order(request, order.order_number)
        return redirect('checkout_success', order_number=order.order_number)
    try:
        context = get_cart_info(request)
    except ValueError:
        return HttpResponseBadRequest('Invalid cart.')
    if not context['bag_products']:
        return redirect('bag')
    quote = cart_quote(context)
    if request.session.get('checkout_quote') != quote:
        request.session.pop('checkout_key', None)
    request.session['checkout_quote'] = quote
    initial = {}
    if request.user.is_authenticated:
        profile = request.user.userprofile
        initial = {f: getattr(profile, 'default_' + f) for f in OrderForm.Meta.fields if f not in ('full_name', 'email')}
        initial.update(full_name=request.user.get_full_name(), email=request.user.email)
    context.update(order_form=OrderForm(initial=initial), checkout_key=checkout_key(request),
                   stripe_public_key=settings.STRIPE_PUBLIC_KEY)
    return render(request, 'checkout/checkout.html', context)

@require_http_methods(['GET'])
def checkout_success(request, order_number):
    order = authorized_order(request, order_number)
    # This GET only displays status. It cannot transfer ownership or confirm payment.
    return render(request, 'checkout/checkout_success.html', {'order': order})
