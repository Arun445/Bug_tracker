from rest_framework import viewsets, status, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from api.custom_permissions import (
    IsProjectManagerOrReadOnly, IsSubmitterOrReadOnly)
from api.serializers import (
    ProjectSerializer, ProjectDetailSerializer, TicketSerializer,
    TicketDetailSerializer, AssignManyToProjectSerializer,
    CommentSerializer)
from core import models


class ProjectViewSet(viewsets.ModelViewSet):
    '''Manage projects in the database'''
    serializer_class = ProjectSerializer
    permission_classes = (IsProjectManagerOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    queryset = models.Project.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        '''Return appropriate serializer class'''

        if self.action == 'retrieve':
            return ProjectDetailSerializer
        if self.action == 'assign_users':
            return AssignManyToProjectSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'], url_path='assign-users')
    def assign_users(self, request, pk=None):
        '''Method to assign users to project'''
        project = self.get_object()
        users = dict(request.data)['users']

        # Get all users assigned to the project
        all_users_assigned_to_project = [
            assigned.user for assigned in
            models.UsersAssignedToProject.objects.filter(project=project)]

        # Check if a user is already assigned to the project
        for user_id in users:
            user = get_user_model().objects.get(id=user_id)
            if user in all_users_assigned_to_project:
                return Response({
                    'detail': f'User {user} is already assigned to the project'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Assign users to project
        for user_id in users:
            user = get_user_model().objects.get(id=user_id)
            models.UsersAssignedToProject.objects.create(
                user=user, project=project
            )

        serializer = ProjectDetailSerializer(
            project, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def perform_update(self, serializer):
    #     instance = serializer.save()
    #     (user=self.request.user, modified=instance)


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    queryset = models.Ticket.objects.all()
    permission_classes = (IsSubmitterOrReadOnly,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        '''Get queryset depending on authentication and http method'''
        if self.action == 'list':
            if self.request.user.is_submitter or \
                    self.request.user.is_superuser:
                return self.queryset.filter(user=self.request.user)
            else:
                return self.queryset.filter(assigned_user=self.request.user)
        elif self.action == 'retrieve':
            return self.queryset
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        '''Return appropriate serializer class'''

        if self.action in ['retrieve', 'update', 'patch']:
            return TicketDetailSerializer

        return self.serializer_class

    def perform_update(self, serializer):
        ticket = self.get_object()
        for key, new_value in (serializer.validated_data.items()):
            if new_value != getattr(ticket, key):
                ticket.tickethistory_set.create(
                    changed_by=self.request.user,
                    properties_changed=key,
                    old_value=getattr(ticket, key),
                    new_value=new_value)

        serializer.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == self.request.user or self.request.user.is_superuser:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'detail': 'User is not the creator of this ticket'},
                status=status.HTTP_401_UNAUTHORIZED)


class CommentViewSet(viewsets.GenericViewSet,
                     mixins.RetrieveModelMixin,
                     mixins.CreateModelMixin,
                     mixins.DestroyModelMixin):

    serializer_class = CommentSerializer
    queryset = models.Comment.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user == self.request.user or self.request.user.is_superuser:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'detail': 'User is not the creator of this comment'},
                status=status.HTTP_401_UNAUTHORIZED)
