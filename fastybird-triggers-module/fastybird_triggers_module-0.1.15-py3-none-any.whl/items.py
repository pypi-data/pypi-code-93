#!/usr/bin/python3

#     Copyright 2021. FastyBird s.r.o.
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

"""
Entities cache to prevent database overloading
"""

# Library dependencies
import uuid
from abc import ABC
from typing import Dict
from devices_module.items import DevicePropertyItem, ChannelPropertyItem
from modules_metadata.triggers_module import TriggerConditionOperator
from modules_metadata.types import SwitchPayload

# Library libs
from triggers_module.utils import PropertiesUtils


class TriggerItem:
    """
    Trigger entity item

    @package        FastyBird:TriggersModule!
    @module         items

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __trigger_id: uuid.UUID

    __device_property_conditions: Dict[str, "DevicePropertyConditionItem"] = dict()
    __channel_property_conditions: Dict[str, "ChannelPropertyConditionItem"] = dict()

    __device_property_actions: Dict[str, "DevicePropertyActionItem"] = dict()
    __channel_property_actions: Dict[str, "ChannelPropertyActionItem"] = dict()

    __is_fulfilled = False
    __is_triggered = False

    # -----------------------------------------------------------------------------

    def __init__(self, trigger_id: uuid.UUID) -> None:
        self.__trigger_id = trigger_id

        self.__device_property_actions = dict()
        self.__channel_property_actions = dict()

        self.__device_property_conditions = dict()
        self.__channel_property_conditions = dict()

        self.__is_fulfilled = False
        self.__is_triggered = False

    # -----------------------------------------------------------------------------

    @property
    def trigger_id(self) -> uuid.UUID:
        """Trigger identifier"""
        return self.__trigger_id

    # -----------------------------------------------------------------------------

    @property
    def is_fulfilled(self) -> bool:
        """Flag informing that trigger conditions are fulfilled"""
        return self.__is_fulfilled

    # -----------------------------------------------------------------------------

    @property
    def is_triggered(self) -> bool:
        """Flag informing that trigger actions are triggered"""
        return self.__is_triggered

    # -----------------------------------------------------------------------------

    @property
    def actions(
        self,
    ) -> Dict[str, "DevicePropertyConditionItem" or "ChannelPropertyConditionItem"]:
        """All trigger actions"""
        return {
            **self.__device_property_actions,
            **self.__channel_property_actions,
        }

    # -----------------------------------------------------------------------------

    @property
    def conditions(
        self,
    ) -> Dict[str, "DevicePropertyConditionItem" or "ChannelPropertyConditionItem"]:
        """All trigger conditions"""
        return {
            **self.__device_property_conditions,
            **self.__channel_property_conditions,
        }

    # -----------------------------------------------------------------------------

    def add_condition(
        self,
        condition_id: str,
        condition: "DevicePropertyConditionItem" or "ChannelPropertyConditionItem",
    ) -> None:
        """Assign condition to trigger"""
        if isinstance(condition, DevicePropertyConditionItem):
            self.__device_property_conditions[condition_id] = condition

        elif isinstance(condition, ChannelPropertyConditionItem):
            self.__channel_property_conditions[condition_id] = condition

    # -----------------------------------------------------------------------------

    def add_action(
        self,
        action_id: str,
        action: "DevicePropertyActionItem" or "ChannelPropertyActionItem",
    ) -> None:
        """Assign action to trigger"""
        if isinstance(action, DevicePropertyActionItem):
            self.__device_property_actions[action_id] = action

        elif isinstance(action, ChannelPropertyActionItem):
            self.__channel_property_actions[action_id] = action

    # -----------------------------------------------------------------------------

    def check_property_item(
        self,
        item: DevicePropertyItem or ChannelPropertyItem,
        previous_value: str or None,
        actual_value: str,
    ) -> None:
        """Check property against trigger actions and conditions"""
        if isinstance(item, DevicePropertyItem):
            for condition in self.__device_property_conditions.values():
                if condition.device_property == item.key:
                    condition.validate(item, previous_value, actual_value)

            for action in self.__device_property_actions.values():
                if action.device_property == item.key:
                    action.validate(item, previous_value, actual_value)

        elif isinstance(item, ChannelPropertyItem):
            for condition in self.__channel_property_conditions.values():
                if condition.channel_property == item.key:
                    condition.validate(item, previous_value, actual_value)

            for action in self.__channel_property_actions.values():
                if action.channel_property == item.key:
                    action.validate(item, previous_value, actual_value)

        self.__check_fulfillment()
        self.__check_triggers()

    # -----------------------------------------------------------------------------

    def __check_fulfillment(self) -> None:
        """Check if all trigger conditions are fulfiller"""
        self.__is_fulfilled = True

        for condition in self.__device_property_conditions.values():
            if condition.enabled and condition.is_fulfilled is False:
                self.__is_fulfilled = False

        for condition in self.__channel_property_conditions.values():
            if condition.enabled and condition.is_fulfilled is False:
                self.__is_fulfilled = False

    # -----------------------------------------------------------------------------

    def __check_triggers(self) -> None:
        """Check if trigger has actions to be triggered"""
        self.__is_triggered = True

        for action in self.__device_property_actions.values():
            if action.enabled and action.is_triggered is False:
                self.__is_triggered = False

        for action in self.__channel_property_actions.values():
            if action.enabled and action.is_triggered is False:
                self.__is_triggered = False


class PropertyConditionItem(ABC):
    """
    Base property condition entity item

    @package        FastyBird:TriggersModule!
    @module         items

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __condition_id: uuid.UUID
    __enabled: bool

    __operator: TriggerConditionOperator
    __operand: str

    __device: str

    __is_fulfilled: bool = False

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        condition_id: uuid.UUID,
        enabled: bool,
        operator: TriggerConditionOperator,
        operand: str,
        device: str,
    ) -> None:
        self.__condition_id = condition_id
        self.__enabled = enabled

        self.__operator = operator
        self.__operand = operand

        self.__device = device

        self.__is_fulfilled = False

    # -----------------------------------------------------------------------------

    @property
    def device(self) -> str:
        """Device key"""
        return self.__device

    # -----------------------------------------------------------------------------

    @property
    def condition_id(self) -> uuid.UUID:
        """Condition identifier"""
        return self.__condition_id

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Flag informing if condition is enabled"""
        return self.__enabled

    # -----------------------------------------------------------------------------

    @property
    def operator(self) -> TriggerConditionOperator:
        """Condition operator"""
        return self.__operator

    # -----------------------------------------------------------------------------

    @property
    def operand(self) -> str:
        """Condition operand"""
        return self.__operand

    # -----------------------------------------------------------------------------

    @property
    def is_fulfilled(self) -> bool:
        """Flag informing that condition has met all conditions"""
        return self.__is_fulfilled

    # -----------------------------------------------------------------------------

    def validate(
        self,
        item: DevicePropertyItem or ChannelPropertyItem,
        previous_value: str or None,
        actual_value: str
    ) -> bool:
        """Property value validation"""
        if previous_value is not None and previous_value == actual_value:
            return False

        normalized_value = PropertiesUtils.normalize_value(item, actual_value)
        normalized_operand = PropertiesUtils.normalize_value(item, self.operand)

        # Reset actual status
        self.__is_fulfilled = False

        if self.__operator == TriggerConditionOperator.EQUAL:
            self.__is_fulfilled = normalized_operand == normalized_value

        elif self.__operator == TriggerConditionOperator.ABOVE:
            self.__is_fulfilled = normalized_operand < normalized_value

        elif self.__operator == TriggerConditionOperator.BELOW:
            self.__is_fulfilled = normalized_operand > normalized_value

        return self.__is_fulfilled


class DevicePropertyConditionItem(PropertyConditionItem):
    """
    Device property condition entity item

    @package        FastyBird:TriggersModule!
    @module         items

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __device_property: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        condition_id: uuid.UUID,
        enabled: bool,
        operator: TriggerConditionOperator,
        operand: str,
        device_property: str,
        device: str,
    ) -> None:
        super().__init__(condition_id, enabled, operator, operand, device)

        self.__device_property = device_property

    # -----------------------------------------------------------------------------

    @property
    def device_property(self) -> str:
        """Device property key"""
        return self.__device_property

    # -----------------------------------------------------------------------------

    def validate(
        self,
        item: DevicePropertyItem,
        previous_value: str or None,
        actual_value: str
    ) -> bool:
        """Device property value validation"""
        return super().validate(item, previous_value, actual_value)


