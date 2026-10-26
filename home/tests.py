from django.test import TestCase
from django.urls import reverse

class PageSmokeTests(TestCase):
    def test_public_and_authentication_pages_render(self):
        for name in ('home', 'products', 'account_login', 'account_signup'):
            with self.subTest(name=name):
                self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_logout_get_requires_confirmation_and_post_logs_out(self):
        from django.contrib.auth.models import User
        user = User.objects.create_user('customer', password='password')
        self.client.force_login(user)
        self.assertEqual(self.client.get(reverse('account_logout')).status_code, 200)
        self.assertIn('_auth_user_id', self.client.session)
        self.client.post(reverse('account_logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
