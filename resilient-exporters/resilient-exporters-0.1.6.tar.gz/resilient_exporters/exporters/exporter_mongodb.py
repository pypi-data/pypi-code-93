import urllib
import logging
from typing import Text
from resilient_exporters.exporters import Exporter, ExportResult
from resilient_exporters.exceptions import MissingConfigError, \
                                           InvalidConfigError, \
                                           MissingModuleError

logger = logging.getLogger(__name__)

try:
    import pymongo
except ModuleNotFoundError:
    logger.error("""PyMongo not available. Install using:
                    pip install resilient-transmitter[mongo]""")
    raise MissingModuleError


class MongoDBExporter(Exporter):
    """Exporter for MongoDB.

    Args:
        target_ip (str):
        target_port (int):
        username (str):
        password (str):
        default_db (str):
        default_collection (str):
        **kwargs : the keyword arguments to pass down to parent class Exporter
    Raises:
        InvalidConfigError: if it cannot retrieve the server information, which
            is likely due an invalid configuration of the target.

    .. admonition:: Example

        .. code-block:: python

            import os
            from resilient_exporters.exporters import MongoDBExporter

            exporter = MongoDBExporter(target_ip="127.0.0.1",
                                       username=os.environ["MONGO_USERNAME"],
                                       password=os.environ["MONGO_PASSWORD"],
                                       default_db="profiles",
                                       default_db="scientists")

            data = {"name": "Richard Feynman",
                    "age": 69}
            exporter.send(data)
    """

    def __init__(self,
                 target_ip: Text,
                 target_port: int = 27017,
                 username: Text = None,
                 password: Text = None,
                 default_db: Text = None,
                 default_collection: Text = None,
                 **kwargs):
        super(MongoDBExporter, self).__init__(**kwargs)

        self.target_ip = target_ip
        self.target_port = target_port
        self.username = username
        self.default_db = default_db
        self.default_collection = default_collection

        if self.target_ip is None:
            logger.error("No IP address provided.")
            raise ValueError("No IP address provided")

        # Parse username and password
        if username:
            username = urllib.parse.quote_plus(self.username)
        if password:
            password = urllib.parse.quote_plus(password)

        # Create kwargs for MongoClient
        if target_port:
            kwargs["port"] = self.target_port
        if username:
            kwargs["username"] = username
        if password:
            kwargs["password"] = password

        # Create MongoClient
        self.__client = pymongo.MongoClient(self.target_ip, **kwargs)

        # Test connection
        try:
            self.__client.server_info()
        except pymongo.errors.ServerSelectionTimeoutError as e:
            logging.debug(e)
            raise InvalidConfigError(self, "Cannot retrieve server info. Is \
                                            the target valid?")

        # Keeping default database/collection if provided
        self.db = None
        if self.default_db:
            self.db = self.__client[self.default_db]
        self.collection = None
        if self.default_collection:
            self.collection = self.db[self.default_collection]

    @property
    def client(self) -> pymongo.MongoClient:
        """The MongoDB client. It cannot be replaced."""
        return self.__client

    def send(self,
             data: dict,
             db: Text = None,
             collection: Text = None) -> ExportResult:
        """Inserts data into a collection. Reuses default database and
        collection names, if provided at initialisation.

        Args:
            data (dict): a dict representing the document to insert into the
                collection.
            db (str): name of the target database. If `None`, will use the
                default value. Default is `None`.
            collection (str): name of the target colleciton. If `None`,
                will use the default value. Default is `None`.

        Returns:
            ExportResult: if successful, returns (ObjectId, True),
                          (None, False) otherwise.

        Raises:
            MissingConfigError: if it cannot find a database and/or collection
                in the arguments and default values.
        """
        data = data.copy()
        if db is None and self.db is not None:
            if collection is None and self.collection is not None:
                try:
                    self.collection.insert_one(data)
                except Exception as e:
                    logger.error(e)
                    return ExportResult(False, None)
                return ExportResult(data["_id"], True)
            elif collection is not None:
                try:
                    self.db[collection].insert_one(data)
                except Exception as e:
                    logger.error(e)
                    return ExportResult(False, None)
                return ExportResult(data["_id"], True)
            else:
                raise MissingConfigError(self, "No reference to a database \
                                          and collection found.")
        elif db is not None and collection is not None:
            try:
                self.__client[db][collection].insert_one(data)
            except Exception as e:
                logger.error(e)
                return ExportResult(None, False)
            return ExportResult(data["_id"], True)
        return ExportResult(None, False)
