import os
# from azure.storage.blob import BlobServiceClient
# def compress_json(json_data):
#     return zlib.compress(bytearray(json.dumps(json_data), 'utf-8'))

# def decompress_json(str):
#     return zlib.decompress(json.loads(str))

# from dotenv import load_dotenv
# load_dotenv("env/.env-dev")

# def _get_service_client():
#     connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
#     if connect_str is None:
#         raise Exception("Connection string not found in env AZURE_STORAGE_CONNECTION_STRING")
#     return BlobServiceClient.from_connection_string(connect_str)

def get_mlmd_store():
    from ml_metadata import metadata_store
    from ml_metadata.proto import metadata_store_pb2
    connection_config = metadata_store_pb2.ConnectionConfig()
    connection_config.mysql.host = os.environ["MLMD_HOST"]
    connection_config.mysql.port = int(os.environ["MLMD_PORT"])
    connection_config.mysql.database = os.environ["MLMD_DB"]
    connection_config.mysql.user = os.environ["MLMD_USER"]
    connection_config.mysql.password = os.environ["MLMD_PASSWORD"]
    return metadata_store.MetadataStore(connection_config)