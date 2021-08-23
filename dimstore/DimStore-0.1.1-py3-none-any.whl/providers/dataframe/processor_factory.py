from dimsum.providers.dataframe.jointer.pyspark_jointer import PySparkJointer
from dimsum.providers.dataframe.jointer.pandas_jointer import PandasJointer
from dimsum.providers.dataframe.converter.pyspark_converter import PySparkConverter
from dimsum.providers.dataframe.converter.pandas_converter import PandasConverter
from dimsum.providers.dataframe.column.normalizer.pyspark_normalizer import PysparkNormalizer
from dimsum.providers.dataframe.column.normalizer.pandas_normalizer import PandasNormalizer

class DataframeProcessorFactory():

    # class variable
    __jointers__ = [PySparkJointer, PandasJointer]
    __converters__ = [PySparkConverter,PandasConverter]
    __normalizer__ = [PysparkNormalizer, PandasNormalizer]

    """
    "
    " get the first jointer that support the join operation
    "
    """
    @classmethod
    def get_jointer(cls, df_type):
        """
        @param::left: the type of left dataframe in string
        @param::right: the type of right dataframe in string
        @param::out: the output dataframe type in string
        return boolean value indicates whether or not the two dataframes can be joined.
        """
        for j in cls.__jointers__:
            if j.is_capable(df_type):
                return j

    """
    "
    " get the first jointer that support the join operation
    "
    """
    @classmethod
    def get_converter(cls, in_type, out_type):
        """
        @param::in_type: the input dataframe type in string
        @param::out_type: the output dataframe type in string
        return the converter class that can perform the dataframe conversion
        """
        for c in cls.__converters__:
            if c.is_capable(in_type, out_type):
                return c

    """
    "
    " get the first normalizer that support the dataframe
    "
    """
    @classmethod
    def get_normalizer(cls, df_type):
        """
        @param::df_type: the input dataframe type in string
        return the converter class that can perform the dataframe conversion
        """
        for n in cls.__normalizer__:
            if n.is_capable(df_type):
                return n

    """
    "
    " report the info of dataframe jointer factory
    "
    """
    @classmethod
    def info(cls):
        possible_joints = []
        possible_conversion = []
        possible_normalizer = []
        for j in cls.__jointers__:
            possible_joints.extend(j.info())
        for c in cls.__converters__:
            possible_conversion.extend(c.info())
        for n in cls.__normalizer__:
            possible_normalizer.extend(n.info())
        summary = {
            'join supports dataframes':possible_joints,
            'conversion supported:':possible_conversion,
            'normalizer supports dataframe':possible_normalizer}
        return summary