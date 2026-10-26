import copy
import json
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
from unittest.mock import patch
from decimal import Decimal
from django.test import TestCase, TransactionTestCase, Client, skipUnlessDBFeature
from django.db import transaction, IntegrityError, connections
from django.contrib.auth.models import User
from django.urls import reverse
import stripe
import hashlib
import hmac
import time
from nutshell.testing import make_product, address
from .models import Order, OrderLineItem, PaymentEvent
from .webhook_handler import StripeWH_Handler

def event_for(order, event_id='evt_test', succeeded=True):
    return dict(id=event_id, type='payment_intent.succeeded' if succeeded else 'payment_intent.payment_failed',
                data={'object': dict(id=order.stripe_pid, amount=int(Decimal(order.grand_total) * 100),
                    amount_received=int(Decimal(order.grand_total) * 100) if succeeded else 0,
                    status='succeeded' if succeeded else 'requires_payment_method',
                    currency=order.currency, metadata={'order_key': str(order.checkout_key)})})

class CheckoutTests(TestCase):
    def setUp(self):
        self.product = make_product()
        self.user = User.objects.create_user('customer', password='password')
        self.other = User.objects.create_user('other', password='password')

    def start(self, client=None):
        client = client or self.client
        client.post(reverse('add_to_bag'), {'product_id': self.product.pk, 'quantity': 2})
        response = client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
        return address(checkout_key=client.session['checkout_key'])

    def prepare(self, client=None):
        data = self.start(client)
        client = client or self.client
        with patch('checkout.views.stripe.PaymentIntent.create', return_value=SimpleNamespace(id='pi_test', client_secret='pi_test_secret_test')) as create:
            response = client.post(reverse('cache_checkout_data'), data)
        self.assertEqual(response.status_code, 200, response.content)
        return Order.objects.get(), data, create

    def test_prepare_snapshots_prices_totals_and_trusted_owner(self):
        self.client.force_login(self.user)
        order, data, create = self.prepare()
        self.assertEqual(order.user_profile, self.user.userprofile)
        self.assertEqual(order.payment_status, 'pending')
        self.assertEqual(order.grand_total, Decimal('12.98'))
        self.assertEqual(order.lineitems.get().unit_price, Decimal('4.99'))
        self.assertEqual(create.call_args.kwargs['amount'], 1298)
        self.assertEqual(create.call_args.kwargs['metadata'], {'order_key': str(order.checkout_key)})
        self.assertIn(str(order.checkout_key), create.call_args.kwargs['idempotency_key'])

    def test_repeated_checkout_creates_one_order_and_uses_same_idempotency_key(self):
        order, data, _ = self.prepare()
        with patch('checkout.views.stripe.PaymentIntent.retrieve', return_value=SimpleNamespace(id='pi_test', client_secret='secret')) as retrieve:
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderLineItem.objects.count(), 1)
        retrieve.assert_called_once_with('pi_test')

    def test_server_does_not_trust_client_prices_or_foreign_intent(self):
        data = self.start()
        data.update(amount='1', price='0.01', client_secret='pi_other_secret_stolen', user_profile=self.other.userprofile.pk)
        with patch('checkout.views.stripe.PaymentIntent.create', return_value=SimpleNamespace(id='pi_bound', client_secret='secret')) as create:
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 200)
        order = Order.objects.get()
        self.assertIsNone(order.user_profile)
        self.assertEqual(order.stripe_pid, 'pi_bound')
        self.assertEqual(create.call_args.kwargs['amount'], 1298)

    def test_invalid_form_does_not_create_order_or_call_stripe(self):
        data = self.start()
        data['email'] = 'invalid'
        with patch('checkout.views.stripe.PaymentIntent.create') as create:
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 400)
        create.assert_not_called()
        self.assertEqual(Order.objects.count(), 0)

    def test_invalid_profile_not_saved_during_checkout(self):
        self.client.force_login(self.user)
        data = self.start()
        data['phone_number'] = 'x' * 21
        data['save-info'] = 'on'
        self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 400)
        self.user.userprofile.refresh_from_db()
        self.assertIsNone(self.user.userprofile.default_phone_number)

    def test_valid_checkout_profile_saved(self):
        self.client.force_login(self.user)
        data = self.start()
        data['save-info'] = 'on'
        with patch('checkout.views.stripe.PaymentIntent.create', return_value=SimpleNamespace(id='pi_test', client_secret='secret')):
            self.client.post(reverse('cache_checkout_data'), data)
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.default_phone_number, data['phone_number'])

    def test_order_and_items_are_atomic(self):
        data = self.start()
        with patch('checkout.views.OrderLineItem.objects.bulk_create', side_effect=RuntimeError('test rollback')):
            with self.assertRaises(RuntimeError):
                self.client.post(reverse('cache_checkout_data'), data)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderLineItem.objects.count(), 0)

    def test_stripe_failure_is_retryable_without_duplicate_order(self):
        data = self.start()
        with patch('checkout.views.stripe.PaymentIntent.create', side_effect=stripe.APIConnectionError('test')):
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 503)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get().payment_status, 'pending')
        with patch('checkout.views.stripe.PaymentIntent.create', return_value=SimpleNamespace(id='pi_test', client_secret='secret')):
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 200)
        self.assertEqual(Order.objects.count(), 1)

    def test_corrected_details_reuse_order_and_existing_payment(self):
        order, data, _ = self.prepare()
        data['email'] = 'changed@example.invalid'
        data['postcode'] = '12345'
        with patch('checkout.views.stripe.PaymentIntent.create') as create, patch(
                'checkout.views.stripe.PaymentIntent.retrieve',
                return_value=SimpleNamespace(id='pi_test', client_secret='secret')) as retrieve:
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 200)
        create.assert_not_called()
        retrieve.assert_called_once_with('pi_test')
        order.refresh_from_db()
        self.assertEqual(order.email, 'changed@example.invalid')
        self.assertEqual(order.postcode, '12345')
        self.assertEqual(order.grand_total, Decimal('12.98'))
        self.assertEqual(order.stripe_pid, 'pi_test')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderLineItem.objects.count(), 1)

    def test_paid_order_details_cannot_be_changed_by_retry(self):
        order, data, _ = self.prepare()
        Order.objects.filter(pk=order.pk).update(payment_status='paid')
        data['email'] = 'changed@example.invalid'
        with patch('checkout.views.stripe.PaymentIntent.create') as create, patch(
                'checkout.views.stripe.PaymentIntent.retrieve') as retrieve:
            response = self.client.post(reverse('cache_checkout_data'), data)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('client_secret', response.json())
        create.assert_not_called()
        retrieve.assert_not_called()
        order.refresh_from_db()
        self.assertEqual(order.email, 'test@example.invalid')

    def test_invalid_correction_preserves_existing_order(self):
        order, data, _ = self.prepare()
        data['email'] = 'invalid'
        data['postcode'] = '12345'
        with patch('checkout.views.stripe.PaymentIntent.retrieve') as retrieve:
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 400)
        retrieve.assert_not_called()
        order.refresh_from_db()
        self.assertEqual(order.email, 'test@example.invalid')
        self.assertEqual(order.postcode, '10000')
        self.assertEqual(Order.objects.count(), 1)

    def test_corrected_details_after_connection_failure_reuse_saved_order(self):
        data = self.start()
        with patch('checkout.views.stripe.PaymentIntent.create', side_effect=stripe.APIConnectionError('test')):
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 503)
        data['postcode'] = '12345'
        with patch('checkout.views.stripe.PaymentIntent.create', return_value=SimpleNamespace(id='pi_test', client_secret='secret')):
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 200)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderLineItem.objects.count(), 1)
        self.assertEqual(Order.objects.get().postcode, '12345')

    def test_expired_checkout_rejected(self):
        data = self.start()
        data['checkout_key'] = 'other'
        self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 409)
        self.assertFalse(Order.objects.exists())

    def test_own_order_access_and_other_user_denied(self):
        self.client.force_login(self.user)
        order, _, _ = self.prepare()
        urls = [reverse('checkout_success', args=[order.order_number]), reverse('order_history', args=[order.order_number])]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200)
        self.client.force_login(self.other)
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 404)
        self.client.logout()
        self.assertEqual(self.client.get(urls[0]).status_code, 404)
        self.assertEqual(self.client.get(urls[1]).status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.user_profile, self.user.userprofile)

    def test_guest_access_is_session_bound_and_never_claimed(self):
        order, _, _ = self.prepare()
        url = reverse('checkout_success', args=[order.order_number])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertEqual(Client().get(url).status_code, 404)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(url).status_code, 200)
        order.refresh_from_db()
        self.assertIsNone(order.user_profile)
        self.assertFalse(self.user.userprofile.orders.exists())

    def test_matching_email_is_not_authorization(self):
        order, _, _ = self.prepare()
        self.other.email = order.email
        self.other.save()
        attacker = Client()
        attacker.force_login(self.other)
        self.assertEqual(attacker.get(reverse('checkout_success', args=[order.order_number])).status_code, 404)

    def test_confirmation_refresh_has_no_business_effects(self):
        order, _, _ = self.prepare()
        url = reverse('checkout_success', args=[order.order_number])
        for _ in range(3):
            self.assertEqual(self.client.get(url).status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'pending')
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(PaymentEvent.objects.count(), 0)
        self.assertTrue(self.client.session['bag'])

    def test_browser_post_cannot_mark_paid(self):
        order, _, _ = self.prepare()
        self.assertEqual(self.client.post(reverse('checkout'), {'client_secret': 'anything'}).status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'pending')

    def test_payment_snapshot_survives_catalogue_price_change(self):
        order, _, _ = self.prepare()
        self.product.price = Decimal('99.00')
        self.product.save()
        item = order.lineitems.get()
        item.save()
        self.assertEqual(item.lineitem_total, Decimal('9.98'))
        self.assertEqual(order.grand_total, Decimal('12.98'))

    def test_price_change_requires_review_before_payment(self):
        data = self.start()
        self.product.price = Decimal('6.00')
        self.product.save()
        with patch('checkout.views.stripe.PaymentIntent.create') as create:
            self.assertEqual(self.client.post(reverse('cache_checkout_data'), data).status_code, 409)
        create.assert_not_called()
        self.assertFalse(Order.objects.exists())
        self.client.get(reverse('checkout'))
        self.assertNotEqual(self.client.session['checkout_key'], data['checkout_key'])

    def test_paid_cart_clear_requires_post_and_preserves_new_cart(self):
        order, _, _ = self.prepare()
        Order.objects.filter(pk=order.pk).update(payment_status='paid')
        self.client.get(reverse('checkout_success', args=[order.order_number]))
        self.assertTrue(self.client.session['bag'])
        self.client.post(reverse('checkout'), {'finish_order': order.order_number})
        self.assertEqual(self.client.session['bag'], {})
        self.client.post(reverse('add_to_bag'), {'product_id': self.product.pk, 'quantity': 3})
        self.client.post(reverse('checkout'), {'finish_order': order.order_number})
        self.assertEqual(self.client.session['bag'][str(self.product.pk)], 3)

    def test_pending_cart_cannot_be_cleared_as_paid(self):
        order, _, _ = self.prepare()
        self.assertEqual(self.client.post(reverse('checkout'), {'finish_order': order.order_number}).status_code, 400)
        self.assertTrue(self.client.session['bag'])

    def test_automatic_cart_completion_is_post_only_and_csrf_protected(self):
        self.prepare()
        self.assertEqual(self.client.get(reverse('complete_cart')).status_code, 405)
        self.assertEqual(Client(enforce_csrf_checks=True).post(reverse('complete_cart')).status_code, 403)
        self.assertTrue(self.client.session['bag'])

    def test_automatic_completion_clears_paid_bag_idempotently(self):
        order, _, _ = self.prepare()
        Order.objects.filter(pk=order.pk).update(payment_status='paid')
        # Rendering alone remains read-only; the browser follows up with a POST.
        self.client.get(reverse('checkout_success', args=[order.order_number]))
        self.assertTrue(self.client.session['bag'])
        response = self.client.post(reverse('complete_cart'))
        self.assertEqual(response.json(), {'status': 'paid', 'cleared': True})
        self.assertEqual(self.client.session['bag'], {})
        self.assertNotIn('checkout_key', self.client.session)
        self.assertNotIn('checkout_quote', self.client.session)
        self.assertEqual(self.client.post(reverse('complete_cart')).json(), {'status': 'none', 'cleared': False})
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderLineItem.objects.count(), 1)

    def test_pending_and_failed_payments_do_not_clear_bag(self):
        order, _, _ = self.prepare()
        for status in ('pending', 'failed'):
            Order.objects.filter(pk=order.pk).update(payment_status=status)
            self.assertEqual(self.client.post(reverse('complete_cart')).json(), {'status': status, 'cleared': False})
            self.assertTrue(self.client.session['bag'])
            self.assertIn('checkout_key', self.client.session)

    def test_delayed_success_webhook_then_completion_clears_bag(self):
        order, _, _ = self.prepare()
        self.assertFalse(self.client.post(reverse('complete_cart')).json()['cleared'])
        response = StripeWH_Handler(None).handle_payment_intent_succeeded(event_for(order))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.post(reverse('complete_cart')).json()['cleared'])
        self.assertEqual(PaymentEvent.objects.count(), 1)

    def test_automatic_completion_preserves_new_identical_bag(self):
        order, _, _ = self.prepare()
        Order.objects.filter(pk=order.pk).update(payment_status='paid')
        self.client.post(reverse('remove_from_bag', args=[self.product.pk]))
        self.client.post(reverse('add_to_bag'), {'product_id': self.product.pk, 'quantity': 2})
        self.assertFalse(self.client.post(reverse('complete_cart')).json()['cleared'])
        self.assertEqual(self.client.session['bag'][str(self.product.pk)], 2)

    def test_automatic_completion_cannot_use_another_users_order(self):
        self.client.force_login(self.user)
        order, _, _ = self.prepare()
        Order.objects.filter(pk=order.pk).update(payment_status='paid')
        attacker = Client()
        attacker.force_login(self.other)
        session = attacker.session
        session['checkout_key'] = str(order.checkout_key)
        session['bag'] = {str(self.product.pk): 3}
        session.save()
        self.assertEqual(attacker.post(reverse('complete_cart')).status_code, 404)
        self.assertEqual(attacker.session['bag'][str(self.product.pk)], 3)
        self.assertTrue(self.client.session['bag'])

    def test_completion_without_saved_order_leaves_cart_alone(self):
        self.start()
        self.assertEqual(self.client.post(reverse('complete_cart')).json(), {'status': 'none', 'cleared': False})
        self.assertTrue(self.client.session['bag'])

