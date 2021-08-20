from .proto import ProtoShell, ProtoCmd

from .auth import Auth, AuthMode

import requests
import json
import certifi

from requests_toolbelt.utils import dump

from urllib.parse import urljoin

from .config import Config


class RestCmd(ProtoCmd):

    def get_endpoint_url(self, api, path):
        return urljoin(self.get_config().get_entry_value('apis', api, 'url'), path)

    def dump(self, response):
        data = dump.dump_all(response)
        print(data.decode('utf-8'))

    def get_arguments(self, api):
        arguments = {'headers': None, 'cookies': None,
            'auth': None, 'timeout': self.get_config().get_entry_value('apis', api, 'timeout', 20), 'allow_redirects': True, 'proxies': None,
            'hooks': None, 'stream': None, 'cert': None, 'json': None}

        auth = Auth(self.get_config().get_entry_cfg('apis', api))
        mode = auth.get_mode()
        arguments['verify'] = auth.ca_bundle
        print('timeout argument is: ', arguments['timeout'])
        print('verify argument is: ', arguments['verify'])

        if mode == AuthMode.AUTH_URL:
            token = auth.retrieve_token()
            arguments['headers'] = {"Authorization": "Bearer " + token}
        elif mode == AuthMode.CLIENT_KEY:
            token = auth.get_api_token()
            arguments['headers'] = {"Authorization": "Bearer " + token}
        elif mode == AuthMode.CLIENT_CERT:
            arguments['cert'] = (auth.client_cert, auth.client_cert_key)
            if auth.ca_bundle is not None:
                arguments['verify'] = auth.ca_bundle
        elif mode == AuthMode.BASIC:
            arguments['auth'] = auth.get_basic_token()

        return arguments


