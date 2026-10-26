from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Order

def authorized_order(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    if order.user_profile_id:
        allowed = request.user.is_authenticated and order.user_profile.user_id == request.user.id
    else:
        allowed = str(order.checkout_key) in request.session.get('guest_orders', [])
    if not allowed:
        raise Http404
    return order
