from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from faker import Faker
from rest_framework import status
from core.models import Project
from api.serializers import ProjectSerializer

fake = Faker()
User = get_user_model()
PROJECT_URL = reverse('api:project-list')


def transaction_detail_url(transaction_id):
    # Return transaction detail url
    return reverse('api:transaction-detail', args=[transaction_id])


# class PublicProjectApiTests(TestCase):
#     '''Test Project view without login'''

#     def setUp(self):
#         self.client = APIClient()

#     def test_get_all_projects_unsuccessful(self):
#         response = self.client.get(PROJECT_URL)
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_get_project_data_unsuccessful(self):
    #     response = self.client.get(PROJECT_URL)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_create_project_unsuccessful(self):
    #     payload = {
    #         'name': fake.name(),
    #         'description': fake.text()
    #     }
    #     response = self.client.post(CREATE_PROJECT_URL, payload)
    #     self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class NotAdminProjectApiTests(TestCase):
    ''' Test Project model with authenticated user '''

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email=fake.email(),
            name=fake.name(),
            password=fake.password(),
        )
        self.client.force_authenticate(self.user)

    def test_get_all_projects_successful(self):
        Project.objects.create(user=self.user, name=fake.name())
        response = self.client.get(PROJECT_URL)

        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_project_not_authorized(self):
        '''Test to create a project when the user is not a project manager'''
        payload = {
            'name': fake.name()
        }
        response = self.client.post(PROJECT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminProjectApiTests(TestCase):
    ''' Test Project model with admin and project manager users'''

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email=fake.email(),
            name=fake.name(),
            password=fake.password(),
            is_project_manager=True
        )
        self.client.force_authenticate(self.user)

    def test_create_project_as_project_manager(self):
        '''Tests if a user can create a project if is project manager'''
        payload = {
            'name': fake.name()
        }
        self.client.post(PROJECT_URL, payload)

        project_exists = Project.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(project_exists)
