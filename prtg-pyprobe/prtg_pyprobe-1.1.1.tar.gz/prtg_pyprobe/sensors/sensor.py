import logging
from abc import ABC
from collections import namedtuple
from typing import Union

import psutil
from pysnmp.error import PySnmpError
from pysnmp.hlapi import asyncio as pysnmp_asyncio
from pysnmp.hlapi.asyncio import (
    CommunityData,
    SnmpEngine,
    ContextData,
    UdpTransportTarget,
    ObjectType,
    ObjectIdentity,
)

from prtg_pyprobe.sensors.helpers import SensorDefinitionGroup


class SensorBase(ABC):
    """Abstract Base Class, from which every sensor should inherit."""

    def __getitem__(self, kind):
        return self.kind

    @property
    def name(self) -> str:
        """Abstract property name of SensorBase.

        Raises:
            NotImplementedError: Has to be overwritten in implementation
        """
        raise NotImplementedError

    @property
    def kind(self) -> str:
        """Abstract property kind of SensorBase.

        Raises:
            NotImplementedError: Has to be overwritten in implementation
        """
        raise NotImplementedError

    @property
    def definition(self) -> dict:
        """Abstract property definition of SensorBase.

        Raises:
            NotImplementedError: Has to be overwritten in implementation
        """
        raise NotImplementedError

    async def work(self, *args, **kwargs) -> None:
        """Abstract method work of SensorBase.

        Args:
            *args:
            **kwargs:

        Raises:
            NotImplementedError: Has to be overwritten in implementation

        """
        raise NotImplementedError


class SensorPSUtilBase(SensorBase, ABC):
    """Base class for all sensors utilizing `psutil`."""

    @property
    def temperature_settings_group(self):
        """Add Group and Field for temperature settings"""
        probe_health_def_group_temperature = SensorDefinitionGroup(name="temperature", caption="Temperature Settings")
        probe_health_def_group_temperature.add_field(
            field_type="radio",
            name="celfar",
            caption="Choose between Celsius or Fahrenheit display",
            help="Choose whether you want to return the value in Celsius or Fahrenheit. "
            "When changed after sensor is created, the unit will disappear in the web interface.",
            options={"1": "Celsius", "2": "Fahrenheit"},
            default="1",
        )
        return probe_health_def_group_temperature

    @property
    def diskspace_settings_group(self):
        """Add Group and Field for diskspace settings"""
        probe_health_def_group_diskspace = SensorDefinitionGroup(name="diskspace", caption="Disk Space Settings")
        probe_health_def_group_diskspace.add_field(
            field_type="radio",
            name="diskfull",
            caption="Full Display of all disk space values",
            help="Choose whether you want to get all disk space data or only percentages.",
            options={"1": "Percentages", "2": "Full Information"},
            default="1",
        )
        return probe_health_def_group_diskspace

    @staticmethod
    def get_system_temperatures(fahrenheit: bool) -> Union[dict, None]:
        """Get system temperature.

        Args:
            fahrenheit (bool): Use Fahrenheut or Celcius as unit.

        Returns:
            Union: Return either a dict or None.
        """
        if not hasattr(psutil, "sensors_temperatures"):
            return None
        temperatures = psutil.sensors_temperatures(fahrenheit=fahrenheit)
        if temperatures == {}:
            return None

        return temperatures

    @staticmethod
    def get_system_partitions() -> list:
        """Get partitions.

        Returns:
            list: A list of partitions.
        """
        return psutil.disk_partitions()

    @staticmethod
    def get_partition_usage(partition: list) -> namedtuple:
        """Get disk usage of partitions.

        Args:
            partition (list): A list of partitions.

        Returns:
            namedtuple: A named tuple containing disk usage data.

        """
        return psutil.disk_usage(partition[1])

    @staticmethod
    def get_memory_usage() -> tuple:
        """Get memory usage.

        Returns:
            tuple: A tuple containing virtual memory and swap usage.

        """
        vmemory = psutil.virtual_memory()
        swapmemory = psutil.swap_memory()

        return vmemory, swapmemory

    @staticmethod
    def get_cpu_load() -> tuple:
        """Get CPU load average.

        Returns:
            tuple: A tuple containing the load average.
        """
        return psutil.getloadavg()


