# Copyright (c) Qotto, 2021

import json
from datetime import datetime
from typing import Union, Any, Dict

from eventy.serialization import RecordSerializer, SerializationError
from eventy.serialization.serialization_errors import UnknownRecordTypeError
from eventy.record import Record, Event, Request, Response


class JsonSerializer(RecordSerializer):

    def encode(self, record: Record) -> bytes:
        record_dict: Dict[str, Any] = {
            'type': record.type,
            'protocol_version': record.protocol_version,
            'schema': record.schema,
            'version': record.version,
            'source': record.source,
            'uuid': record.uuid,
            'correlation_id': record.correlation_id,
            'partition_key': record.partition_key,
            'date_timestamp': int(record.date.timestamp() * 1000),
            'date_iso8601': record.date.isoformat(),
        }
        if isinstance(record, (Request, Response)):
            record_dict.update(
                {
                    'destination': str(record.destination),
                }
            )
        if isinstance(record, Response):
            record_dict.update(
                {
                    'request_uuid': record.request_uuid,
                    'ok': record.ok,
                    'error_code': record.error_code,
                    'error_message': record.error_message,
                }
            )
        record_dict.update(
            {
                'context': record.context,
                'data': record.data
            }
        )
        return bytes(json.dumps(record_dict), encoding='utf-8')

    def decode(self, encoded: bytes) -> Union[Event, Request, Response]:
        try:
            record_json = json.loads(encoded)
            record_type = record_json.pop('type')
            date = datetime.fromisoformat(record_json.pop('date_iso8601'))
            record_json.pop('date_timestamp')
            record_json['date'] = date
            record: Union[Event, Request, Response]
            if record_type == 'EVENT':
                record = Event(**record_json)
            elif record_type == 'REQUEST':
                record = Request(**record_json)
            elif record_type == 'RESPONSE':
                record = Response(**record_json)
            else:
                raise UnknownRecordTypeError(record_type)
            return record
        except Exception as e:
            raise SerializationError from e
