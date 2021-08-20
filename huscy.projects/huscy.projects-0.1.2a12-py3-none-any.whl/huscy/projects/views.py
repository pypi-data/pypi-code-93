import logging

from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated, IsAdminUser

from huscy.projects import helpers, serializer, services
from huscy.projects.models import Project
from huscy.projects.permissions import AllowAnyToCreate, IsProjectCoordinator, ReadOnly

logger = logging.getLogger('projects')


class DataAcquisitionMethodViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                                   mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = services.get_data_acquisition_methods()
    serializer_class = serializer.DataAcquisitionMethodSerializer
    permission_classes = (IsAuthenticated, )


class ExperimentViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                        mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializer.ExperimentSerializer
    permission_classes = (IsAuthenticated, )

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_experiments(self.project)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.project
        return context


class MembershipViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                        mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializer.MembershipSerializer
    permission_classes = (IsAuthenticated, IsAdminUser | IsProjectCoordinator | ReadOnly)

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_memberships(self.project)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project'] = self.project
        return context

    def perform_destroy(self, membership):
        services.remove_member(membership)


class ProjectViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                     mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializer.ProjectSerializer
    permission_classes = (IsAuthenticated, DjangoModelPermissions | AllowAnyToCreate)

    def get_queryset(self):
        return services.get_projects()

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        logger.info('User %s from ip %s requested deletion of project with id:%d',
                    request.user.username, helpers.get_client_ip(request), pk)
        return super().destroy(request, args, kwargs)

    def perform_destroy(self, project):
        services.delete_project(project)


class ResearchUnitViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissions, )
    queryset = services.get_research_units()
    serializer_class = serializer.ResearchUnitSerializer


class SessionViewSet(viewsets.ModelViewSet):
    queryset = services.get_sessions()
    serializer_class = serializer.SessionSerializer
    permission_classes = (IsAuthenticated, )