class ChannelPropertyConditionItem(PropertyConditionItem):
    """
    Channel property condition entity item

    @package        FastyBird:TriggersModule!
    @module         items

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __channel_property: str
    __channel: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        condition_id: uuid.UUID,
        enabled: bool,
        operator: TriggerConditionOperator,
        operand: str,
        channel_property: str,
        channel: str,
        device: str,
    ) -> None:
        super().__init__(condition_id, enabled, operator, operand, device)

        self.__channel_property = channel_property
        self.__channel = channel

    # -----------------------------------------------------------------------------

    @property
    def channel(self) -> str:
        """Channel key"""
        return self.__channel

    # -----------------------------------------------------------------------------

    @property
    def channel_property(self) -> str:
        """Channel property key"""
        return self.__channel_property

    # -----------------------------------------------------------------------------

    def validate(
        self,
        item: ChannelPropertyItem,
        previous_value: str or None,
        actual_value: str
    ) -> bool:
        """Channel property value validation"""
        return super().validate(item, previous_value, actual_value)


class PropertyActionItem(ABC):
    """
    Base property action entity item

    @package        FastyBird:TriggersModule!
    @module         items

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __action_id: uuid.UUID
    __enabled: bool

    __value: str
    __actual_value: str or None = None

    __device: str

    __is_triggered: bool = False

    # -----------------------------------------------------------------------------

    def __init__(self, action_id: uuid.UUID, enabled: bool, value: str, device: str) -> None:
        self.__action_id = action_id
        self.__enabled = enabled

        self.__value = value

        self.__device = device

        self.__is_triggered = False

    # -----------------------------------------------------------------------------

    @property
    def device(self) -> str:
        """Device key"""
        return self.__device

    # -----------------------------------------------------------------------------

    @property
    def action_id(self) -> uuid.UUID:
        """Action identifier"""
        return self.__action_id

    # -----------------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Flag informing if action is enabled"""
        return self.__enabled

    # -----------------------------------------------------------------------------

    @property
    def value(self) -> str:
        """Action property value to be set"""
        return self.__value

    # -----------------------------------------------------------------------------

    @property
    def is_triggered(self) -> bool:
        """Flag informing that action is ready to be triggered"""
        return self.__is_triggered

    # -----------------------------------------------------------------------------

    def validate(
        self,
        item: DevicePropertyItem or ChannelPropertyItem,
        previous_value: str or None,  # pylint: disable=unused-argument
        actual_value: str
    ) -> bool:
        """Property value validation"""
        if self.__value == SwitchPayload(SwitchPayload.TOGGLE).value:
            self.__is_triggered = False

            if self.__actual_value is None:
                self.__actual_value = actual_value

            elif self.__actual_value == actual_value:
                self.__is_triggered = True

        else:
            self.__is_triggered = PropertiesUtils.normalize_value(
                item, self.__value
            ) == PropertiesUtils.normalize_value(item, actual_value)

        return self.__is_triggered


