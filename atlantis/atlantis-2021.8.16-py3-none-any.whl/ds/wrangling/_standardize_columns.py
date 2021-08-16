from pandas import DataFrame as PandasDF
from pyspark.sql import DataFrame as SparkDF
from pyspark.sql import functions as f

from ...text import remove_non_alphanumeric as _remove_alpha_func
from ...text import convert_camel_to_snake


def standardize_name(
		x, camel_to_snake=True, remove_non_alphanumeric=True,
		replace_with = '_', join_by = '__', ignore_errors = False
):
	"""
	:type x: list[str] or tuple or str
	:type camel_to_snake: bool
	:type remove_non_alphanumeric: bool
	:type replace_with: str
	:type join_by: str
	:type ignore_errors: bool
	:rtype: str
	"""
	if isinstance(x, tuple):
		x = list(x)

	# remove empty strings and remove non alphanumeric
	if isinstance(x, list):
		x = [str(s).strip() for s in x if s != '']
		x = join_by.join(x)

	try:
		if remove_non_alphanumeric:
			x = _remove_alpha_func(s=x, replace_with=' ')
			x = x.strip()
			x = _remove_alpha_func(s=x, replace_with=replace_with)
		if camel_to_snake:
			x = convert_camel_to_snake(x, remove_non_alphanumeric=remove_non_alphanumeric)
		x = x.lower().replace(' ', '_')
	except Exception as e:
		if ignore_errors:
			print('Error was ignored for: "', x, '" ', e, sep='')
		else:
			raise e

	return x


def standardize_columns(data, inplace=False, camel_to_snake=True, remove_non_alphanumeric=True):
	"""
	:type data: PandasDF or SparkDF
	:type inplace: bool
	:type camel_to_snake: bool
	:rtype: PandasDF or SparkDF
	"""
	if isinstance(data, PandasDF):
		if inplace:
			new_data = data
		else:
			new_data = data.copy()

		new_data.columns = list(map(
			lambda x: standardize_name(
				x=x, camel_to_snake=camel_to_snake, remove_non_alphanumeric=remove_non_alphanumeric
			),
			list(new_data.columns)
		))

		return new_data

	elif isinstance(data, SparkDF):
		return data.select([
			f.col(col).alias(
				standardize_name(x=col, camel_to_snake=camel_to_snake, remove_non_alphanumeric=remove_non_alphanumeric)
			)
			for col in data.columns
		])
