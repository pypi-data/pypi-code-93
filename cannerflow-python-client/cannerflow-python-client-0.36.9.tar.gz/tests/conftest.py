from cannerflow.client import Client
import pytest
import cannerflow
from uuid import uuid4
from .config import TestConfig
from faker import Faker
from logging import getLogger
from cannerflow.payloads import DeleteFilesPayload

logger = getLogger("conftest")


# case one, secret-based client
secret_client = cannerflow.client.bootstrap(
    endpoint=TestConfig.ENDPOINT,
    workspace_id=TestConfig.WORKSPACE_ID,
    headers={
        "X-CANNERFLOW-SECRET": TestConfig.JUPYTER_SECRET,
        "X-CANNERFLOW-WORKSPACE-ID": TestConfig.WORKSPACE_ID,
    },
)

# case two, token-based client
token_client = cannerflow.client.bootstrap(
    endpoint=TestConfig.ENDPOINT,
    workspace_id=TestConfig.WORKSPACE_ID,
    token=TestConfig.PERSONAL_ACCESS_TOKEN,
)


@pytest.fixture(scope="session", params=[secret_client, token_client])
def cannerflow_client(request):
    return request.param


# This is a general function which used by fixture below clean temporary files
def file_cleaner(cannerflow_client: Client, filename: str):
    ### delete file
    cannerflow_client.delete_file(filename)
    logger.info(f"tested temp file '{filename}' delete ...OK!!")


@pytest.fixture(scope="function")
def csv_filename(cannerflow_client: Client):
    fake = Faker()
    filename = fake.file_name(extension="csv")
    filename = f"{str(uuid4())[:8]}-{filename}"
    logger.info(f"csv filename = {filename}")
    yield filename
    ### delete file
    file_cleaner(cannerflow_client, filename)


@pytest.fixture(scope="function")
def json_filename(cannerflow_client: Client):
    fake = Faker()
    filename = fake.file_name(extension="json")
    filename = f"{str(uuid4())[:8]}-{filename}"
    logger.info(f"json filename = {filename}")
    yield filename
    ### delete file
    file_cleaner(cannerflow_client, filename)


@pytest.fixture(scope="function")
def binary_filename(cannerflow_client: Client):
    fake = Faker()
    filename = fake.file_name(extension="bin")
    filename = f"{str(uuid4())[:8]}-{filename}"
    logger.info(f"bin filename = {filename}")
    yield filename
    ### delete file
    file_cleaner(cannerflow_client, filename)


@pytest.fixture(scope="function")
def png_filename(cannerflow_client: Client):
    fake = Faker()
    filename = fake.file_name(extension="png")
    filename = f"{str(uuid4())[:8]}-{filename}"
    logger.info(f"image png filename = {filename}")
    yield filename
    ### delete file
    file_cleaner(cannerflow_client, filename)
