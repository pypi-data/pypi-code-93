from onlineafspraken.api.client import OnlineAfsprakenAPI, client
from onlineafspraken.schema.appointment import (
    CancelAppointmentResponse,
    ConfirmAppointmentResponse,
    GetAppointmentsResponse,
    GetAppointmentResponse,
    SetAppointmentResponse,
    SetAppointmentSchema,
)


def cancel_appointment(
    appointment_id, mode=None, remarks=None, confirmation=None, dry_run=None
) -> CancelAppointmentResponse:

    resp = client.get(
        "cancelAppointment",
        id=appointment_id,
        mode=mode,
        remarks=remarks,
        confirmation=confirmation,
        dryRun=dry_run,
    )

    return CancelAppointmentResponse.parse_obj(resp)


def confirm_appointment(
    appointment_id, confirmation_code
) -> ConfirmAppointmentResponse:

    resp = client.get(
        "confirmAppointment", id=appointment_id, confirmationCode=confirmation_code
    )

    return ConfirmAppointmentResponse.parse_obj(resp)


def get_appointments(
    agenda_id,
    start_date,
    end_date,
    customer_id=None,
    appointment_type_id=None,
    resource_id=None,
    include_cancelled=None,
    limit=None,
    offset=None,
) -> GetAppointmentsResponse:

    resp = client.get(
        "getAppointments",
        agendaId=agenda_id,
        startDate=start_date,
        endDate=end_date,
        customerId=customer_id,
        appointmentTypeId=appointment_type_id,
        resourceId=resource_id,
        includeCancelled=include_cancelled,
        limit=limit,
        offset=offset,
    )

    return GetAppointmentsResponse.parse_obj(resp)


def get_appointment(appointment_id) -> GetAppointmentResponse:

    resp = client.get("getAppointment", id=appointment_id)

    return GetAppointmentResponse.parse_obj(resp)


def remove_appointment(appointment_id) -> None:

    response = client.get("removeAppointment", id=appointment_id)

    return response


def set_appointment(
    agenda_id,
    start_time,
    date,
    customer_id,
    appointment_type_id,
    end_time=None,
    appointment_id=None,
    name=None,
    description=None,
    booking_mode=None,
) -> SetAppointmentSchema:

    resp = client.get(
        "setAppointment",
        Id=appointment_id,
        AgendaId=agenda_id,
        StartTime=start_time,
        Date=date,
        CustomerId=customer_id,
        AppointmentTypeId=appointment_type_id,
        EndTime=end_time,
        Name=name,
        Description=description,
        BookingMode=booking_mode,
    )

    response = SetAppointmentResponse.parse_obj(resp)

    return response.objects["Appointment"]
