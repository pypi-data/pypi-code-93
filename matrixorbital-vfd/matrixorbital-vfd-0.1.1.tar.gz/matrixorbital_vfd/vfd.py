from enum import Enum

from smbus2 import SMBus

CHARMAP = str.maketrans({
	' ':  0x20, '0': 0x30, '@': 0x40, 'P': 0x50, '`': 0x60, 'p': 0x70, '♪':  0x19,
	'!':  0x21, '1': 0x31, 'A': 0x41, 'Q': 0x51, 'a': 0x61, 'q': 0x71, '℃':  0x1a,
	'"':  0x22, '2': 0x32, 'B': 0x42, 'R': 0x52, 'b': 0x62, 'r': 0x72, '℉':  0x1b,
	'#':  0x23, '3': 0x33, 'C': 0x43, 'S': 0x53, 'c': 0x63, 's': 0x73, '⇓':  0x1c,
	'$':  0x24, '4': 0x34, 'D': 0x44, 'T': 0x54, 'd': 0x64, 't': 0x74, '⇒':  0x1d,
	'%':  0x25, '5': 0x35, 'E': 0x45, 'U': 0x55, 'e': 0x65, 'u': 0x75, '⇐':  0x1e,
	'&':  0x26, '6': 0x36, 'F': 0x46, 'V': 0x56, 'f': 0x66, 'v': 0x76, '⇑':  0x1f,
	"'":  0x27, '7': 0x37, 'G': 0x47, 'W': 0x57, 'g': 0x67, 'w': 0x77, '\\': 0x8c,
	'(':  0x28, '8': 0x38, 'H': 0x48, 'X': 0x58, 'h': 0x68, 'x': 0x78, '≠':  0x8d,
	')':  0x29, '9': 0x39, 'I': 0x49, 'Y': 0x59, 'i': 0x69, 'y': 0x79, '~':  0x8e,
	'*':  0x2a, ':': 0x3a, 'J': 0x4a, 'Z': 0x5a, 'j': 0x6a, 'z': 0x7a, '•':  0x96,
	'+':  0x2b, ';': 0x3b, 'K': 0x4b, '[': 0x5b, 'k': 0x6b, '{': 0x7b, '≤':  0x9b,
	',':  0x2c, '<': 0x3c, 'L': 0x4c, '¥': 0x5c, 'l': 0x6c, '|': 0x7c, '≥':  0x9c,
	'-':  0x2d, '=': 0x3d, 'M': 0x4d, ']': 0x5d, 'm': 0x6d, '}': 0x7d, '↑':  0x9e,
	'.':  0x2e, '>': 0x3e, 'N': 0x4e, '^': 0x5e, 'n': 0x6e, '→': 0x7e, '↓':  0x9f,
	'/':  0x2f, '?': 0x3f, 'O': 0x4f, '_': 0x5f, 'o': 0x6f, '←': 0x7f, 'º':  0xdf,
	'\n': 0x0a,
})

class Brightness(int, Enum):
	HIGH = 0x00
	MEDIUM = 0x01
	LOW = 0x02
	LOWEST = 0x03

class VFD:
	def __init__(self, bus, addr):
		self.bus = bus
		self.addr = addr

	def __enter__(self):
		self.open()
		return self

	def __exit__(self, *args):
		self.close()

	def open(self):
		self.smbus = SMBus(self.bus)

	def close(self):
		if self.smbus:
			self.smbus.close()

	def display(self, enable=True):
		"""turn display on/off"""

		self.smbus.write_byte_data(self.addr, 0xfe, 0x42 if enable else 0x46)

	def home(self):
		"""move cursor to home 0x0 position"""

		self.smbus.write_byte_data(self.addr, 0xfe, 0x48)

	def position(self, col, row):
		"""move cursor to col x row position"""

		self.smbus.write_byte_data(self.addr, 0xfe, 0x47)
		self.smbus.write_byte_data(self.addr, col, row)

	def move(self, direction):
		"""move cursor 'left' or 'right'"""

		if direction == 'left':
			self.smbus.write_byte_data(self.addr, 0xfe, 0x4c)
		elif direction == 'right':
			self.smbus.write_byte_data(self.addr, 0xfe, 0x4d)
		else:
			raise ValueError('invalid direction')

	def clear(self):
		"""clear screen"""

		self.smbus.write_byte_data(self.addr, 0xfe, 0x58)

	def brightness(self, value):
		"""set display brightness, using Brightness enum"""

		value = getattr(Brightness, value, None)
		if value is None:
			raise ValueError('invalid brightness')

		self.smbus.write_word_data(self.addr, 0xfe, (value << 8) + 0x59)

	def cursor(self, enable=True):
		"""enable/disable block (blinking) cursor"""

		self.smbus.write_byte_data(self.addr, 0xfe, 0x53 if enable else 0x54)

	def wrap(self, enable=True):
		"""enable/disable line wrapping"""

		self.smbus.write_byte_data(self.addr, 0xfe, 0x43 if enable else 0x44)

	def scroll(self, enable=True):
		"""enable/disable auto line scrolling"""

		self.smbus.write_byte_data(self.addr, 0xfe, 0x51 if enable else 0x52)

	def write(self, string):
		"""write text to display"""

		string = ''.join(x for x in string if ord(x) in CHARMAP)
		string = string.translate(CHARMAP)
		for c in string.encode():
			self.smbus.write_byte(self.addr, c)
