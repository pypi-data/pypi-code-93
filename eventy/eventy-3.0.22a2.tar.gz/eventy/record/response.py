# Copyright (c) Qotto, 2021

"""
Response record
"""

from datetime import datetime
from typing import Dict, Any, Union, Optional
from uuid import UUID, uuid4

from urnparse import URN8141, InvalidURNFormatError

from .record import Record
from .record_errors import RecordAttributeTypeError, RecordAttributeValueError

__all__ = [
    'Response',
]


class Response(Record):

    def __init__(
        self,
        protocol_version: str,
        schema: str,
        version: str,
        source: str,
        destination: str,
        request_uuid: str,
        uuid: str = None,
        ok: bool = True,
        error_code: int = None,
        error_message: str = None,
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
        :param destination: URN of the request destination
        :param request_uuid: UUID v4 of the corresponding request
        :param uuid: UUID v4 of the response. Default: auto-generated
        :param ok:
        :param error_code:
        :param error_message:
        :param correlation_id: Trace / correlation ID for trace_id. Default: auto-generated
        :param partition_key: Partition or database key. Default: None
        :param date: Date of the event. Default: now
        :param context: Keys should be URN of a service using the context
        :param data: Domain data

        :raises RecordAttributeError:
        """
        super().__init__(
            protocol_version,
            schema,
            version,
            source,
            uuid,
            correlation_id,
            partition_key,
            date,
            context,
            data,
        )
        self.destination = destination
        self.request_uuid = request_uuid
        self.ok = ok
        self.error_code = error_code
        self.error_message = error_message

    @property
    def type(self) -> str:
        return 'RESPONSE'

    @property
    def destination(self) -> str:
        return self._destination

    @destination.setter
    def destination(self, destination: str):
        try:
            URN8141.from_string(destination)
        except InvalidURNFormatError:
            raise RecordAttributeValueError('destination', destination, 'Not in URN format')
        self._destination = destination

    @property
    def request_uuid(self) -> str:
        return self._request_uuid

    @request_uuid.setter
    def request_uuid(self, request_uuid: str):
        if request_uuid is None:
            request_uuid = str(uuid4())
        try:
            UUID(request_uuid)
        except TypeError as e:
            raise RecordAttributeValueError('request_uuid', request_uuid, str(e)) from e
        except ValueError as e:
            raise RecordAttributeValueError('request_uuid', request_uuid, str(e)) from e
        self._request_uuid = request_uuid

    @property
    def ok(self) -> bool:
        return self._ok

    @ok.setter
    def ok(self, ok: Union[bool, str]):
        if isinstance(ok, bool):
            self._ok = ok
        elif isinstance(ok, str):
            if ok.lower() == 'true':
                self._ok = True
            elif ok.lower() == 'false':
                self._ok = False
            else:
                raise RecordAttributeValueError('ok', bool, ok)
        else:
            raise RecordAttributeTypeError('ok', bool, ok)

    @property
    def error_code(self) -> Optional[int]:
        return self._error_code

    @error_code.setter
    def error_code(self, error_code):
        # TODO: Check if ok is True? This would impose to update ok before error_code, but why not?
        if error_code is not None and not isinstance(error_code, int):
            raise RecordAttributeTypeError('error_code', 'int or None', error_code)
        self._error_code = error_code

    @property
    def error_message(self) -> Optional[str]:
        return self._error_message

    @error_message.setter
    def error_message(self, error_message):
        # TODO: Check if ok is True? This would impose to update ok before error_message, but why not?
        if error_message is not None and not isinstance(str, error_message):
            raise RecordAttributeTypeError('error_message', 'str or None', error_message)
        self._error_message = error_message
