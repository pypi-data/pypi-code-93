import datetime as dt
from datetime import date


FORMATS = (
	'%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d', '%Y%m%d',
	'%Y-%m', '%Y/%m', '%Y.%m', '%Y',
	'%y-%m-%d', '%y/%m/%d', '%y.%m.%d',
	'%b %d, %Y', '%b %d, %Y', '%B %d, %Y', '%B %d %Y', '%m/%d/%Y', '%m/%d/%y', '%b %Y', ' %B%Y', '%b %d,%Y'
)

def find_date_and_format(x, format=None):
	"""
	:type x: str or int or date
	:type format: NoneType or str
	:rtype: NoneType or date
	"""
	if format is None:
		if isinstance(x, str):
			formats = FORMATS
		elif isinstance(x, int):
			formats = ['%Y%m%d']
			x = str(x)
		else:
			raise TypeError(f'type {type(x)} is not supported!')
	else:
		formats = [format]

	for _format in formats:
		try:
			return dt.datetime.strptime(x, _format).date(), _format
		except ValueError:
			pass

	return None, None


def find_date_format(x, format=None):
	"""
	:type x: str or int or date
	:type format: NoneType or str
	:rtype: NoneType or date
	"""
	return find_date_and_format(x=x, format=format)[1]


def parse_date(x, format=None):
	"""
	:type x: str or int or date
	:type format: NoneType or str
	:rtype: NoneType or date
	"""
	return find_date_and_format(x=x, format=format)[0]
