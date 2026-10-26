from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from nutshell.testing import make_product
from .views import money

class CartTests(TestCase):
    def setUp(self):
        self.product = make_product()

    def add(self, quantity=1, **kwargs):
        return self.client.post(reverse('add_to_bag'), {'product_id': self.product.pk, 'quantity': quantity, **kwargs})

    def test_database_prices_and_delivery_totals(self):
        self.add(3, price='0.01', total='0.03')
        context = self.client.get(reverse('bag')).context
        self.assertEqual(context['total'], Decimal('14.97'))
        self.assertEqual(context['delivery'], Decimal('3.00'))
        self.assertEqual(context['grand_total'], Decimal('17.97'))
        self.add(3)
        context = self.client.get(reverse('bag')).context
        self.assertEqual(context['grand_total'], Decimal('29.94'))
        self.assertEqual(context['delivery'], Decimal('0.00'))
        self.assertEqual(money('1.005'), Decimal('1.01'))

    def test_shipping_boundary_and_empty_cart(self):
        self.product.price = Decimal('25.00')
        self.product.save()
        self.add()
        self.assertEqual(self.client.get(reverse('bag')).context['delivery'], Decimal('0.00'))
        self.client.post(reverse('remove_from_bag', args=[self.product.pk]))
        self.assertEqual(self.client.get(reverse('bag')).context['grand_total'], Decimal('0.00'))

    def test_invalid_quantities(self):
        for value in ('abc', '', 0, -1, 100, '1.5', '1e3', '²', '9' * 5000):
            with self.subTest(value=value):
                self.assertEqual(self.add(value).status_code, 400)
                self.assertFalse(self.client.session.get('bag'))
        self.add(99)
        self.assertEqual(self.add(1).status_code, 400)
        self.assertEqual(self.client.session['bag'][str(self.product.pk)], 99)

    def test_quantity_changes_and_removal(self):
        self.add()
        url = reverse('quantity', args=[self.product.pk])
        self.client.post(url, {'action': 'plus'})
        self.assertEqual(self.client.session['bag'][str(self.product.pk)], 2)
        self.client.post(url, {'action': 'minus'})
        self.client.post(url, {'action': 'minus'})
        self.assertEqual(self.client.session['bag'], {})
        self.assertEqual(self.client.post(url, {'action': 'minus'}).status_code, 400)
        self.add()
        remove = reverse('remove_from_bag', args=[self.product.pk])
        self.client.post(remove)
        self.client.post(remove)
        self.assertEqual(self.client.session['bag'], {})

    def test_mutations_post_only(self):
        self.add()
        for name, args in [('add_to_bag', []), ('quantity', [self.product.pk]), ('remove_from_bag', [self.product.pk])]:
            self.assertEqual(self.client.get(reverse(name, args=args)).status_code, 405)
        self.assertEqual(self.client.session['bag'][str(self.product.pk)], 1)

    def test_invalid_product(self):
        self.assertEqual(self.client.post(reverse('add_to_bag'), {'product_id': 'no', 'quantity': 1}).status_code, 400)
        self.assertEqual(self.client.post(reverse('add_to_bag'), {'product_id': 999999, 'quantity': 1}).status_code, 404)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(reverse('add_to_bag'), {'product_id': self.product.pk, 'quantity': 1}).status_code, 403)