class SensorSNMPBase(SensorBase, ABC):
    """Base class for all SNMP sensors."""

    @property
    def snmp_specific_settings_group(self):
        """Add Group and Field for SNMP related settings."""
        snmp_group_snmp_specifications = SensorDefinitionGroup(name="snmpspecific", caption="SNMP Specific")
        snmp_group_snmp_specifications.add_field(
            field_type="edit",
            name="community",
            caption="Community String",
            required="1",
            help="Please enter the community string.",
        )
        snmp_group_snmp_specifications.add_field(
            field_type="integer",
            name="port",
            caption="SNMP Port",
            required="1",
            help="Please enter SNMP Port.",
        )
        snmp_group_snmp_specifications.add_field(
            field_type="radio",
            name="snmp_version",
            caption="SNMP Version",
            required="1",
            help="Choose your SNMP Version",
            options={"0": "V1", "1": "V2c", "2": "V3"},
            default="1",
        )
        return snmp_group_snmp_specifications

    async def get(
        self,
        target: str,
        oids: list,
        credentials: CommunityData,
        port: int = 161,
        engine: SnmpEngine = SnmpEngine(),
        context: ContextData = ContextData(),
    ) -> list:
        """SNMP single get.

        Args:
            target (str): The target of the SNMP request.
            oids (list): A list of OIDs to query.
            credentials (CommunityData): The PySnmp authentication data.
            port (int): The port the target listens for SNMP requests.
            engine (SnmpEngine): PySnmp SNMP Engine.
            context (ContextData): PySnmp context data

        Returns:
            list: A list of OIDs and values.

        Raises:
            PySnmpError: Raised when something goes wrong.
        """
        (error_indication, error_status, error_index, var_binds,) = await pysnmp_asyncio.getCmd(
            engine,
            credentials,
            UdpTransportTarget((target, port)),
            context,
            *self.construct_object_types(oids),
        )
        if error_indication:
            logging.error(error_indication)
            raise PySnmpError(error_indication)
        elif error_status:
            msg = f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}"
            logging.error(msg)
            raise PySnmpError(msg)
        return var_binds

    async def get_bulk(
        self,
        target: str,
        oids: list,
        credentials: CommunityData,
        port: int = 161,
        engine: SnmpEngine = SnmpEngine(),
        context: ContextData = ContextData(),
    ):
        """SNMP bulk get (getnext).

        Args:
            target (str): The target of the SNMP request.
            oids (list): A list of OIDs to query.
            credentials (CommunityData): The PySnmp authentication data.
            port (int): The port the target listens for SNMP requests.
            engine (SnmpEngine): PySnmp SNMP Engine.
            context (ContextData): PySnmp context data

        Returns:
            list: A list of OIDs and values.

        Raises:
            PySnmpError: Raised when something goes wrong.
        """
        # todo:  Probably we won't need bulk get
        result = []
        var_binds = self.construct_object_types(oids)
        initial_var_binds = var_binds
        while True:
            (error_indication, error_status, error_index, var_bind_table,) = await pysnmp_asyncio.nextCmd(
                engine,
                credentials,
                UdpTransportTarget((target, port)),
                context,
                *var_binds,
                lookupValues=True,
                lookupNames=True,
            )

            if error_indication:
                logging.error(error_indication)
                raise PySnmpError(error_indication)
            elif error_status:
                msg = f"{error_status.prettyPrint()} at {error_index and var_binds[int(error_index) - 1][0] or '?'}"
                logging.error(msg)
                raise PySnmpError(msg)
            else:
                for var_bind_row in var_bind_table:
                    result.append(var_bind_row)

                var_binds = var_bind_table[-1]
                if pysnmp_asyncio.isEndOfMib(var_binds):
                    break

                for idx, var_bind in enumerate(var_binds):
                    if initial_var_binds[0][idx].isPrefixOf(var_bind[0]):
                        break

                else:
                    break

        return result

    @staticmethod
    def construct_object_types(list_of_oids: list) -> list:
        """Construnc objects from given OIDs

        Args:
            list_of_oids: A list of OIDs.

        Returns:
            list: A list of PySnmp Object Identities.

        """
        object_types = []
        for oid in list_of_oids:
            object_types.append(ObjectType(ObjectIdentity(oid)))
        return object_types

    @staticmethod
    def cast(value: str) -> Union[str, float, int]:
        """A brute force cast method.

        Args:
            value (str): A string.

        Returns:
            Union: A hopefully cast value.
        """
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return float(value)
            except (ValueError, TypeError):
                return str(value)
