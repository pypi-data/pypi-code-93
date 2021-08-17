import json
from numpy import float64, int64
import sensiml.base.utility as utility
import logging
import time
from sensiml.datamanager.base import Base, BaseSet
from sensiml.datamanager.labelvalue import LabelValue


logger = logging.getLogger(__name__)


class MetadataValue(LabelValue):
    """Base class for a label object."""

    def __init__(self, connection, project, metadata):
        """Initialize a metadata object.

            Args:
                connection
                project
                label
        """

        if not metadata._metadata:
            raise Exception("Must be metadta not label")

        self._uuid = ""
        self._value = ""
        self._last_modified = ""
        self._created_at = ""
        self._connection = connection
        self._project = project
        self._label = metadata


class MetadataValueSet(BaseSet):
    def __init__(self, connection, project, metadata, initialize_set=True):
        """Initialize a metadata object.

            Args:
                connection
                project
        """
        self._connection = connection
        self._project = project
        self._metadata = metadata
        self._set = None
        self._objclass = MetadataValue
        self._attr_key = "value"

        if initialize_set:
            self.refresh()

    @property
    def metadata_values(self):
        return self.objs

    @property
    def get_set_url(self):
        return "project/{0}/{1}/{2}/labelvalue/".format(
            self._project.uuid, self._metadata._label_or_metadata, self._metadata.uuid
        )

    def _new_obj_from_dict(self, data):
        """Creates a new label from data in the dictionary.

            Args:
                data (dict): contains label_value properties value, uuid

            Returns:
                label object

        """

        obj = self._objclass(self._connection, self._project, self._metadata)
        obj.initialize_from_dict(data)
        return obj

    def __str__(self):
        s = ""
        if self._set:
            metadata = self._set[0]._label
            s = "METADATA\n"
            s += "\tname: " + str(metadata.name) + " uuid: " + str(metadata.uuid) + "\n"
            s += "METADATA VALUES\n"
            for mdv in self._set:
                s += "\tvalue: " + str(mdv.value) + " uuid:" + str(mdv.uuid) + "\n"

        return s
