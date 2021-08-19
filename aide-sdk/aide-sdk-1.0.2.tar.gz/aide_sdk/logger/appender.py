import json_logging

from aide_sdk.manifests.execution_context import get_execution_context


class JsonAppender(json_logging.JSONLogFormatter):
    def _format_log_object(self, record, request_util):
        context = get_execution_context()

        json_log_object = super(JsonAppender, self) \
            ._format_log_object(record,
                                request_util)
        json_log_object.update({
            "model_name": context.model_name,
            "model_version": context.model_version,
            "execution_id": str(context.execution_uid) if context.execution_uid else ""
        })

        return json_log_object
