import os

from xappt_qt.__version__ import __version__, __build__

from xappt_qt.interface import QtInterface

# suppress "qt.qpa.xcb: QXcbConnection: XCB error: 3 (BadWindow)"
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false'

version = tuple(map(int, __version__.split('.'))) + (__build__, )
version_str = f"{__version__}-{__build__}"

executable = None