class Rest(ProtoShell):

    class RestGet(RestCmd):

        def __init__(self):
            super().__init__('get', 'make a REST GET API call')
            self.cfg = Config.init()

        def add_arguments(self, parser):
            parser.add_argument('api', help="specifies the api to use")
            parser.add_argument('path', help="specifies the path", default='/', const='/', nargs='?')
            parser.add_argument('--params', help="list of key:value pairs", nargs='+')
            parser.add_argument('--debug', action='store_true', help="enable debugging")

        def run(self, args):
            return self.get(args.api,
                            args.path,
                            args.debug,
                            dict([kv.split(':') for kv in args.params]) if args.params else None)

        def get(self, api, path, debug=False, params=None):

            resp = requests.get(self.get_endpoint_url(api, path), params=params, **self.get_arguments(api))

            if debug:
                self.dump(resp)

            if resp.status_code == requests.codes.ok:
                if resp.headers.get('content-type').startswith('application/json'):
                    return resp.json()
                else:
                    return resp.content
            elif resp.status_code == 401:
                auth = Auth(self.get_config())
                mode = auth.get_mode()
                if mode == AuthMode.AUTH_URL:
                    auth.login()
                    return self.get(path, debug, params)
                else:
                    print('Unauthorized')
            else:
                if not debug:
                    self.dump(resp)
                return None

    class RestPost(RestCmd):

        def __init__(self):
            super().__init__('post', 'make a POST request on the API')
            self.cfg = Config.init()

        def add_arguments(self, parser):
            parser.add_argument('api', help="specifies the api to use")
            parser.add_argument('path', help="specifies the path", default='/', const='/', nargs='?')
            parser.add_argument('--params', help="list of key:value pairs", nargs='+')
            parser.add_argument('--json', help="json message body")
            parser.add_argument('--debug', action='store_true', help="enable debugging")

        def run(self, args):
            return self.post(args.api,
                             args.path,
                             args.debug,
                             dict([kv.split(':') for kv in args.params]) if args.params else None,
                             json_str=args.json)

        def post(self, api, path, debug=False, params=None, json_str=None):
            arguments = self.get_arguments(api)
            arguments['json'] = json.loads(json_str) if json_str else None

            resp = requests.post(self.get_endpoint_url(api, path), data=params, **arguments)

            if debug:
                self.dump(resp)

            if resp.status_code == requests.codes.ok:
                return resp.json()
            elif resp.status_code == 401:
                auth = Auth(self.get_config())
                mode = auth.get_mode()
                if mode == AuthMode.AUTH_URL:
                    auth.login()
                    return self.post(api, path, debug, params)
                else:
                    print('Unauthorized')
            else:
                if not debug:
                    self.dump(resp)
                return None

    class RestPut(RestCmd):

        def __init__(self):
            super().__init__('put', 'make a PUT request to the API')
            self.cfg = Config.init()

        def add_arguments(self, parser):
            parser.add_argument('api', help="specifies the api to use")
            parser.add_argument('path', help="specifies the path", default='/', const='/', nargs='?')
            parser.add_argument('--params', help="list of key:value pairs", nargs='+')
            parser.add_argument('--json', help="json message body")
            parser.add_argument('--debug', action='store_true', help="enable debugging")

        def run(self, args):
            return self.put(args.api,
                            args.path,
                            args.debug,
                            dict([kv.split(':') for kv in args.params]) if args.params else None,
                            json_str=args.json)

        def put(self, api, path, debug=False, data=None, json_str=None):

            arguments = self.get_arguments(api)
            arguments['json'] = json.loads(json_str) if json_str else None

            resp = requests.put(self.get_endpoint_url(api, path), data=data, **arguments)

            if debug:
                self.dump(resp)

            if resp.status_code == requests.codes.ok:
                return resp.json()
            elif resp.status_code == 401:
                auth = Auth(self.get_config())
                mode = auth.get_mode()
                if mode == AuthMode.AUTH_URL:
                    auth.login()
                    return self.put(api, path, debug, data, json)
                else:
                    print('Unauthorized')
            else:
                print(resp.status_code, resp.text)
                if not debug:
                    self.dump(resp)
                return None

        def put_file(self, api, path, file):

            resp = requests.put(self.get_endpoint_url(api, path), files=dict(file=file), **self.get_arguments())

            if self.get_config().get_debug():
                self.dump(resp)

            if resp.status_code == requests.codes.ok:
                return resp.status_code
            elif resp.status_code == 401:
                auth = Auth(self.get_config())
                mode = auth.get_mode()
                if mode == AuthMode.AUTH_URL:
                    auth.login()
                    return self.put_file(api, path, file)
                else:
                    print('Unauthorized')
            else:
                print(resp.status_code, resp.text)
                if not self.get_config().get_debug():
                    self.dump(resp)
                return None

    class RestDelete(RestCmd):

        def __init__(self):
            super().__init__('delete', 'make a DELETE request to the API')
            self.cfg = Config.init()

        def add_arguments(self, parser):
            parser.add_argument('api', help="specifies the api to use")
            parser.add_argument('path', help="specifies the path", default='/', const='/', nargs='?')
            parser.add_argument('--debug', action='store_true', help="enable debugging")

        def run(self, args):
            return self.delete(args.api, args.path, args.debug)

        def delete(self, api, path, debug=False):

            resp = requests.delete(self.get_endpoint_url(api, path), **self.get_arguments(api))

            if debug:
                self.dump(resp)

            if resp.status_code == requests.codes.ok:
                return resp.json()
            elif resp.status_code == 401:
                auth = Auth(self.get_config())
                mode = auth.get_mode()
                if mode == AuthMode.AUTH_URL:
                    auth.login()
                    return self.delete(api, path, debug)
                else:
                    print('Unauthorized')
            else:
                if not debug:
                    self.dump(resp)
                return None

    def __init__(self):
        super().__init__('rest', [Rest.RestGet(),
                                  Rest.RestPost(),
                                  Rest.RestPut(),
                                  Rest.RestDelete()], 'makes standard Rest calls')

