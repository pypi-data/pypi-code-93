from l0n0lutils.funcs import on_close_function, asyncio_run_forever
import asyncio

clients = {}
servers = {}


def regist_client(c):
    clients[c] = True


def regist_server(s):
    servers[s] = True


def unregist_client(c):
    if clients.get(c):
        del clients[c]


def unregist_server(s):
    if servers.get(s):
        del servers[s]


@on_close_function
def on_process_close():
    for c in clients.keys():
        c.close(False)
        print(c)
    clients.clear()

    for s in servers.keys():
        s.close(False)
    servers.clear()


def run_forever(loop: asyncio.BaseEventLoop = None):
    asyncio_run_forever(loop)
