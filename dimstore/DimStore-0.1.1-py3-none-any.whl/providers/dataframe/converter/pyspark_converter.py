"""
"
" the pyspark dataframe converter
"
"""
from pyspark.sql.dataframe import DataFrame
from dimsum.providers.dataframe.converter.converter_base import ConverterBase

class PySparkConverter(ConverterBase):
    # class attributes
    __support__ = {('pyspark','pandas'),
                   ('pyspark','pyspark')}

    """
    "
    " report conversion capability
    " 
    """
    @classmethod
    def is_capable(cls, in_type, out_type):
        """
        @param::in_type: the type of input dataframe in string
        @param::out_type: the type of output dataframe in string
        return boolean value indicates whether or not the conversion is supported
        """
        return (in_type.lower(),out_type.lower()) in cls.__support__
        

    """
    "
    " perform the dataframe conversion
    "
    """
    @classmethod
    def astype(cls,df,out_type,**kwargs):
        """
        @param::out_type: the type of output dataframe in string
        return the converted dataframe or None if not feasible
        """
        # handle edge cases
        if df == None:
            raise Exception('> PySparkConverter astype(): input dataframe is None')
        if not hasattr(df, 'toPandas'):
            raise Exception('> PySparkConverter astype(): input dataframe must be a PySpark dataframe')
        if out_type == None:
            raise ValueError('> PySparkConverter astype(): dataframe out_type parameter can not be none.')
        if not cls.is_capable('pyspark',out_type):
            raise Exception('> PySparkConverter astype(): convert to type: %s not supported.'%(out_type))

        # convert to target type
        if out_type.lower() == 'pandas':
            return df.toPandas()
        return df
            

    """
    "
    " report the capability of convert operation
    "
    """
    @classmethod
    def info(cls):
        """
        @param: empty intended
        return list of possbile join combinations
        """
        return ["[%s] => [%s]"%(i,o) for i,o in cls.__support__]