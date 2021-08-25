#!python

import sys
import redis
import json
import requests
import time
import argparse
import logging

def get_redis():

    if args.redis.startswith('/'):
        path = args.redis
        host = None
        port = None
    else:
        host, port = args.redis.split(':')
        path = None

    print(f"connect to unix: {path} network: {host}:{port}")
    return redis.Redis(
        db=args.db,
        unix_socket_path=path, 
        host=host, port=port,
        decode_responses=True)

def iteration(redis):
        request = redis.lpop(args.queue)
        if request:
            req = json.loads(request)
            method = req['method'].upper()
            url = req['url']
            payload = req['payload']
            if payload:
                payload_len = len(payload)
            else:
                payload_len = 0

            log.debug(f"processing {method} {url}")
            r = None
            try:

                if method == 'GET':
                    r = requests.get(url, timeout=args.timeout)
                elif method == 'POST':
                    r = requests.post(url, data = payload, timeout=args.timeout)
                else:
                    print("unknown method", method)
            except requests.exceptions.RequestException as e:
                log.info("err while report to {}: {}".format(url, e))
            else:
                log.info(f"reported ({r.status_code}) to {method} {url} payload: {payload_len}")
            finally:
                log.debug(f"result: {r}")
                return True
        else:
            return False

def loop(redis):
    while True:
        if not iteration(redis):
            time.sleep(1)

def main():

    global log, args

    def_redis = 'localhost:6379'
    def_queue = 'http_requests_queue'

    parser = argparse.ArgumentParser(description='Redis-to-HTTP proxy')
    parser.add_argument('-v', dest='verbose', action='store_true',
        default=False, help='verbose mode')
    parser.add_argument('-t', dest='timeout', type=int, default=3,
        help='HTTP timeout in seconds')
    parser.add_argument('-n', dest='db', type=int, default=0,
        help='Redis database number (0 default)')
    parser.add_argument('--one', default=False, action='store_true',
        help='Run just one iteration')
    parser.add_argument('--send', nargs='+',
        help='Client mode, put request to db, e.g. --send POST http://example.com/path ["payload"]')
    parser.add_argument('--redis', default=def_redis,
        help=f'redis location unix/network socket def: {def_redis}')
    parser.add_argument('-q', '--queue', default=def_queue,
        help=f'queue (list) key name def: {def_queue}')

    args = parser.parse_args()

    #signal.signal(signal.SIGINT, sighandler)

    logging.basicConfig(
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.INFO)

    log = logging.getLogger()

    if args.verbose:
        log.setLevel(logging.DEBUG)
        log.debug('Verbose mode')
        # err = logging.StreamHandler(sys.stderr)
        # log.addHandler(err)

    log.info('Redis2HTTP started')

    r = get_redis()
    if args.send:
        print(args.send)
        data = {
            'method': args.send[0],
            'url': args.send[1],
            'payload': args.send[2] if len(args.send)>=3 else None
        }
        request = json.dumps(data)
        r.lpush(args.queue, request)

    elif args.one:
        iteration(r)
    else:
        loop(r)

main()
