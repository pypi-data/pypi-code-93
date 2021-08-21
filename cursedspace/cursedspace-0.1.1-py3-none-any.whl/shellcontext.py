import curses


class ShellContext:
    """Conveniently allows you to run a subprocess in curses shell mode

    Example usage::

        # in a cursedspace.Application
        with ShellContext(self.screen):
            subprocess.run(...)
        self.paint(True)
    """
    def __init__(self, win):
        self.win = win

    def __enter__(self, *args, **kwargs):
        curses.reset_shell_mode()

    def __exit__(self, *args, **kwargs):
        curses.reset_prog_mode()

        self.win.move(0, 0)
        self.win.clear()
        self.win.refresh()