class WebhookTests(TestCase):
    def setUp(self):
        self.order = Order.objects.create(**address(), stripe_pid='pi_test', payment_status='pending', grand_total='12.98')
        self.handler = StripeWH_Handler(None)

    def deliver(self, event):
        with patch('checkout.webhooks.stripe.Webhook.construct_event', return_value=event):
            return self.client.post(reverse('webhook'), data='{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='mock')

    def test_valid_signed_success_updates_only_correct_order(self):
        other = Order.objects.create(**address(), stripe_pid='pi_other', payment_status='pending')
        self.assertEqual(self.deliver(event_for(self.order)).status_code, 200)
        self.order.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertEqual(other.payment_status, 'pending')

    def test_real_valid_signature_accepted(self):
        payload = json.dumps(event_for(self.order))
        timestamp = int(time.time())
        signature = hmac.new(b'whsec_test_mock', f'{timestamp}.{payload}'.encode(), hashlib.sha256).hexdigest()
        response = self.client.post(reverse('webhook'), data=payload, content_type='application/json',
                                    HTTP_STRIPE_SIGNATURE=f't={timestamp},v1={signature}')
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')

    def test_duplicate_delivery_is_idempotent(self):
        event = event_for(self.order)
        self.deliver(event)
        self.deliver(event)
        self.assertEqual(PaymentEvent.objects.count(), 1)
        self.assertEqual(Order.objects.count(), 1)

    def test_invalid_or_missing_signature_rejected(self):
        self.assertEqual(self.client.post(reverse('webhook'), data='{}', content_type='application/json').status_code, 400)
        # Exercise Stripe's real verifier; no network call occurs.
        self.assertEqual(self.client.post(reverse('webhook'), data='{}', content_type='application/json', HTTP_STRIPE_SIGNATURE='t=1,v1=bad').status_code, 400)
        self.assertEqual(PaymentEvent.objects.count(), 0)

    def test_failed_payment_does_not_mark_paid(self):
        self.assertEqual(self.deliver(event_for(self.order, succeeded=False)).status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'failed')

    def test_mismatched_payment_never_marks_paid(self):
        original = event_for(self.order)
        for field, value in [('amount', 1), ('amount_received', 1), ('currency', 'eur'), ('status', 'processing'), ('metadata', {'order_key': 'wrong'})]:
            event = copy.deepcopy(original)
            event['data']['object'][field] = value
            self.assertEqual(self.deliver(event).status_code, 400)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'pending')
        self.assertFalse(PaymentEvent.objects.exists())

    def test_failure_after_success_does_not_regress_paid(self):
        self.deliver(event_for(self.order, 'evt_success'))
        self.deliver(event_for(self.order, 'evt_failed', False))
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')

    def test_success_after_failure_marks_paid(self):
        self.deliver(event_for(self.order, 'evt_failed', False))
        self.deliver(event_for(self.order, 'evt_success'))
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')

    def test_unbound_intent_is_retryable_and_does_not_create_order(self):
        event = event_for(self.order)
        event['data']['object']['id'] = 'pi_not_yet_bound'
        self.assertEqual(self.deliver(event).status_code, 503)
        self.assertEqual(Order.objects.count(), 1)

    def test_unknown_event_acknowledged(self):
        self.assertEqual(self.deliver({'id': 'evt_unknown', 'type': 'charge.refunded'}).status_code, 200)

    def test_database_constraints(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.create(**address(), stripe_pid='pi_test')
        with self.assertRaises(IntegrityError), transaction.atomic():
            Order.objects.create(**address(), checkout_key=self.order.checkout_key)
        product = make_product()
        with self.assertRaises(IntegrityError), transaction.atomic():
            OrderLineItem.objects.create(order=self.order, product=product, quantity=-1)

class PostgreSQLConcurrencyTests(TransactionTestCase):
    @skipUnlessDBFeature('has_select_for_update')
    def test_simultaneous_duplicate_events(self):
        order = Order.objects.create(**address(), stripe_pid='pi_concurrent', payment_status='pending', grand_total='12.98')
        event = event_for(order)
        def worker():
            try:
                return StripeWH_Handler(None).handle_payment_intent_succeeded(event).status_code
            finally:
                connections.close_all()
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: worker(), range(2)))
        self.assertEqual(results, [200, 200])
        self.assertEqual(PaymentEvent.objects.count(), 1)
        order.refresh_from_db()
        self.assertEqual(order.payment_status, 'paid')

    @skipUnlessDBFeature('has_select_for_update')
    def test_simultaneous_checkout_posts_create_one_snapshot(self):
        from django.test import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        from .views import cache_checkout_data, cart_quote
        from bag.views import get_cart_info
        import uuid
        product = make_product()
        key = str(uuid.uuid4())
        state = {'bag': {str(product.pk): 2}, 'checkout_key': key}
        quote_request = RequestFactory().get('/')
        quote_request.session = state
        state['checkout_quote'] = cart_quote(get_cart_info(quote_request))
        def worker():
            try:
                request = RequestFactory().post('/', address(checkout_key=key))
                request.user = AnonymousUser()
                request.session = copy.deepcopy(state)
                return cache_checkout_data(request).status_code
            finally:
                connections.close_all()
        with patch('checkout.views.stripe.PaymentIntent.create', return_value=SimpleNamespace(id='pi_concurrent_checkout', client_secret='secret')), patch('checkout.views.stripe.PaymentIntent.retrieve', return_value=SimpleNamespace(id='pi_concurrent_checkout', client_secret='secret')):
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _: worker(), range(2)))
        self.assertEqual(results, [200, 200])
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderLineItem.objects.count(), 1)


