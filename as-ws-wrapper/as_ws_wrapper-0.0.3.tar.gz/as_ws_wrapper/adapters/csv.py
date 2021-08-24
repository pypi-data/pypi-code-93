from csv import DictReader, DictWriter
from io import StringIO
from typing import List, Union

from pydantic import BaseModel

from ..models.base import TransactionModel


class PydanticCSVAdapter:
    """
    Adaptador

    BaseModel(pydantic) <===> csv
    """

    COMMA = ","
    SEMICOLON = ";"
    SPACE = " "
    TAB = "\t"
    PIPE = "|"
    USE_BYTES = True
    PYDANTIC_CLASS = TransactionModel

    def pydantic_to_csv(
        self,
        instances: List[BaseModel],
        pydantic_class: BaseModel.__class__ = PYDANTIC_CLASS,
        delimiter=SEMICOLON,
        use_bytes=USE_BYTES,
    ):
        instances_data = [instance.dict() for instance in instances]

        buffer = StringIO()

        writer = DictWriter(
            buffer, list(pydantic_class.__fields__.keys()), delimiter=delimiter
        )
        writer.writeheader()
        writer.writerows(instances_data)

        result = buffer.getvalue()

        if use_bytes:
            result = result.encode()

        return result

    def csv_to_pydantic(
        self,
        csv: Union[str, bytes],
        pydantic_class: BaseModel.__class__ = PYDANTIC_CLASS,
        delimiter=SEMICOLON,
        use_bytes=USE_BYTES,
    ):
        _input = csv

        if use_bytes:
            _input = _input.decode()

        buffer = StringIO(_input)
        reader = DictReader(
            buffer, list(pydantic_class.__fields__.keys()), delimiter=delimiter
        )
        instances = []
        for index, row in enumerate(reader):
            if index == 0:
                continue
            instances.append(pydantic_class(**row))
        return instances
