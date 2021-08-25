from time import sleep
from .request_base import mindset_request


def aguarda_api_subir():
    while not mindset_request('GET', '').ok:
        sleep(5)