class LegacyMigrationTests(TransactionTestCase):
    def test_existing_order_preserves_identity_totals_and_gets_distinct_key(self):
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        executor = MigrationExecutor(connection)
        latest = executor.loader.graph.leaf_nodes()
        old_target = [('checkout', '0002_order_user_profile')]
        executor.migrate(old_target)
        try:
            apps = executor.loader.project_state(old_target).apps
            OldOrder = apps.get_model('checkout', 'Order')
            OldLine = apps.get_model('checkout', 'OrderLineItem')
            OldProduct = apps.get_model('products', 'Product')
            product = OldProduct.objects.create(name='Walnuts', slug='legacy', price='99.00', description='Legacy')
            one = OldOrder.objects.create(**address(), order_number='LEGACY_ONE', stripe_pid='pi_legacy', order_total='9.98', delivery_cost='3.00', grand_total='12.98')
            two = OldOrder.objects.create(**address(), order_number='LEGACY_TWO')
            OldLine.objects.create(order=one, product=product, quantity=2, lineitem_total='9.98')
        finally:
            executor = MigrationExecutor(connection)
            executor.migrate(latest)
        order = Order.objects.get(pk=one.pk)
        self.assertEqual(order.order_number, 'LEGACY_ONE')
        self.assertEqual(order.grand_total, Decimal('12.98'))
        self.assertEqual(order.lineitems.get().unit_price, Decimal('4.99'))
        self.assertEqual(order.payment_status, 'legacy')
        self.assertNotEqual(order.checkout_key, Order.objects.get(pk=two.pk).checkout_key)
