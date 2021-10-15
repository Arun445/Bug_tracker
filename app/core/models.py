from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager, AbstractUser)
from django.db.models.fields.related import ForeignKey


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        # Creates and saves a new user
        if not email:
            raise ValueError('Users must have email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.is_staff = True
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        # Creates and saves a new super user
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractUser):
    username = None
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_submitter = models.BooleanField(default=False)
    is_project_manager = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email


class Project(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True
    )
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200, blank=True)
    is_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class UsersAssignedToProject(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{str(self.user)}, {str(self.project)}'

    class Meta:
        unique_together = [['user', 'project']]


class Ticket(models.Model):
    PRIORITY_CHOICES = (
        ('NONE', 'None'),
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
    )
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('IN PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('DONE', 'Done'),
    )
    TYPE_CHOICES = (
        ('BUGS/ERRORS', 'Bugs/Errors'),

    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        related_name='user'
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=200, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    ticket_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    assigned_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='assigned_user',
        on_delete=models.CASCADE, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    ticket_files = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through='TicketFiles')

    def __str__(self):
        return str(self.title)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             null=True)
    ticket = models.ForeignKey(
        'Ticket', related_name='ticket_comments', on_delete=models.CASCADE)
    message = models.TextField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class TicketHistory(models.Model):
    ticket = models.ForeignKey(
        'Ticket', related_name='ticket_history', on_delete=models.DO_NOTHING)
    changed_by = ForeignKey(settings.AUTH_USER_MODEL,
                            on_delete=models.DO_NOTHING)
    properties_changed = models.CharField(max_length=100)
    old_value = models.CharField(max_length=100)
    new_value = models.CharField(max_length=100)
    date_changed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{str(self.ticket)} {self.date_changed}'


class TicketFiles(models.Model):
    ticket = models.ForeignKey('Ticket', on_delete=models.CASCADE, null=True)
    uploaded_by = ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, null=True)
    file = models.FileField(null=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{str(self.ticket)} uploaded by {str(self.uploaded_by)}'
