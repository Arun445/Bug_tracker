from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework import reverse
from rest_framework.test import APIClient
from faker import Faker
from core.models import Project

fake = Faker()
User = get_user_model()
CREATE_PROJECT_URL = reverse('project:create')


class PublicProjectApiTests(TestCase):
    # Test Project Creation with not authenticated users

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email=fake.email(),
            name=fake.name(),
            password=fake.password()
        )

    def test_create_project_unsuccessful(self):
        Project.objects.create(fake.name)


class PrivateProjectApiTests(TestCase):
    # Test Project Creation with authenticated users

    def setUp(self):
        self.client = APIClient()
