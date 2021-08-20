import logging

from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import execution_context
from stackifyapm.utils.helper import is_async_span

logger = logging.getLogger("stackifyapm.instrument")


class PyMongoInstrumentation(AbstractInstrumentedModule):
    name = "pymongo"

    instrument_list = [
        ("pymongo.collection", "Collection.aggregate"),
        ("pymongo.collection", "Collection.bulk_write"),
        ("pymongo.collection", "Collection.count"),
        ("pymongo.collection", "Collection.create_index"),
        ("pymongo.collection", "Collection.create_indexes"),
        ("pymongo.collection", "Collection.delete_many"),
        ("pymongo.collection", "Collection.delete_one"),
        ("pymongo.collection", "Collection.distinct"),
        ("pymongo.collection", "Collection.drop"),
        ("pymongo.collection", "Collection.drop_index"),
        ("pymongo.collection", "Collection.drop_indexes"),
        ("pymongo.collection", "Collection.ensure_index"),
        ("pymongo.collection", "Collection.estimated_document_count"),
        ("pymongo.collection", "Collection.find"),
        ("pymongo.collection", "Collection.find_and_modify"),
        ("pymongo.collection", "Collection.find_one"),
        ("pymongo.collection", "Collection.find_one_and_delete"),
        ("pymongo.collection", "Collection.find_one_and_replace"),
        ("pymongo.collection", "Collection.find_one_and_update"),
        ("pymongo.collection", "Collection.group"),
        ("pymongo.collection", "Collection.inline_map_reduce"),
        ("pymongo.collection", "Collection.insert"),
        ("pymongo.collection", "Collection.insert_many"),
        ("pymongo.collection", "Collection.insert_one"),
        ("pymongo.collection", "Collection.map_reduce"),
        ("pymongo.collection", "Collection.reindex"),
        ("pymongo.collection", "Collection.remove"),
        ("pymongo.collection", "Collection.rename"),
        ("pymongo.collection", "Collection.replace_one"),
        ("pymongo.collection", "Collection.save"),
        ("pymongo.collection", "Collection.update"),
        ("pymongo.collection", "Collection.update_many"),
        ("pymongo.collection", "Collection.update_one"),
    ]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            cls_name, method_name = method.split(".", 1)
            collection = instance.collection
            context = {
                "CATEGORY": "MongoDB",
                "SUBCATEGORY": "Execute",
                "COMPONENT_CATEGORY": "DB Query",
                "COMPONENT_DETAIL": "Execute SQL Query",
                "PROVIDER": self.name,
                "MONGODB_COLLECTION": collection.full_name,
                "OPERATION": method_name,
            }

            nodes = instance.database.client.nodes
            if nodes:
                host, port = list(nodes)[0]
                context['URL'] = "{}:{}".format(host, port)

        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("db.mongodb.query", context, leaf=True, is_async=is_async_span()):
            return wrapped(*args, **kwargs)


class PyMongoBulkInstrumentation(AbstractInstrumentedModule):
    name = "pymongo"

    instrument_list = [("pymongo.bulk", "BulkOperationBuilder.execute")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            collection = instance._BulkOperationBuilder__bulk.collection
            context = {
                "CATEGORY": "MongoDB",
                "SUBCATEGORY": "Execute",
                "COMPONENT_CATEGORY": "DB Query",
                "COMPONENT_DETAIL": "Execute SQL Query",
                "PROVIDER": self.name,
                "MONGODB_COLLECTION": collection.full_name,
                "OPERATION": "bulk.execute",
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("db.mongodb.query", context, is_async=is_async_span()):
            return wrapped(*args, **kwargs)


class PyMongoCursorInstrumentation(AbstractInstrumentedModule):
    name = "pymongo"

    instrument_list = [("pymongo.cursor", "Cursor._refresh")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            collection = instance.collection
            context = {
                "CATEGORY": "MongoDB",
                "SUBCATEGORY": "Execute",
                "COMPONENT_CATEGORY": "DB Query",
                "COMPONENT_DETAIL": "Execute SQL Query",
                "PROVIDER": self.name,
                "MONGODB_COLLECTION": collection.full_name,
                "ROW_COUNT": instance.count(),
                "OPERATION": "cursor.refresh",
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("db.mongodb.query", context, is_async=is_async_span()) as span:
            response = wrapped(*args, **kwargs)

            try:
                if span.context and instance.address:
                    host, port = instance.address
                    span.context['URL'] = "{}:{}".format(host, port)

                    transaction = execution_context.get_transaction()
                    transaction.update_span_context(span.id, span.context)
            except Exception as e:
                logger.debug("Error while parsing response data. Error: {}.".format(e))

            return response
