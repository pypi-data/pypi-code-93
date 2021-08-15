"""
Advanced text container for Minecraft
Credit: Pandaria98 https://github.com/Pandaria98 https://github.com/TISUnion/stext
"""

import json
from enum import Enum, auto
from typing import Iterable, List, Union, Optional, Any, Tuple

from colorama import Fore, Style


class RItem:
	def __init__(self, mc_code: str, console_code: str):
		self.mc_code = mc_code
		self.console_code = console_code


class RColor(Enum):
	black = RItem('§0', Fore.BLACK)
	dark_blue = RItem('§1', Fore.BLUE)
	dark_green = RItem('§2', Fore.GREEN)
	dark_aqua = RItem('§3', Fore.CYAN)
	dark_red = RItem('§4', Fore.RED)
	dark_purple = RItem('§5', Fore.MAGENTA)
	gold = RItem('§6', Fore.YELLOW)
	gray = RItem('§7', Style.RESET_ALL)
	dark_gray = RItem('§8', Style.RESET_ALL)
	blue = RItem('§9', Fore.LIGHTBLUE_EX)
	green = RItem('§a', Fore.LIGHTGREEN_EX)
	aqua = RItem('§b', Fore.LIGHTCYAN_EX)
	red = RItem('§c', Fore.LIGHTRED_EX)
	light_purple = RItem('§d', Fore.LIGHTMAGENTA_EX)
	yellow = RItem('§e', Fore.LIGHTYELLOW_EX)
	white = RItem('§f', Style.RESET_ALL)

	reset = RItem('§r', Style.RESET_ALL)


class RColorConvertor:
	MC_COLOR_TO_CONSOLE = dict([(rcolor.value.mc_code, rcolor.value.console_code) for rcolor in RColor])
	MC_COLOR_TO_RCOLOR = dict([(rcolor.value.mc_code, rcolor) for rcolor in RColor])
	RCOLOR_TO_CONSOLE = dict([(rcolor, rcolor.value.console_code) for rcolor in RColor])
	RCOLOR_NAME_TO_CONSOLE = dict([(rcolor.name, rcolor.value.console_code) for rcolor in RColor])


class RStyle(Enum):
	bold = RItem('§l', Style.BRIGHT)
	italic = RItem('§o', '')
	underlined = RItem('§n', '')
	strikethrough = RItem('§m', '')
	obfuscated = RItem('§k', '')


class RAction(Enum):
	suggest_command = auto()
	run_command = auto()
	open_url = auto()
	open_file = auto()
	copy_to_clipboard = auto()


class RTextBase:
	def to_json_object(self):
		raise NotImplementedError()

	def to_json_str(self) -> str:
		return json.dumps(self.to_json_object(), ensure_ascii=False)

	def to_plain_text(self) -> str:
		raise NotImplementedError()

	def to_colored_text(self) -> str:
		raise NotImplementedError()

	def copy(self) -> 'RTextBase':
		raise NotImplementedError()

	def set_color(self, color: RColor) -> 'RTextBase':
		raise NotImplementedError()

	def set_styles(self, styles: Union[RStyle, Iterable[RStyle]]) -> 'RTextBase':
		raise NotImplementedError()

	def set_click_event(self, action: RAction, value: str) -> 'RTextBase':
		raise NotImplementedError()

	def set_hover_text(self, *args) -> 'RTextBase':
		raise NotImplementedError()

	def c(self, action: RAction, value: str) -> 'RTextBase':
		return self.set_click_event(action, value)

	def h(self, *args) -> 'RTextBase':
		return self.set_hover_text(*args)

	def __str__(self):
		return self.to_plain_text()

	def __add__(self, other):
		return RTextList(self, other)

	def __radd__(self, other):
		return RTextList(other, self)

	@staticmethod
	def from_any(text) -> 'RTextBase':
		"""
		:param text: can be a RTextBase, or a str, or anything
		:rtype: RTextBase
		"""
		if isinstance(text, RTextBase):
			return text
		return RText(text)

	@staticmethod
	def join(divider: Any, iterable: Iterable[Any]) -> 'RTextBase':
		result = RTextList()
		for i, item in enumerate(iterable):
			if i > 0:
				result.append(divider)
			result.append(item)
		return result

	@staticmethod
	def format(fmt: str, *args, **kwargs) -> 'RTextBase':
		args = list(args)
		kwargs = kwargs.copy()
		counter = 0
		rtext_elements = []  # type: List[Tuple[str, RTextBase]]

		def get():
			nonlocal counter
			rv = '@@MCDR#RText.format#Placeholder#{}@@'.format(counter)
			counter += 1
			return rv

		for i, arg in enumerate(args):
			if isinstance(arg, RTextBase):
				placeholder = get()
				rtext_elements.append((placeholder, arg))
				args[i] = placeholder
		for key, value in kwargs.items():
			if isinstance(value, RTextBase):
				placeholder = get()
				rtext_elements.append((placeholder, value))
				kwargs[key] = placeholder

		texts = [fmt.format(*args, **kwargs)]
		for placeholder, rtext in rtext_elements:
			new_texts = []
			for text in texts:
				processed_text = []
				if isinstance(text, str):
					for j, ele in enumerate(text.split(placeholder)):
						if j > 0:
							processed_text.append(rtext)
						processed_text.append(ele)
				else:
					processed_text.append(text)
				new_texts.extend(processed_text)
			texts = new_texts
		return RTextList(*texts)


