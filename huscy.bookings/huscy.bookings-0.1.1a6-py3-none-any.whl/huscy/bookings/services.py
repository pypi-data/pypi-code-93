from datetime import datetime

from django.db import transaction

from huscy.appointments.services import (
    create_appointment,
    remove_appointment,
    set_participants
)

from huscy.bookings import models


class BookingExistsException(Exception):
    pass


class CannotBookInactiveTimeslotException(Exception):
    pass


def get_timeslots(project, experiment=None):
    timeslots = models.Timeslot.objects.filter(session__experiment__project=project,
                                               start__gte=datetime.now())
    if experiment:
        timeslots = timeslots.filter(session__experiment=experiment)
    return timeslots


def add_timeslot(session, start):
    timeslot = models.Timeslot(session=session, start=start)
    timeslot.active = not timeslot.has_overlap_with_booked_timeslots()
    timeslot.save()
    return timeslot


def delete_timeslot(timeslot):
    if timeslot.has_booking:
        raise BookingExistsException('Cannot remove booked timeslot')
    timeslot.delete()


def move_timeslot(timeslot, start):
    if timeslot.has_booking:
        raise BookingExistsException('Cannot move booked timeslot')
    timeslot.start = start
    timeslot.active = not timeslot.has_overlap_with_booked_timeslots()
    timeslot.save()
    return timeslot


@transaction.atomic
def unbook_timeslot(timeslot):
    for booking in timeslot.booking_set.all():
        remove_appointment(booking.appointment)

    # timeslot is again active
    timeslot.active = True
    timeslot.save()

    # check overlapping timeslots
    overlapping_timeslots = models.Timeslot.objects.get_overlapping_timeslots(timeslot)
    for t in overlapping_timeslots:
        if not t.has_overlap_with_booked_timeslots():
            t.active = True
            t.save()


@transaction.atomic
def book_timeslot(timeslot, subject):
    if not timeslot.active:
        raise CannotBookInactiveTimeslotException('Only active timeslots can be booked')

    if timeslot.has_booking:
        booking = timeslot.booking_set.get()
        appointment = booking.appointment
        participants = list(appointment.invitations.values_list('participant', flat=True))
        participants.append(subject)
        set_participants(appointment, participants)
    else:
        appointment = create_appointment(
            timeslot.session.operator,
            timeslot.start, timeslot.end,
            title=timeslot.session.experiment.project.title,
            description='',
            # resource=timeslot.session.dataacquisitionmethod_set.get().location,
            participants=[subject]
        )
        booking = models.Booking.objects.create(appointment=appointment, timeslot=timeslot)
        models.Timeslot.objects.set_overlapping_timeslots_inactive(timeslot)

    if timeslot.session.max_number_of_participants == appointment.invitations.count():
        timeslot.active = False
        timeslot.save(update_fields=['active'])

    return booking
