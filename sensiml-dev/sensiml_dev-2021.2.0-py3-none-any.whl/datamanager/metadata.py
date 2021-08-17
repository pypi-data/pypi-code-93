from sensiml.datamanager.label import Label
from sensiml.datamanager.base import BaseSet
import logging


logger = logging.getLogger(__name__)


class Metadata(Label):
    """Base class for a label object."""

    @property
    def _label_or_metadata(self):
        return "metadata"

    @property
    def _metadata(self):
        return True


class MetadataSet(BaseSet):
    def __init__(self, connection, project, initialize_set=True):
        """Initialize a metadata object.

            Args:
                connection
                project
        """

        self._connection = connection
        self._project = project
        self._objclass = Metadata
        self._set = None
        self._attr_key = "name"
        self._data = None

        if initialize_set:
            self.refresh()

    @property
    def metadata(self):
        return self.objs

    @property
    def get_set_url(self):
        return "project/{0}/metadata/".format(self._project.uuid)

    def __str__(self):
        s = ""
        for obj in self.objs:
            s += "name: {0} uuid {1}\n".format(obj.name, obj.uuid)

        return s
