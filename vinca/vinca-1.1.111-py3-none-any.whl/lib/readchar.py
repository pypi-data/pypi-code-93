ESC = chr(27)
ESCC = ESC + '['
DEL = DELETE = ESCC + '3~'
BACK = BACKSPACE = chr(127)
UP, DOWN, LEFT, RIGHT = ESCC + chr(65), ESCC + chr(66), ESCC + chr(67) ,ESCC + chr(68)
KEYS = (DEL, UP, DOWN, LEFT, RIGHT)

# readchar
try:
	import termios, sys, tty
	def readchar():
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(fd)
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch
except ImportError:
	from msvcrt import getch as readchar  # Windows support

def readkey():
	c = readchar()
	if c != ESC:
		return c
	key = c  # we build up the key character by character
	while any([k.startswith(key) for k in KEYS]):
		key += readchar()
		if key in KEYS:
			return key

