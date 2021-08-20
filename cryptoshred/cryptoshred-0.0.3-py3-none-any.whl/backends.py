from typing import Any, Tuple
from functools import lru_cache
from uuid import UUID, uuid4
import boto3
from boto3.dynamodb.conditions import Key
import logging
from secrets import token_bytes

from cryptoshred.exceptions import KeyNotFoundException


class KeyBackend:
    """
    The base class for KeyBackends this exists for typing and documentation purposes
    """

    def get_key(self, id: UUID) -> Tuple[UUID, bytes]:
        """
        For a given key id returns the id and the key.

        Args:
            id (UUID4): The id of the subject for which to get the key

        Returns:
            The id and the corresponding key

        Raises:
            KeyNotFoundException: If there is no key for the given UUID
        """
        raise NotImplementedError()

    def get_iv(self) -> bytes:
        """
        Returns the initialization vector.

        Returns:
            The initialization vector
        """
        raise NotImplementedError()

    def generate_key(self) -> UUID:
        """
        Used to generate a new cryptoshredding key. Will return the id of the key.

        Returns:
            The id of the newly generated key
        """
        raise NotImplementedError()


class DynamoDbSsmBackend(KeyBackend):
    """
    An implementation of the key backend interface using AWS DynamoDb as
    key persistence layer. The initialization vector is stored in AWS SSM PS.

    Args:
        iv_param (str): The path to the SSM parameter holding the initialization vector
        table_name (str): The name of the dynamo table to use for fetching and storing keys
        dynamo (DynamoDbResource): Optional parameter for injecting custom boto3 dynamodb resource implementations
    """

    def __init__(
        self,
        *,
        iv_param: str,
        table_name: str = "cryptoshred-keys",
        dynamo: Any = None,
    ) -> None:
        if not dynamo:
            dynamo = boto3.resource("dynamodb")
        self._dynamo = dynamo
        self._table = self._dynamo.Table(table_name)
        self._log = logging.getLogger(self.__class__.__name__)
        self._iv = DynamoDbSsmBackend.fetch_iv(iv_param)

    @staticmethod
    def fetch_iv(param: str) -> bytes:
        ssm = boto3.client("ssm")
        return bytes(ssm.get_parameter(Name=param)["Parameter"]["Value"], "utf-8")

    @lru_cache(
        maxsize=1000, typed=True
    )  # maxsize chosen at random. Might need adjustment
    def get_key(self, id: UUID) -> Tuple[UUID, bytes]:
        response = self._table.query(
            KeyConditionExpression=Key("subjectId").eq(str(id))
        )
        results = response["Items"]

        if len(results) == 0:
            raise KeyNotFoundException()

        if len(results) > 1:
            # This is extremely defensive as it actually CAN NOT happen given how
            # DynamoDB works today. It either overwrites based on key or it rejects the insert.
            raise ValueError("Multiple Keys for Subject.")

        key = results[0]["AES256"].value  # See https://github.com/boto/boto3/issues/846

        return (id, key)

    def get_iv(self) -> bytes:
        return self._iv

    def generate_key(self) -> UUID:
        sid = uuid4()
        return self._generate_key(sid)[0]

    def _generate_key(self, id: UUID) -> Tuple[UUID, bytes]:
        key = token_bytes(32)
        item = {"subjectId": str(id), "AES256": key}
        self._table.put_item(Item=item)

        return (id, key)
