import os
import json
import uuid
import hashlib
import base64
import traceback

from azure.storage.queue import QueueClient
from azure.storage.blob import BlobClient
from azure.cosmosdb.table import TableService, TableBatch
from typing import List
from multiprocessing.pool import ThreadPool
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError

enough_workers_message = "There are already enough active workers"
workers_long_running = "Workers are active for too long. Going to process as well."
unhandled_exception_message = "Unhandled exception is appeared."
state_table = "workerState"
failure_table = "executionFailures"
segment_failure_table = "segmentExecutionFailures"

input_container = "input"
output_container = "output"


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


class TaskResult:
    def __init__(self, result, error_message, stack_trace, offset, request_id, state):
        self.result = result
        self.error_message = error_message
        self.stack_trace = stack_trace
        self.offset = offset
        self.request_id = request_id
        self.state = state

    @staticmethod
    def create_from_request_entity(entity):
        result, error, trace, offset, state = None, None, None, None, None
        if 'Result' in entity:
            result = entity['Result']
        if 'Error' in entity:
            error = entity['Error']
        if 'StackTrace' in entity:
            trace = entity['StackTrace']
        if 'Offset' in entity:
            offset = entity['Offset']
        if "State" in entity:
            state = entity["State"]

        request_id = "%s_%s" % (entity['PartitionKey'], entity['RowKey'])
        
        return TaskResult(result, error, trace, offset, request_id, state)

    def to_json(self):
        json_response = {"Completed": False, "RequestId": self.request_id}
        if self.result:
            json_response['Result'] = json.loads(self.result)
            json_response['Completed'] = True
        if self.error_message:
            json_response['Error'] = self.error_message
            json_response['StackTrace'] = self.stack_trace
            json_response['Completed'] = True
        if self.offset:
            json_response['Progress'] = self.offset
        if self.state and self.state == "Completed":
            json_response["Completed"] = True
        return json_response


def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


