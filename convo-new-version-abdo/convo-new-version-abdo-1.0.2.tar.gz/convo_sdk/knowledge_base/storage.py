import json
import logging
import os
import random
from typing import DefaultDict, Text, Callable, Dict, List, Any, Optional, cast
from collections import defaultdict

from convo_sdk import utils

log = logging.getLogger(__name__)


class RootKnowledge:
    def __init__(self) -> None:

        self.ordinal_mention_mapping = {
            "1": lambda l: l[0],
            "2": lambda l: l[1],
            "3": lambda l: l[2],
            "4": lambda l: l[3],
            "5": lambda l: l[4],
            "6": lambda l: l[5],
            "7": lambda l: l[6],
            "8": lambda l: l[7],
            "9": lambda l: l[8],
            "10": lambda l: l[9],
            "ANY": lambda l: random.choice(l),
            "LAST": lambda l: l[-1],
        }

        self.key_attribute: DefaultDict[Text, Text] = defaultdict(lambda: "id")
        self.representation_function: DefaultDict[
            Text, Callable[[Dict[Text, Text]], Text]
        ] = defaultdict(lambda: lambda obj: obj["name"])

    async def get_attrs_of_obj(self, object_type: Text) -> List[Text]:
        """
        Returns a list of all attributes that belong to the provided object type.

        Args:
            object_type: the object type

        Returns: list of attributes of object_type
        """
        raise NotImplementedError("Method is not implemented.")

    async def get_key_attr_of_obj(self, object_type: Text) -> Text:
        """
        Returns the key attribute for the given object type.

        Args:
            object_type: the object type

        Returns: key attribute
        """
        return self.key_attribute[object_type]

    async def get_representation_func_of_obj(
        self, object_type: Text
    ) -> Callable:
        """
        Returns a lamdba function that takes the object and returns a string
        representation of it.

        Args:
            object_type: the object type

        Returns: lamdba function
        """
        return self.representation_function[object_type]

    def put_ordinal_mention_mapping(self, mapping: Dict[Text, Callable]) -> None:
        """
        Overwrites the default ordinal mention mapping. E.g. the mapping that
        maps, for example, "first one" to the first element in a list.

        Args:
            mapping: the ordinal mention mapping
        """
        self.ordinal_mention_mapping = mapping

    async def get_objs(
        self, object_type: Text, attributes: List[Dict[Text, Text]], limit: int = 5
    ) -> List[Dict[Text, Any]]:
        """
        Query the knowledge base for objects of the given type. Restrict the objects
        by the provided attributes, if any attributes are given.

        Args:
            object_type: the object type
            attributes: list of attributes
            limit: maximum number of objects to return

        Returns: list of objects
        """
        raise NotImplementedError("Method is not implemented.")

    async def get_obj(
        self, object_type: Text, object_identifier: Text
    ) -> Optional[Dict[Text, Any]]:
        """
        Returns the object of the given type that matches the given object identifier.

        Args:
            object_type: the object type
            object_identifier: value of the key attribute or the string
            representation of the object

        Returns: the object of interest
        """
        raise NotImplementedError("Method is not implemented.")


class InMemoryRootKnowledge(RootKnowledge):
    def __init__(self, data_file: Text) -> None:
        """
        Initialize the in-memory knowledge base.
        Loads the data from the given data file into memory.

        Args:
            data_file: the path to the file containing the data
        """
        self.data_file = data_file
        self.data: Dict[Text, Any] = {}
        self.loading()
        super().__init__()

    def loading(self) -> None:
        """
        Load the data from the given file and initialize an in-memory knowledge base.
        """
        try:
            with open(self.data_file, encoding="utf-8") as f:
                matter = f.read()
        except OSError:
            raise ValueError(f"File '{self.data_file}' does not exist.")

        try:
            self.data = json.loads(matter)
        except ValueError as e:
            raise ValueError(
                f"Failed to read json from '{os.path.abspath(self.data_file)}'. Error: {e}"
            )

    def set_representation_func_of_obj(
        self, object_type: Text, representation_function: Callable
    ) -> None:
        """
        Set the representation function of the given object type.

        Args:
            object_type: the object type
            representation_function: the representation function
        """
        self.representation_function[object_type] = representation_function

    def set_key_attr_of_obj(
        self, object_type: Text, key_attribute: Text
    ) -> None:
        """
        Set the key attribute of the given object type.

        Args:
            object_type: the object type
            key_attribute: the name of the key attribute
        """
        self.key_attribute[object_type] = key_attribute

    async def get_attrs_of_obj(self, object_type: Text) -> List[Text]:
        if object_type not in self.data or not self.data[object_type]:
            return []

        first_object = self.data[object_type][0]

        return list(first_object.keys())

    async def get_objs(
        self, object_type: Text, attributes: List[Dict[Text, Text]], limit: int = 5
    ) -> List[Dict[Text, Any]]:
        if object_type not in self.data:
            return []

        objs = self.data[object_type]

        # filter objs by attributes
        if attributes:
            objs = list(
                filter(
                    lambda obj: [
                        obj[a["name"]] == a["value"] for a in attributes
                    ].count(False)
                    == 0,
                    objs,
                )
            )

        random.shuffle(objs)

        return objs[:limit]

    async def get_obj(
        self, object_type: Text, object_identifier: Text
    ) -> Optional[Dict[Text, Any]]:
        if object_type not in self.data:
            return None

        objs = self.data[object_type]

        if utils.co_routine_action_check(self.get_key_attr_of_obj):
            key_attr = await self.get_key_attr_of_obj(object_type)
        else:
            # see https://github.com/python/mypy/issues/5206
            key_attr = cast(Text, self.get_key_attr_of_obj(object_type))

        # filter the objs by its key attribute, for example, 'id'
        interested_obj = list(
            filter(
                lambda obj: str(obj[key_attr]).lower()
                == str(object_identifier).lower(),
                objs,
            )
        )

        # if the object was referred to directly, we need to compare the representation
        # of each object with the given object identifier
        if not interested_obj:
            if utils.co_routine_action_check(self.get_representation_func_of_obj):
                repr_func = await self.get_representation_func_of_obj(
                    object_type
                )
            else:
                # see https://github.com/python/mypy/issues/5206
                repr_func = cast(
                    Callable, self.get_representation_func_of_obj(object_type)
                )

            interested_obj = list(
                filter(
                    lambda obj: str(object_identifier).lower()
                    in str(repr_func(obj)).lower(),
                    objs,
                )
            )

        if not interested_obj or len(interested_obj) > 1:
            # TODO:
            #  if multiple objs are found, the objs could be shown
            #  to the user. the user then needs to clarify what object he meant.
            return None

        return interested_obj[0]
