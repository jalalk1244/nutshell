from django.db import transaction
from django.http import HttpResponse
from .models import Order, PaymentEvent

class StripeWH_Handler:
    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        return HttpResponse(status=200)

    def process(self, event, succeeded):
        intent = event['data']['object']
        key = intent.get('metadata', {}).get('order_key')
        if not key:
            return HttpResponse(status=400)
        with transaction.atomic():
            # Lock by intent, never by user-controlled email or shipping details.
            order = Order.objects.select_for_update().filter(stripe_pid=intent['id']).first()
            if order is None:
                # Stripe can deliver before the intent ID is persisted. Retry later.
                return HttpResponse(status=503)
            if str(order.checkout_key) != key or intent.get('currency') != order.currency:
                return HttpResponse(status=400)
            amount = int(order.grand_total * 100)
            if intent.get('amount') != amount or (succeeded and (
                    intent.get('amount_received') != amount or intent.get('status') != 'succeeded')):
                return HttpResponse(status=400)
            _, created = PaymentEvent.objects.get_or_create(event_id=event['id'], defaults={
                'order': order, 'event_type': event['type']})
            if not created:
                return HttpResponse(status=200)
            if succeeded:
                order.payment_status = 'paid'
            elif order.payment_status != 'paid':
                order.payment_status = 'failed'
            order.save(update_fields=['payment_status'])
        return HttpResponse(status=200)

    def handle_payment_intent_succeeded(self, event):
        return self.process(event, True)

    def handle_payment_intent_payment_failed(self, event):
        return self.process(event, False)
