import logging
from typing import Any

from prtg_pyprobe.utils.validators import validate


class SensorDefinitionGroup(object):
    """Represents a group within the sensor definition"""

    class SensorDefinitionGroupField(object):
        """Represents a field within a sensor definition group"""

        def __init__(self, field_type: str, name: str, caption: str, **kwargs):
            """
            Constructor of SensorDefinitionGroupField
            Args:
                field_type (str): The field type.
                name (str): The field name.
                caption (str): The field caption.
                **kwargs: Arbitrary keyword arguments. See utils.validators for details.

            """
            self._field_type = field_type
            self._name = name
            self._caption = caption
            self._kwargs = kwargs

        @property
        @validate
        def data(self) -> dict:
            """Validated data property of SensorDefinitionGroupField
            Returns:
                dict: A validated dictionary.

            """
            field = {
                "type": self._field_type,
                "name": self._name,
                "caption": self._caption,
            }
            for k, v in self._kwargs.items():
                field[k] = v
            return field

    def __init__(self, name: str, caption: str):
        """Constructor of SensorDefinitionGroup

        Args:
            name (str): The name of the group.
            caption (str):  The caption of the group.
        """
        self._name = name
        self._caption = caption
        self._fields = []

    @property
    @validate
    def data(self) -> dict:
        """Validated data property of SensorDefinitionGroup

        Returns:
            dict: A validated dictionary.

        """
        group = {"name": self._name, "caption": self._caption, "fields": self._fields}
        return group

    def add_field_timeout(self, default: int, minimum: int, maximum: int):
        """Add a timeout field to a group.

        Args:
            default (int): The default timeout.
            minimum (int): The maximum value.
            maximum (int): The minimum value.

        """
        timeout = self.SensorDefinitionGroupField(
            field_type="integer",
            name="timeout",
            caption="Timeout (in s)",
            required="1",
            default=default,
            minimum=minimum,
            maximum=maximum,
            help=f"If the reply takes longer than this value the request is aborted "
            f"and an error message is triggered. Maximum value is {maximum} sec. (= {maximum / 60} minutes)",
        )
        self._fields.append(timeout.data)

    def add_field(self, field_type: str, name: str, caption: str, **kwargs):
        """Add a field to a group.

        Args:
            field_type (str): The field type.
                The field type should be of these types: "edit", "integer", "password", "radio"
            name (str): The field name.
            caption (str): The field caption.
            **kwargs: Arbitrary keyword arguments. See utils.validators for details.

        Examples:
                >>> ping_def_group_settings.add_field(
                        field_type="integer",
                        name="ping_count",
                        caption="Ping Count",
                        required="1",
                        default=4,
                        minimum=1,
                        maximum=20,
                        help="Enter the count of Ping requests PRTG will send to the device during an interval",
                    )

        """
        field = self.SensorDefinitionGroupField(field_type=field_type, name=name, caption=caption, **kwargs)
        self._fields.append(field.data)


class SensorDefinition(object):
    """Represents the Sensor Definition."""

    class NotASensorDefinitionGroupError(Exception):
        """Exception when an added group is not of type SensorDefinitionGroup."""

        def __init__(self):
            super().__init__("Group has to be of type SensorDefinitionGroup.")

    def __init__(
        self,
        kind: str,
        name: str,
        description: str,
        sensor_help: str,
        tag: str,
        default: str = None,
    ):
        """Constructor for `SensorDefinition`.

        Args:
            kind (str): The sensor kind.
            name (str):  The sensor name.
            description (str): The sensor description.
            sensor_help (str): The sensor help. Shows when hovering over the question mark in PRTG interface.
            tag (str): The tag for the sensor.
            default (str, optional): Determines if the sensor is created when the probe is connected.
                Allowed values "yes", "1", "true".
        """
        self._kind = kind
        self._name = name
        self._description = description
        self._help = sensor_help
        self._tag = tag
        self._default = default
        self._groups = []

    @property
    @validate
    def data(self) -> dict:
        """Validated data property of `SensorDefinition`.

        Returns:
            dict: A validated dict.
        """
        definition = {
            "name": self._name,
            "kind": self._kind,
            "description": self._description,
            "help": self._help,
            "tag": self._tag,
            "groups": self._groups,
        }
        if self._default:
            definition["default"] = self._default
        logging.debug(f"Sensor Definition for sensor {self._name}: {str(definition)}")
        return definition

    def add_group(self, group: SensorDefinitionGroup):
        """Add a group to the `SensorDefinition`.

        Args:
            group (SensorDefinitionGroup):

        Raises:
            NotASensorDefinitionGroupError: Raised when the object passed is not of type `SensorDefinitionGroup`.

        """
        if isinstance(group, SensorDefinitionGroup):
            self._groups.append(group.data)
        else:
            raise self.NotASensorDefinitionGroupError


