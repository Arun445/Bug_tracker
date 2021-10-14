from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from faker import Faker
from rest_framework import status
from core.models import Project, UsersAssignedToProject, Ticket
from api.serializers import ProjectSerializer

fake = Faker()
User = get_user_model()
PROJECT_URL = reverse('api:project-list')


def fake_user(wow=None):
    '''Creates a fake user'''
    return User.objects.create_user(
        email=fake.email(), password=fake.password(), name=fake.name())


def project_detail_url(project_id):
    return reverse('api:project-detail', args=[project_id])


def users_assignment_url(project_id):
    # Return URL for transaction image upload
    return reverse('api:project-assign-users', args=[project_id])


def create_test_ticket(user, project, assigned_user=None):
    '''Creates a test ticket'''
    ticket = Ticket.objects.create(
        user=user,
        project=project,
        title=fake.word(),
        priority='Medium',
        status='Open',
        ticket_type='Debug',
        assigned_user=assigned_user
    )
    return ticket


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
        '''Test listing all projects successful'''
        Project.objects.create(user=self.user, name=fake.name())
        response = self.client.get(PROJECT_URL)

        projects = Project.objects.all()
        serializer = ProjectSerializer(projects, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_all_projects_with_assigned_users(self):
        '''Test listing all project assinged users'''
        project = Project.objects.create(user=self.user, name=fake.name())
        user1 = fake_user()
        assigned_user = project.usersassignedtoproject_set.create(
            user=self.user)
        project.usersassignedtoproject_set.create(user=user1)
        url = project_detail_url(project.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['assigned_users'][0]['user'], assigned_user.user.id)
        self.assertEqual(
            len((response.data)['assigned_users']), 2)

    def test_list_all_project_tickets(self):
        '''Test listing all project tickets'''
        project = Project.objects.create(user=self.user, name=fake.name())
        project1 = Project.objects.create(user=self.user, name=fake.name())

        ticket1 = create_test_ticket(user=self.user, project=project)
        create_test_ticket(user=self.user, project=project1)
        url = project_detail_url(project.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            (response.data)['project_tickets'][0]['title'], ticket1.title)
        self.assertEqual(
            len((response.data)['project_tickets']), 1)

    def test_create_project_not_authorized(self):
        '''Test to create a project when the user is not a project manager'''
        payload = {
            'name': fake.name()
        }
        response = self.client.post(PROJECT_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_project_not_authorized(self):
        '''Test that an unauthorized user cant delete a project'''
        project = Project.objects.create(user=self.user, name=fake.name())

        url = project_detail_url(project.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assign_users_to_project_unsuccessful(self):
        '''Test to check what a developer can assign users to projects'''
        user = fake_user()
        project = Project.objects.create(user=self.user, name=fake.name())
        url = users_assignment_url(project.id)
        payload = {'users': [user.id]}
        response = self.client.post(url, payload)

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
        be assigned to the same procject twice'''
        user = fake_user()
        project = Project.objects.create(user=self.user, name=fake.name())
        url = users_assignment_url(project.id)

        payload = {'users': [user.id]}
        self.client.post(url, payload)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_project_not_by_creator(self):
        '''Test fail to delete project by another manager'''
        project_manager = User.objects.create_user(
            email=fake.email(),
            password=fake.password(),
            is_project_manager=True)
        project = Project.objects.create(
            user=project_manager, name=fake.name())

        url = project_detail_url(project.id)
        response = self.client.delete(url)
        projects = Project.objects.all()

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(len(projects), 1)
