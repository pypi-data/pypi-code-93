# -*- coding: utf-8 -*-

from pip_services3_commons.refer import Descriptor
from pip_services3_components.build import Factory

from pip_services3_mysql.connect.MySqlConnection import MySqlConnection


class DefaultMySqlFactory(Factory):
    """
    Creates MySql components by their descriptors.

    See: :class:`MySqlConnection <pip_services3_mysql.persistence.MySqlConnection.MySqlConnection>`, :class:`Factory <pip_services3_components.build.Factory.Factory>`
    """

    MySqlConnectionDescriptor = Descriptor("pip-services", "connection", "mysql", "*", "1.0")

    def __init__(self):
        """
        Create a new instance of the factory.
        """
        super(DefaultMySqlFactory, self).__init__()
        self.register_as_type(DefaultMySqlFactory.MySqlConnectionDescriptor, MySqlConnection)
