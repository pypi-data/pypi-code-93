import argparse
import asyncio
from l0n0lnat.ReverseServer import ReverseServer
from l0n0lnat.ReverseClient import ReverseClient
from l0n0lnat.EncChaCha20 import EncChaCha20
from hashlib import md5


def make_chacha20(password: str):
    if isinstance(password, str):
        password = password.encode()
    m = md5()
    m.update(password)
    passwd = m.hexdigest().encode()
    return EncChaCha20(passwd)


def run_reverse_server():
    parser = argparse.ArgumentParser(description="创建内网穿透服务器")
    parser.add_argument("listenhost", type=str, help="监听host")
    parser.add_argument("listenport", type=int, help="监听端口")
    parser.add_argument("password", type=str, help="密钥", default='')
    args = parser.parse_args()

    async def main():
        if len(args.password) == 0:
            server = ReverseServer(args.listenhost, args.listenport)
        else:
            enc = make_chacha20(args.password)
            server = ReverseServer(args.listenhost, args.listenport, enc)

        await server.start()

    asyncio.get_event_loop().create_task(main())
    try:
        print("Press Ctrl+C to Close.")
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop = asyncio.get_event_loop()
        for task in asyncio.Task.all_tasks(loop):
            task.cancel()
        loop.stop()


def run_reverse_client():
    parser = argparse.ArgumentParser(description="创建内网穿透客户端")
    parser.add_argument("serverhost", type=str, help="监听host")
    parser.add_argument("serverport", type=int, help="监听端口")
    parser.add_argument("serverlistenport", type=int, help="服务器要监听端口")
    parser.add_argument("localhost", type=str, help="本地服务host")
    parser.add_argument("localport", type=int, help="本地服务端口")
    parser.add_argument("password", type=str, help="密钥", default=b'')
    args = parser.parse_args()

    async def main():
        if len(args.password) == 0:
            client = ReverseClient(args.serverhost,
                                   args.serverport,
                                   args.localhost,
                                   args.localport,
                                   args.serverlistenport)
        else:
            enc = make_chacha20(args.password)
            client = ReverseClient(args.serverhost,
                                   args.serverport,
                                   args.localhost,
                                   args.localport,
                                   args.serverlistenport,
                                   enc)

        await client.start()

    asyncio.get_event_loop().create_task(main())
    try:
        print("Press Ctrl+C to Close.")
        asyncio.get_event_loop().run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        loop = asyncio.get_event_loop()
        for task in asyncio.Task.all_tasks(loop):
            task.cancel()
        loop.stop()
