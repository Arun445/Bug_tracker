from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from faker import Faker

User = get_user_model()
fake = Faker()

CREATE_USER_URL = reverse('user:create')


def create_user(**params):
    return User.objects.create_user(**params)


class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        payload = {
            'email': fake.email(),
            'password': fake.password(),
            'name': fake.name()
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_exists(self):
        # Test creating user that already exists fails
        payload = {
            'email': fake.email(),
            'password': fake.password(),
            'name': fake.name()
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_to_short(self):
        # Test that the pasword is more than 5 chars
        payload = {
            'email': fake.email(),
            'password': 'pw',
            'name': fake.name()
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = User.objects.filter(
            email=payload['email']
        )
        self.assertFalse(user_exists)
