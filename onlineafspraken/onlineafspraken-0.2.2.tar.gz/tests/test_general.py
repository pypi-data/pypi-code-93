import respx

from onlineafspraken.api import general
from onlineafspraken.schema.general import (
    AppointmentTypeSchema,
    AgendaSchema,
    ResourceSchema,
)
from tests.utils import mock_request


def test_get_agendas_200():
    mock_request("getAgendas")

    response = general.get_agendas()

    assert isinstance(response, list)
    assert isinstance(response[0], AgendaSchema)
    assert len(response) == 3
    assert response[0].name == "Test 1"


@respx.mock
def test_get_agenda(agenda_id):
    mock_request("getAgenda")

    response = general.get_agenda(agenda_id=agenda_id)
    assert isinstance(response, AgendaSchema)
    assert response.id == 270
    assert response.name is None


@respx.mock
def test_get_appointment_types():
    mock_request("getAppointmentType")

    result = general.get_appointment_types()
    assert isinstance(result, list)
    assert isinstance(result[0], AppointmentTypeSchema)

    mock_request("getAppointmentType")

    result = general.get_appointment_type(result[0].id)

    assert isinstance(result, AppointmentTypeSchema)


@respx.mock
def test_get_resources():
    mock_request("getResources")

    response = general.get_resources()
    assert isinstance(response, list)
    assert isinstance(response[0], ResourceSchema)

    mock_request("getResource")

    response = general.get_resource(response[0].id)
    assert isinstance(response, ResourceSchema)
