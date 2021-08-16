from vinca.lib import ansi
import shutil

COLUMNS, LINES = shutil.get_terminal_size()

# A Context Manager for the terminal's alternate screen
class AlternateScreen:

	def __init__(self):
		pass

	def __enter__(self):
		ansi.save_cursor()
		ansi.hide_cursor()
		ansi.save_screen()
		ansi.clear()
		ansi.move_to_top()

	def __exit__(self, *exception_args):
		ansi.restore_screen()
		ansi.restore_cursor()
