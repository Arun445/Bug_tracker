# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from django.urls import reverse
# from rest_framework.test import APIClient
# from faker import Faker
# from rest_framework import status
# from core.models import Project
# from api.serializers import ProjectSerializer

# fake = Faker()
# User = get_user_model()
# PROJECT_URL = reverse('api:project-list')


# class UnauthorizedAssingnmentApiTests(TestCase):

#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create_user(
#             email=fake.email(),
#             name=fake.name(),
#             password=fake.password(),
#         )
#         self.client.force_authenticate(self.user)
