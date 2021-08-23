"""
    meta manager factory
"""

from dimsum.providers.meta_manager.flatfile_meta_manager import FlatFileMetaManager
from dimsum.providers.meta_manager.ibm_wkc_meta_manager import WatsonKnowledgeCatalogMetaManager
from dimsum.providers.meta_manager.ibm_object_storage_meta_manager import IBMObjectStorageMetaManager

class MetaManagerFactory():

    # meta manager factory
    @staticmethod
    def get_meta_manager(config):
        if config['type'] == 'flat_file':
            return FlatFileMetaManager(config)
        elif config['type'] == 'ibm_watson_knowledge_catalog':
            return WatsonKnowledgeCatalogMetaManager(config)
        elif config['type']  == 'ibm_object_storage':
            return IBMObjectStorageMetaManager(config)
        else:
            raise Exception('> meta manager provider: %s is not supported' % (config['type']))

    # return supported meta manager info
    @staticmethod
    def info():
        return ['flat_file: flat file meta manager.','ibm_watson_knowledge_catalog: watson knowledge catalog meta manager.']