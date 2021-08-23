"""
"  default flat file meta data manager, keep records of all features in store
"""
import os
import pickle as pl
from dimsum.providers.meta_manager.meta_manager_base import MetaManagerBase
from dimsum.core.feature_set import FeatureSet
from dimsum.utility.file_functions import file_exist, read_binary_file, write_binary_file
from dimsum.core.feature_metadata import FeatureOperation

class FlatFileMetaManager(MetaManagerBase):

    def __init__(self, config):
        self.config = config
        self.path = "%s/%s"%(config['root_dir'], config['folder_name'])
        self.filename = self.config['file_name']

    """
    "
    " provide a list of operations that are valid for the given feature
    "
    """
    def get_valid_operations(self, feature):
        uid, version = self.__is_feature_name_exist__(feature)
        operations = set([FeatureOperation.DELETE])
        if uid and uid == feature.uid:
            operations.add(FeatureOperation.UPDATE)
        if not uid:
            operations.add(FeatureOperation.CREATE)
        if uid and feature.versioning:
            feature.uid = uid
            feature.latest_version = version + 1
            operations.add(FeatureOperation.CREATE_NEW_VERSION)
        return operations    

    """
    "
    " register the feature metadata to the registry
    "
    """
    def register(self, feature, **kwargs):
        # handle edge case
        self.__apply_default_namespace__(feature)
        operation_list = self.get_valid_operations(feature)
        if (FeatureOperation.CREATE not in operation_list and 
            FeatureOperation.CREATE_NEW_VERSION not in operation_list):
            print("> the feature name: '%s' is not unique in namespace: %s" % (feature.name, feature.namespace))
            return
        # get catalog object and register feature
        uid = str(feature.uid)
        namespace = feature.namespace
        catalog = self.__get_catalog__(namespace = namespace)
        catalog[uid] = feature
        # write back catalog
        self.__save_catalog__(catalog, namespace = namespace)


    """
    "
    " read feature meta data by given namespace
    "
    """
    def read(self, namespace='default', match_child=True, **kwargs):
        """
        @param::namespace: the namespace in string
        @param::match_child: boolean value indicate whether match sub namespaces
        @param::kwargs: the keyword parameter list
        return a dictionary of {uid:feature meta data}
        """
        feature_dict = {}
        if file_exist(self.path, self.filename):
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
            canonical_ns = self.__build_canonical_namespace__(namespace)
            if match_child:
                for key_ns in catalog:
                    if self.__namespace_match__(canonical_ns, key_ns):
                        feature_dict.update(catalog[key_ns])
            else:
                if canonical_ns in catalog:
                    feature_dict = catalog[canonical_ns]
        return feature_dict

    """
    "
    " get all namespaces in feature store
    "
    """
    def namespaces(self, **kwargs):
        """
        @param::kwargs: keyword parameter list
        return list of canonical namespace objects and the counts of features in that namespace
        """
        catalog = {}
        if file_exist(self.path, self.filename):
            # read and deserialize catalog object
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
        return catalog.keys(),list(map(len,catalog.values()))

    """
    "
    " delete features in the given FeatureSet instance
    "
    """
    def delete(self, ufd, verbose=True, **kwargs):
        """
        @param::ufd: the instance of dictionary contain uid:feature pairs
        @param::kwargs: keyword parameter list
        return none
        """
        # check edge case
        if not isinstance(ufd, dict):
            raise ValueError('> delete: feature_set parameter is not an instance of FeatureSet class.')
        namespace = None
        catalog = None
        for uid, feature in ufd.items():
            # sanity check of feature meta data
            self.__apply_default_namespace__(feature)
            # load new catalog when namespace mismatch
            if namespace != feature.namespace:
                # save existing catalog
                if isinstance(catalog, dict):
                    self.__save_catalog__(catalog, namespace=namespace)
                # load new catalog in different namespace
                catalog = self.__get_catalog__(namespace=feature.namespace)
                namespace = feature.namespace
            # delete feature
            if isinstance(catalog, dict) and uid in catalog:
                del catalog[uid]
        # save the last catalog back into storage
        if isinstance(catalog, dict):
            self.__save_catalog__(catalog, namespace=namespace)
        if verbose:
            print('> delete: %d feature(s) affected.'%(len(ufd)))
        

    """
    "
    " update features in the given FeatureSet instance
    "
    """
    def update(self, ufd, verbose=True, **kwargs):
        """
        @param::ufd: the instance of dictionary contain uid:feature pairs
        @param::kwargs: keyword parameter list
        return none
        """
        # check edge case
        if not isinstance(ufd, dict):
            raise ValueError('> update: feature_set parameter is not an instance of FeatureSet class.')
        namespace = None
        catalog = None
        for uid, feature in ufd.items():
            # sanity check of feature meta data
            self.__apply_default_namespace__(feature)
            operatoin_list = self.get_valid_operations(feature)
            if FeatureOperation.UPDATE not in operatoin_list:
                raise ValueError('> update: feature name "%s" is not unique in namespace or feature does not exist. "%s"'%(feature.name, feature.namespace))
            # load new catalog when namespace mismatch
            if namespace == None or namespace != feature.namespace:
                # save existing catalog
                if isinstance(catalog, dict) and len(catalog) > 0:
                    self.__save_catalog__(catalog, namespace=namespace)
                # load new catalog in different namespace
                catalog = self.__get_catalog__(feature.namespace)
                namespace = feature.namespace
            # update feature
            if uid in catalog:
                catalog[uid] = feature
        # save the last catalog back into storage
        if isinstance(catalog, dict) and len(catalog) > 0:
            self.__save_catalog__(catalog, namespace=namespace)
        if verbose:
            print('> update: %d feature(s) affected.'%(len(ufd)))

    

    """
    "
    " implementation of base class method.
    " operation takes O(N), where N is the max of number of features in any namespace.
    "
    """
    def __is_feature_name_exist__(self, feature):
        """
        @param::feature: the feature metadata object.
        return boolean value of uniqueness of feature name in given namespace.
        """
        if file_exist(self.path, self.filename):
            # read and deserialize catalog object
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
            # check uniques
            feature_name = feature.name
            namespace = feature.namespace
            canonical_ns = self.__build_canonical_namespace__(namespace)
            if canonical_ns in catalog:
                for _,feat in catalog[canonical_ns].items():
                    if feat.name.lower() == feature_name.lower():
                        return feat.uid, feat.latest_version
        return None, None

    """
    "
    " read the catalog dumps and deserialize it
    " *** <note> may have performance issue when request/s is high, a cache can address this problem.
    " *** general cache mechanism: cache catalog using namespace as key, destroy/update when cached catalog with same namespace is updated.
    "
    """
    def __get_catalog__(self, namespace=None):
        """
        @param::namespace: the string namespace of catalog
        return the catalog object or None
        """
        catalog_rtn = {}
        namespace = self.__build_canonical_namespace__(namespace)
        if file_exist(self.path, self.filename):
            # read and deserialize catalog object
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
            if namespace in catalog:
                catalog_rtn = catalog[namespace]        
        return catalog_rtn

    """
    "
    " serialize the catalog and save it to flat file
    "
    """
    def __save_catalog__(self, sub_catalog, namespace=None):
        """
        @param::sub_catalog: the catelog object contains feature metadata
        @param::namespace: the string namespace of catalog
        return None
        """
        # check edge case
        if sub_catalog == None:
            raise Exception('> save_catalog: (sub)catalog can not be None!')
        if not isinstance(sub_catalog, dict):
            raise Exception('> save_catalog: (sub)catalog is not dictionary type!')
        # save (sub)catalog into flat file
        catalog = {}
        namespace = self.__build_canonical_namespace__(namespace)
        if file_exist(self.path, self.filename):
            bytes_obj = read_binary_file(self.path, self.filename)
            catalog = pl.loads(bytes_obj)
            if len(sub_catalog) == 0:
                # delete the namespace associate with empty sub catalog.
                del catalog[namespace]
            else:
                catalog[namespace] = sub_catalog
        else:
            if len(sub_catalog) > 0:
                catalog[namespace] = sub_catalog
        dumps = pl.dumps(catalog)
        write_binary_file(self.path, self.filename, dumps)


    """
    "
    " method apply default namespace if given namespace is invalid
    " 
    """
    def __apply_default_namespace__(self, feature):
        """
        @param::feature: the instance of feature metadata class
        return none
        """
        if feature.namespace == None or feature.namespace.strip() == '':
            feature.namespace = 'default'


    """
    "
    " build a set of canonical namespaces optimized for query/filter operation
    " e.g., foo.bar.kai => {(foo,0),(bar,1),(kai,2)}
    " check whether or not namepace match take O(N), where N is the number of tuples in namespace.
    "
    """
    def __build_canonical_namespace__(self, namespace):
        """
        @param::namespace: string representation of namespace.
        return a set contains canonical namespace
        """
        canonical_ns = []
        existed_parts = set([])
        if namespace == None or namespace.strip() == '':
            canonical_ns.append((0,'default'))
        else:
            for index,part in enumerate(namespace.split('.')):
                if not part.isalnum():
                    raise Exception("> The namespace is invalid! Make sure the namespace contains alphanumeric and '.' symbol only.")
                if part.lower() in existed_parts:
                    raise Exception("> The namespace can not contains duplicated tuples!")
                else:
                    canonical_ns.append((index,part.lower()))
                    existed_parts.add(part.lower())

        return tuple(canonical_ns)

    """
    "
    " check if the canonical namespaces match. The match operation is not communicative.
    " e.g., a match b  !=> b match a
    " operation takes O(N), where N is the number of tuples in namespace
    "
    """
    def __namespace_match__(self,namespace1, namespace2):
        if namespace1 == None or namespace2 == None:
            return False
        for part in namespace1:
            if part not in namespace2:
                return False
        return True

                    






