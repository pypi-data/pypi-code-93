import traceback

import logging

import sys

from django.conf import settings
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler as default_exception_handler


def exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = default_exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data = {
            "status_code": response.status_code,
            "message": exc.default_detail if hasattr(exc, "default_detail") else "",
            "more_info": response.data,
        }
    else:
        if settings.DEBUG:
            # Display raw exception if debug mode is on
            return None
        else:
            logger = logging.getLogger("django")
            exc_type, exc_value, exc_tb = sys.exc_info()
            logger.error(
                "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
            )

            # We should not return info on application internal behavior
            return Response(
                data={
                    "status_code": 500,
                    "message": "An internal error occurred.",
                    "more_info": "Contact the administrator of the application.",
                },
                status=500,
                exception=APIException(detail="An internal error occurred."),
            )

    return response
