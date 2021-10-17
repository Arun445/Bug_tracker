import tempfile
import os
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from faker import Faker
from rest_framework import status
from core import models
from api.serializers import TicketDetailSerializer

User = get_user_model()
fake = Faker()

TICKET_URL = reverse('api:ticket-list')


def create_comment(user, ticket):
    return models.Comment.objects.create(
        user=user, ticket=ticket, message=fake.word())


def file_upload_url(ticket_id):
    '''Return url for ticket file upload'''
    return reverse('api:ticket-upload-file', args=[ticket_id])


def ticket_detail_url(ticket_id):
    # Return ticket detail url
    return reverse('api:ticket-detail', args=[ticket_id])


def fake_ticket_payload(project_id):
    '''Returns a fake payload to create a ticket'''
    payload = {

        'project': project_id,
        'title': fake.word(),
        'priority': 'MEDIUM',
        'status': 'OPEN',
        'ticket_type': 'BUGS/ERRORS',
    }
    return payload


def create_test_ticket(user, project, assigned_user=None):
    '''Creates a test ticket'''
    ticket = models.Ticket.objects.create(
        user=user,
        project=project,
        title=fake.word(),
        priority='Medium',
        status='Open',
        ticket_type='Debug',
        assigned_user=assigned_user
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

    def test_list_all_tickets_assigned_to_user(self):
        '''List all tickets that are assigned to a developer'''

        super_user = User.objects.create_superuser(
            email=fake.email(), password=fake.password())
        ticket1 = create_test_ticket(super_user, self.project, self.user)
        create_test_ticket(super_user, self.project)
        response = self.client.get(TICKET_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['title'], ticket1.title)
        self.assertEqual(len(response.data), 1)

    def test_get_ticket_details(self):
        '''Test that an authenticated user can check any ticket'''

        ticket = create_test_ticket(user=self.user, project=self.project)
        create_test_ticket(user=self.user, project=self.project)
        url = ticket_detail_url(ticket.id)
        response = self.client.get(url)
        serializer = TicketDetailSerializer(ticket, many=False)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_list_all_ticket_comments(self):
        '''Test listing all the comments on a specific ticket'''

        ticket1 = create_test_ticket(user=self.user, project=self.project)
        ticket2 = create_test_ticket(user=self.user, project=self.project)
        comment = create_comment(user=self.user, ticket=ticket1)
        create_comment(user=self.user, ticket=ticket1)
        create_comment(user=self.user, ticket=ticket2)
        url = ticket_detail_url(ticket1.id)
        response = self.client.get(url)
        ticket1_comments = models.Comment.objects.filter(ticket=ticket1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['ticket_comments'][0]['message'], comment.message)
        self.assertEqual(len(ticket1_comments), 2)

    def test_create_ticket_unsuccessful(self):
        '''Test that not submitter and not admin cant create tickets'''

        payload = fake_ticket_payload(self.project.id)
        response = self.client.post(TICKET_URL, payload)
        tickets = models.Ticket.objects.all()

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertAlmostEquals(0, len(tickets))


class SubmitterUserTicketApiTests(TestCase):
    '''Tests to check if submitter and
    admin users can create and edit tickets'''

    def setUp(self):

        self.client = APIClient()
        self.user = User.objects.create_user(
            email=fake.email(), is_submitter=True, password=fake.password())
        self.project = models.Project.objects.create(
            user=self.user, name=fake.name())
        self.client.force_authenticate(self.user)

    def test_list_all_submitted_tickets(self):
        '''Test list all tickets submitted by the sumbitter or admin'''

        ticket1 = create_test_ticket(self.user, self.project)
        ticket2 = create_test_ticket(self.user, self.project)

        response = self.client.get(TICKET_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ticket1.title, response.data[0]['title'])
        self.assertIn(ticket2.title, response.data[1]['title'])

    def test_create_ticket_successful(self):
        '''Test create ticket with User who is_submitter'''

        payload = fake_ticket_payload(self.project.id)
        response = self.client.post(TICKET_URL, payload)
        ticket_exists = models.Ticket.objects.filter(
            user=self.user.id,
            project=self.project.id,
            title=payload['title']
        ).exists()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], payload['title'])
        self.assertTrue(ticket_exists)

    def test_create_ticket_invalid_data(self):
        '''Test create ticket with invalid input'''

        payload = payload = {
            'project': self.project.id,
            'title': fake.word(),
            'priority': '',
            'status': 'OPEN',
            'ticket_type': 'BUGS/ERRORS',
        }
        response = self.client.post(TICKET_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_ticket_by_another_sumbitter(self):
        '''Test the connection between sumbiters'''
        submitter = User.objects.create_user(email=fake.email())
        ticket1 = create_test_ticket(user=submitter, project=self.project)

        url = ticket_detail_url(ticket1.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], ticket1.title)

    def test_delete_ticket_only_by_creator(self):
        '''Test deletion of another submitters ticket is invalid'''
        submitter = User.objects.create_user(
            email=fake.email(), is_submitter=True)
        ticket1 = create_test_ticket(user=submitter, project=self.project)

        url = ticket_detail_url(ticket1.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_ticket_by_creator(self):
        '''Test deletion of ticket'''
        ticket1 = create_test_ticket(user=self.user, project=self.project)

        url = ticket_detail_url(ticket1.id)
        response = self.client.delete(url)
        tickets = models.Ticket.objects.all()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(tickets), 0)

    def test_updating_ticket_create_history(self):
        '''Tests that history models tracks every change made to the ticket'''
        test_user = User.objects.create_user(
            email=fake.email(), password=fake.password(), is_submitter=True)
        payload = {
            'title': fake.word(),
            'priority': 'LOW',
        }
        ticket = create_test_ticket(test_user, self.project)
        url = ticket_detail_url(ticket.id)
        response = self.client.patch(url, payload)
        ticket_history = models.TicketHistory.objects.filter(ticket=ticket)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ticket_history.first(
        ).properties_changed, 'title')
        self.assertEqual(ticket_history.last(
        ).old_value, 'Medium')
        self.assertEqual(ticket_history.last(
        ).new_value, payload['priority'])


