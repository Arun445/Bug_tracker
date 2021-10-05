from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
# from rest_framework.decorators import permission_classes
from api.permissions import IsAdminOrReadOnly
from api.serializers import ProjectSerializer
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

    # def perform_update(self, serializer):
    #     instance = serializer.save()
    #     (user=self.request.user, modified=instance)
