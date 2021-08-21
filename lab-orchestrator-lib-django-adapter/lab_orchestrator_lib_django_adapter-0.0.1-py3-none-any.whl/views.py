from django.shortcuts import get_object_or_404
from lab_orchestrator_lib.controller.controller_collection import ControllerCollection

from lab_orchestrator_lib.kubernetes.api import APIRegistry
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from lab_orchestrator_lib.kubernetes.config import get_development_config, get_kubernetes_config, get_registry, \
    KubernetesConfig
from lab_orchestrator_lib_django_adapter.controller_collection import create_django_controller_collection
from lab_orchestrator_lib_django_adapter.models import LabInstanceModel, LabModel, DockerImageModel
from lab_orchestrator_lib_django_adapter.serializers import LabInstanceModelSerializer, LabInstanceKubernetesSerializer, \
    LabModelSerializer, DockerImageModelSerializer


class DockerImageViewSet(viewsets.ModelViewSet):
    #permission_classes = [permissions.IsAuthenticated]
    queryset = DockerImageModel.objects.all()
    serializer_class = DockerImageModelSerializer


class LabViewSet(viewsets.ModelViewSet):
    #permission_classes = [permissions.IsAuthenticated]
    queryset = LabModel.objects.all()
    serializer_class = LabModelSerializer


class LabInstanceViewSet(viewsets.ViewSet):
    def __init__(self, development: bool = False, kubernetes_config: KubernetesConfig = None,
                 registry: APIRegistry = None, controller_collection: ControllerCollection = None):
        super().__init__()
        if kubernetes_config is None:
            development = False
            if development:
                kubernetes_config = get_development_config()
            else:
                kubernetes_config = get_kubernetes_config()
        if registry is None:
            registry = get_registry(kubernetes_config)
        if controller_collection is None:
            self.cc = create_django_controller_collection(registry)
        else:
            self.cc = controller_collection

    def list(self, request):
        queryset = LabInstanceModel.objects.all()
        serializer = LabInstanceModelSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = LabInstanceModel.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = LabInstanceModelSerializer(user)
        return Response(serializer.data)

    def create(self, request):
        lab_id = request.POST.get("lab_id")
        lab_instance_kubernetes = self.cc.lab_instance_ctrl.create(lab_id=lab_id, user_id=request.user.id)
        serializer = LabInstanceKubernetesSerializer(lab_instance_kubernetes)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        self.cc.lab_instance_ctrl.delete(pk)
