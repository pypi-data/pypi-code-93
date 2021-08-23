import uuid
import time
import yaml
from dimsum.providers.cache.null_cache import NullCache
import inspect
from dimsum.providers.persistor.persistor_factory import PersistorFactory
from dimsum.providers.serializer.serializer_factory import SerializerFactory
from dimsum.providers.meta_manager.meta_manager_factory import MetaManagerFactory 
from dimsum.providers.output_render.output_render_factory import OutputRenderFactory
from dimsum.providers.dataframe.processor_factory import DataframeProcessorFactory
from dimsum.providers.cache.cache_factory import CacheFactory
from dimsum.core.feature_metadata import FeatureMetaData, FeatureOperation
from dimsum.core.feature_set import FeatureSet
from dimsum.utility.file_functions import read_text_file, http_read_file, parse_file_protocol, parse_file_uri
from dimsum.utility.dataframe_functions import df_to_csv, csv_to_df

"""
    Feature Store class store provide API:
    1. register new features
    2. checkout existing features
    3. manage features
"""

class Store():

    """
    "   init the store and configure feature store 
    """
    def __init__(self, config_file, verbose=True):
        self.config = None
        self.verbose = verbose
        # read store configuration
        if hasattr(config_file, 'lower'):
            config_data = self.__fetch_config__(config_file)
            if not config_data:
                raise FileNotFoundError('> Error: configuration file does not exist.')
            self.config = yaml.safe_load(config_data)
        elif hasattr(config_file, 'read'):
            self.config = yaml.safe_load(config_file.read())
        else:
            raise TypeError('> Error: The configuration file is not valid type.')

        # get serializer
        self.serializer = SerializerFactory.get_serializer(self.config['serializer'])

        # init cache layer
        self.cache = CacheFactory.get_cache(self.config.get('cache'))

        # get persistor
        self.persistor = PersistorFactory.get_persistor(self.config['persistor'])

        # get output render
        self.output_render = OutputRenderFactory.get_output_render(self.config['output_render'])

        # get feature registry
        self.meta_manager = MetaManagerFactory.get_meta_manager(self.config['registry_manager'])

    def __fetch_config__(self, config_file_path):
        config = None
        # parse config file protocol
        protocol = parse_file_protocol(config_file_path)
        # read config file based on the protocol
        if protocol == 'http' or protocol == 'https':
            config = http_read_file(config_file_path)
        elif protocol == 'file':
            dirname, filename = parse_file_uri(config_file_path)
            config = read_text_file(dirname,filename)
        else:
            pass
        return config

    """
    "  register the feature to store
    """
    def register(self, pipeline, **kwargs):
        # serialize pipeline
        pipeline.source_code = inspect.getsource(pipeline)
        dumps = self.serializer.encode(pipeline, **kwargs)
        # make sure the initial uuid is always different,
        # it will make sure the uniqueness checking is accurate.
        if not hasattr(pipeline, 'metadata'):
            raise ValueError('> the metadata must be provided using the metadata decorator.')
        feature = pipeline.metadata
        feature.uid = str(uuid.uuid4())
        operation_list = self.meta_manager.get_valid_operations(feature)
        if (FeatureOperation.CREATE_NEW_VERSION in operation_list or
            FeatureOperation.CREATE in operation_list):
            try:
                # persist the serialized pipeline
                self.persistor.write(feature, dumps, supported_operation = operation_list, **kwargs)
            except Exception as e:
                print('> the persistor write operation failed.', e)
                raise

            try:
                # add new registered feature into store catalog
                self.meta_manager.register(feature)
            except Exception as e:
                print('> the meta manager registration operation failed.', e)
                self.persistor.delete(feature.uid)
                raise
        else:
            print("> The feature name '%s' is not unique in namespace: %s" % (feature.name, feature.namespace))

    """
        list all matched features by filter function in given matched namespace
    """
    def features(self, namespace='default', match_child=True, **kwargs):
        ufd = self.meta_manager.read(namespace=namespace, match_child=match_child, **kwargs)
        return FeatureSet(self, ufd=ufd)
        

    """
    "
    "   list all namespaces defined in feature store
    "
    """
    def list_namespaces(self, **kwargs):
        namespace_data = self.meta_manager.namespaces(**kwargs)
        self.output_render.namespace_list(namespace_data)
    
  

    """
        show store info
    """

    def info(self, verbose=False, **kwargs):
        brand = (
            r"______ _           _____                  ""\n"             
            r"|  _  (_)         /  ___|                 ""\n" 
            r"| | | |_ _ __ ___ \ `--. _   _ _ __ ___   ""\n" 
            r"| | | | | '_ ` _ \ `--. \ | | | '_ ` _ \  ""\n" 
            r"| |/ /| | | | | | /\__/ / |_| | | | | | | ""\n" 
            r"|___/ |_|_| |_| |_\____/ \__,_|_| |_| |_| ""\n" 
        )
        print(brand)
        store_name = self.config['name'].capitalize() if self.config['name'] else 'Feature Store'
        store_line = f"{store_name} Information"
        print('=' * len(store_line))
        print(store_line)
        print('=' * len(store_line))
        print(f"- Meta Data Manager: {self.config['registry_manager']['type']}")
        print(f"- Persistor: {(self.config['persistor']['type'])}")
        print(f"- Serializers: {(self.config['serializer']['type'])}")
        print(f"- Output Render: {(self.config['output_render']['type'])}")
        cache = self.config.get('cache')
        if not isinstance(cache, dict):
            print(f"- Cache: None")
        else:
            registry = cache.get('registry', {})
            storage = cache.get('storage', {})
        if verbose:
            print(f"- Cache:")
            print(f"    - Registry: { registry.get('type') if isinstance(registry, dict) else 'None' }")
            print(f"    - Storage: { storage.get('type') if isinstance(storage, dict) else 'None' }")
        else:
            print(f"- Cache: { registry.get('type') if isinstance(registry, dict) else 'None' } + {storage.get('type') if isinstance(storage, dict) else 'None'}")


    """
    "
    " render the feature list to output, intended to be called by FeatureSet object
    " through store proxy object.
    "
    """
    def list_features(self, feature_list):
        self.output_render.feature_list(feature_list)

    """
    "
    " delete the features from the store
    " 
    """
    def delete(self, ufd, hard=False, verbose=True, **kwargs):
        """
        @param::ufd: the {uid:feature} dictionary
        @param::verbose: toggle the log information output
        @param::kwargs: the keyworded parameters
        return the dataframe built from feature list
        """
        # perform hard/soft deletion
        if hard:
            processed = {}
            for u, f in ufd.items():
                try:
                    self.persistor.delete(f.uid)
                    processed[u] = f
                except Exception as e:
                    print('> the hard deletion failed.', e)
                    self.meta_manager.delete(processed,verbose)
                    raise
            self.meta_manager.delete(processed, verbose)
        else:
            self.meta_manager.delete(ufd, verbose)

    
    """
    "
    " update the features from the store
    " 
    """
    def update(self, ufd, verbose=True, **kwargs):
        """
        @param::ufd: the {uid:feature} dictionary
        @param::verbose: toggle the log information output
        @param::kwargs: the keyworded parameters
        return the dataframe built from feature list
        """
        self.meta_manager.update(ufd, verbose)

    """
    "
    " build features into dataframe, intended to be called by FeatureSet object
    " through store proxy object.
    "
    """
    def build(self, ufd, dataframe='pyspark', verbose=True, **kwargs):
        """
        @param::ufd: the {uid:feature} dictionary
        @param::dataframe: the dataframe type in string
        @param::verbose: toggle log information
        @param::kwargs: the keyworded parameters
        return the dataframe built from feature list
        """
        if ufd != None or len(ufd) > 0:
            if verbose:
                print('> task: build %s dataframe from %d features ...'%(dataframe, len(ufd)))
            # init
            output_df = None
            in_df = None
            index1 = None
            index2 = None  
            cold_start = True
            for _,feature in ufd.items():
                unique_id = self.__get_unique_id__(feature, **kwargs)
                in_cache_csv = self.cache.get(unique_id, **kwargs)
                if in_cache_csv is not None: # feature already in cache
                    in_df = csv_to_df(in_cache_csv, dataframe)
                else:
                    start_time = time.process_time()
                    in_df = self.checkout(feature, dataframe, verbose=verbose, **kwargs)
                    end_time = time.process_time()
                    computation_time = end_time - start_time    
                    if computation_time > self.cache.time_threshold: # add feature in cache if computationally extensive
                        csv_data = df_to_csv(in_df, dataframe)
                        self.cache.put(unique_id, csv_data, computation_time = computation_time)
                if cold_start:
                    output_df = in_df
                    index1 = feature.index
                    cold_start = False
                else:
                    index2 = feature.index
                    # query supported jointers
                    jointer = DataframeProcessorFactory.get_jointer(dataframe)
                    if jointer == None:
                        raise Exception('> Store.build(): join "%s" dataframe is not supported.'%(dataframe))
                    output_df = jointer.try_join(output_df,in_df,index1,index2)               
        return output_df
    
    """
    "
    " check out feature from persistence layer
    "
    """
    def checkout(self, feature, out_type, verbose=True, **kwargs):
        """
        @param::feature: the FeatureMetaData object
        @param::out_type: the output feature dataframe type in string
        @param::verbose: the boolean value toggles log info output
        @param::kwargs: the keyworded parameter list
        return the feature extracted by executing the pipeline
        """
        # check edge case
        if out_type == None:
            raise ValueError('> Store.checkout(): the output dataframe type can not be None.')
        if not isinstance(feature, FeatureMetaData):
            raise TypeError('> Store.checkout(): the feature object is not an instance of FeatureMetaData class.')
        df_converter = DataframeProcessorFactory.get_converter(feature.output, out_type)
        if df_converter == None:
            raise Exception('> Store.checkout(): convert operation does not support the output dataframe.')
        df_normalizer = DataframeProcessorFactory.get_normalizer(feature.output)
        if df_normalizer == None:
            raise Exception('> Store.checkout(): normalizer does not support the feature dataframe.')

        # extract parameter
        qualify_name = '.'.join([feature.namespace,feature.name])
        params = kwargs[qualify_name] if qualify_name in kwargs else {}
        pipeline_params = params['parameter'] if 'parameter' in params else {}
        # load and deserialize pipeline
        dumps = self.persistor.read(feature.uid, **params)
        pipeline = self.serializer.decode(dumps, **params)
        # log
        if pipeline_params and verbose:
            print('> info: checkout %s feature "%s" with params: %s ...'%(feature.output, feature.name, pipeline_params))
        elif verbose:
            print('> info: checkout %s feature "%s" with default params ...'%(feature.output, feature.name))
        # execute pipeline
        try:
            qualified_df = df_normalizer.qualify_column(pipeline(**pipeline_params),feature)
            return df_converter.astype( qualified_df, out_type)
        except Exception as e:
            print('> error: execute feature extraction pipeline, ', e)
        
    """
    " 
    " Clear the cache registry and storage
    "
    """
    def clear_cache(self):
        if not isinstance(self.cache, NullCache):
            self.cache.clear()

    """
    "
    " Inspect the source code of saved feature
    "
    """
    def inspect(self, feature_name, namespace, version = None):
        if not feature_name:
            print('> feature name is required')
        if not namespace:
            print('> feature namespace is required')
        feature_list = self.meta_manager.read(namespace)
        target_uid = None
        for uid, feature in feature_list.items():
            if feature.name.lower()  == feature_name.lower():
                target_uid = uid
                break
        if target_uid:
            pipeline_dump = self.persistor.read(uid, version=version)
            pipeline = self.serializer.decode(pipeline_dump)
            print(pipeline.source_code)
        else:
            print('> feature does not exist.')

    """
    "
    " Get unique ID
    "
    """
    def __get_unique_id__(self, feature, **kwargs):
        """
        @param:: feature: the featureMetaData object
        @param:: kwargs: the keyworded parameter list
        return unique ID
        """
        qualify_name = '.'.join([feature.namespace,feature.name])
        pipeline_params = {}
        version = 'v%s' % (feature.latest_version)
        if qualify_name in kwargs:
            params = kwargs[qualify_name]
            pipeline_params = params['parameter'] if 'parameter' in params else pipeline_params
            v_version = params['version'].lower() if 'version' in params else version
            version_num = int(v_version[1:]) if v_version[0] == 'v' else float('inf')
            if 0 <= version_num < feature.latest_version:
                version = v_version
        unique_id = '%s-%s' % (qualify_name, version)
        for param in pipeline_params:
            unique_id = '.'.join([unique_id, 
                                  '%s=%s' % (param, str(pipeline_params[param]))])
        return unique_id

