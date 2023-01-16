from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.views import get_cart_info

import stripe


def checkout(request):
    ''' A view to handle checkout '''
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, 'There is nothing in your bag at the moment')
        return redirect(reverse('products'))

    context = get_cart_info(request)
    total = context['grand_total']
    stripe_total = round(total * 100)
    stripe.api_key = stripe_secret_key
    intent = stripe.PaymentIntent.create(
        amount=stripe_total,
        currency=settings.STRIPE_CURRENCY,
    )

    order_form = OrderForm()

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing. \
           Did you forget to set it in your enviroment? ')

    template = 'checkout/checkout.html'

    # Add to the already existing context
    context['order_form'] = order_form
    context['stripe_public_key'] = stripe_public_key
    context['client_secret'] = intent.client_secret

    return render(request, template, context)
