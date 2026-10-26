from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from nutshell.testing import make_product
from .models import Product, ProductRating, WishList

class ProductTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser('owner', 'owner@example.invalid', 'password')
        self.user = User.objects.create_user('customer', password='password')
        self.product = make_product()
        self.data = dict(name='Updated walnuts', slug='walnuts', price='6.25', description='Updated', sku='123')

    def test_edit_updates_identity_and_relationships(self):
        rating = ProductRating.objects.create(product=self.product, user=self.user, title='Good', rating=4)
        WishList.objects.create(user=self.user, wished_product=self.product)
        self.client.force_login(self.owner)
        response = self.client.post(reverse('edit_product', args=[self.product.pk]), self.data)
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated walnuts')
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(rating.product_id, self.product.pk)
        self.assertTrue(WishList.objects.filter(wished_product=self.product).exists())

    def test_invalid_edit_keeps_database_unchanged(self):
        self.client.force_login(self.owner)
        self.data['price'] = '-1'
        response = self.client.post(reverse('edit_product', args=[self.product.pk]), self.data)
        self.assertEqual(response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(str(self.product.price), '4.99')
        self.assertEqual(self.product.name, 'Walnuts')
        self.assertEqual(Product.objects.count(), 1)

    def test_management_requires_owner(self):
        for user in (None, self.user):
            self.client.logout()
            if user:
                self.client.force_login(user)
            for name, args in [('add_new_product', []), ('edit_product', [self.product.pk]), ('delete_product', [self.product.pk])]:
                with self.subTest(user=user, name=name):
                    response = self.client.post(reverse(name, args=args), self.data)
                    self.assertIn(response.status_code, (302, 403))
            self.assertEqual(Product.objects.count(), 1)
            self.product.refresh_from_db()
            self.assertEqual(self.product.name, 'Walnuts')

    def test_owner_create_and_delete(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('add_new_product'), dict(self.data, slug='another'))
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(self.client.get(reverse('delete_product', args=[self.product.pk])).status_code, 405)
        self.client.post(reverse('delete_product', args=[self.product.pk]))
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_average_and_half_up_stars(self):
        for value in (4, 5):
            ProductRating.objects.create(product=self.product, user=self.user, title='Good', rating=value)
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertEqual(response.context['average_rating'], 4.5)
        self.assertEqual(response.context['avg'], 5)
        self.assertEqual(len(response.context['star_range']), 5)

    def test_no_reviews(self):
        response = self.client.get(reverse('product_detail', args=[self.product.pk]))
        self.assertEqual(response.context['avg'], 0)
        self.assertEqual(response.context['average_rating'], 0)

    def test_catalogue_search_sort_and_category_work_together(self):
        from .models import Category, Subcategory
        nuts = Category.objects.create(name='Nuts', slug='nuts')
        seeds = Category.objects.create(name='Seeds', slug='seeds')
        raw = Subcategory.objects.create(name='Raw', slug='raw', parent_category=nuts)
        self.product.category = nuts
        self.product.sub_category = raw
        self.product.save()
        expensive = make_product(name='Premium walnuts', slug='premium', price='8.00', category=nuts, sub_category=raw)
        make_product(name='Walnut seeds', slug='seed-product', price='1.00', category=seeds)
        response = self.client.get(reverse('products'), {'category': 'nuts', 'q': 'walnut', 'sort': 'h2l'})
        self.assertEqual(list(response.context['products']), [expensive, self.product])
        response = self.client.get(reverse('products'), {'category': 'seeds', 'subcategory': 'raw'})
        self.assertEqual(list(response.context['products']), [])
        response = self.client.get(reverse('products'), {'category': 'nuts', 'subcategory': 'raw', 'q': 'missing'})
        self.assertContains(response, 'No matches just yet.')

    def test_anonymous_review_redirects(self):
        response = self.client.post(reverse('product_detail', args=[self.product.pk]), {'title': 'Good', 'rating': 5})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ProductRating.objects.count(), 0)

    def test_review_identity_and_validation(self):
        self.client.force_login(self.user)
        url = reverse('product_detail', args=[self.product.pk])
        self.client.post(url, {'title': 'Good', 'rating': 5, 'user': self.owner.pk})
        self.assertEqual(ProductRating.objects.get().user, self.user)
        self.client.post(url, {'title': 'Bad', 'rating': 100})
        self.assertEqual(ProductRating.objects.count(), 1)

    def test_wishlist_post_only_owner_scoped_and_idempotent(self):
        WishList.objects.create(user=self.owner, wished_product=self.product)
        self.client.force_login(self.user)
        add = reverse('add_to_wishlist', args=[self.product.pk])
        remove = reverse('remove_from_wishlist', args=[self.product.pk])
        self.assertEqual(self.client.get(add).status_code, 405)
        self.assertEqual(self.client.get(remove).status_code, 405)
        self.client.post(add)
        self.client.post(add)
        self.assertEqual(WishList.objects.count(), 2)
        self.client.post(remove)
        self.client.post(remove)
        self.assertEqual(WishList.objects.get().user, self.owner)

    def test_csrf_required(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        self.assertEqual(client.post(reverse('delete_product', args=[self.product.pk])).status_code, 403)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_ordered_product_cannot_be_deleted(self):
        from checkout.models import Order, OrderLineItem
        from nutshell.testing import address
        order = Order.objects.create(**address())
        OrderLineItem.objects.create(order=order, product=self.product, quantity=1)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.post(reverse('delete_product', args=[self.product.pk])).status_code, 302)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())
        self.assertTrue(order.lineitems.exists())
