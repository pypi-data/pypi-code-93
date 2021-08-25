from .ip_to_int import ip_to_int, int_to_ip


class IP:
	def __init__(self, x):
		if isinstance(x, str):
			if '.' not in x:
				x = int(x)

		if isinstance(x, IP):
			self._int = x._int
			self._string = x._string

		elif isinstance(x, str):
			self._string = x
			self._int = ip_to_int(x)

		elif isinstance(x, int):
			self._int = x
			self._string = int_to_ip(x)

		else:
			raise ValueError(f'Cannot accept {x} of type {type(x)}')

	@property
	def int(self):
		"""
		:rtype: int
		"""
		return self._int

	def __repr__(self):
		return f'ip:{self._string}'

	def __str__(self):
		return self._string

	def __lt__(self, other):
		if not isinstance(other, IP):
			other = IP(other)

		return self._int < other._int

	def __gt__(self, other):
		if not isinstance(other, IP):
			other = IP(other)
		return self._int > other._int

	def __eq__(self, other):
		if not isinstance(other, IP):
			other = IP(other)
		return self._int == other._int

	def __ge__(self, other):
		if not isinstance(other, IP):
			other = IP(other)
		return self._int >= other._int

	def __le__(self, other):
		if not isinstance(other, IP):
			other = IP(other)
		return self._int <= other._int

	def __ne__(self, other):
		if not isinstance(other, IP):
			other = IP(other)
		return self._int != other._int
