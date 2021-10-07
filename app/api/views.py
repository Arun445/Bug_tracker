from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.decorators import action

from django.contrib.auth import get_user_model

from api.permissions import IsAdminOrReadOnly, IsSubmitter
from api.serializers import ProjectSerializer, TicketSerializer
from core import models


class ProjectViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.CreateModelMixin
                     ):
    '''Manage projects in the database'''
    serializer_class = ProjectSerializer
    permission_classes = (IsAdminOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
    queryset = models.Project.objects.all()

    def get_queryset(self):
        return self.queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['POST'])
    def assign_users(self, request, pk=None):
        project = models.Project.objects.get(id=request.POST.get('project_id'))
        for user in request.POST.getlist('users'):
            user = get_user_model().objects.get(id=user)
            models.UsersAssignedToProject.objects.create(
                user=user, project=project
            )
        serializer = ProjectSerializer(
            project, many=False)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # def perform_update(self, serializer):
    #     instance = serializer.save()
    #     (user=self.request.user, modified=instance)


class TicketViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    serializer_class = TicketSerializer
    queryset = models.Ticket.objects.all()
    permission_classes = (IsSubmitterOrReadOnly,)
    authentication_classes = (TokenAuthentication,)
