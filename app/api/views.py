from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import get_user_model

from api.custom_permissions import IsAdminOrReadOnly, IsSubmitterOrReadOnly
from api.serializers import ProjectSerializer, TicketSerializer, OneTwo
from core import models


class ProjectViewSet(viewsets.ModelViewSet
                     ):
    '''Manage projects in the database'''
    serializer_class = ProjectSerializer
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    queryset = models.Project.objects.all()

    def get_queryset(self):
        return self.queryset

    def get_serializer_class(self):
        '''Return appropriate serializer class'''

        # if self.action == 'retrieve':
        #     return
        if self.action == 'assign_users':
            return OneTwo
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'], url_path='assign-users')
    def assign_users(self, request, pk=None):
        '''Method to assign users to project'''
        project = self.get_object()
        users = dict(request.data)['users']
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

        serializer = ProjectSerializer(
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
        if self.request.user.is_submitter or self.request.user.is_superuser:
            return self.queryset.filter(user=self.request.user)
        elif self.action == 'retrieve':
            return self.queryset
        return self.queryset.filter(assigned_user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
