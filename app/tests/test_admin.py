from django.test import TestCase, Client
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from faker import Faker

fake = Faker()
User = get_user_model()


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(
            email=fake.email(),
            password=fake.password()
        )
        self.client.force_login(self.admin_user)
        self.user = User.objects.create_user(
            email=fake.email(),
            password=fake.password(),
            name=fake.name()
        )

    def test_users_listed(self):
        # Test that users are listed on user page
        url = reverse('admin:core_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.email)

    def test_user_change_page(self):
        # Test that the user edit page works
        url = reverse('admin:core_user_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_user_page(self):
        # TEst that the create user page works
        url = reverse('admin:core_user_add')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