class TicketFileUploadApi(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email=fake.email(), password=fake.password(), is_submitter=True)
        self.project = models.Project.objects.create(
            user=self.user, name=fake.name())
        self.ticket = create_test_ticket(self.user, self.project)
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def tearDown(self):
        '''Check if there is a file uploaded if so delete it'''
        if self.ticket.ticketfiles_set.first():
            self.ticket.ticketfiles_set.first().file.delete()

    def test_upload_image_to_ticket(self):
        '''Test uploading image to ticket'''
        url = file_upload_url(self.ticket.id)

        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            file = Image.new('RGB', (10, 10))
            file.save(ntf, format='JPEG')
            ntf.seek(0)
            response = self.client.post(url, {'file': ntf}, format='multipart')
        self.ticket.refresh_from_db()
        file = models.TicketFiles.objects.all().first()

        print((file.file))
        print((ntf.name))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file', response.data)
        # self.assertTrue(os.path.exists(
        #     self.ticket.ticketfiles_set.first().file.path))

    def test_upload_video_file_to_ticket(self):
        '''Test uploading a video file to ticket'''
        url = file_upload_url(self.ticket.id)

        file = SimpleUploadedFile(
            "file.mp4", b"file_content", content_type="video/mp4")

        response = self.client.post(url, {'file': file}, format='multipart')
        self.ticket.refresh_from_db()
        files = models.TicketFiles.objects.all().first()

        print((files.file))
        print((file))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('file', response.data)
        # self.assertTrue(os.path.exists(
        #     self.ticket.ticketfiles_set.first().file.path))

    def test_upload_file_bad_request(self):
        '''Test uploading an invalid file'''
        url = file_upload_url(self.ticket.id)
        response = self.client.post(url, {'file': 'none'}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
