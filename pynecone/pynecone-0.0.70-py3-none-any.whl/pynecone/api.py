from .proto import ProtoShell, ProtoCmd
from .config import Config

import yaml


class Api(ProtoShell):

    class Auth(ProtoShell):

        class Basic(ProtoCmd):

            def __init__(self):
                super().__init__('basic',
                                 'configure API to use basic authentication')

            def add_arguments(self, parser):
                parser.add_argument('name', help="specifies the api name")
                parser.add_argument('basic_username', help="specifies the username")
                parser.add_argument('basic_password', help="specifies the password")
                parser.add_argument('basic_use_digest', help="specifies whether to use digest")

            def run(self, args):
                cfg = Config.init()
                cfg.put_entry_value('apis', args.name, 'auth_mode', 'BASIC')
                cfg.put_entry_value('apis', args.name, 'basic_username', args.basic_username)
                cfg.put_entry_value('apis', args.name, 'basic_password', args.basic_password)
                cfg.put_entry_value('apis', args.name, 'basic_use_digest', args.basic_use_digest)

        class Cert(ProtoCmd):

            def __init__(self):
                super().__init__('cert',
                                 'configure API to use client certificate based authentication')

            def add_arguments(self, parser):
                parser.add_argument('name', help="specifies the api name")
                parser.add_argument('client_cert', help="specifies the path to the client certificate file")
                parser.add_argument('client_cert_key', help="specifies the path to the client certificate key file")
                parser.add_argument('ca_bundle', help=" the path to the certificate authority file")

            def run(self, args):
                cfg = Config.init()
                cfg.put_entry_value('apis', args.name, 'auth_mode', 'CLIENT_CERT')
                cfg.put_entry_value('apis', args.name, 'client_cert', args.client_cert)
                cfg.put_entry_value('apis', args.name, 'client_cert_key', args.client_cert_key)
                cfg.put_entry_value('apis', args.name, 'ca_bundle', args.ca_bundle)

        class NoAuth(ProtoCmd):

            def __init__(self):
                super().__init__('none',
                                 'disable authentication')

            def add_arguments(self, parser):
                parser.add_argument('name', help="specifies the api name")

            def run(self, args):
                cfg = Config.init()
                cfg.put_entry_value('apis', args.name, 'auth_mode', 'NONE')

        class Secret(ProtoCmd):

            def __init__(self):
                super().__init__('secret',
                                 'configure API to use client key and secret based authentication')

            def add_arguments(self, parser):
                parser.add_argument('name', help="specifies the api name")
                parser.add_argument('client_id', help="specifies the client id")
                parser.add_argument('client_key', help="specifies the client key")
                parser.add_argument('client_secret', help="specifies the client secret")
                parser.add_argument('token_url', help="specifies the token url")

            def run(self, args):
                cfg = Config.init()
                cfg.put_entry_value('apis', args.name, 'auth_mode', 'CLIENT_KEY')
                cfg.put_entry_value('apis', args.name, 'client_id', args.client_id)
                cfg.put_entry_value('apis', args.name, 'client_key', args.client_key)
                cfg.put_entry_value('apis', args.name, 'client_secret', args.client_secret)
                cfg.put_entry_value('apis', args.name, 'token_url', args.token_url)

        class User(ProtoCmd):

            def __init__(self):
                super().__init__('user',
                                 'configure API to use user oauth2 flow')

            def add_arguments(self, parser):
                parser.add_argument('name', help="specifies the api name")
                parser.add_argument('callback_url', help="specifies the callback url")
                parser.add_argument('auth_url', help="specifies the auth url")

            def run(self, args):
                cfg = Config.init()
                cfg.put_entry_value('apis', args.name, 'auth_mode', 'AUTH_URL')
                cfg.put_entry_value('apis', args.name, 'auth_url', args.auth_url)
                cfg.put_entry_value('apis', args.name, 'callback_url', args.callback_url)

        def __init__(self):
            super().__init__('auth', [Api.Auth.NoAuth(),
                                      Api.Auth.Basic(),
                                      Api.Auth.Cert(),
                                      Api.Auth.Secret(),
                                      Api.Auth.User()], 'manage authentication')

    class Url(ProtoShell):

        class Get(ProtoCmd):

            def __init__(self):
                super().__init__('get',
                                 'get api url')

            def add_arguments(self, parser):
                parser.add_argument('name', help="specifies the api name")

            def run(self, args):
                print(Config.init().get_entry_value('apis', args.name, 'url'))

        class Set(ProtoCmd):

            def __init__(self):
                super().__init__('set',
                                 'set api url')

            def add_arguments(self, parser):
                parser.add_argument('name', help="specifies the name of the API")
                parser.add_argument('url', help="specifies the url of the API")

            def run(self, args):
                res = Config.init().put_entry_value('apis', args.name, 'url', args.url)
                if res:
                    return res
                else:
                    print('Unable to modify url parameter for API {0}'.format(args.name))

        def __init__(self):
            super().__init__('url',
                             [Api.Url.Get(), Api.Url.Set()],
                             'manage api url')

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create',
                             'create an API')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the API")
            parser.add_argument('url', help="specifies the url of the API")

        def run(self, args):
            api = Config.init().create_entry('apis', args.name, **{'auth_mode': 'NONE', 'url': args.url})
            if api:
                print('API {0} created'.format(args.name))
            else:
                print('API {0} already exists'.format(args.name))

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get',
                             'get api info')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the api name")

        def run(self, args):
            print(yaml.dump(Config.init().get_entry_cfg('apis', args.name, True)))

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete',
                             'delete an API')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the API")

        def run(self, args):
            res = Config.init().delete_entry('apis', args.name)
            if res:
                return res
            else:
                print('Unable to delete API {0}'.format(args.name))

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list',
                             'list APIs')

        def run(self, args):
            print(Config.init().list_entries('apis'))

    def __init__(self):
        super().__init__('api',
                         [Api.Auth(), Api.Url(), Api.Create(), Api.Delete(), Api.List()],
                         'manage api')



