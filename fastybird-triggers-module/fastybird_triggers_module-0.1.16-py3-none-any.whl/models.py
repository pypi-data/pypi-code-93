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
Module models definitions
"""

# Library dependencies
import uuid
import datetime
from typing import List
from modules_metadata.triggers_module import TriggerConditionOperator
from pony.orm import core as orm, Database, PrimaryKey, Required, Optional, Set, Discriminator, Json

# Library libs
from triggers_module.items import (
    TriggerItem,
    DevicePropertyConditionItem,
    ChannelPropertyConditionItem,
    DevicePropertyActionItem,
    ChannelPropertyActionItem,
)


def define_entities(db: Database):  # pylint: disable=invalid-name
    """Register all module entities and initialize repositories cache"""

    class TriggerEntity(db.Entity):
        """
        Base trigger entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _table_: str = "fb_triggers"

        type = Discriminator(str, column="trigger_type")
        _discriminator_: str = "trigger"

        trigger_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="trigger_id")
        name: str or None = Required(str, column="trigger_name", max_len=100, nullable=False)
        comment: str or None = Optional(str, column="trigger_comment", nullable=True, default=None)
        enabled: bool = Required(bool, column="trigger_enabled", nullable=False, default=True)
        params: Json or None = Optional(Json, column="params", nullable=True)
        created_at: datetime.datetime or None = Optional(datetime.datetime, column="created_at", nullable=True)
        updated_at: datetime.datetime or None = Optional(datetime.datetime, column="updated_at", nullable=True)

        actions: List["ActionEntity"] = Set("ActionEntity", reverse="trigger")
        notifications: List["NotificationEntity"] = Set("NotificationEntity", reverse="trigger")

        def before_insert(self) -> None:
            """Before insert entity hook"""
            self.created_at = datetime.datetime.now()

        def before_update(self) -> None:
            """Before update entity hook"""
            self.updated_at = datetime.datetime.now()

    class ManualTriggerEntity(TriggerEntity):
        """
        Manual trigger entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "manual"

    class AutomaticTriggerEntity(TriggerEntity):
        """
        Automatic trigger entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "automatic"

        conditions: List["ConditionEntity"] = Set("ConditionEntity", reverse="trigger")

    class ActionEntity(db.Entity):
        """
        Base action entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _table_: str = "fb_actions"

        type = Discriminator(str, column="action_type")

        action_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="action_id")
        enabled: bool = Required(bool, column="action_enabled", nullable=False, default=True)
        created_at: datetime.datetime or None = Optional(datetime.datetime, column="created_at", nullable=True)
        updated_at: datetime.datetime or None = Optional(datetime.datetime, column="updated_at", nullable=True)

        trigger: TriggerEntity = Required("TriggerEntity", reverse="actions", column="trigger_id", nullable=False)

        def before_insert(self) -> None:
            """Before insert entity hook"""
            self.created_at = datetime.datetime.now()

        def before_update(self) -> None:
            """Before update entity hook"""
            self.updated_at = datetime.datetime.now()

    class PropertyActionEntity(ActionEntity):
        """
        Property action entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        device: str = Required(str, column="action_device", max_len=100, nullable=True)

        value: str = Required(str, column="action_value", max_len=100, nullable=True)

    class DevicePropertyActionEntity(PropertyActionEntity):
        """
        Device property action entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "device_property"

        device_property: str = Required(str, column="action_device_property", max_len=100, nullable=True)

    class ChannelPropertyActionEntity(PropertyActionEntity):
        """
        Channel property action entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "channel_property"

        channel: str = Required(str, column="action_channel", max_len=100, nullable=True)
        channel_property: str = Required(str, column="action_channel_property", max_len=100, nullable=True)

    class NotificationEntity(db.Entity):
        """
        Base notification entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _table_: str = "fb_notifications"

        type = Discriminator(str, column="notification_type")

        notification_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="notification_id")
        enabled: bool = Required(bool, column="notification_enabled", nullable=False, default=True)
        created_at: datetime.datetime or None = Optional(datetime.datetime, column="created_at", nullable=True)
        updated_at: datetime.datetime or None = Optional(datetime.datetime, column="updated_at", nullable=True)

        trigger: TriggerEntity = Required("TriggerEntity", reverse="notifications", column="trigger_id", nullable=False)

        def before_insert(self) -> None:
            """Before insert entity hook"""
            self.created_at = datetime.datetime.now()

        def before_update(self) -> None:
            """Before update entity hook"""
            self.updated_at = datetime.datetime.now()

    class EmailNotificationEntity(NotificationEntity):
        """
        Email notification entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "email"

        email: str = Required(str, column="notification_email", max_len=150, nullable=True)

    class SmsNotificationEntity(NotificationEntity):
        """
        SMS notification entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "sms"

        phone: str = Required(str, column="notification_phone", max_len=150, nullable=True)

    class ConditionEntity(db.Entity):
        """
        Base condition entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _table_: str = "fb_conditions"

        type = Discriminator(str, column="condition_type")

        condition_id: uuid.UUID = PrimaryKey(uuid.UUID, default=uuid.uuid4, column="condition_id")
        enabled: bool = Required(bool, column="condition_enabled", nullable=False, default=True)
        created_at: datetime.datetime or None = Optional(datetime.datetime, column="created_at", nullable=True)
        updated_at: datetime.datetime or None = Optional(datetime.datetime, column="updated_at", nullable=True)

        trigger: AutomaticTriggerEntity = Required(
            "AutomaticTriggerEntity",
            reverse="conditions",
            column="trigger_id",
            nullable=False,
        )

        def before_insert(self) -> None:
            """Before insert entity hook"""
            self.created_at = datetime.datetime.now()

        def before_update(self) -> None:
            """Before update entity hook"""
            self.updated_at = datetime.datetime.now()

    class PropertyConditionEntity(ConditionEntity):
        """
        Property condition entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        operator: TriggerConditionOperator = Required(TriggerConditionOperator, column="condition_operator",
                                                      nullable=True)
        operand: str = Required(str, column="condition_operand", max_len=100, nullable=True)

        device: str = Required(str, column="condition_device", max_len=100, nullable=True)

    class DevicePropertyConditionEntity(PropertyConditionEntity):
        """
        Device property condition entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "device_property"

        device_property: str = Required(str, column="condition_device_property", max_len=100, nullable=True)

    class ChannelPropertyConditionEntity(PropertyConditionEntity):
        """
        Channel property condition entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "channel_property"

        channel: str = Required(str, column="condition_channel", max_len=100, nullable=True)
        channel_property: str = Required(str, column="condition_channel_property", max_len=100, nullable=True)

    class TimeConditionEntity(ConditionEntity):
        """
        Time property condition entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "time"

        time: datetime.timedelta = Required(datetime.timedelta, column="condition_time", nullable=True)
        days: str = Required(str, column="condition_days", max_len=100, nullable=True)

    class DateConditionEntity(ConditionEntity):
        """
        Date property condition entity

        @package        FastyBird:TriggersModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        _discriminator_: str = "date"

        date: datetime.datetime = Required(datetime.datetime, column="condition_date", nullable=True)

    class TriggersRepository:
        """
        Triggers repository

        @package        FastyBird:DevicesModule!
        @module         models

        @author         Adam Kadlec <adam.kadlec@fastybird.com>
        """
        __items: List[TriggerItem] or None = None

        __iterator_index = 0

        # -----------------------------------------------------------------------------

        def clear(self) -> None:
            """Clear items cache"""
            self.__items = None

        # -----------------------------------------------------------------------------

        @orm.db_session
        def initialize(self) -> None:
            """Initialize repository by fetching entities from database"""
            self.__items = []

            for trigger in TriggerEntity.select():
                record = TriggerItem(trigger.trigger_id)

                if isinstance(trigger, AutomaticTriggerEntity):
                    for condition in trigger.conditions:
                        if isinstance(condition, DevicePropertyConditionEntity):
                            record.add_condition(
                                condition.condition_id.__str__(),
                                DevicePropertyConditionItem(
                                    condition.condition_id,
                                    condition.enabled,
                                    condition.operator,
                                    condition.operand,
                                    condition.device_property,
                                    condition.device,
                                ),
                            )

                        elif isinstance(condition, ChannelPropertyConditionEntity):
                            record.add_condition(
                                condition.condition_id.__str__(),
                                ChannelPropertyConditionItem(
                                    condition.condition_id,
                                    condition.enabled,
                                    condition.operator,
                                    condition.operand,
                                    condition.channel_property,
                                    condition.channel,
                                    condition.device,
                                ),
                            )

                for action in trigger.actions:
                    if isinstance(action, ChannelPropertyActionEntity):
                        record.add_action(
                            action.action_id.__str__(),
                            ChannelPropertyActionItem(
                                action.action_id,
                                action.enabled,
                                action.value,
                                action.channel_property,
                                action.channel,
                                action.device,
                            ),
                        )

                    elif isinstance(action, DevicePropertyActionEntity):
                        record.add_action(
                            action.action_id.__str__(),
                            DevicePropertyActionItem(
                                action.action_id,
                                action.enabled,
                                action.value,
                                action.device_property,
                                action.device,
                            ),
                        )

                self.__items.append(record)

        # -----------------------------------------------------------------------------

        def __iter__(self) -> "TriggersRepository":
            # Reset index for nex iteration
            self.__iterator_index = 0

            return self

        # -----------------------------------------------------------------------------

        def __len__(self):
            if self.__items is None:
                self.initialize()

            return len(self.__items)

        # -----------------------------------------------------------------------------

        def __next__(self) -> TriggerItem:
            if self.__items is None:
                self.initialize()

            if self.__iterator_index < len(self.__items):
                result: TriggerItem = self.__items[self.__iterator_index]

                self.__iterator_index += 1

                return result

            # Reset index for nex iteration
            self.__iterator_index = 0

            # End of iteration
            raise StopIteration

    triggers_repository = TriggersRepository()

    return TriggerEntity, ManualTriggerEntity, AutomaticTriggerEntity, \
           ActionEntity, PropertyActionEntity, DevicePropertyActionEntity, ChannelPropertyActionEntity, \
           NotificationEntity, EmailNotificationEntity, SmsNotificationEntity, \
           ConditionEntity, TimeConditionEntity, DateConditionEntity, \
           PropertyConditionEntity, ChannelPropertyConditionEntity, DevicePropertyConditionEntity, \
           triggers_repository
