def ip_to_int(ip):
	parts = ip.split('.')
	return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])


def int_to_ip(x):
	return '.'.join([str(x >> (i << 3) & 0xFF) for i in range(4)[::-1]])


def get_cidr_block(ip_address, bits):
	"""
	reduces ip address to a cidr block
	:type ip_address: str or Column
	:type bits: int
	:rtype: str
	"""

	if bits >= 32:
		return ip_address
	reduced_bytes = (32 - bits) // 8
	reduced_bits = (32 - bits) % 8
	parts = ip_address.split('.')[:4 - reduced_bytes]

	parts[-1] = str((int(parts[-1]) >> reduced_bits) << reduced_bits)
	return f'{".".join(parts)}/{bits}'


def get_ip_range(cidr_block):
	"""
	gets a cidr block of with cidr format '24.0.0.0/12'
	returns a start and end ip address of format '24.0.0.0', '24.15.255.255'
	:param cidr_block:
	:return:
	"""
	start, bits = cidr_block.split('/')
	start = start.strip()
	bits = int(bits.strip())

	start_int = ip_to_int(start)
	end_int = start_int + 2 ** (32 - bits) - 1
	end = int_to_ip(end_int)
	return start, end

def get_ip_range_int(cidr_block):
	start, bits = cidr_block.split('/')
	start = start.strip()
	bits = int(bits.strip())

	start_int = ip_to_int(start)
	end_int = start_int + 2 ** (32 - bits) - 1
	return start_int, end_int
