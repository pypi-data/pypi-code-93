import typing
from typing import Text, Callable, Dict, List, Any, Optional, cast

from convo_sdk import Action
from convo_sdk.events import SlotSet
from convo_sdk.knowledge_base.utils import (
    OBJ_TYPE_SLOT,
    SLOT_LATEST_OBJ_TYPE,
    SLOT_ATTR,
    reset_attr_slots,
    MENTION_SLOT,
    SLOT_LATEST_OBJ,
    SLOT_LISTED_OBJS,
    fetch_obj_name,
    get_attr_slots,
)
from convo_sdk import utils
from convo_sdk.executor import CollectingDispatcher
from convo_sdk.interfaces import Tracker
from convo_sdk.knowledge_base.storage import RootKnowledge

if typing.TYPE_CHECKING:  # pragma: no cover
    from convo_sdk.types import DomainDictionary


class ActQueryKnowledgeBase(Action):
    """
    Action that queries the knowledge base for objects and attributes of an object.
    The action needs to be inherited and the knowledge base needs to be set.
    In order to actually query the knowledge base you need to:
    - create your knowledge base
    - add mandatory slots to the domain file: 'object_type', 'attribute', 'mention'
    - create NLU data where the required objects are annotated
    - create a story that includes this action
    - add the intent and action to domain file
    """

    def __init__(
        self, knowledge_base: RootKnowledge, use_last_object_mention: bool = True
    ) -> None:
        self.knowledge_base = knowledge_base
        self.use_last_object_mention = use_last_object_mention

    def name(self) -> Text:
        return "action_query_knowledge_base"

    def utter_attr_val(
        self,
        dispatcher: CollectingDispatcher,
        object_name: Text,
        attribute_name: Text,
        attribute_value: Text,
    ):
        """
        Utters a response that informs the user about the attribute value of the
        attribute of interest.

        Args:
            dispatcher: the dispatcher
            object_name: the name of the object
            attribute_name: the name of the attribute
            attribute_value: the value of the attribute
        """
        if attribute_value:
            dispatcher.utter_message(
                text=f"'{object_name}' has the value '{attribute_value}' for attribute '{attribute_name}'."
            )
        else:
            dispatcher.utter_message(
                text=f"Did not find a valid value for attribute '{attribute_name}' for object '{object_name}'."
            )

    async def utter_objs(
        self,
        dispatcher: CollectingDispatcher,
        object_type: Text,
        objects: List[Dict[Text, Any]],
    ):
        """
        Utters a response to the user that lists all found objects.

        Args:
            dispatcher: the dispatcher
            object_type: the object type
            objects: the list of objects
        """
        if objects:
            dispatcher.utter_message(
                text=f"Found the following objects of type '{object_type}':"
            )

            if utils.co_routine_action_check(
                self.knowledge_base.get_representation_func_of_obj
            ):
                repr_func = (
                    await self.knowledge_base.get_representation_func_of_obj(
                        object_type
                    )
                )
            else:
                # see https://github.com/python/mypy/issues/5206
                repr_func = cast(
                    Callable,
                    self.knowledge_base.get_representation_func_of_obj(
                        object_type
                    ),
                )

            for i, obj in enumerate(objects, 1):
                dispatcher.utter_message(text=f"{i}: {repr_func(obj)}")
        else:
            dispatcher.utter_message(
                text=f"I could not find any objects of type '{object_type}'."
            )

    async def execute(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: "DomainDictionary",
    ) -> List[Dict[Text, Any]]:
        """
        Executes this action. If the user ask a question about an attr,
        the knowledge base is queried for that attr. Otherwise, if no
        attr was detected in the request or the user is talking about a new
        object type, multiple objects of the requested type are returned from the
        knowledge base.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker
            domain: the domain

        Returns: list of slots

        """
        obj_type = tracker.get_slot(OBJ_TYPE_SLOT)
        latest_obj_type = tracker.get_slot(SLOT_LATEST_OBJ_TYPE)
        attr = tracker.get_slot(SLOT_ATTR)

        new_req = obj_type != latest_obj_type

        if not obj_type:
            # object type always needs to be set as this is needed to query the
            # knowledge base
            dispatcher.utter_message(template="utter_ask_rephrase")
            return []

        if not attr or new_req:
            return await self._query_objs(dispatcher, obj_type, tracker)
        elif attr:
            return await self._query_attr(
                dispatcher, obj_type, attr, tracker
            )

        dispatcher.utter_message(template="utter_ask_rephrase")
        return []

    async def _query_objs(
        self, dispatcher: CollectingDispatcher, object_type: Text, tracker: Tracker
    ) -> List[Dict]:
        """
        Queries the knowledge base for objs of the requested object type and
        outputs those to the user. The objs are filtered by any attribute the
        user mentioned in the request.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker

        Returns: list of slots
        """
        if utils.co_routine_action_check(self.knowledge_base.get_attrs_of_obj):
            obj_attrs = await self.knowledge_base.get_attrs_of_obj(
                object_type
            )
        else:
            # see https://github.com/python/mypy/issues/5206
            obj_attrs = cast(
                List[Text], self.knowledge_base.get_attrs_of_obj(object_type)
            )

        # get all set attribute slots of the object type to be able to filter the
        # list of objs
        attrs = get_attr_slots(tracker, obj_attrs)
        # query the knowledge base
        if utils.co_routine_action_check(self.knowledge_base.get_objs):
            objs = await self.knowledge_base.get_objs(object_type, attrs)
        else:
            # see https://github.com/python/mypy/issues/5206
            objs = cast(
                List[Dict[Text, Any]],
                self.knowledge_base.get_objs(object_type, attrs),
            )

        if utils.co_routine_action_check(self.utter_objs):
            await self.utter_objs(dispatcher, object_type, objs)
        else:
            self.utter_objs(dispatcher, object_type, objs)

        if not objs:
            return reset_attr_slots(tracker, obj_attrs)

        if utils.co_routine_action_check(self.knowledge_base.get_key_attr_of_obj):
            key_attr = await self.knowledge_base.get_key_attr_of_obj(
                object_type
            )
        else:
            # see https://github.com/python/mypy/issues/5206
            key_attr = cast(
                Text, self.knowledge_base.get_key_attr_of_obj(object_type)
            )

        latest_obj = None if len(objs) > 1 else objs[0][key_attr]

        fetch_slots = [
            SlotSet(OBJ_TYPE_SLOT, object_type),
            SlotSet(MENTION_SLOT, None),
            SlotSet(SLOT_ATTR, None),
            SlotSet(SLOT_LATEST_OBJ, latest_obj ),
            SlotSet(SLOT_LATEST_OBJ_TYPE, object_type),
            SlotSet(
                SLOT_LISTED_OBJS, list(map(lambda e: e[key_attr], objs))
            ),
        ]

        return fetch_slots + reset_attr_slots(tracker, obj_attrs)

    async def _query_attr(
        self,
        dispatcher: CollectingDispatcher,
        object_type: Text,
        attribute: Text,
        tracker: Tracker,
    ) -> List[Dict]:
        """
        Queries the knowledge base for the val of the requested attribute of the
        mentioned object and outputs it to the user.

        Args:
            dispatcher: the dispatcher
            tracker: the tracker

        Returns: list of slots
        """

        obj_name = fetch_obj_name(
            tracker,
            self.knowledge_base.ordinal_mention_mapping,
            self.use_last_object_mention,
        )

        if not obj_name or not attribute:
            dispatcher.utter_message(template="utter_ask_rephrase")
            return [SlotSet(MENTION_SLOT, None)]

        if utils.co_routine_action_check(self.knowledge_base.get_obj):
            interested_obj = await self.knowledge_base.get_obj(
                object_type, obj_name
            )
        else:
            # see https://github.com/python/mypy/issues/5206
            interested_obj = cast(
                Optional[Dict[Text, Any]],
                self.knowledge_base.get_obj(object_type, obj_name),
            )

        if not interested_obj or attribute not in interested_obj:
            dispatcher.utter_message(template="utter_ask_rephrase")
            return [SlotSet(MENTION_SLOT, None)]

        val = interested_obj[attribute]
        if utils.co_routine_action_check(
            self.knowledge_base.get_representation_func_of_obj
        ):
            repr_func = (
                await self.knowledge_base.get_representation_func_of_obj(
                    object_type
                )
            )
        else:
            # see https://github.com/python/mypy/issues/5206
            repr_func = cast(
                Callable,
                self.knowledge_base.get_representation_func_of_obj(object_type),
            )
        obj_view = repr_func(interested_obj)
        if utils.co_routine_action_check(self.knowledge_base.get_key_attr_of_obj):
            key_attr = await self.knowledge_base.get_key_attr_of_obj(
                object_type
            )
        else:
            # see https://github.com/python/mypy/issues/5206
            key_attr = cast(
                Text, self.knowledge_base.get_key_attr_of_obj(object_type)
            )
        obj_identifier = interested_obj[key_attr]

        if utils.co_routine_action_check(self.utter_attr_val):
            await self.utter_attr_val(
                dispatcher, obj_view, attribute, val
            )
        else:
            self.utter_attr_val(
                dispatcher, obj_view, attribute, val
            )

        fetch_slots = [
            SlotSet(OBJ_TYPE_SLOT, object_type),
            SlotSet(SLOT_ATTR, None),
            SlotSet(MENTION_SLOT, None),
            SlotSet(SLOT_LATEST_OBJ, obj_identifier),
            SlotSet(SLOT_LATEST_OBJ_TYPE, object_type),
        ]

        return fetch_slots
