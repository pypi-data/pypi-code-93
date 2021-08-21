def BadRequest(*_):
    print("400 Bad Request")
    raise ConnectionError


def Forbidden(*_):
    print("403 Forbidden")
    raise ConnectionError


def NotFound(*_):
    print("404 Not Found")
    raise ConnectionError


def DiscordError(code):
    print(f"{code} Error")
    raise ConnectionError


def Unknown(code):
    print(f"{code} Error")
    raise ConnectionError


def RateLimited(*_):
    print("Rate Limited")
    raise ConnectionError


class CommandRegistrationError(Exception):
    def error(*args, **kwargs):
        print(f"Command registration failed: Try another command name?")
