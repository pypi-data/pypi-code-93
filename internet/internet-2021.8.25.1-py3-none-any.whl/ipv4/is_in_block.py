from .ip_to_int import get_ip_range, ip_to_int


def is_in_ip_range(ip, start_ip, end_ip):
	ip_int = ip_to_int(ip)
	start_int = ip_to_int(start_ip)
	end_int = ip_to_int(end_ip)

	return start_int <= ip_int and ip_int <= end_int


def is_in_block(ip, cidr_block):
	start_ip, end_ip = get_ip_range(cidr_block)
	return is_in_ip_range(ip=ip, start_ip=start_ip, end_ip=end_ip)
