from .proto import ProtoShell, ProtoCmd
from .config import Config


class Env(ProtoShell):

    class Create(ProtoCmd):

        def __init__(self):
            super().__init__('create',
                             'create an api')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the environment")

        def run(self, args):
            res = Config.init().create_environment(args.name)
            if res:
                print('environment {0} created'.format(args.name))
            else:
                print('environment {0} already exists'.format(args.name))

    class List(ProtoCmd):

        def __init__(self):
            super().__init__('list',
                             'list environments')

        def run(self, args):
            envs = Config.init().list_environments()
            active = Config.init().get_active_environment_name()

            for env in envs:
                if env['name'] == active:
                    print('-> {0}'.format(env['name']))
                else:
                    print('   {0}'.format(env['name']))

    class Delete(ProtoCmd):

        def __init__(self):
            super().__init__('delete',
                             'delete an environment')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the environment to be deleted")

        def run(self, args):
            if Config.init().delete_environment(args.name):
                print('environment {0} deleted'.format(args.name))
            else:
                print('unable to delete environment {0}'.format(args.name))

    class Activate(ProtoCmd):

        def __init__(self):
            super().__init__('activate',
                             'activate an environment')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the environment to be set as active")

        def run(self, args):
            env = Config.init().set_active_environment(args.name)
            if env:
                print('environment {0} activated'.format(args.name))
            else:
                print('environment {0} does not exist'.format(args.name))

    class Get(ProtoCmd):

        def __init__(self):
            super().__init__('get',
                             'gets an environment')

        def add_arguments(self, parser):
            parser.add_argument('name', help="specifies the name of the environment to be retrieved, defaults to active", default=None, nargs='?')

        def run(self, args):
            cfg = Config.init()
            name = args.name if args.name else cfg.get_active_environment()
            print(cfg.get_environment(name, yaml=True))

    def __init__(self):
        super().__init__('env', [Env.Create(), Env.List(), Env.Delete(), Env.Get(), Env.Activate()], 'manage environments')