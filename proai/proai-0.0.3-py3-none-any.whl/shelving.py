"""Tools for persisting (pickling) machine learning pipelines to disk using `shelf`.

Alternatively, use `dill.dump_session(filepath)` and `dill.load_session(filepath)`
However, `dill.load_session` will only work if all the dependencies are importable and the same version.

Another package `joblib` is designed to work with parallelizable pipelines that work with large data.

Dependencies:
- shelve
- GitPython
"""
import shelve
from pathlib import Path
import datetime
import git

try:
    from pip._internal.operations.freeze import freeze as pip_freeze
except ImportError:  # pip < 10.0
    from pip.operations.freeze import freeze as pip_freeze

DEFAULT_EXCLUDE = ('load_globals', __name__, '__builtins__', 'sklearn', 'pd', 'pandas', 'np', 'numpy', 'shelve', 'tqdm')


def dump_session(
        filepath='python_globals_namespace.shelve',
        include=None,
        exclude=DEFAULT_EXCLUDE):
    """ Use shelf to save all variables in globals() to disk

    TODO: add a git refspec and datetime stamp to the file name and/or contents
    """
    include = include if include is not None else globals().keys()
    shelf = shelve.open(filepath, 'n')  # 'n' for new
    SHELVING_METADATA = dict(
        shelving_started=datetime.datetime.now())
    try:
        repo = git.Repo(str(Path(__file__).resolve().absolute().parent.parent))
        SHELVING_METADATA['git.Repo().active_branch'] = repo.active_branch
        SHELVING_METADATA['git.Repo().head.commit'] = repo.head.commit
        SHELVING_METADATA['git.Repo().head.abspath'] = repo.head.abspath
        SHELVING_METADATA['git.Repo().head.name'] = repo.head.name
        SHELVING_METADATA['git.Repo().head.ref'] = repo.head.ref
        SHELVING_METADATA['git.repo().head.log()[-1]'] = list(repo.head.log())[-1]
        SHELVING_METADATA['pip_freeze'] = list(pip_freeze())
    except TypeError as e:
        print(e)

    shelf['SHELVING_METADATA'] = globals()['SHELVING_METADATA']

    print(f'Shelving...\nfilepath: {filepath}\ninclude: {include}\nignore: {exclude}\n')
    for varname in include:
        if varname in exclude:
            continue
        try:
            shelf[varname] = globals()[varname]
        except (TypeError, KeyError, AttributeError) as e:
            print(f'ERROR shelving: {varname}')
            print(e)
    shelf.close()
    return shelf


def load_session(
        filepath='python_globals_namespace.shelve',
        include=None,
        exclude=DEFAULT_EXCLUDE):
    """ Use shelf to load all variables into globals() from a shelf file on disk """
    filepath = Path(filepath)
    if Path(filepath).suffix in '.dat .dir .bak'.split():
        filepath = filepath.with_suffix('')
    shelf = shelve.open(str(filepath))
    if not include:
        include = shelf.keys()
    if not exclude:
        exclude = DEFAULT_EXCLUDE
    for varname in shelf:
        if varname in exclude:
            continue
        try:
            globals()[varname] = shelf[varname]
        except (TypeError, KeyError, AttributeError) as e:
            print(f'ERROR upickling/unshelving/loading: {varname}')
            print(e)
    shelf.close()
