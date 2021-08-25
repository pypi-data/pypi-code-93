from ..basic import AdvancedEnum, AbbreviatedEnum

class Http(AbbreviatedEnum):
    GET = 1,
    POST = 2,
    PUT = 3

class Endpoint(AdvancedEnum, AbbreviatedEnum):
    def __init__(self, _:int, methods: list[Http], path: str) -> None:
        self.ValidMethods: list[Http] = methods
        self.Path = path

# todo, endpoints to dict, not enum
class ServerEndpoint(Endpoint):
    LOGIN = 1, [Http.POST], 'login'
    AUTHENTICATE = 2, [Http.POST], 'authenticate'
    INIT = 3, [Http.GET], 'init'
    ADD = 4, [Http.POST], 'add'
    LIST = 5, [Http.POST], 'list'
    CALL = 6, [Http.POST], 'call'
    SEARCH = 7, [Http.POST], 'search'

class ELabEndpoint(Endpoint):
    LOGIN = 1, [Http.POST], 'auth/user'
    SAMPLES = 2, [Http.POST, Http.GET], 'samples'

class ProviderEndpoint(Endpoint):
    CHECK_STATUS = 1, [Http.GET], 'status'
    GET_SCHEMA = 2, [Http.GET], 'schema'
    MAKE_REQUEST = 3, [Http.POST], 'generic' # this is tied to the method name in Handler
