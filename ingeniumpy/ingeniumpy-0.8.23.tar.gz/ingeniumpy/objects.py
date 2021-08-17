import asyncio
import inspect
from enum import Enum
from typing import Callable, List, TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from .api import IngeniumAPI


class Package:
    def __init__(self, source: int, target: int, command: int, data1: int, data2: int):
        self.source = source
        self.target = target
        self.command = command
        self.data1 = data1
        self.data2 = data2

    def __str__(self):
        return 'Package ( source={}, target={}, command={}, data1={}, data2={} )' \
            .format(self.source, self.target, self.command, self.data1, self.data2)

    def as_bytes(self):
        return bytes([
            0xFF,
            0xFF,
            (self.target >> 8) & 0xFF,
            self.target & 0xFF,
            self.command & 0xFF,
            self.data1 & 0xFF,
            self.data2 & 0xFF,
            0,
            0  # To make it length 9
        ])


class IngComponentType(Enum):
    NOT_IMPLEMENTED = -1

    COD_AIR_QUALITY = 8

    COD_NOISE = 9

    """
    Actuadores Busing
    """
    COD2E2S = 24
    COD4E4S = 15
    COD6E6S = 4
    COD_KCTR = 13

    COD2S300 = 3
    CODRB1500 = 12
    CODRF10A = 13
    COD_T_KNX_DIMMER = 2

    COD_RGB = 52

    """
    Actuadores KNX
    """
    T_KNX_ONOFF = 1

    SCENE = 26
    COD_TRMD = 6
    COD_MEC_BUS = 29
    COD_TEC_BUS = 33
    COD_TSIF = 34
    COD_TSIF_W = 43
    COD_TEC_ING = 44
    COD_METERBUS = 46
    COD_TERMOSTATO_LG = 47
    COD_TSIF_LDR = 51
    COD_INTERNAL_THERMOSTAT = 56
    COD_DANFOSS = 61
    COD_UNIT_AUCORE = 49
    COD_KA_FERMAX = 60
    COD_CHINESE_CAMERA = 84

    T_KNX_BLIND = 5
    T_KNX_LABEL = 100
    T_KNX_BUTTON = 101
    T_KNX_SLIDER = 102
    T_KNX_STEPPER = 103
    T_KNX_CONF_BUTTON = 104

    T_KNX_COLOR_PICKER = 9

    def is_air_sensor(self): return self in [self.COD_AIR_QUALITY]

    def is_noise_sensor(self): return self in [self.COD_NOISE]

    def is_actuator(self): return self in [self.COD2E2S, self.COD4E4S, self.COD6E6S, self.COD_KCTR, self.T_KNX_ONOFF]

    def is_meterbus(self): return self in [self.COD_METERBUS]

    def is_tsif(self): return self in [self.COD_TSIF, self.COD_TSIF_W, self.COD_TSIF_LDR]

    def is_scene(self): return self in [self.SCENE]

    def is__lg_thermostat(self): return self in [self.COD_TERMOSTATO_LG]

    def is_unit_aucore(self): return self in [self.COD_UNIT_AUCORE]

    def is_chinese_camera(self): return self in [self.COD_CHINESE_CAMERA]

    def is_ka_fermax(self): return self in [self.COD_KA_FERMAX]

    def is_knx_label(self): return self in [self.T_KNX_LABEL]

    def is_knx_button(self): return self in [self.T_KNX_BUTTON]

    def is_knx_slider(self): return self in [self.T_KNX_SLIDER]

    def is_knx_stepper(self): return self in [self.T_KNX_STEPPER]

    def is_knx_conf_button(self): return self in [self.T_KNX_CONF_BUTTON]

    def is_knx_blind(self): return self in [self.T_KNX_BLIND]

    def is_thermostat(self): return self in [self.COD_TRMD, self.COD_MEC_BUS, self.COD_TEC_ING, self.COD_TEC_BUS,
                                             self.COD_INTERNAL_THERMOSTAT, self.COD_DANFOSS]

    def is_knx_regulator(self): return self in [self.COD_T_KNX_DIMMER]

    def is_busing_regulator(self): return self in [self.COD2S300, self.CODRB1500, self.CODRF10A]

    def is_knx_rgb_color_picker(self): return self in [self.T_KNX_COLOR_PICKER]

    def is_busing_rgb_color_picker(self): return self in [self.COD_RGB]


# noinspection PyBroadException
def safecast(value, cast_fn):
    try:
        return cast_fn(value)
    except BaseException:
        return None


