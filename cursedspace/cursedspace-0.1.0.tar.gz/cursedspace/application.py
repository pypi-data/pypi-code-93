import locale
import curses

from .colors import Colors
from .key import Key


class Application:
    """A generic application with curses

    Use self.screen for drawing operations"""
    def __init__(self):
        self.screen = None
        self.is_initialized = False
        self.preferred_encoding = None

    def refresh(self, force=False):
        """Refreshes the screen

        If force is set to True, it will touch the screen first
        to enforce a full refresh"""
        if force:
            self.screen.touchwin()
        self.screen.noutrefresh()

    def size(self):
        """Refreshes the size of the screen and returns the (height,width) tuple"""
        curses.update_lines_cols()
        return self.screen.getmaxyx()

    def main(self):
        """Your entry point for the main loop"""
        raise NotImplementedError()

    def read_key(self):
        """Read the next key press from the system

        Returns a cursedspace.Key instance"""
        return Key.read(self.screen)

    def run(self):
        """The main function to call when actually running the application"""
        exception = None

        try:
            self.init_curses()
            self.main()
        except Exception as exc:
            exception = exc

        self.end_curses()

        if exception is not None:
            raise exception

    def init_colors(self):
        """Initializes the basic foreground colors and sets up color pairs for each"""
        curses.use_default_colors()
        curses.init_pair(Colors.DEFAULT, curses.COLOR_BLACK, -1)
        curses.init_pair(Colors.RED, curses.COLOR_RED, -1)
        curses.init_pair(Colors.GREEN, curses.COLOR_GREEN, -1)
        curses.init_pair(Colors.YELLOW, curses.COLOR_YELLOW, -1)
        curses.init_pair(Colors.BLUE, curses.COLOR_BLUE, -1)
        curses.init_pair(Colors.CYAN, curses.COLOR_CYAN, -1)
        curses.init_pair(Colors.MAGENTA, curses.COLOR_MAGENTA, -1)

    def init_curses(self):
        """Will be called prior to using any curses operations in self.run()

        Normally you should not have to call this."""
        if self.is_initialized:
            return

        locale.setlocale(locale.LC_ALL, '')
        self.preferred_encoding = locale.getpreferredencoding()

        self.screen = curses.initscr()
        curses.def_shell_mode()

        if curses.has_colors():
            curses.start_color()
            self.init_colors()

        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)

        curses.def_prog_mode()

        self.is_initialized = True


    def end_curses(self):
        try:
            curses.endwin()
        except:
            pass

    def __delete__(self):
        self.end_curses()

