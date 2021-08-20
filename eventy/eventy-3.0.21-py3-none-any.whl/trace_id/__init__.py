# Copyright (c) Qotto, 2021

"""
Include support for context bound trace ids

* :obj:`correlation_id_var` a Correlation ID to correlate multiple services
  involved in the same business operation
* :obj:`request_id_var` a Request ID to identify a single request on a service

Include support to generate trace ids

* :obj:`generator.gen_trace_id` trace id generator from a function
"""

from contextvars import ContextVar

__all__ = [
    'correlation_id_var',
    'request_id_var',
]

correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')
"""
correlation_id context variable

>>> from eventy.trace_id import correlation_id_var
>>> correlation_id_var.set('my_operation_using_many_services')
>>> print(correlation_id_var.get())
'my_operation_using_many_services'
"""

request_id_var: ContextVar[str] = ContextVar('request_id', default='')
"""
request_id trace context variable

>>> from eventy.trace_id import request_id_var
>>> request_id_var.set('my_service_request')
>>> print(request_id_var.get())
'my_service_request'
"""
