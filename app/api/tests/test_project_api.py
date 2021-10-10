from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from faker import Faker
from rest_framework import status
from core.models import Project, UsersAssignedToProject
from api.serializers import ProjectSerializer

fake = Faker()
User = get_user_model()
PROJECT_URL = reverse('api:project-list')


def fake_user(wow=None):
    '''Creates a fake user'''
    return User.objects.create_user(
        email=fake.email(), password=fake.password(), name=fake.name())


def users_assignment_url(project_id):
    # Return URL for transaction image upload
    return reverse('api:project-assign-users', args=[project_id])


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

    def test_assign_users_to_project(self):
        '''Test to check if project manager can assign users to projects'''
        user = fake_user()
        user1 = fake_user()
        project = Project.objects.create(user=self.user, name=fake.name())
        url = users_assignment_url(project.id)

        payload = {'users': [user.id, user1.id]}
        response = self.client.post(url, payload)
        users = UsersAssignedToProject.objects.filter(project=project)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(user, users[0].user)
        self.assertEqual(user1, users[1].user)

    def test_assign_the_same_user_to_project_twice(self):
        '''Test to check if a user can
        be assigned to the same procejt twice'''
        user = fake_user()
        project = Project.objects.create(user=self.user, name=fake.name())
        url = users_assignment_url(project.id)

        payload = {'users': [user.id]}
        self.client.post(url, payload)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