class Worker:
    def __init__(
        self, 
        worker_name, 
        create_if_not_exist=True, 
        segment_limit=200, 
        connection_string=None, 
        return_only_source=True
    ):
        if connection_string is None:
            self.connection_string = os.environ['AzureWebJobsStorage']
        else:
            self.connection_string = connection_string
        self.metadata_table_name = worker_name + "Data"
        self.queue_name = worker_name.lower()
        self.poison_queue_name = self.queue_name + "-poison"
        self.worker_name = worker_name
        self.segment_limit = segment_limit
        self.return_only_source = return_only_source

        self.table_client = TableService(connection_string=self.connection_string)
        self.queue = QueueClient.from_connection_string(conn_str=self.connection_string, queue_name=self.queue_name)
        self.poison_queue = QueueClient.from_connection_string(conn_str=self.connection_string, queue_name=self.poison_queue_name)

        if create_if_not_exist:
            try:
                self.table_client.create_table(self.metadata_table_name)
            except ResourceExistsError:
                pass
            try:
                self.queue.create_queue()
            except ResourceExistsError:
                pass
        self.pool = ThreadPool(processes=1)

    def exists(self) -> bool:
        return self.table_client.exists(self.metadata_table_name)

    def trigger_blob(self, blob_name, params=None):
        request_id = self._insert_blob_metadata(blob_name, params)
        self._enqueue(request_id)
        return request_id
    
    def trigger_blobs(self, blob_names: List[str], params=None, guid=None):
        if guid is None:
            guid = self._generate_id()
        if params is not None:
            params = json.dumps(params)
        request_ids = []
        for blobs_chunk in chunks(blob_names, 99):
            batch = TableBatch()
            for blob_name in blobs_chunk:
                guid, request_hash, request_id = self._generate_request_id(blob_name, guid)
                batch.insert_or_replace_entity({"PartitionKey": guid, "RowKey": request_hash, "BlobName": blob_name, "Params": params})
                request_ids.append(request_id)
            self.table_client.commit_batch(self.metadata_table_name, batch)

        for request_id in request_ids:
            self._enqueue(request_id)
        return request_ids

    def trigger(self, data, params):
        request_id = self._insert_request_metadata({"Data": data, "Params": params})
        self._enqueue(request_id)
        return request_id
        
    def get_result(self, request_id):
        self._process_poison_messages()
        guid, request_hash = self._decode_id(request_id)
        entity = self.table_client.get_entity(self.metadata_table_name, guid, request_hash, select="PartitionKey,RowKey,Result,Error,StackTrace,State,Offset")
        entity = self._expand_result(entity)
        return TaskResult.create_from_request_entity(entity)

    def get_results(self, guid):
        self._process_poison_messages()
        entities = list(
            self.table_client.query_entities(
                self.metadata_table_name, 
                filter="PartitionKey eq '%s'" % guid, 
                select="PartitionKey,RowKey,Result,Error,StackTrace,State,Offset"
            )
        )
        entities = [self._expand_result(e) for e in entities]
        return [TaskResult.create_from_request_entity(entity) for entity in entities]

    def _process_poison_messages(self):
        try:
            messages = self.poison_queue.receive_messages()
            for msg in messages:
                request_id = base64.decodestring(msg.content.encode()).decode()
                guid, hash = self._decode_id(request_id)
                request_entity = {
                    "PartitionKey": guid,
                    "RowKey": hash,
                    "Error": unhandled_exception_message,
                    "StackTrace": "" 
                }
                self.table_client.merge_entity(self.metadata_table_name, request_entity)
                function_failure_entity = {
                    "PartitionKey": self.worker_name, 
                    "RowKey": request_id, 
                    "FailureMessage": unhandled_exception_message, 
                    "StackTrace": ""
                }
                self.table_client.insert_or_replace_entity(failure_table, function_failure_entity)
                self.poison_queue.delete_message(msg)
        except ResourceNotFoundError:
            pass

    def _expand_result(self, entity):
        if "Result" not in entity:
            return entity

        result_value = entity['Result']
        if result_value is None:
            return entity

        if len(result_value.split("/")) == 4: # f"{self.worker_name}/Requests/{request_entity['PartitionKey']}/{request_entity['RowKey']}"
            blob = self._get_output_blob(result_value)
            result = blob.download_blob().readall().decode()
            entity["Result"] = result
        return entity

    def process_message(self, request_id, func):
        guid, request_hash = self._decode_id(request_id)
        request_entity = self.table_client.get_entity(self.metadata_table_name, guid, request_hash)
        try:
            if 'Request' in request_entity:
                self._process_request_body(request_entity, func)
            if 'BlobName' in request_entity:
                self._process_blob(request_id, request_entity, func)
        except Exception as e:
            self._record_request_failure(request_entity, e)
            self._record_failure(request_id, e)

    def _process_request_body(self, request_entity, func):
        request_body = json.loads(request_entity["Request"])
        response = func(request_body["Data"], request_body["Params"])
        blob_name = f"{self.worker_name}/Request/{request_entity['PartitionKey']}/{request_entity['RowKey']}"
        out_blob = self._get_output_blob(blob_name)
        out_blob.upload_blob(json.dumps(response), timeout=1200, overwrite=True)
        request_entity['Result'] = blob_name
        self.table_client.update_entity(self.metadata_table_name, request_entity)

    def _process_blob(self, request_id, request_entity, func):
        blob_name, params, offset, retry_count, batch_count, next_chunk = self._read_metadata(request_entity)
        try:
            if next_chunk:
                result, failures, next_chunk = self._process_next_chunk(next_chunk, blob_name, func, offset, params)
            else:
                result, failures, next_chunk = self._process_blob_by_segments(blob_name, func, params)
        except Exception as e:
            if retry_count == 3:
                raise e
            else:
                request_entity['RetryCount'] = retry_count + 1
                self.table_client.update_entity(self.metadata_table_name, request_entity)
                self._enqueue(request_id)
            return

        if failures:
            self._record_segment_failures(request_id, blob_name, failures)
            
        serialized_result = "\n".join(json.dumps(r) for r in result)
        if next_chunk:
            out_blob = self._get_output_blob("%s/%s_%d" % (self.worker_name, blob_name, batch_count))
            out_blob.upload_blob(serialized_result, timeout=1200, overwrite=True)
                
            request_entity['Offset'] = offset + len(result)
            request_entity['Batch'] = batch_count + 1
            request_entity['NextChunk'] = json.dumps(next_chunk, ensure_ascii=False)
            self.table_client.update_entity(self.metadata_table_name, request_entity)
            self._enqueue(request_id)
        else:
            out_blob = self._get_output_blob("%s/%s" % (self.worker_name, blob_name))
            if offset == 0:
                out_blob.upload_blob(serialized_result, timeout=1200, overwrite=True)
            else:     
                content = []
                for batch in range(batch_count):
                    in_blob = self._get_output_blob("%s/%s_%d" % (self.worker_name, blob_name, batch))
                    blob_content = in_blob.download_blob().readall().decode()
                    content.append(blob_content)
                content.append(serialized_result)
                out_blob.upload_blob("\n".join(content), timeout=1200, overwrite=True)
            request_entity['State'] = "Completed"
            request_entity['Offset'] = offset + len(result)
            self.table_client.update_entity(self.metadata_table_name, request_entity)

    def _get_input_blob(self, blob_name):
        return BlobClient.from_connection_string(self.connection_string, container_name=input_container, blob_name=blob_name)

    def _get_output_blob(self, blob_name):
        return BlobClient.from_connection_string(self.connection_string, container_name=output_container, blob_name=blob_name)

    def _read_metadata(self, request_entity):
        blob_name = request_entity['BlobName']
        params, offset, retry_count, batch_count, next_chunk = None, 0, 0, 0, None
        if 'Params' in request_entity:
            params = json.loads(request_entity['Params'])
        if 'Offset' in request_entity:
            offset = request_entity['Offset']
        if 'RetryCount' in request_entity:
            retry_count = request_entity['RetryCount']
        if 'Batch' in request_entity:
            batch_count = request_entity['Batch']
        if 'NextChunk' in request_entity and len(request_entity['NextChunk']) > 0:
            next_chunk = json.loads(request_entity['NextChunk'])
        return blob_name, params, offset, retry_count, batch_count, next_chunk

    def _process_blob_by_segments(self, blob_name, func, params):
        batch, result, failures = [], [], []
        in_blob = self._get_input_blob(blob_name)
        blobs_iterator = self._read_blob_by_segments(in_blob)
        for segment in blobs_iterator:
            batch.append(segment)
            if self.segment_limit is not None and len(batch) == self.segment_limit:
                result, failures = func(batch, params)
                batch = []
                break

        if len(batch) > 0: 
            # If segments in blob are less than segment_limit or there is no segment limit at all
            result, failures = func(batch, params)

        if self.segment_limit is None:
            # If there is no segment limit, then blob is processed in one batch
            return result, failures, []
            
        next_chunk = []
        for segment in blobs_iterator:
            next_chunk.append(segment)
            if len(next_chunk) == self.segment_limit:
                break

        return result, failures, next_chunk

    def _process_next_chunk(self, next_chunk, blob_name, func, offset, params):
        chunk_read_task = self.pool.apply_async(self._get_next_batch, args=(offset + len(next_chunk), blob_name)) # Start reading new chunk
        result, failures = func(next_chunk, params) # Process current chunk
        for i in range(len(failures)):
            s, e, reason = failures[i]
            failures[i] = (s + offset, e + offset, reason)
        next_chunk = chunk_read_task.get()
        return result, failures, next_chunk

    def _get_next_batch(self, offset, blob_name):
        in_blob = self._get_input_blob(blob_name)
        segment_id = -1
        next_chunk = []
        blobs_iterator = self._read_blob_by_segments(in_blob)
        for source_segment in blobs_iterator:
            segment_id += 1
            if segment_id < offset:
                continue

            next_chunk.append(source_segment)
            if len(next_chunk) == self.segment_limit:
                break
        return next_chunk

    def _record_failure(self, request_id, e: Exception):
        track = traceback.format_exc()
        function_failure_entity = {"PartitionKey": self.worker_name, "RowKey": request_id, "FailureMessage": str(e), "StackTrace": track}
        self.table_client.insert_entity(failure_table, function_failure_entity)

    def _record_segment_failures(self, request_id, blob_name, failures):
        batch, count = TableBatch(), 0
        for start, end, reason in failures:
            entity = {"PartitionKey": "%s_%s" % (self.worker_name, request_id), "RowKey": "%d_%d" % (start, end), "FailureMessage": reason, "Start": start, "End": end}
            batch.insert_or_replace_entity( entity)
            count += 1
            if count == 99:
                self.table_client.commit_batch(segment_failure_table, batch)
                batch = TableBatch()
        if count > 0:
            self.table_client.commit_batch(segment_failure_table, batch)

    def _record_request_failure(self, request_entity, e: Exception):
        trace = traceback.format_exc()
        error_message = str(e)
        request_entity['Error'] = error_message
        request_entity['StackTrace'] = trace
        self.table_client.update_entity(self.metadata_table_name, request_entity)

    def _insert_request_metadata(self, data):
        serialized_body = json.dumps(data)
        guid, request_hash, request_id = self._generate_request_id(serialized_body)
        metadata = {"PartitionKey": guid, "RowKey": request_hash, "Request": serialized_body }
        self.table_client.insert_entity(self.metadata_table_name, metadata)
        return request_id

    def _insert_blob_metadata(self, blob_name, params=None, guid=None):
        guid, request_hash, request_id = self._generate_request_id(blob_name, guid)
        metadata_entity = {"PartitionKey": guid, "RowKey": request_hash, "BlobName": blob_name}
        if params:
            metadata_entity['Params'] = json.dumps(params)
        self.table_client.insert_entity(self.metadata_table_name, metadata_entity)
        return request_id

    def _enqueue(self, request_id):
        self.queue.send_message(base64.b64encode(request_id.encode()).decode())

    @staticmethod
    def _preprocess(text):
        return text.replace("\xa0", " ").replace("&nbsp;", " ").strip()

    def _read_blob_by_segments(self, input_blob):
        blob_data = input_blob.download_blob()
        last_piece = ""
        for chunk in blob_data.chunks():
            lines = [l.strip() for l in chunk.decode().splitlines() if len(l.strip()) > 0]
            lines[0] = last_piece + lines[0]
            last_piece = lines[-1]
            for l in lines[:-1]:
                l = self._preprocess(l)
                if len(l) == 0:
                    continue
                source, target = json.loads(l)
                if self.return_only_source:
                    yield self._preprocess(source)
                else:
                    yield self._preprocess(source), self._preprocess(target)

        last_piece = self._preprocess(last_piece)
        if len(last_piece) > 0:
            source, target = json.loads(last_piece)
            if self.return_only_source:
                yield self._preprocess(source)
            else:
                yield self._preprocess(source), self._preprocess(target)

    @staticmethod
    def _generate_request_id(data, guid=None):
        if not guid:
            guid = Worker._generate_id()
        request_hash = str(hashlib.md5(data.encode()).hexdigest())
        request_id = "%s_%s" % (guid, request_hash)
        return guid, request_hash, request_id

    @staticmethod
    def _generate_id():
        return str(uuid.uuid4()).replace("-", "")
    
    @staticmethod
    def _decode_id(request_id):
        guid, request_hash = request_id.split("_")
        return guid, request_hash