class RText(RTextBase):
	def __init__(self, text, color: Optional[RColor] = None, styles: Optional[Union[RStyle, Iterable[RStyle]]] = None):
		if isinstance(text, type(self)):
			self._copy_from(text)
		else:
			self.data = {'text': str(text)}  # type: dict
			if color is not None:
				self.set_color(color)
			if styles is not None:
				self.set_styles(styles)

	def _copy_from(self, text: 'RText'):
		self.data = text.data.copy()

	def set_color(self, color: RColor):
		self.data['color'] = color.name
		return self

	def set_styles(self, styles: Union[RStyle, Iterable[RStyle]]):
		if isinstance(styles, RStyle):
			styles = {styles}
		elif isinstance(styles, Iterable):
			styles = set(styles)
		else:
			raise TypeError('Unsupported style type {}'.format(type(styles)))
		for style in RStyle:
			if style in styles:
				self.data[style.name] = True
			elif style.name in self.data:
				self.data.pop(style.name)
		return self

	def set_click_event(self, action: RAction, value: str):
		self.data['clickEvent'] = {
			'action': action.name,
			'value': value
		}
		return self

	def set_hover_text(self, *args):
		self.data['hoverEvent'] = {
			'action': 'show_text',
			'value': {
				'text': '',
				'extra': RTextList(*args).to_json_object(),
			}
		}
		return self

	def to_json_object(self):
		return self.data

	def to_plain_text(self) -> str:
		return self.data['text']

	def to_colored_text(self) -> str:
		color = RColorConvertor.RCOLOR_NAME_TO_CONSOLE[self.data['color']] if 'color' in self.data else ''
		for style in RStyle:
			if self.data.get(style.name, False):
				color += style.value.console_code
		return color + self.to_plain_text() + Style.RESET_ALL

	def copy(self) -> 'RText':
		copied = RText('')
		copied._copy_from(self)
		return copied


class RTextTranslation(RText):
	def __init__(self, translation_key, color: RColor = RColor.reset, styles: Optional[Union[RStyle, Iterable[RStyle]]] = None):
		super().__init__(translation_key, color, styles)
		self.data.pop('text')
		self.data['translate'] = translation_key

	def to_plain_text(self) -> str:
		return self.data['translate']

	def copy(self) -> 'RTextTranslation':
		copied = RTextTranslation('')
		copied._copy_from(self)
		return copied


class RTextList(RTextBase):
	def __init__(self, *args):
		self.header = RText('')
		self.header_empty = True
		self.children = []  # type: List[RTextBase]
		self.append(*args)

	def set_color(self, color: RColor):
		self.header.set_color(color)
		self.header_empty = False
		return self

	def set_styles(self, styles: Union[RStyle, Iterable[RStyle]]):
		self.header.set_styles(styles)
		self.header_empty = False
		return self

	def set_click_event(self, action: RAction, value):
		self.header.set_click_event(action, value)
		self.header_empty = False
		return self

	def set_hover_text(self, *args):
		self.header.set_hover_text(*args)
		self.header_empty = False
		return self

	def append(self, *args) -> 'RTextList':
		for obj in args:
			if isinstance(obj, RTextList):
				self.children.extend(obj.children)
			elif isinstance(obj, RTextBase):
				self.children.append(obj)
			else:
				self.children.append(RText(obj))
		return self

	def is_empty(self) -> bool:
		return len(self.children) == 0

	def to_json_object(self) -> list:
		ret = ['' if self.header_empty else self.header.to_json_object()]
		ret.extend(map(lambda rtext: rtext.to_json_object(), self.children))
		return ret

	def to_plain_text(self) -> str:
		return ''.join(map(lambda rtext: rtext.to_plain_text(), self.children))

	def to_colored_text(self) -> str:
		return ''.join(map(lambda rtext: rtext.to_colored_text(), self.children))

	def copy(self) -> 'RTextList':
		copied = RTextList()
		copied.header = self.header.copy()
		copied.header_empty = self.header_empty
		copied.children = [child.copy() for child in self.children]
		return copied