class SensorData(object):
    """Represents the SensorData."""

    class SensorDataChannel(object):
        """Represents a SensorDataChannel"""

        def __init__(self, name: str, mode: str, value: Any, **kwargs):
            """Constructor of SensorDataChannel

            Args:
                name (str): The channel name.
                mode (str): The channel mode.
                    Allowed values are "integer", "float", "counter".
                value (Any): The channel value.
                    Allowed values "integer", "float"
                **kwargs: Arbitrary keyword arguments. See utils.validators for details.

            """
            self._name = name
            self._mode = mode
            self._value = value
            self._kwargs = kwargs

        @property
        @validate
        def data(self) -> dict:
            """Validated data property of `SensorDataChannel`.

            Returns:
                dict: A validated dict.

            """
            channel = {"name": self._name, "mode": self._mode, "value": self._value}
            for k, v in self._kwargs.items():
                channel[k] = v
            return channel

    def __init__(self, sensor_id: str):
        """Constructor of SensorData

        Args:
            sensor_id (str): The sensor id. Contained in the taskdata from the PRTG Core.
        """
        self._sensor_id = sensor_id
        self._message = None
        self._error = None
        self._error_code = None
        self._channel_list = []

    @property
    def message(self) -> str:
        """str: Property message of SensorData"""
        return self._message

    @message.setter
    def message(self, value: str = None):

        self._message = value

    @property
    def error(self) -> str:
        """str: Property error of SensorData"""
        return self._error

    @error.setter
    def error(self, value: str = None):
        self._error = value

    @property
    def error_code(self) -> int:
        """str: Property error_code of SensorData"""
        return self._error_code

    @error_code.setter
    def error_code(self, value: int = None):
        self._error_code = value

    @property
    @validate
    def data(self) -> dict:
        """Validated data property of `SensorDataChannel`.

        Returns:
            dict: A validated dict.

        """
        sensordata = {"sensorid": self._sensor_id, "message": self._message}
        if self._error and self._error_code:
            sensordata["error"] = self._error
            sensordata["code"] = self._error_code
            return sensordata
        if len(self._channel_list) > 0:
            sensordata["channel"] = self._channel_list
        logging.debug(f"Monitoring data for sensorid {self._sensor_id}: {str(sensordata)}")
        return sensordata

    def add_channel(self, name: str, mode: str, value, **kwargs):
        """Add a channel to SensorData

        name (str): The channel name.
                mode (str): The channel mode.
                    Allowed values are "integer", "float", "counter".
                value (Any): The channel value.
                    Allowed values "integer", "float"
                **kwargs: Arbitrary keyword arguments. See utils.validators for details.

            Examples:
                >>> ping_data.add_channel(
                name="Ping Time Max",
                mode="float",
                kind="TimeResponse",
                value=float(max(ping_raw_data)),
            )

        """
        channel = self.SensorDataChannel(name=name, mode=mode, value=value, **kwargs)
        self._channel_list.append(channel.data)


class SensorProbeData(SensorData):
    """Represents SensorProbeData a special subset of SensorData"""

    def add_load_avg_channel(self, cpu_load: float, minute_avg: int):
        """Add a load average channel.

        Args:
            cpu_load (float): Load Average value.
            minute_avg (int): Minutes. Shoule be 1, 5 or 10

        """
        self.add_channel(
            name=f"Load average {str(minute_avg)} min",
            mode="float",
            kind="Custom",
            customunit="",
            value=float(cpu_load),
        )

    def add_temperature_channel(self, name: str, current_temp: float, celfar: str):
        """Add a temperature channel.

        Args:
            name (str): The channel name.
            current_temp: The current temperature.
            celfar: The temperature unit as number 1 = Celsius, 2 = Fahrenheit.

        """
        temp_unit = "C"
        if celfar == "2":
            temp_unit = "F"
        self.add_channel(
            name=name, mode="float", kind="Custom", unit="Custom", customunit=temp_unit, value=current_temp
        )

    def add_disk_space_percentage_use(self, partition: str, disk_usage: list):
        """Add disk space channel.

        Args:
            partition (str): The partition name.
            disk_usage (list): List of usage values.

        """
        self.add_channel(
            name=f"Disk Space Percent {partition[1]}",
            mode="float",
            kind="Percent",
            value=disk_usage[3],
        )

    def add_disk_space_details_channel(self, name: str, partition: list, disk_usage: float):
        """Add disk space details channel,

        Args:
            name (str): The partition name.
            partition (list): List of partitions.
            disk_usage (float): The used value.

        """
        self.add_channel(
            name=f"Disk Space {name} {partition[1]}",
            mode="integer",
            kind="BytesDisk",
            value=disk_usage,
        )
