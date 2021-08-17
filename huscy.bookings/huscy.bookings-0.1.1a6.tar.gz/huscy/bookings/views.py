from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from huscy.bookings import models, serializers, services
from huscy.projects.models import Project, Experiment


class CanAddBookings(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('bookings.add_booking')


class CanDeleteBookings(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.has_perm('bookings.delete_booking')


class TimeslotViewSet(viewsets.ModelViewSet):
    queryset = models.Timeslot.objects.all()
    serializer_class = serializers.TimeslotSerializer
    permission_classes = (permissions.DjangoModelPermissions, )

    def perform_destroy(self, timeslot):
        try:
            services.delete_timeslot(timeslot)
        except services.BookingExistsException as e:
            raise ValidationError(e)

    @action(detail=True, methods=['post'], permission_classes=[CanAddBookings])
    def book(self, request, pk):
        timeslot = self.get_object()
        try:
            services.book_timeslot(timeslot, "abc")
        except services.CannotBookInactiveTimeslotException as e:
            raise ValidationError(e)
        return Response(self.get_serializer(timeslot).data, status=HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], permission_classes=[CanDeleteBookings])
    def unbook(self, request, pk):
        timeslot = self.get_object()
        services.unbook_timeslot(timeslot)
        return Response(status=HTTP_204_NO_CONTENT)


class ListTimeslotsViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.TimeslotSerializer
    permission_classes = (IsAuthenticated, )

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        self.experiment = (get_object_or_404(Experiment, pk=kwargs['experiment_pk'])
                           if 'experiment_pk' in kwargs else None)

    def get_queryset(self):
        return services.get_timeslots(self.project, self.experiment)
