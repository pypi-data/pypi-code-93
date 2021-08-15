#               Copyright (c) 2021 Zenqi.

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import sys
from hype import Hype
from .utils import import_string
from .rload import Rload
from .event import EventType

try:
    import colorama
    COLOR_SUPPORTED = True
except ModuleNotFoundError:
    COLOR_SUPPORTED = False

from hype.errors import PluginError

app = Hype()


@app.command()
@app.argument('module')
def run(module, delay: int=0):
    
    try:
        _module = import_string(module) 
    except ImportError as e:
        app.echo('[red]It looks like {} is not a module?'.format(module))
        app.exit()

    app.echo("""[magenta]\noooo                            .o8  \n`888                           "888  \noooo d8b  888   .ooooo.   .oooo.    .oooo888  \n`888""8P  888  d88' `88b `P  )88b  d88' `888  \n 888      888  888   888  .oP"888  888   888  \n 888      888  888   888 d8(  888  888   888  \nd888b    o888o `Y8bod8P' `Y888""8o `Y8bod88P" \n       \n [cyan]A hot reloading tool for fast development\n[/cyan]""")

    name = getattr(_module[0], '__name__')
    rload = Rload(name, ['__pycache__'], delay=delay)

    @rload.on('reload')
    def handle_reload(data):
        app.echo('[yellow]RELOADING: [green]%s[/green]' %(data))

    @rload.on('reloaded')
    def handle_reloaded(data):
        app.echo('[yellow]DONE RELOADING: [green]%s[/green]' %(data))

    @rload.on('change')
    def handle_changes(type, data):
        for k, v in data.items():
            app.echo('[cyan]%s: [green]%s[/green]' % (k.upper(), v))

    rload.run(target=_module[1])

@app.command()
def version():
    from rload import __version__ as rver
    from hype import __version__ as hver

    rload_version = rver
    hype_version  = hver
    py_version    = "%s.%s" % (sys.version_info[0], sys.version_info[1])

    app.echo("""[magenta]\noooo                            .o8  \n`888                           "888  \noooo d8b  888   .ooooo.   .oooo.    .oooo888  \n`888""8P  888  d88' `88b `P  )88b  d88' `888  \n 888      888  888   888  .oP"888  888   888  \n 888      888  888   888 d8(  888  888   888  \nd888b    o888o `Y8bod8P' `Y888""8o `Y8bod88P" \n       \n [cyan]A hot reloading tool for fast development\n[/cyan]""")
    app.echo('[cyan]Rload Version: [yellow] %s' % (rload_version))
    app.echo('[cyan]Hype Version: [yellow] %s' % (hype_version))
    app.echo('[cyan]Python Version: [yellow] %s' % (py_version))
    app.echo('\n')