class DevicePropertyActionItem(PropertyActionItem):
    """
    Device property action entity item

    @package        FastyBird:TriggersModule!
    @module         items

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __device_property: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        action_id: uuid.UUID,
        enabled: bool,
        value: str,
        device_property: str,
        device: str,
    ) -> None:
        super().__init__(action_id, enabled, value, device)

        self.__device_property = device_property

    # -----------------------------------------------------------------------------

    @property
    def device_property(self) -> str:
        """Device property key"""
        return self.__device_property

    # -----------------------------------------------------------------------------

    def validate(
        self,
        item: DevicePropertyItem,
        previous_value: str or None,
        actual_value: str
    ) -> bool:
        """Device property value validation"""
        return super().validate(item, previous_value, actual_value)


class ChannelPropertyActionItem(PropertyActionItem):
    """
    Channel property action entity item

    @package        FastyBird:TriggersModule!
    @module         items

    @author         Adam Kadlec <adam.kadlec@fastybird.com>
    """
    __channel_property: str
    __channel: str

    # -----------------------------------------------------------------------------

    def __init__(
        self,
        action_id: uuid.UUID,
        enabled: bool,
        value: str,
        channel_property: str,
        channel: str,
        device: str,
    ) -> None:
        super().__init__(action_id, enabled, value, device)

        self.__channel_property = channel_property
        self.__channel = channel

    # -----------------------------------------------------------------------------

    @property
    def channel(self) -> str:
        """Channel key"""
        return self.__channel

    # -----------------------------------------------------------------------------

    @property
    def channel_property(self) -> str:
        """Channel property key"""
        return self.__channel_property

    # -----------------------------------------------------------------------------

    def validate(
        self,
        item: ChannelPropertyItem,
        previous_value: str or None,
        actual_value: str
    ) -> bool:
        """Channel property value validation"""
        return super().validate(item, previous_value, actual_value)
