import os
import sys

import xappt_qt
import xappt_qt.browser
import xappt_qt.launcher
import xappt_qt.builder


def main() -> int:
    argc = len(sys.argv)
    if argc == 1:
        return xappt_qt.browser.entry_point()
    else:
        if sys.argv[1] == "builder" and argc > 2:
            return xappt_qt.builder.main(sys.argv[2:])
        return xappt_qt.launcher.entry_point()


if __name__ == '__main__':
    if getattr(xappt_qt, "__compiled__", None) is not None:
        xappt_qt.executable = os.path.abspath(sys.argv[0])
    elif getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        xappt_qt.executable = os.path.abspath(sys.executable)
    sys.exit(main())
