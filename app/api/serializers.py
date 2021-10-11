from rest_framework import serializers
from core import models


class ProjectSerializer(serializers.ModelSerializer):
    assigned_users = serializers.SerializerMethodField()

    class Meta:
        model = models.Project
        fields = '__all__'
        read_only_fields = (id,)

    def get_assigned_users(self, obj):
        assigned_users = obj.usersassignedtoproject_set.filter(
            project=obj.id
        )
        serializer = AssignToProjectSerializer(assigned_users, many=True)
        return serializer.data


class AssignToProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UsersAssignedToProject
        fields = ['user', 'id']
        read_only_fields = (id,)


class AssignManyToProjectSerializer(serializers.Serializer):
    users = AssignToProjectSerializer(many=True)


class TicketSerializer(serializers.ModelSerializer):
    ticket_comments = serializers.SerializerMethodField()

    class Meta:
        model = models.Ticket
        fields = ['id', 'user', 'project', 'title', 'description', 'priority',
                  'status', 'ticket_type', 'assigned_user', 'date_created',
                  'ticket_comments']
        read_only_fields = (id,)

    def get_ticket_comments(self, obj):
        ticket_comments = obj.comment_set.filter(
            ticket=obj.id
        )
        serializer = CommentSerializer(ticket_comments, many=True)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields = (id,)
