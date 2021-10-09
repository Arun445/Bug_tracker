from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from faker import Faker
from rest_framework import status
from core import models
from api.serializers import TicketSerializer

User = get_user_model()
fake = Faker()

TICKET_URL = reverse('api:ticket-list')


def ticket_detail_url(ticket_id):
    # Return ticket detail url
    return reverse('api:ticket-detail', args=[ticket_id])


def create_test_ticket(user, project):
    ticket = models.Ticket.objects.create(
        user=user,
        project=project,
        title=fake.text()[:15],
        priority='Medium',
        status='Open',
        ticket_type='Debug'
    )
    return ticket


class DeveloperUserTicketApiTests(TestCase):
    '''TestCase for Developer authentication users'''

    def setUp(self):

        self.client = APIClient()
        self.user = User.objects.create_user(
            email=fake.email(), name=fake.name(), password=fake.password())
        self.project = models.Project.objects.create(
            user=self.user, name=fake.name())
        self.client.force_authenticate(self.user)

    # def test_list_all_tickets_assigned_to_user(self):
    #     '''List all tickets that are assigned to a developer'''
    # t

    def test_get_ticket_details(self):
        '''Test that an authenticated user can check any ticket'''
        ticket = create_test_ticket(user=self.user, project=self.project)
        url = ticket_detail_url(ticket.id)
        response = self.client.get(url)
        serializer = TicketSerializer(ticket, many=False)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_ticket_unsuccessful(self):
        '''Test that not submitter and not admin cant create tickets'''

        payload = {
            'project': self.project.id,
            'title': fake.text()[0:15],
            'priority': 'Medium',
            'status': 'Open',
            'ticket_type': 'Bugs/Errors',
        }
        response = self.client.post(TICKET_URL, payload)
        tickets = models.Ticket.objects.all()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertAlmostEquals(0, len(tickets))


class SubmitterUserTicketApiTests(TestCase):
    '''Tests to check if submitter and admin users can create and edit tickets'''

    def setUp(self):

        self.client = APIClient()
        self.user = User.objects.create_superuser(
            email=fake.email(), name=fake.name(), password=fake.password())
        self.project = models.Project.objects.create(
            user=self.user, name=fake.name())
        self.client.force_authenticate(self.user)

    def test_create_ticket_successful(self):
        '''Test create ticket with User who is_submitter'''
        payload = {

            'project': self.project.id,
            'title': fake.text()[0:15],
            'priority': 'MEDIUM',
            'status': 'OPEN',
            'ticket_type': 'BUGS/ERRORS',
        }
        response = self.client.post(TICKET_URL, payload)
        ticket_exists = models.Ticket.objects.filter(
            user=self.user.id,
            project=self.user.id,
            title=payload['title']
        ).exists()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], payload['title'])
        self.assertTrue(ticket_exists)

    def test_create_ticket_invalid_data(self):
        '''Test create ticket with invalid input'''
        payload = {

            'project': self.project.id,
            'title': fake.text()[0:15],
            'priority': '',
            'status': 'OPEN',
            'ticket_type': 'BUGS/ERRORS',
        }
        response = self.client.post(TICKET_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
