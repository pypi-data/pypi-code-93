import pytest
from decouple import config


@pytest.fixture
def agenda_id():
    return config('ONLINE_AFSRPAKEN_AGENDA_ID', cast=int)


@pytest.fixture
def appointment_type_id():
    return config('ONLINE_AFSPRAKEN_APPOINTMENT_TYPE_ID', cast=int)

