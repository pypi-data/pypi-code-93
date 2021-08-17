import asyncio
from typing import Optional, TYPE_CHECKING

from .objects import Package, IngActuator, ACTUATOR_BLIND, IngMeterBus, IngSif, IngThermostat, IngAirSensor

if TYPE_CHECKING:
    from .api import IngeniumAPI

import aiohttp


class CustomConnection:
    def __init__(self, api: 'IngeniumAPI', host: Optional[str], user: Optional[str], passwd: Optional[str]):
        self.api = api

        self._login_dict = {'id': 1, 'kind': 'login', 'host': host, 'user': user, 'passwd': passwd}
        self._id: int = 2

        self._ws_sess: Optional[aiohttp.ClientSession] = None
        self._ws_resp: Optional[aiohttp.ClientWebSocketResponse] = None
        self._is_closed = False

        self._hass_integration = False

    def id(self):
        self._id += 1
        return self._id

    async def _notify_package(self, p: Package):
        # TODO Make sure we aren't throwing any important data away
        # if p.command not in [1, 3, 4, 10, 23]:
        #    print("Unexpected command: " + str(p))
        #    pass

        if p.command not in [4, 23]:
            return

        for o in self.api.objects:
            # Only allow the command 23 on a Sif
            if p.command == 23 and not isinstance(o, IngSif):
                return

            should_update = await o.update_state(p)
            if should_update:
                for c in o.components:
                    try:
                        c.update_notify()
                    except RuntimeError as e:
                        print("Error notifying of change! " + str(e))

    async def _notify_state(self, address: int, available: bool):
        for o in self.api.objects:
            if o.address == address and o.available != available:
                o.available = available
                for c in o.components:
                    try:
                        c.update_notify()
                    except RuntimeError as e:
                        print("Error notifying of change! " + str(e))

    async def async_connect(self, reconnect=False, just_login=False, hass_integration=False):
        self._hass_integration = hass_integration

        if not reconnect and (self._is_closed or (self._ws_resp is not None and not self._ws_resp.closed)):
            return None

        # TODO Launch binary server

        while True:
            try:
                self._is_closed = False
                if self._ws_resp is not None:
                    await self._ws_resp.close()

                self._ws_sess = aiohttp.ClientSession()
                self._ws_resp = await self._ws_sess.ws_connect("ws://127.0.0.1:39812")

                login_body = {'just_login': just_login, 'hass_integration': hass_integration, **self._login_dict}
                await self._ws_resp.send_json(login_body)

                res: dict = await self._ws_resp.receive_json(timeout=300)  # Max 5 mins

                if res.get("kind") != "login":
                    print("Invalid login kind: " + str(res))
                    return None

                return res
            except Exception as e:
                if just_login:
                    return None

                # If we aren't doing the first login, retry this
                await asyncio.sleep(10)

    async def conn_loop(self):
        while not self._is_closed:
            try:
                res: dict = await self._ws_resp.receive_json(timeout=300)  # Max 5 mins
                if res.get("kind") == "raw":
                    await self._notify_package(
                        Package(res["source"], res["target"], res["command"], res["data1"], res["data2"]))
                elif res.get("kind") == "status":
                    await self._notify_state(res["address"], res["available"])
                elif res.get("kind") == "keepAlive":
                    pass
                else:
                    print("Invalid package kind: " + str(res))

            except (aiohttp.ClientError, TypeError, asyncio.TimeoutError) as e:
                print("Connection error, closed: ", repr(e), e)
                if not self._is_closed:
                    self._is_closed = True
                    if self._ws_resp is not None:
                        await self._ws_resp.close()

                    await asyncio.sleep(3)

                    print("Initiating reconnect")
                    await self.async_connect(reconnect=True, hass_integration=self._hass_integration)
                    loop = asyncio.get_event_loop()
                    loop.create_task(self.conn_loop())
                return

    async def send(self, data: Package):
        if data is None or self._ws_resp.closed:
            return

        p = dict(id=self.id(), kind="raw", source=data.source,
                 target=data.target, command=data.command,
                 data1=data.data1, data2=data.data2)
        await self._ws_resp.send_json(p)

    async def close(self):
        self._is_closed = True
        if self._ws_resp is not None:
            await self._ws_resp.close()

    async def delay_cpolling(self):
        await asyncio.sleep(4)
        await self.send(Package(0xFFFF, 0xFFFF, 10, 0, 0))


async def initial_read(api: 'IngeniumAPI'):
    await asyncio.sleep(8)
    for o in api.objects:
        if isinstance(o, IngThermostat):
            await api.connection.send(Package(0xFFFF, o.address, 10, 0, 0))

        elif (isinstance(o, IngMeterBus) or isinstance(o, IngSif) or
              (isinstance(o, IngActuator) and o.mode == ACTUATOR_BLIND)):
            await api.connection.send(Package(0xFFFF, o.address, 10, 0, 0))
            # This is weird on the sif
            # await o.read_state()
        elif isinstance(o, IngAirSensor):
            # A read to data1 10 also does reads for 11-13
            await api.connection.send(Package(0xFFFF, o.address, 3, 10, 0))
        else:
            continue
        await asyncio.sleep(0.5)


async def start_connection(api: 'IngeniumAPI', host: Optional[str], user: Optional[str], paswd: Optional[str],
                           just_login=False, hass_integration=False):
    conn = CustomConnection(api, host, user, paswd)
    api._connection = conn
    login_result = await conn.async_connect(just_login=just_login, hass_integration=hass_integration)
    if login_result is None:
        print("Invalid login result!")
        return None

    if just_login:
        return login_result

    loop = asyncio.get_event_loop()
    loop.create_task(conn.conn_loop())

    loop.create_task(conn.delay_cpolling())
    loop.create_task(initial_read(api))

    return login_result
