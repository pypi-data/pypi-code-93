from os import path


from .clinic.list_modules import load_stdlib_sitepackages, load_user_modules, \
    ModulesFinder


def pack(searchpath, stdlib_searchpath, outdir, filename, excludes=None):
    print(
        'Create brython_modules.js with all the modules used by the '
        'application'
    )

    print('Searching brython_stdlib.js...')
    stdlib_dir, stdlib = load_stdlib_sitepackages(
        stdlib_searchpath
    )

    print('Finding packages...')
    user_modules = load_user_modules(searchpath, excludes)
    finder = ModulesFinder(
        stdlib=stdlib,
        user_modules=user_modules,
        excludes=excludes
    )
    finder.inspect()
    outfilename = path.join(outdir, filename)
    finder.make_brython_modules(outfilename)
