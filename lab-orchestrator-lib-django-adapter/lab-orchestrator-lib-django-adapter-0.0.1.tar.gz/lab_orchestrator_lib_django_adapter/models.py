from django.db import models
from django.contrib.auth import get_user_model


class DockerImageModel(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32, unique=True, null=False)
    description = models.CharField(max_length=128, null=True)
    url = models.CharField(max_length=256, null=False)


class LabModel(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=32, unique=True, null=False)
    namespace_prefix = models.CharField(max_length=32, unique=True, null=False)
    description = models.CharField(max_length=128, null=True)
    docker_image_id = models.ForeignKey(DockerImageModel, on_delete=models.DO_NOTHING, null=True, related_name="labs")
    docker_image_name = models.CharField(max_length=32, null=False)


class LabInstanceModel(models.Model):
    id = models.IntegerField(primary_key=True)
    lab_id = models.ForeignKey(LabModel, on_delete=models.CASCADE, null=False, related_name="lab_instances")
    user_id = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=False, related_name="lab_instances")