def get_device_type(ctype) -> IngComponentType:
    try:
        return IngComponentType(safecast(ctype, int))
    except ValueError:
        print("Invalid component: " + str(ctype))
        return IngComponentType.NOT_IMPLEMENTED


class IngComponent:
    id: str
    label: str
    output: int
    icon: int

    _notify_update: List[Callable]

    def __init__(self, json: Dict[str, Any] = None):
        if json is not None:
            self.id = json.get("id")
            self.label = json.get("label")
            self.output = safecast(json.get("output"), int)
            self.icon = safecast(json.get("icon"), int)
        self._notify_update = []

    def __str__(self):
        return "Component ( id='{}', label='{}', output={} )" \
            .format(self.id, self.label, self.output)

    def set_update_notify(self, callback: Callable):
        self._notify_update = [callback]

    def add_update_notify(self, callback: Callable):
        self._notify_update.append(callback)

    def update_notify(self):
        for cb in self._notify_update:
            try:
                cb()
            except BaseException as e:
                print("Exception {} at {}".format(e, inspect.getsource(cb)))


class IngObject:
    api: 'IngeniumAPI'
    is_knx: bool
    address: int
    type: IngComponentType
    type_name: str
    components: List[IngComponent]

    available: bool

    def __init__(self, api: 'IngeniumAPI', is_knx: bool, address: int, ctype: IngComponentType,
                 comps: List[IngComponent]):
        self.api = api
        self.is_knx = is_knx
        self.address = address
        self.type = ctype
        self.type_name = ctype.name.replace("COD_", "").replace("COD", "")
        self.components = comps
        self.available = False

    def __str__(self) -> str:
        return "IngObject ( address='{}', type={}, components={} )" \
            .format(self.address, self.type, [str(c) for c in self.components])

    async def update_state(self, p: Package) -> bool:
        raise NotImplementedError

    def get_info(self):
        return {
            "name": ", ".join([x.label for x in self.components]),
            "identifiers": {("ingenium", self.address)},
            "model": self.type_name,
            "manufacturer": "Ingenium",
        }


ACTUATOR_BLIND = 0
ACTUATOR_NORMAL = 2


