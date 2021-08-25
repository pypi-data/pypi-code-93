from .ip_to_int import get_ip_range, get_ip_range_int, ip_to_int
from .IP import IP
import bisect

class CidrBlock:
	def __init__(self, s):
		if isinstance(s, CidrBlock):
			self._start_ip = s.start
			self._end_ip = s.end
			self._bits = s.bits
		else:
			start_ip, end_ip = get_ip_range(s)
			self._bits = int(s.split('/')[1])
			self._start_ip = IP(start_ip)
			self._end_ip = IP(end_ip)

	@property
	def start(self):
		"""
		:rtype: IP
		"""
		return self._start_ip

	@property
	def end(self):
		"""
		:rtype: IP
		"""
		return self._end_ip

	@property
	def bits(self):
		"""
		:rtype: int
		"""
		return self._bits

	def contains(self, item):
		if isinstance(item, str):
			if '/' in item:
				item = CidrBlock(item)

		if isinstance(item, (CidrBlock, IPSpace)):
			return self.start <= item.start and item.end <= self.end

		if not isinstance(item, IP):
			item = IP(item)
		return self.start <= item and item <= self.end

	def is_adjacent_to(self, other):
		if not isinstance(other, CidrBlock):
			other = CidrBlock(other)
		if other.start.int - self.end.int == 1:
			return True
		elif self.start.int - other.end.int == 1:
			return True
		else:
			return False

	@property
	def size(self):
		return 2 ** (32 - self.bits)

	def __str__(self):
		return f'{self.start}/{self.bits}'

	def __repr__(self):
		return f'CIDR Block: {str(self)}'

	def __lt__(self, other):
		if not isinstance(other, CidrBlock):
			other = CidrBlock(other)
		return (self.bits, self.start) < (other.bits, other.start)

	def __contains__(self, item):
		return self.contains(item)

	def __gt__(self, other):
		if not isinstance(other, CidrBlock):
			other = CidrBlock(other)
		return (self.bits, self.start) > (other.bits, other.start)

	def __le__(self, other):
		if not isinstance(other, CidrBlock):
			other = CidrBlock(other)
		return (self.bits, self.start) <= (other.bits, other.start)

	def __ge__(self, other):
		if not isinstance(other, CidrBlock):
			other = CidrBlock(other)
		return (self.bits, self.start) >= (other.bits, other.start)

	def __eq__(self, other):
		if not isinstance(other, CidrBlock):
			other = CidrBlock(other)
		return (self.bits, self.start) == (other.bits, other.start)

	def __ne__(self, other):
		if not isinstance(other, CidrBlock):
			other = CidrBlock(other)
		return (self.bits, self.start) != (other.bits, other.start)

	def __add__(self, other):
		if not isinstance(other, (CidrBlock, IPSpace)):
			other = CidrBlock(other)

		if isinstance(other, CidrBlock):
			if self in other:
				return other
			elif other in self:
				return self
			else:
				return IPSpace(cidr_blocks=[self, other])
		else:
			return IPSpace(cidr_blocks=[self] + other.cidr_blocks)


class IPSpace:
	def __init__(self, cidr_blocks):
		"""
		:type cidr_blocks: list[CidrBlocks] or list[str]
		"""

		self._blocks = []
		for block in cidr_blocks:
			self.append(block)

			if not isinstance(block, CidrBlock):
				x = CidrBlock(block)
			else:
				x = block
			if x not in self._blocks:
				self._blocks.append(x)

	def __len__(self):
		return len(self._blocks)

	def __str__(self):
		return '\n'.join([str(block) for block in self.cidr_blocks])

	def __repr__(self):
		return f'IPSpace:\n{str(self)}'

	@property
	def start(self):
		"""
		:rtype: IP
		"""
		return min([block.start for block in self.cidr_blocks])

	@property
	def end(self):
		"""
		:rtype: IP
		"""
		return max([block.end for block in self.cidr_blocks])

	def append(self, cidr_block):
		"""
		:type cidr_block: CidrBlock or str
		"""
		if not isinstance(cidr_block, CidrBlock):
			cidr_block = CidrBlock(cidr_block)

		if self.contains(cidr_block):
			pass

		else:
			# if cidr_block contains any block, it should replace it
			blocks = []
			for i in range(len(self)):
				item = self.cidr_blocks[i]
				if not cidr_block.contains(item):
					bisect.insort(blocks, item)
			bisect.insort(blocks, cidr_block)
			self._blocks = blocks

	@property
	def cidr_blocks(self):
		"""
		:rtype: list[CidrBlock]
		"""
		return self._blocks

	def contains(self, item):
		if isinstance(item, IPSpace):
			for item_block in item.cidr_blocks:
				if not self.__contains__(item_block):
					return False
			return True

		else:
			for block in self.cidr_blocks:
				if block.contains(item):
					return True
			return False

	def copy(self):
		result = IPSpace(cidr_blocks=[])
		for block in self.cidr_blocks:
			result._blocks.append(block)
		return result

	def __contains__(self, item):
		return self.contains(item)

	def __add__(self, other):
		result = self.copy()
		if isinstance(other, list):
			other = IPSpace(cidr_blocks=other)

		if isinstance(other, IPSpace):
			for block in other.cidr_blocks:
				result.append(block)
		else:
			other = CidrBlock(other)
			result.append(other)

		return result

	def get_contains_function(self):
		"""
		creates a stand-alone function that doesn't need the class
		:rtype: callable
		"""
		blocks = [(b.start.int, b.end.int) for b in self.cidr_blocks]

		def contains(item):
			if '/' in item:
				start_int, end_int = get_ip_range_int(item)
				for block_start, block_end in blocks:
					if block_start <= start_int and end_int <= block_end:
						return True
				return False
			else:
				ip_int = ip_to_int(item)
				for block_start, block_end in blocks:
					if block_start <= ip_int and ip_int <= block_end:
						return True
				return False

		return contains
