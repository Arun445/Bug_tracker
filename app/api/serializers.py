from rest_framework import serializers
from core import models
from django.contrib.auth import get_user_model


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = ['id', 'user', 'name', 'description', 'is_complete', ]
        read_only_fields = (id,)


class ProjectDetailSerializer(serializers.ModelSerializer):
    assigned_users = serializers.SerializerMethodField()
    project_tickets = serializers.SerializerMethodField()

    class Meta:
        model = models.Project
        fields = ['id', 'user', 'name', 'description', 'is_complete',
                  'assigned_users', 'project_tickets'
                  ]
        read_only_fields = (id,)

    def get_assigned_users(self, obj):
        assigned_users = obj.usersassignedtoproject_set.filter(
            project=obj.id
        )
        serializer = AssignToProjectSerializer(assigned_users, many=True)
        return serializer.data

    def get_project_tickets(self, obj):
        project_tickets = obj.ticket_set.filter(
            project=obj.id
        )
        serializer = TicketSerializer(project_tickets, many=True)
        return serializer.data


class AssignToProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UsersAssignedToProject
        fields = ['user', 'id']
        read_only_fields = (id,)


class AssignManyToProjectSerializer(serializers.Serializer):
    users = AssignToProjectSerializer(many=True)


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='email', queryset=get_user_model().objects.all())

    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields = (id, 'user')


class TicketHistorySerializer(serializers.ModelSerializer):
    changed_by = serializers.SlugRelatedField(
        slug_field='email', queryset=get_user_model().objects.all())

    class Meta:
        model = models.TicketHistory
        fields = '__all__'


class TicketFilesSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='email', queryset=get_user_model().objects.all())

    class Meta:
        model = models.TicketFiles
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Ticket
        fields = ['id', 'project', 'title',
                  'priority', 'status', 'ticket_type', ]
        read_only_fields = (id,)


class TicketDetailSerializer(serializers.ModelSerializer):
    ticket_comments = CommentSerializer(many=True)
    ticket_history = TicketHistorySerializer(many=True, read_only=True)
    ticket_files = TicketFilesSerializer(many=True)

    class Meta:
        model = models.Ticket
        fields = ('id', 'user', 'project', 'title', 'description', 'priority',
                  'status', 'ticket_type', 'assigned_user', 'date_created',
                  'ticket_comments', 'ticket_history', 'ticket_files')
        read_only_fields = (id,)


class TicketFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TicketFiles
        fields = ('id', 'file')
        read_only_fields = ('id',)
