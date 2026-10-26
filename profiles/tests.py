from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('customer', password='password')
        self.other = User.objects.create_user('other', password='password')
        self.client.force_login(self.user)

    def test_valid_update_is_owner_scoped(self):
        self.client.post(reverse('profile'), {'default_phone_number': '123', 'default_country': 'SE', 'user': self.other.pk})
        self.user.userprofile.refresh_from_db()
        self.other.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.default_phone_number, '123')
        self.assertIsNone(self.other.userprofile.default_phone_number)

    def test_invalid_update_does_not_save(self):
        self.client.post(reverse('profile'), {'default_phone_number': '123'})
        response = self.client.post(reverse('profile'), {'default_phone_number': 'x' * 21})
        self.assertFalse(response.context['form'].is_valid())
        self.user.userprofile.refresh_from_db()
        self.assertEqual(self.user.userprofile.default_phone_number, '123')

    def test_profile_requires_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse('profile')).status_code, 302)