class IngActuator(IngObject):
    def __init__(self, api: 'IngeniumAPI', is_knx: bool, address: int, ctype: IngComponentType,
                 comps: List[IngComponent]):
        super().__init__(api, is_knx, address, ctype, comps)

        self.blind1 = 0
        self.blind2 = 0
        self.blind3 = 0
        self.blind4 = 0

        self.updating_blinds = []

        self.consumption = -1

        self.current = -1
        self.voltage = -1
        self.active_power_bits = [-1, -1]
        self.active_power = -1

        self.is_sock = False

        if self.address in self.api._detected_socks:
            self.is_sock = True

        self.output_state = 0
        self.mode = ACTUATOR_BLIND if self.components[0].icon == 5 else ACTUATOR_NORMAL

    def get_switch_val(self, c: IngComponent):
        power = 1 << c.output
        return (self.output_state & power) == power

    async def action_switch(self, c: IngComponent):
        power = 1 << c.output
        d2 = c.output + 8 if (self.output_state & power) == power else c.output
        p = Package(0xFFFF, self.address, 4, 2, d2)
        await self.api.send(p)

        if d2 < 8:
            self.output_state |= (1 << d2)
        else:
            self.output_state &= ~(1 << (d2 - 8))

        c.update_notify()

    async def set_cover_val(self, c: IngComponent, value: int):
        data1 = 0
        if c.output < 2:
            data1 = 4
            self.blind1 = value
        elif 2 <= c.output < 4:
            data1 = 5
            self.blind2 = value
        elif 4 <= c.output < 6:
            data1 = 6
            self.blind3 = value
        elif 6 <= c.output < 8:
            data1 = 7
            self.blind4 = value

        p = Package(0xFFFF, self.address, 4, data1, value)
        await self.api.send(p)

        c.update_notify()

    def get_cover_val(self, c: IngComponent):
        if c.output < 2:
            return self.blind1
        elif 2 <= c.output < 4:
            return self.blind2
        elif 4 <= c.output < 6:
            return self.blind3
        elif 6 <= c.output < 8:
            return self.blind4

    async def read_state(self):
        self.updating_blinds = []

        for c in self.components:
            if c.output < 2:
                self.updating_blinds.append(4)
            elif 2 <= c.output < 4:
                self.updating_blinds.append(5)
            elif 4 <= c.output < 6:
                self.updating_blinds.append(6)
            elif 6 <= c.output < 8:
                self.updating_blinds.append(7)

        await self._read()

    async def _read(self):  # blind_number between 1 and 4
        if len(self.updating_blinds) > 0:
            val = self.updating_blinds[-1]

            p = Package(0xFF, self.address, 3, val, 0)
            await self.api.send(p)

    async def maybe_detect_sock(self):
        if not self.is_sock:
            self.is_sock = True
            if self.api._detected_sock_fn is not None:
                await self.api._detected_sock_fn(self.address, self.components[0].label)

    async def update_state(self, p: Package) -> bool:
        # This part is run when receiving the response to a manual read
        if self.address == p.source and p.data1 == p.data2:
            if len(self.updating_blinds) > 0:
                val = self.updating_blinds.pop()
                if val == 4:
                    self.blind1 = p.data2
                elif val == 5:
                    self.blind2 = p.data2
                elif val == 6:
                    self.blind3 = p.data2
                elif val == 7:
                    self.blind4 = p.data2

                if len(self.updating_blinds) > 0:
                    await self._read()

                return True

        if self.address != p.target:
            return False

        if self.mode == ACTUATOR_BLIND:
            for c in self.components:
                if c.output < 2 and p.data1 == 4:
                    old_value = self.blind1
                    self.blind1 = p.data2
                    return old_value != self.blind1
                elif 2 <= c.output < 4 and p.data1 == 5:
                    old_value = self.blind2
                    self.blind2 = p.data2
                    return old_value != self.blind2
                elif 4 <= c.output < 6 and p.data1 == 6:
                    old_value = self.blind3
                    self.blind3 = p.data2
                    return old_value != self.blind3
                elif 6 <= c.output < 8 and p.data1 == 7:
                    old_value = self.blind4
                    self.blind4 = p.data2
                    return old_value != self.blind4
                return False

        else:
            old_state = self.output_state

            if p.data1 == 1:
                self.output_state = p.data2
                return self.output_state != old_state
            elif p.data1 == 2:
                if p.data2 < 8:
                    self.output_state |= (1 << p.data2)
                else:
                    self.output_state &= ~(1 << (p.data2 - 8))
                return self.output_state != old_state
            elif p.data1 == 3:
                self.output_state ^= (1 << p.data2)
                return self.output_state != old_state

            elif p.data1 == 86:
                # In case we get a weird zero when it's not a power meter
                if self.consumption == -1 and self.voltage == -1 and p.data2 == 0:
                    return False
                await self.maybe_detect_sock()
                voltage = 230 if self.voltage <= 0 else self.voltage
                factor = voltage / 10.0
                old_cons = self.consumption
                self.consumption = p.data2 * factor
                self.current = p.data2 / 10.0
                return self.consumption != old_cons
            elif p.data1 == 87:
                await self.maybe_detect_sock()
                # Voltage
                old_voltage = self.voltage
                self.voltage = p.data2
                return self.voltage != old_voltage
            elif p.data1 == 88:
                await self.maybe_detect_sock()
                old_value = self.active_power_bits[0]
                self.active_power_bits[0] = p.data2
                return self.active_power_bits[0] != old_value
            elif p.data1 == 89:
                await self.maybe_detect_sock()
                old_value = self.active_power_bits[1]
                self.active_power_bits[1] = p.data2
                if self.active_power_bits[0] != -1:
                    self.active_power = (self.active_power_bits[0] << 8) + self.active_power_bits[1]
                return self.active_power_bits[1] != old_value

        return False


# Each of the data1 number corresponds to one of the specific fields of the object
METERBUS_FIELDS = {
    0: ('thresh1', None), 10: ('cons1', 'available1'),
    1: ('thresh2', None), 11: ('cons2', 'available2'),
    2: ('thresh3', None), 12: ('cons3', 'available3'),
    3: ('thresh4', None), 13: ('cons4', 'available4'),
}


