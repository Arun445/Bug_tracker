from rest_framework import serializers
from core import models


class ProjectSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Project
        fields = '__all__'
        read_only_fields = (id,)
