from pyspark.sql import functions as f
from pyspark.sql import DataFrame as SparkDF
from pyspark.ml.feature import MinMaxScaler
from pyspark.ml.feature import VectorAssembler
from pyspark.ml import Pipeline
from pyspark.sql.types import DoubleType


@f.udf(DoubleType())
def unlist(x):
  return float(list(x)[0])


class SingleScaler:
    def __init__(self, column):
        self._column = column
        self._pipeline = None

    def __getstate__(self):
        return {'_column': self._column, '_pipeline': self._pipeline}

    def __setstate__(self, state):
        for key, value in state.items():
            setattr(self, key, value)

    def fit(self, X):
        # normalizing
        assembler = VectorAssembler(
            inputCols=[self._column], outputCol=f'{self._column}_vector'
        ).setHandleInvalid('skip')
        scaler = MinMaxScaler(inputCol=f'{self._column}_vector', outputCol=f'{self._column}_scaled')
        self._pipeline = Pipeline(stages=[assembler, scaler]).fit(X)

    def transform(self, X):
        df_scaled = self._pipeline.transform(X).withColumn(
            f'{self._column}_scaled', unlist(f'{self._column}_scaled')
        ).drop(f'{self._column}_vector', self._column)
        return df_scaled

    def fit_transform(self, X):
        self.fit(X)
        return self.transform(X)


class Scaler:
    def __init__(self, columns=None):
        self._columns = columns
        self._single_scalers = None

    def __getstate__(self):
        return {'_columns': self._columns, '_single_scalers': self._single_scalers}

    def __setstate__(self, state):
        for key, value in state.items():
            setattr(self, key, value)

    def fit(self, X):
        if self._columns is not None:
            X = X.select(*self._columns)
        else:
            self._columns = X.columns

        self._single_scalers = {}
        for column in self._columns:
            print(f'Scaler fitting "{column}"')
            single_scaler = SingleScaler(column=column)
            single_scaler.fit(X=X)
            self._single_scalers[column] = single_scaler

    @property
    def single_scalers(self):
        """
        :rtype: dict[str, SingleScaler]
        """
        return self._single_scalers

    def transform(self, X):
        for column in self._columns:
            print(f'Scaler transforming "{column}"')
            single_scaler = self.single_scalers[column]
            X = single_scaler.transform(X=X)
        return X

    def fit_transform(self, X):
        self.fit(X=X)
        return self.transform(X=X)
