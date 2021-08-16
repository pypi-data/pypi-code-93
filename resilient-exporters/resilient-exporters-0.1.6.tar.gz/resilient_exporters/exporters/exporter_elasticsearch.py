import logging
from typing import Optional, Text, Iterable
from resilient_exporters.exporters import Exporter, ExportResult
from resilient_exporters.exceptions import MissingModuleError, \
                                           MissingConfigError, \
                                           InvalidConfigError

logger = logging.getLogger(__name__)

try:
    import elasticsearch
except ModuleNotFoundError:
    logger.error("""Elasticsearch not available. Install using:
                    pip install resilient-transmitter[elastic]""")
    raise MissingModuleError


class ElasticSearchExporter(Exporter):
    """Exporter for ElasticSearch.

    Args:
        target_ip (str): an IP address of a ElasticSearch server.
        target_port (int): the port to connect to. Default to 9300.
        username (str): the username for authentication.
        password (str): the password as plain text for authentication.
                        Use an environement variable for security.
        cluster_hosts (Iterable[Text]): cluster of hosts, passed to ES's client
                        application.
        cloud_id (str): cloud id used to connect to a Elastic Cloud server.
                        A username and password is most likely required to be
                        able to connect.
        api_key (str): a base64 encoded token to authenticate to an
                       ElasticSearchserver.
        sniff_on_start (bool): see Elasticsearch documentation.
        default_index (str): a default index to use when ``send`` is called. If
                        None, an index will have to be provided as an argument
                        when calling ``send``.
        **kwargs : the keyword arguments to pass down to parent class Exporter

    .. admonition:: Warning

        If ``target_ip`` is provided, it will supercede ``cluster_hosts``.
    """

    def __init__(self,
                 target_ip: Text = None,
                 target_port: int = 9300,
                 username: Text = None,
                 password: Text = None,
                 cluster_hosts: Iterable[Text] = None,
                 cloud_id: Text = None,
                 api_key: Text = None,  # base 64 encoded token
                 sniff_on_start: bool = True,
                 default_index: Optional[Text] = None,
                 use_ssl: bool = False,
                 ssl_certfile: Text = None,
                 ssl_ca_certs: Text = None,
                 **kwargs):
        super(ElasticSearchExporter, self).__init__(**kwargs)

        self.target_ip = target_ip
        self.target_port = target_port
        self.cluster_hosts = cluster_hosts
        self.cloud_id = cloud_id
        self.api_key = api_key
        self.sniff_on_start = sniff_on_start
        self.default_index = default_index
        self.use_ssl = use_ssl
        self.ssl_certfile = ssl_certfile
        self.ssl_ca_certs = ssl_ca_certs

        # Need to provide an address
        if self.target_ip is None \
           and self.cluster_hosts is None \
           and self.cloud_id is None:
            logger.error("No target address provided.")
            raise ValueError

        kwargs = {}
        if username and password:
            kwargs["http_auth"] = (username, password)
            #kwargs["scheme"] = "https"
        if self.cloud_id:
            kwargs["cloud_id"] = self.cloud_id
        if self.api_key:
            kwargs["api_key"] = self.api_key
        if self.sniff_on_start:
            kwargs["sniff_on_start"] = self.sniff_on_start
        if self.use_ssl:
            kwargs["use_ssl"] = self.use_ssl
        if self.ssl_certfile:
            kwargs["client_cert"] = self.ssl_certfile
        if self.ssl_ca_certs:
            kwargs["ca_certs"] = self.ssl_ca_certs

        hosts = None
        if self.target_ip:
            hosts = {"host": self.target_ip}
            if self.target_port:
                hosts["port"] = self.target_port
        elif self.cluster_hosts:
            hosts = self.cluster_hosts

        if hosts:
            self.__client = elasticsearch.Elasticsearch(hosts, **kwargs)
        else:
            self.__client = elasticsearch.Elasticsearch(**kwargs)

    @property
    def client(self) -> elasticsearch.Elasticsearch:
        """The Elasticsearch client. It cannot be replaced."""
        return self.__client

    def send(self, data: dict, index: Optional[Text] = None) -> ExportResult:
        """Indexes the data into an ElasicSearch index.

        Args:
            data (dict): the data, as a dict, to index.
            index (str): the index name. If `None`, it uses the default value
                provided at initialisation.

        Returns:
            ExportResult: (Object, True) if successful, (None, False) otherwise

        Raises:
            MissingConfigError: if no index is found.
            InvalidConfigError: if cannot send data because of a configuration
                issue (authentication or other type of issues).
        """
        if index is None:
            index = self.default_index
        if index is None:
            raise MissingConfigError(self, "No index found.")
        try:
            res = self.__client.index(index=index, body=data)
            return ExportResult(res, True)
        except elasticsearch.exceptions.ConnectionError:
            logger.warning("elasticsearch.exceptions.ConnectionError")
        except elasticsearch.exceptions.RequestError:
            logger.error("elasticsearch.exceptions.RequestError")
            raise InvalidConfigError(self,
                                     "elasticsearch.exceptions.RequestError")
        return ExportResult(None, False)
