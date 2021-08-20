# Copyright (c) Qotto, 2021

"""
Record abstract base class
"""

from datetime import datetime, timezone
from typing import Any, Dict, Union, Optional
from uuid import UUID, uuid4

from semver import VersionInfo
from urnparse import URN8141, InvalidURNFormatError

from .record_errors import RecordAttributeTypeError, RecordAttributeValueError

__all__ = [
    'Record',
]


class Record:
    """
    Common Record interface

    This class is a base for Event, Request, and Response. It should not be instantiated.
    """

    def __init__(
        self,
        protocol_version: str,
        schema: str,
        version: str,
        source: str,
        uuid: str = None,
        correlation_id: str = None,
        partition_key: str = None,
        date: datetime = None,
        context: Dict[str, Dict[str, Any]] = None,
        data: Dict[str, Any] = None

    ) -> None:
        """
        Initialize Record attributes

        :param protocol_version: SemVer version of the Eventy protocol
        :param schema: URN of the record schema
        :param version: SemVer version of the record schema
        :param source: URN of the record emitter
        :param uuid: UUID v4 of the record. Default: auto-generated
        :param correlation_id: Trace / correlation ID for trace_id. Default: auto-generated
        :param partition_key: Partition or database key. Default: None
        :param date: Date of the event. Default: now
        :param context: Keys should be URN of a service using the context
        :param data: Domain data

        :raises RecordAttributeError:
        """
        self.protocol_version = protocol_version
        self.schema = schema
        self.version = version
        self.source = source
        self.uuid = uuid  # type: ignore
        self.correlation_id = correlation_id  # type: ignore
        self.partition_key = partition_key  # type: ignore
        self.date = date  # type: ignore
        self.context = context  # type: ignore
        self.data = data  # type: ignore

    @property
    def type(self) -> str:
        """
        Type of the record: EVENT | REQUEST | RESPONSE
        """
        raise NotImplementedError

    @property
    def protocol_version(self) -> str:
        """
        Eventy protocol version (SemVer)
        """
        return self._protocol_version

    @protocol_version.setter
    def protocol_version(self, protocol_version: str):
        try:
            VersionInfo.parse(protocol_version)
        except ValueError:
            raise RecordAttributeValueError('protocol_version', protocol_version, 'Not in SemVer format')
        self._protocol_version = protocol_version

    @property
    def schema(self) -> str:
        """
        Record schema (URN)
        """
        return self._schema

    @schema.setter
    def schema(self, schema: str):
        try:
            URN8141.from_string(schema)
        except InvalidURNFormatError:
            raise RecordAttributeValueError('schema', schema, 'Not in URN format')
        self._schema = schema

    @property
    def version(self) -> str:
        """
        Record schema version (SemVer)
        """
        return self._version

    @version.setter
    def version(self, version: str):
        try:
            VersionInfo.parse(version)
        except ValueError:
            raise RecordAttributeValueError('version', version, 'Not in SemVer format')
        self._version = version

    @property
    def source(self) -> str:
        """
        Record source (URN)
        """
        return self._source

    @source.setter
    def source(self, source: str):
        try:
            URN8141.from_string(source)
        except InvalidURNFormatError:
            raise RecordAttributeValueError('source', source, 'Not in URN format')
        self._source = source

    @property
    def uuid(self) -> str:
        """
        Record unique identifier (UUID v4)
        """
        return self._uuid

    @uuid.setter
    def uuid(self, uuid: str):
        if uuid is None:
            uuid = str(uuid4())
        try:
            UUID(uuid)
        except TypeError as e:
            raise RecordAttributeValueError('uuid', uuid, str(e)) from e
        except ValueError as e:
            raise RecordAttributeValueError('uuid', uuid, str(e)) from e
        self._uuid = uuid

    @property
    def correlation_id(self) -> str:
        """
        Record correlation_id to be propagated
        """
        return self._trace_id

    @correlation_id.setter
    def correlation_id(self, trace_id: str):
        if trace_id is None:
            trace_id = f'{uuid4()}:{int(datetime.now(timezone.utc).timestamp() * 1000)}'
        if isinstance(trace_id, str):
            self._trace_id = trace_id
        else:
            raise RecordAttributeTypeError('trace_id', str, trace_id)

    @property
    def partition_key(self) -> Optional[str]:
        """
        Key for partitioned states, e.g. Kafka topics partitions
        """
        return self._key

    @partition_key.setter
    def partition_key(self, key: str):
        if key is None or isinstance(key, str):
            self._key = key
        else:
            raise RecordAttributeTypeError('partition_key', str, key)

    @property
    def date(self) -> datetime:
        """
        Date of the event (unrelated to event production)
        """
        return self._date

    @date.setter
    def date(self, date: Union[datetime, int, str]):
        """
        Set the date, keeping a millisecond precision.

        :param date: record date, as a datetime, or iso str, or timestamp int
        """
        if date is None:
            date = datetime.now(timezone.utc)
        elif isinstance(date, str):
            try:
                date = datetime.fromisoformat(date)
            except Exception:
                raise RecordAttributeValueError('date', date, 'Not in iso format')
        elif isinstance(date, int):
            try:
                date = datetime.fromtimestamp(date / 1000, timezone.utc)
            except Exception:
                raise RecordAttributeValueError('date', date, 'Not a ms timestamp')

        if isinstance(date, datetime):
            ts = int(date.timestamp() * 1000) / 1000
            date = datetime.fromtimestamp(ts, timezone.utc)
            self._date = date
        else:
            raise RecordAttributeTypeError('date', datetime, date)

    @property
    def context(self) -> Dict[str, Dict[str, Any]]:
        """
        Execution context to be propagated
        """
        return self._context

    @context.setter
    def context(self, context: Dict[str, Dict[str, Any]]):
        if context is None:
            context = dict()
        if not isinstance(context, Dict):
            raise RecordAttributeTypeError('context', Dict, context)
        for key, val in context.items():
            if not isinstance(key, str):
                raise RecordAttributeTypeError(f'context key', str, key)
            if not isinstance(val, Dict):
                raise RecordAttributeTypeError(f'value for key {key}', 'Dict', val)
        self._context = context

    @property
    def data(self) -> Dict[str, Any]:
        """
        Actual record payload
        """
        return self._data

    @data.setter
    def data(self, data):
        self._data = dict()
        if data is None:
            data = dict()
        for key in data:
            if not isinstance(key, str):
                raise RecordAttributeTypeError('data key', 'str', key)
        self._data = data

    def __repr__(self):
        return f"{self.type} {self.schema} v{self.version} uuid={self.uuid} trace_id={self.correlation_id} key={self.partition_key}"

    def _debug_str(self):
        return self.__repr__() + f"\n      CONTEXT={self.context}\n      DATA={self.data}"