class IngMeterBus(IngObject):
    def __init__(self, api: 'IngeniumAPI', is_knx: bool, address: int, ctype: IngComponentType,
                 comps: List[IngComponent]):
        super().__init__(api, is_knx, address, ctype, comps)

        self.updating_channels = []

        self.factor = 1

        self.available1: bool = False
        self.available2: bool = False
        self.available3: bool = False
        self.available4: bool = False

        self.cons1: int = 255
        self.cons2: int = 255
        self.cons3: int = 255
        self.cons4: int = 255

        self.thresh1: int = 255
        self.thresh2: int = 255
        self.thresh3: int = 255
        self.thresh4: int = 255

    # def action_set_limit(self, c: IngComponent):
    #    c.update_notify()

    def get_cons(self, channel: int):
        return [self.cons1, self.cons2, self.cons3, self.cons4][channel - 1]

    def get_thresh(self, channel: int):
        return [self.thresh1, self.thresh2, self.thresh3, self.thresh4][channel - 1]

    def get_available(self, channel: int):
        return self.available and [self.available1, self.available2, self.available3, self.available4][channel - 1]

    async def read_state(self):
        self.updating_channels = list(METERBUS_FIELDS.keys())
        await self._read()

    async def _read(self):
        if len(self.updating_channels) > 0:
            chan = self.updating_channels[-1]

            p = Package(0xFF, self.address, 3, chan, 0)
            await self.api.send(p)

    async def update_state(self, p: Package) -> bool:
        if self.address == p.source:
            if len(self.updating_channels) > 0:
                mode = self.updating_channels.pop()

                factor = 230 / 10
                value = p.data2 * factor * self.factor
                available = p.data2 != 255

                if mode not in METERBUS_FIELDS:
                    return False

                key, available_key = METERBUS_FIELDS[mode]
                old_val = getattr(self, key)
                setattr(self, key, value)

                if available_key is not None:
                    setattr(self, available_key, available)

                if len(self.updating_channels) > 0:
                    await self._read()

                return value != old_val

        if self.address != p.target:
            return False

        if p.data1 == 9: # and p.data2 == 50:
            self.factor = 2
            return False

        factor = 230 / 10
        value = p.data2 * factor * self.factor
        available = p.data2 != 255

        if p.data1 not in METERBUS_FIELDS:
            return False

        key, available_key = METERBUS_FIELDS[p.data1]
        old_val = getattr(self, key)
        setattr(self, key, value)

        if available_key is not None:
            setattr(self, available_key, available)

        return value != old_val


SIF_AVAILABLE_MODES = [0, 2, 3, 4]


def convert_sif_value(value, mode: int):
    if mode == 0:
        return value / 5
    elif mode == 2:
        return 1 if value > 0 else 0
    elif mode == 3:
        return value * 10
    elif mode == 4:
        return round(value * 100 / 255, 1)


class IngSif(IngObject):
    def __init__(self, api: 'IngeniumAPI', is_knx: bool, address: int, ctype: IngComponentType,
                 comps: List[IngComponent]):
        super().__init__(api, is_knx, address, ctype, comps)

        self.updating_modes = []

        # [Temperature, Noise(unimplemented), Presence, Illuminance, Humidity]
        self.values = [0, 0, False, 0, 0]
        self.values_255 = [255, 255, 255, 255, 255]
        self.values_len = 5

        self.bat_baja = False

    async def read_state(self):
        self.updating_modes = SIF_AVAILABLE_MODES.copy()
        await self._read()

    async def _read(self):
        if len(self.updating_modes) > 0:
            val = self.updating_modes[-1]

            p = Package(0xFF, self.address, 3, val, 0)
            await self.api.send(p)

    async def update_state(self, p: Package) -> bool:
        if self.address == p.source:
            if len(self.updating_modes) > 0:
                mode = self.updating_modes.pop()

                if mode < self.values_len:
                    old_value = self.values[mode]
                    self.values[mode] = convert_sif_value(p.data2, mode)
                    self.values_255[mode] = p.data2

                    if len(self.updating_modes) > 0:
                        await self._read()

                    return self.values[mode] != old_value

        if self.address != p.target:
            return False

        if p.data1 > self.values_len - 1:
            return False

        old_value = self.values[p.data1]
        self.values[p.data1] = convert_sif_value(p.data2, p.data1)
        self.values_255[p.data1] = p.data2

        if p.command == 23:
            old_bat_baja = self.bat_baja
            self.bat_baja = True
            return not old_bat_baja

        return self.values[p.data1] != old_value

    def get_available(self, mode: int):
        return self.available and self.values_255[mode] != 255

    def get_value(self, mode):
        return self.values[mode]


class IngAirSensor(IngObject):
    def __init__(self, api: 'IngeniumAPI', is_knx: bool, address: int, ctype: IngComponentType,
                 comps: List[IngComponent]):
        super().__init__(api, is_knx, address, ctype, comps)

        self.bit_values = [0, 0, 0, 0, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0]
        self.values = [0, 0]
        self.thresh_values = [0, 0]

    async def update_state(self, p: Package) -> bool:
        if self.address != p.target:
            return False

        old_value = self.bit_values[p.data1]
        self.bit_values[p.data1] = p.data2

        if p.data1 == 3:
            self.values[0] = (self.bit_values[0] << 8) | self.bit_values[1]
            self.values[1] = (self.bit_values[2] << 8) | self.bit_values[3]
            return self.bit_values[3] != old_value

        if p.data1 == 13:
            self.thresh_values[0] = (self.bit_values[10] << 8) | self.bit_values[11]
            self.thresh_values[1] = (self.bit_values[12] << 8) | self.bit_values[13]
            return self.bit_values[13] != old_value

        return False

    def get_available(self, mode: int):
        # If the current mode value is max, or if _both_ mode values are 0, device is unavailable
        return self.values[mode] != 65535 and (self.values[0] != 0 or self.values[1] != 0)

    def get_value(self, mode):
        return self.values[mode]

    def get_threshold_available(self, mode: int):
        return self.thresh_values[mode] != 65535 and self.thresh_values[mode] != 0

    def get_threshold(self, mode):
        return self.thresh_values[mode]


