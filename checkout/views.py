from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from bag.views import get_cart_info


def checkout(request):

    bag = request.session.get('bag', {})
    if not bag:
        messages.error(request, 'There is nothing in your bag at the moment')
        return redirect(reverse('products'))

    order_form = OrderForm()
    template = 'checkout/checkout.html'

    context = get_cart_info(request)
    context['order_form'] = order_form
    context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
    context['client_secret'] = 'test client secret'

    return render(request, template, context)
