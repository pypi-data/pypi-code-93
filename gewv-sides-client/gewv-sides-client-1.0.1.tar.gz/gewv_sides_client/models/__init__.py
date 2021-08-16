# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from gewv_sides_client.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from gewv_sides_client.model.array_of_boxes import ArrayOfBoxes
from gewv_sides_client.model.array_of_buildings import ArrayOfBuildings
from gewv_sides_client.model.array_of_contacts import ArrayOfContacts
from gewv_sides_client.model.array_of_devices import ArrayOfDevices
from gewv_sides_client.model.array_of_fieldtests import ArrayOfFieldtests
from gewv_sides_client.model.array_of_logs import ArrayOfLogs
from gewv_sides_client.model.array_of_measur_services import ArrayOfMeasurServices
from gewv_sides_client.model.array_of_readings import ArrayOfReadings
from gewv_sides_client.model.box import Box
from gewv_sides_client.model.box_all_of import BoxAllOf
from gewv_sides_client.model.box_prototype import BoxPrototype
from gewv_sides_client.model.building import Building
from gewv_sides_client.model.contact import Contact
from gewv_sides_client.model.device import Device
from gewv_sides_client.model.energy_type import EnergyType
from gewv_sides_client.model.fieldtest import Fieldtest
from gewv_sides_client.model.id import ID
from gewv_sides_client.model.inline_object import InlineObject
from gewv_sides_client.model.inline_object1 import InlineObject1
from gewv_sides_client.model.inline_object2 import InlineObject2
from gewv_sides_client.model.inline_object3 import InlineObject3
from gewv_sides_client.model.inline_object4 import InlineObject4
from gewv_sides_client.model.inline_object5 import InlineObject5
from gewv_sides_client.model.inline_object6 import InlineObject6
from gewv_sides_client.model.log import Log
from gewv_sides_client.model.log_all_of import LogAllOf
from gewv_sides_client.model.log_level import LogLevel
from gewv_sides_client.model.log_prototype import LogPrototype
from gewv_sides_client.model.measur_service import MeasurService
from gewv_sides_client.model.measur_service_all_of import MeasurServiceAllOf
from gewv_sides_client.model.measur_service_prototype import MeasurServicePrototype
from gewv_sides_client.model.measur_service_prototype_all_of import MeasurServicePrototypeAllOf
from gewv_sides_client.model.measur_service_update import MeasurServiceUpdate
from gewv_sides_client.model.reading import Reading
from gewv_sides_client.model.service_state import ServiceState
from gewv_sides_client.model.service_type import ServiceType
from gewv_sides_client.model.user import User
