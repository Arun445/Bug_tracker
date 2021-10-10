from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from faker import Faker
from rest_framework import status
from core.models import Project, Ticket
from core import models
# from api.serializers import CommentSerializer

fake = Faker()
User = get_user_model()
# COMMENT_URL = reverse('api:comment-list')


def comment_detail_url(comment_id):
    # Return ticket detail url
    return reverse('api:comment-detail', args=[comment_id])


def create_comment(user, ticket):
    return models.Comment.objects.create(
        user=user, ticket=ticket, message=fake.word())


def create_test_ticket(user, project):
    '''Creates a test ticket'''
    ticket = Ticket.objects.create(
        user=user,
        project=project,
        title=fake.word(),
        priority='Medium',
        status='Open',
        ticket_type='Debug',
    )
    return ticket


class AuthenticatedUserTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email=fake.email(), password=fake.password())
        self.client = APIClient()
        self.project = Project.objects.create(user=self.user, name=fake.word())
        self.ticket = Ticket.objects.create(
            user=self.user, project=self.project,
            title=fake.word(), priority='Medium',
            status='Open', ticket_type='Debug')
        self.client.force_authenticate(self.user)

    # def test_list_comments_filtered_by_tickets(self):
    #     ticket1 = create_test_ticket(user=self.user, project=self.project)
    #     create_comment(user=self.user,ticket=self.ticket)
    #     create_comment(user=self.user,ticket=ticket1)

    #     response = self.client.get(COMMENT_URL)

    def test_retrieve_comment(self):
        comment = create_comment(user=self.user, ticket=self.ticket)
        url = comment_detail_url(comment.id)
        response = self.client.get(url)

        comment_exists = models.Comment.objects.filter(
            message=comment.message).exists()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(comment_exists)
