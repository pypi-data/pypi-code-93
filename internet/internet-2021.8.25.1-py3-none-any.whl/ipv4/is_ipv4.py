def is_ipv4(x):
	if not isinstance(x, str):
		raise TypeError('is_ipv4 only works on strings!')
	if '.' not in x:
		return False

	if x.count('/') > 1:
		return False

	if x.count('.') != 3:
		return False

	if x.count('/') == 1:
		x, bits = x.split('/')
		try:
			if int(bits) > 32 or int(bits) < 1:
				return False
		except ValueError:
			return False

	try:
		elements = [int(e) for e in x.split('.')]
		return all([e >= 0 and e <= 255 for e in elements])
	except ValueError:
		return False
