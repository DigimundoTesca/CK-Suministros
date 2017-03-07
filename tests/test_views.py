
from django.test import TestCase
from django.urls import reverse

from users.models import User


class SimpleClass(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='usuario', password='contrasenaSegur4')

    def test_views_not_authenticated(self):
        res = self.client.get(reverse('users:login'))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('users:logout'))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(reverse('users:new_customer'))
        self.assertEqual(res.status_code, 200)

        res = self.client.get(reverse('users:customers_list'))
        self.assertEqual(res.status_code, 302)

    def test_views_authenticated(self):
        self.client.login(username='usuario', password='contrasenaSegur4')

        res = self.client.get(reverse('users:logout'))
        self.assertEqual(res.status_code, 302)

        self.client.login(username='usuario', password='contrasenaSegur4')

        res = self.client.get(reverse('users:index'))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(reverse('users:login'))
        self.assertEqual(res.status_code, 302)

        res = self.client.get(reverse('users:customers_list'))
        self.assertEqual(res.status_code, 200)
