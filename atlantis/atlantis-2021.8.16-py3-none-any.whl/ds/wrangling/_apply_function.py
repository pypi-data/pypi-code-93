from pandas import DataFrame as PandasDF
from pyspark.sql import DataFrame as SparkDF
from pyspark.sql import functions as f
from ...functions import get_function_arguments


def apply_function_in_a_simple_way(data, function, new_column, return_type=None):
	"""
	:type data: PandasDF or SparkDF
	:type function: callable
	:type new_column: str
	:type return_type:
	"""
	args = get_function_arguments(function=function)
	missing_columns = [arg for arg in args if arg not in data.columns]
	if len(missing_columns) > 0:
		raise KeyError(f'Columns missing: "{", ".join(missing_columns)}"')

	if isinstance(data, SparkDF):
		if return_type is None:
			raise ValueError(f'return_type should be provided for pyspark DataFrame.')
		data = data.withColumn(
			new_column,
			f.udf(function, return_type)(*[f.col(arg) for arg in args])
		)

	elif isinstance(data, PandasDF):
		data = data.copy()
		def _function(row):
			return function(*[row[arg] for arg in args])
		data[new_column] = data.apply(lambda row: _function(row), axis=1)

	else:
		raise TypeError(f'data of type "{type(data)}" is not supported!')

	return data


def apply_function(data, function, new_column, return_type=None, unique_ratio=0.01, echo=0):
	"""
	takes a function and applies it to all rows of the data
	the keyword arguments of the function should match the columns of the data
	for example, if the function is: f(feature_1, feature_2, feature_3) --> feature_1 + feature_2 + feature_3
	apply function finds the three columns called feature_1, feature_2, feature_3 and runs the function
	on each row of the data and saves the result as values in a new column called new_column

	unique_ratio is used to decide if performance should be optimized or not.
	if ratio of unique cases to all cases (number of rows of data) is smaller than unique_ratio
	then the function will only be applied to unique cases and then the result will be joined with the original data

	:type data: PandasDF or SparkDF
	:type function: callable
	:type new_column: str
	:type unique_ratio: float
	:type echo: int or bool
	"""

	if unique_ratio == 0:
		return apply_function_in_a_simple_way(
			data=data, function=function, return_type=return_type, new_column=new_column
		)

	else:
		args = get_function_arguments(function=function)
		missing_columns = [arg for arg in args if arg not in data.columns]
		if len(missing_columns) > 0:
			raise KeyError(f'Columns missing: "{", ".join(missing_columns)}"')

		if isinstance(data, PandasDF):
			uniques = data[args].drop_duplicates()
			n_uniques = uniques.shape[0]
			n_total = data.shape[0]
		elif isinstance(data, SparkDF):
			uniques = data.select(*args).distinct()
			n_uniques = uniques.count()
			n_total = data.count()
		else:
			raise TypeError(f'data of type "{type(data)}" is not supported!')

		if n_uniques / n_total > unique_ratio:
			return apply_function_in_a_simple_way(
				data=data, function=function, return_type=return_type, new_column=new_column
			)

		else:
			if echo:
				print(f'applying the function only on {n_uniques} unique cases instead of {n_total} cases.')

			uniques = apply_function_in_a_simple_way(
				data=uniques, function=function, return_type=return_type, new_column=new_column
			)

			columns = list(data.columns) + [new_column]

			if isinstance(data, PandasDF):
				return uniques.merge(data, on=args, how='left')[columns]
			else:
				return uniques.join(data, on=args, how='left').select(*columns)
