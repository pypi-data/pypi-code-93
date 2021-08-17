import os

from easycli import Root, Argument, SubCommand


EXIT_SUCCESS = 0
EXIT_FAILURE = 1


class PackDependencies(SubCommand):
    __command__ = 'pack-dependencies'
    __aliases__ = ['pack-deps', 'deps']
    __help__ = 'Create brython_modules.js with all the modules used by the ' \
               'application'
    __arguments__ = [
        Argument(
            '-l', '--stdlib-directory',
            default='.',
            help='The directory to search for brython_stdlib.js. default: ".".'
        ),
        Argument(
            '-s', '--search-directory',
            default='.',
            help='The directory to search for python dependencies. '
                 'default: ".".'
        ),
        Argument(
            '-o', '--output-directory',
            default='.',
            help='The directory to generate the brython modules, default: ".".'
        ),
        Argument(
            '-f', '--filename',
            default='brython_modules.js',
            help='Output filename. default: brython_modules.js.'
        ),
        Argument(
            '-e', '--exclude',
            action='append',
            help='glob pattern to exclude. this option can be specified '
                 'multiple times.'
        )
    ]

    def __call__(self, args):
        from .dependencies import pack
        pack(
            args.search_directory,
            args.stdlib_directory,
            args.output_directory,
            filename=args.filename,
            excludes=args.exclude
        )


class Serve(SubCommand):
    __command__ = 'serve'
    __aliases__ = ['s']
    __help__ = 'Start Brython development server.'
    __arguments__ = [
        Argument(
            '-p', '--port',
            default=8080,
            type=int,
            help='The TCP port to bind. default: 8080.'
        ),
    ]

    def __call__(self, args):
        from .httpserver import start
        start(args.port)


class Pack(SubCommand):
    __command__ = 'pack'
    __aliases__ = ['p']
    __help__ = 'Creates name.brython.js file.'
    __arguments__ = [
        Argument('name', help='Name for newly generated package.'),
        Argument(
            '-d', '--package-directory',
            default='.',
            help='The directory to search for the package, default: ".".'
        ),
        Argument(
            '-o', '--output-directory',
            default='.',
            help='The directory to generate the brython package, default: ".".'
        ),
        Argument(
            '--suffix',
            default='.js',
            help='The suffix to appended to package name as the name for '
                 'output file. default: ".js".'
        ),
        # TODO: Glob pattern
        Argument(
            '-e', '--exclude',
            action='append',
            help='Package name to exclude. this option can be specified '
                 'multiple times.'
        )
    ]

    def __call__(self, args):
        from .pack import create_package
        create_package(
            args.name,
            args.package_directory,
            excludes=args.exclude,
            outpath=args.output_directory,
            suffix=args.suffix
        )
        return EXIT_SUCCESS


class Brython(Root):
    __completion__ = True
    __help__ = 'Brython command line interface'
    __arguments__ = [
        Argument('-V', '--version', action='store_true'),
        Argument(
            '-C', '--change-directory',
            default='.',
            help='Change the current working directory before executing, '
                 'default: ".".'
        ),
        Pack,
        Serve,
        PackDependencies,
    ]

    def _execute_subcommand(self, args):
        if args.change_directory != '.':
            os.chdir(args.change_directory)
        return super()._execute_subcommand(args)

    def __call__(self, args):
        if args.version:
            import brythoncli
            import brython
            print(f'Brython: {brython.__version__}')
            print(f'Brythoncli: {brythoncli.__version__}')
            return

        self._parser.print_help()
        return EXIT_FAILURE
