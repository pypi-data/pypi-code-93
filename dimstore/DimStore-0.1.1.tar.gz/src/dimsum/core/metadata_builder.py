"""
"  define the feature metadata keys 
"""
from dimsum.core.feature_metadata import FeatureMetaData
import re

class MetadataBuilder():
    def __init__(self):
        pass
    """
    "
    " return a list of metadata keys describes feature object
    "
    """
    @staticmethod
    def keys():
        """
        @param: empty parameter inteneded
        return a list of keys in string
        """
        return ['name', 
                'index',
                'namespace',
                'author',
                'dataset',
                'params',
                'output',
                'comment',
                'versioning',
                'create_date',
                'latest_version']

    """
    "
    " build the feature metadata object
    "
    """
    @classmethod
    def feature(cls, name, index, output, namespace=None):
        """
        @param::name: feature name in string
        @param::index: feature index column in string
        @param::namespace: namespace in string
        return feature metadata object
        """
        # assign default namespace value
        if namespace ==  None:
            namespace = 'default'
        if namespace != None and namespace.strip() == '':
            namespace = 'default'

        # assign default value
        meta_data = FeatureMetaData(name, index, output, namespace=namespace)
        if cls.sanity_check(meta_data):
            return meta_data
        else:
            raise ValueError('> MetadataBuilder.feature(): feature object sanity check failed.')

    """
    "
    " sanity check feature name
    "
    """
    @classmethod
    def sanity_check(cls, feature):
        if not isinstance(feature, FeatureMetaData):
            raise TypeError ('> MetadataBuilder.sanity_check(): feature object is not instance of FeatureMetaData class.')
        if feature.name == None:
            raise ValueError('> MetadataBuilder.sanity_check(): feature name can not be None.')
        if re.match(r"^[\w_]+$", feature.name) is None:
            raise ValueError('> MetadataBuilder.sanity_check(): feature name can only contain alphnumeric and "_" characters.')
        if feature.index == None or feature.index.strip() == '':
            raise ValueError('> MetadataBuilder.sanity_check(): feature index can not be None or empty!')
        if feature.output == None or feature.output.strip() == '' or feature.output.lower() not in ['pyspark', 'pandas']:
            raise ValueError('> MetadataBuilder.sanity_check(): feature output type can only be PySpark or Pandas!')
        if re.match(r"^[\w.]+$", feature.namespace) is None:
            raise ValueError('> MetadataBuilder.sanity_check(): feature namespace type can only contain alphanumeric and "." charaxters.')
        return True

    """
    "
    "  todo: provide valdiation logic for each metadata attributes
    "  todo: verify that metadata builder design is necessary comparing to merging the logic into feature_metadata.py
    "
    """
        