class IngNoiseSensor(IngObject):
    def __init__(self, api: 'IngeniumAPI', is_knx: bool, address: int, ctype: IngComponentType,
                 comps: List[IngComponent]):
        super().__init__(api, is_knx, address, ctype, comps)

        self.value = 255

    async def update_state(self, p: Package) -> bool:
        if self.address != p.target:
            return False

        if p.data1 == 0:
            old_value = self.value
            self.value = p.data2
            return self.value != old_value

        if p.data1 == 1:  # Max value
            pass

        if p.data1 == 2:  # Min value
            pass

        return False

    def get_available(self):
        # If the current mode value is max, or if _both_ mode values are 0, device is unavailable
        return self.value != 255

    def get_value(self):
        return self.value


class IngBusingRegulator(IngObject):
    def __init__(self, api: 'IngeniumAPI', is_knx: bool, address: int, ctype: IngComponentType,
                 comps: List[IngComponent]):
        super().__init__(api, is_knx, address, ctype, comps)

        self.channels = [0, 0, 0, 0]

    async def update_state(self, p: Package) -> bool:
        if self.address != p.target:
            return False

        if p.data1 > 3:
            return False

        old_value = self.channels[p.data1]
        self.channels[p.data1] = p.data2

        return self.channels[p.data1] != old_value

    def get_value(self, channel):
        return self.channels[channel]

    async def set_value(self, channel: int, value: int):
        self.channels[channel] = value
        p = Package(0xFFFF, self.address, 4, channel, value)
        await self.api.send(p)


class IngThermostat(IngObject):
    def __init__(self, api: 'IngeniumAPI', is_knx: bool, address: int, ctype: IngComponentType,
                 comps: List[IngComponent]):
        super().__init__(api, is_knx, address, ctype, comps)

        self.temp = 0
        self.set_point = 0
        self.cmode = 0
        self.wmode = 0

    async def update_state(self, p: Package) -> bool:
        if self.address != p.target:
            return False

        if p.data1 == 0:
            old = self.temp
            self.temp = p.data2 / 5
            return old != self.temp

        elif p.data1 == 1:
            old = self.set_point
            self.set_point = p.data2 / 5
            return old != self.set_point

        elif p.data1 == 10:
            old = self.cmode
            self.cmode = p.data2
            return old != self.cmode

        elif p.data1 == 14:
            old = self.wmode
            self.wmode = p.data2
            return old != self.wmode

        return False

    def get_mode(self):
        #  [HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_HEAT_COOL]
        if self.cmode == 0:
            return 0
        elif self.wmode == 5 or self.wmode == 1:
            return 1
        elif self.wmode == 6 or self.wmode == 2:
            return 2
        elif self.wmode == 7 or self.wmode == 3:
            return 3
        return 0

    def get_action(self):
        # [CURRENT_HVAC_OFF, CURRENT_HVAC_HEAT, CURRENT_HVAC_COOL]
        mode = self.get_mode()
        if mode == 0:
            return 0

        if mode == 1:
            return 1 if self.temp < self.set_point else 0

        if mode == 2:
            return 2 if self.temp > self.set_point else 0

        if mode == 3:
            return 2 if self.temp > self.set_point else 1

    async def set_temp(self, temp):
        self.set_point = temp
        p = Package(0xFFFF, self.address, 4, 1, int(temp * 5))
        await self.api.send(p)

    async def set_mode(self, mode):
        if mode == 0:
            self.cmode = 0
            p = Package(0xFFFF, self.address, 4, 10, 0)
            await self.api.send(p)
        else:
            if self.cmode == 0:
                self.cmode = 1
                p = Package(0xFFFF, self.address, 4, 10, 1)
                await self.api.send(p)
                await asyncio.sleep(0.2)
            self.wmode = mode

            p2 = Package(0xFFFF, self.address, 4, 14, mode + 4)
            await self.api.send(p2)
