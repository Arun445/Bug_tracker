from django.test import TestCase
from django.contrib.auth import get_user_model
from faker import Faker
User = get_user_model()
fake = Faker()


class ModelTest(TestCase):

    def test_create_user_with_email_successful(self):
        # Test creating a new user with a email is successful
        email = fake.email()
        password = fake.password()
        user = User.objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test a email for a new user normalized
        email = 'test@EMAIL.COM'
        password = fake.password()
        user = User.objects.create_user(email, password)

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        # Test creating user with no email raises error
        with self.assertRaises(ValueError):
            User.objects.create_user(None, fake.password())

    def test_create_new_superuser(self):
        # Test Creating a new superuser
        user = User.objects.create_superuser(
            fake.email(),
            fake.password()
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
