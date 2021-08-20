from collections import namedtuple

from refinitiv.dataplatform import configure
from refinitiv.dataplatform.tools._common import urljoin

keys = configure.keys
config = configure.config

delay_coef = 5


class LookupDict(dict):
    """Dictionary lookup object."""

    def __init__(self, name=None):
        self.name = name
        super(LookupDict, self).__init__()

    def __repr__(self):
        return "<lookup '%s'>" % self.name

    def __getitem__(self, key):
        # We allow fall-through here, so values default to None
        return self.__dict__.get(key, None)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


def create_platform_config(connect_term, raw_services):
    validate(raw_services)

    ws_services = [
        service
        for service in convert_services(raw_services)
        if service.transport == "websocket" and "tr_json2" in service.data_fmts
    ]

    target_locations = config.get(keys.stream_connects_locations(connect_term))

    protocol = "wss"
    postfix = "/WebSocket"
    urls = get_urls_by_locations(target_locations, ws_services)
    urls = [f"{protocol}://{url}{postfix}" for url in urls]

    connect_type = config.get(keys.stream_connects_type(connect_term), "OMM")

    default_data_fmt = {"OMM": "tr_json2", "RDP": "rdp_streaming"}.get(
        connect_type, "tr_json2"
    )
    data_fmt = config.get(keys.stream_connects_format(connect_term), default_data_fmt)

    delays = [i * delay_coef for i in range(len(urls))]

    c = LookupDict("PlatformConnectConfig")
    c.connect_type = connect_type
    c.secure = protocol == "wss"
    c.uris = urls
    c.delays = delays
    c.data_fmt = data_fmt
    c.headers = []
    bind(c, make_rotator(urls, "uri"), as_name="set_next_uri")
    bind(c, make_rotator(delays, "delay"), as_name="set_next_delay")
    c.set_next_uri()

    c.proxy_config = None
    c.no_proxy = None

    return c


def create_desktop_config(port, app_key):
    c = LookupDict("DesktopConnectConfig")
    urls = [
        f"127.0.0.1:{port}/api/v1/data/streaming/pricing",
    ]

    delays = [i * delay_coef for i in range(len(urls))]
    c.secure = False
    c.uris = urls
    c.delays = delays
    c.data_fmt = "tr_json2"
    c.headers = [f"x-tr-applicationid: {app_key}"]
    bind(c, make_rotator(urls, "uri"), as_name="set_next_uri")
    bind(c, make_rotator(delays, "delay"), as_name="set_next_delay")
    c.set_next_uri()

    c.proxy_config = None
    c.no_proxy = None

    return c


async def request_services(connect_term, uri, request_func):
    connects_by_term = configure.config.get(configure.keys.stream_connects)
    connect_uri = connects_by_term.get(f"{connect_term}.url")
    version = connects_by_term.get(f"{connect_term}.version", "v1")

    service_key = ""
    if version == "v1":
        service_key = "services"
    elif version == "beta":
        service_key = "service"

    uri = urljoin(uri, connect_uri)
    response = await request_func(uri)
    data = response.json()
    services = data.get(service_key)
    return services


def validate(services):
    pass


def convert_services(raw_services):
    Service = namedtuple(
        "Service", "port, locations, transport, provider, endpoint, data_fmts"
    )
    for raw_service in raw_services:
        port = raw_service.get("port")
        locations = raw_service.get("location", [])
        transport = raw_service.get("transport")
        provider = raw_service.get("provider")
        endpoint = raw_service.get("endpoint")
        data_fmts = raw_service.get("dataFormat", [])

        service = Service(port, locations, transport, provider, endpoint, data_fmts)
        yield service


def has_location(locations, target_location):
    num = len(
        [
            location
            for location in locations
            if location.strip().startswith(target_location)
        ]
    )
    return num > 0


def get_urls_by_locations(locations, services):
    urls = []
    if locations:
        for location in locations:
            for service in services:
                url = f"{service.endpoint}:{service.port}"
                service_locations = service.locations

                if len(service_locations) == 1 and service_locations[0] == location:
                    urls.append(url)
                    break

                has_location(service_locations, location) and urls.append(url)

    else:
        urls.extend(f"{service.endpoint}:{service.port}" for service in services)

    return urls


def bind(instance, func, as_name=None):
    """
    Bind the function *func* to *instance*, with either provided name *as_name*
    or the existing name of *func*. The provided *func* should accept the
    instance as the first argument, i.e. "self".
    """
    if as_name is None:
        as_name = func.__name__
    bound_method = func.__get__(instance, instance.__class__)
    setattr(instance, as_name, bound_method)
    return bound_method


def make_rotator(items, key):
    i = -1
    l = len(items)

    def rotator(self, cmd=""):
        nonlocal i

        if cmd == "reset":
            i = -1

        i = (i + 1) % l
        value = items[i]
        self[key] = value
        return value

    return rotator
