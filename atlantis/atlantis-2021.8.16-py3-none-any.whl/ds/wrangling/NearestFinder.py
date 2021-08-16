from pandas import DataFrame as PandasDF
from pyspark.sql.session import SparkSession
from pyspark.sql import DataFrame as SparkDF
from pyspark.sql.types import IntegerType, DateType, StringType
from pyspark.sql import functions as f
from bisect import bisect_right, bisect_left
from datetime import date as Date
from datetime import timedelta
from multiprocessing.pool import ThreadPool
from ...time.date import parse_date, find_date_and_format


class NearestFinder:
	"""
	sometimes we have a dataset with only a handful of values (e.g., dates) but we need to use it
	for any value within the range.
	this class creates a mapping from each date to the last date from a list of dates which is equal or before
	the date in question
	"""
	def __init__(self, direction='before', time_complexity='O(1)', parse_int_as_date_if_possible=True, n_jobs=8):
		"""

		:type time_complexity: str
		:param time_complexity: O(1) --> use dictionary, O(log(n)) --> use binary search (takes less memory)
		"""
		if direction.lower() not in ['before', 'after']:
			raise ValueError(f'direction "{direction}" is not supported.')
		self._direction = direction.lower()

		if time_complexity.lower() not in {'o(1)', 'o(log(n))'}:
			raise ValueError(f'Time complexity {time_complexity} is not supported!')

		if time_complexity == 'o(1)':
			self._function_type = 'map'
		else:
			self._function_type = 'binary_search'

		self._list = None
		self._bisect_function = None
		self._type = None
		self._represents = None
		self._date_format = None
		self._parse_int_as_date_if_possible = parse_int_as_date_if_possible
		self._column = None
		self._n_jobs = n_jobs
		self._mapping = None

	def __getstate__(self):
		attributes = [
			'_direction', '_mapping',
			'_list', '_type', '_represents', '_date_format', '_parse_int_as_date_if_possible', '_column', '_n_jobs'
		]
		return {
			name: getattr(self, name)
			for name in attributes
		}

	def __setstate__(self, state):
		for name, value in state.items():
			setattr(self, name, value)

		if self._function_type == 'map':
			self._create_map_function()
		else:
			self._create_binary_search_function()

	@staticmethod
	def _to_list(X, return_column=False):
		if isinstance(X, (SparkDF, PandasDF)):
			column = list(X.columns)[0]
			if len(X.columns) > 1:
				raise ValueError(f'DataFrame has {len(X.columns)} columns! Which one should I use?')

			if isinstance(X, SparkDF):
				X = X.toPandas()

			if isinstance(X, PandasDF):
				X = X[column]
		else:
			column = None

		if return_column:
			return list(X), column
		else:
			return list(X)

	@property
	def _first(self):
		return self._list[0]

	@property
	def _last(self):
		return self._list[-1]

	def fit(self, X):
		l, self._column = self._to_list(X=X, return_column=True)
		self._list = sorted(l)

		if type(self._first) != type(self._last):
			raise TypeError(f'different types are used in the list {type(self._first)}, {type(self._last)}')

		if self._function_type == 'map':
			self._create_map_function()
		else:
			self._create_binary_search_function()

		return self

	def _create_binary_search_function(self):
		if self._direction == 'before':
			def function(x):
				index = bisect_right(self._list, x) - 1
				index = max(0, index)
				return self._list[index]

		else:
			max_index = len(self._list) - 1
			def function(x):
				index = bisect_left(self._list, x)
				index = min(max_index, index)
				return self._list[index]

		self._bisect_function = function

	def _create_map_function(self):
		if self._bisect_function is None:
			self._create_binary_search_function()

		if isinstance(self._first, int):
			self._type = 'int'
		elif isinstance(self._first, Date):
			self._type = 'date'
		elif isinstance(self._first, str):
			self._type = 'str'

		date1, format1 = find_date_and_format(self._first)
		date2 = parse_date(self._last)
		if date1 is not None:
			self._represents = 'date'
			self._date_format = format1
		else:
			self._represents = self._type
			self._date_format = None

		if self._represents == 'date':
			with ThreadPool(self._n_jobs) as pool:
				values = pool.map(lambda n: date1 + timedelta(days=n), range((date2 - date1).days))

			if self._type == 'str' or self._type == 'int':
				with ThreadPool(self._n_jobs) as pool:
					values = pool.map(lambda x: x.strftime(self._date_format), values)

			if self._type == 'int':
				with ThreadPool(self._n_jobs) as pool:
					values = pool.map(lambda x: int(x), values)

		elif self._represents == 'int':
			values = list(range(self._list[-1] - self._list[0] + 1))

		else:
			values = None

		if values is not None:
			self._mapping = {x: self._bisect_function(x) for x in values}

			def function(x):
				return self._mapping[x]
		else:
			self._mapping = {x: x for x in self._list}

			def function(x):
				if x in self._mapping:
					return x
				else:
					y = self._bisect_function(x)
					self._mapping[x] = y
					return y

		self._mapping_function = function

	@property
	def mapping(self):
		"""
		:rtype: dict
		"""
		if self._mapping is None:
			self._create_map_function()
		return self._mapping

	def to_spark_df(self, spark=None, from_column='from', to_column='to'):
		"""
		:rtype: SparkDF
		"""
		if spark is None:
			spark = SparkSession.builder.getOrCreate()

		return spark.createDataFrame(
			[(key, value) for key, value in self.mapping.items()],
			[from_column, to_column]
		)

	def to_pandas_df(self, from_column='from', to_column='to'):
		"""
		:rtype: PandasDF
		"""
		return PandasDF({from_column: self.mapping.keys(), to_column: self.mapping.values()})

	def map(self, x):
		if self._function_type == 'dict':
			return self._mapping_function(x)
		else:
			return self._bisect_function(x)

	def predict(self, X):
		if isinstance(X, SparkDF):
			if self._column not in X.columns:
				raise ValueError(f'Column {self._column} does not exist in X.')

			if self._type == 'date':
				the_type = DateType()
			elif self._type == 'int':
				the_type = IntegerType()
			else:
				the_type = StringType()

			@f.udf(the_type)
			def _f(x):
				return self.map(x=x)

			return X.withColumn('prediction', _f(self._column))

		elif isinstance(X, PandasDF):
			if self._column not in X.columns:
				raise ValueError(f'Column {self._column} does not exist in X.')

			return X[self._column].apply(self.map)

		elif isinstance(X, list):
			with ThreadPool(self._n_jobs) as pool:
				result = pool.map(self.map, X)
			return result

		else:
			raise TypeError(f'type {type(X)} is not supported!')
