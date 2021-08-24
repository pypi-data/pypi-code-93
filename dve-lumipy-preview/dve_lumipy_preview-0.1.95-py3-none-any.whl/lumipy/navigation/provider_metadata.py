from lumipy.common.lockable import Lockable
from lumipy.common.string_utils import handle_available_string, connector, indent_str, prettify_tree
from lumipy.navigation.field_metadata import FieldMetadata
from lumipy.query.expression.sql_value_type import SqlValType
from lumipy.client import Client
from typing import List
from datetime import datetime


class ProviderMetadata(Lockable):
    """Represents information that defines a Luminesce provider such as its fields and metadata.

    Attributes:
        A dynamic set depending on the provider. Each provider field (column/parameter) will present as an associated
        FieldDefinition attribute on the ProviderDefinition instance.
        All public attributes on this class correspond to provider fields.
        Provider metadata attributes are internal and are accessed via get_*() methods to avoid naming conflicts.
    """

    def __init__(
            self, table_name: str, description: str, provider_type: str,
            category: str, last_ping_at: datetime, documentation: str,
            fields: List[FieldMetadata], client: Client
    ):
        """__init__ method of the ProviderDefinition class.

        Args:
            table_name (str): name of the provider.
            description (str): string containing description of provider.
            provider_type (str): type of the provider (data provider or direct provider)
            category (str): category of the provider (e.g. System, Logs, Lusid etc.)
            last_ping_at (datetime): datetime of last ping from provider.
            documentation (str): string containing the documentation url of the provider.
            fields List[FieldDefinition]: list of field definitions that belong to this provider.
            client (Client): Luminese WebApi client. To be passed to ProviderClassFactory when make_class() is called.
        """
        self._client = client

        self._table_name = table_name
        self._name = table_name.replace('.', '_').lower()
        self._description = handle_available_string(description)
        self._provider_type = provider_type
        self._category = category
        self._last_ping_at = last_ping_at
        self._documentation = handle_available_string(documentation)

        for field in fields:
            self.__dict__[field.get_name()] = field

        super().__init__()

    def list_fields(self) -> List[FieldMetadata]:
        """List all fields definitions belonging to provider.

        Returns:
            List[FieldMetadata]: list of all field definitions on provider definition.

        """
        return [v for _, v in self.__dict__.items() if isinstance(v, FieldMetadata)]

    def list_columns(self) -> List[FieldMetadata]:
        """List all provider column definitions.

        Returns:
            List[FieldMetadata]: list of all field definitions on this object that are columns.

        """
        return [v for v in self.list_fields() if v.field_type == 'Column']

    def list_parameters(self) -> List[FieldMetadata]:
        """List all provider parameter definitions.

        Returns:
            List[FieldMetadata]: list of all field definitions on this object that are parameters.

        """
        return [v for v in self.list_fields() if v.field_type == 'Parameter']

    def __str__(self, mini_str: bool = False) -> str:
        """Conversion to string method.

        Args:
            mini_str (bool): whether to include the fields when creating a string representation of the provider def.
            Defaults to False.
        Returns:
            str: string representation of the provider definition.
        """
        header = f'{connector}Provider Definition: {self._name}'

        attribute_strings = [
            f"{connector}Table SQL Name: {self._table_name}",
            f"{connector}Type: {self._provider_type}",
            f"{connector}Category: {self._category}",
            f"{connector}Description: {self._description}",
            f"{connector}Documentation: {self._documentation}",
            f"{connector}Last Ping At: {self._last_ping_at}",
        ]

        if not mini_str:
            fields_str = f"{connector}Fields:\n"
            fields_str += indent_str(
                '\n'.join(
                    [f"{connector}{k:30s} {v.field_type:10s}  {v.data_type.name:10s}"
                     for k, v in self.__dict__.items()
                     if isinstance(v, FieldMetadata)]
                ),
                n=3
            )
            attribute_strings += [fields_str]

        else:
            attribute_strings.append(" "*25)

        out_str = header + '\n' + indent_str(
            "\n".join(attribute_strings)
        )
        return prettify_tree(out_str)

    def __repr__(self) -> str:
        return str(self)

    def get_client(self) -> Client:
        """Retrieve web api client that's pointing to the grid that the provider is accessed from.

        Returns:
            Client: luminesce web api client
        """
        return self._client

    def get_name(self):
        """Get the pythonic name of the provider

        Returns:
            str: pythonic provider name
        """
        return self._name

    def get_table_name(self):
        """Original Luminesce-format provider name

        Returns:
            str: original provider name.
        """
        return self._table_name

    # noinspection PyMethodMayBeStatic
    def get_type(self):
        return SqlValType.Table

    def get_description(self):
        return self._description
