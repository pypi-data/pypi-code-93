from django.db import models

from huscy.appointments.models import Appointment
from huscy.projects.models import Session


class TimeslotManager(models.Manager):
    def get_overlapping_timeslots(self, timeslot):
        locations = timeslot.session.dataacquisitionmethod_set.values_list('location', flat=True)

        qs = self.get_queryset()
        qs = qs.exclude(pk=timeslot.pk)
        qs = qs.exclude(start__gte=timeslot.end)
        qs = qs.exclude(start__lte=timeslot.start - models.F('session__setup_time')
                        - models.F('session__duration') - models.F('session__teardown_time'))
        qs = qs.filter(session__dataacquisitionmethod__location__in=locations)
        return qs

    def set_overlapping_timeslots_inactive(self, timeslot):
        qs = self.get_overlapping_timeslots(timeslot)
        qs.update(active=False)


class Timeslot(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='timeslots')

    active = models.BooleanField(default=True)
    start = models.DateTimeField()

    objects = TimeslotManager()

    @property
    def end(self):
        return (self.start + self.session.setup_time + self.session.duration
                + self.session.teardown_time)

    @property
    def has_booking(self):
        return self.booking_set.exists()

    def has_overlap_with_booked_timeslots(self):
        qs = Booking.objects.filter(
            appointment__resource__in=self.session.dataacquisitionmethod_set.values_list('location',
                                                                                         flat=True)
        )
        qs = qs.exclude(models.Q(appointment__start__gte=self.end) |
                        models.Q(appointment__end__lte=self.start))
        return qs.exists()


class Booking(models.Model):
    timeslot = models.ForeignKey(Timeslot, on_delete=models.CASCADE)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
