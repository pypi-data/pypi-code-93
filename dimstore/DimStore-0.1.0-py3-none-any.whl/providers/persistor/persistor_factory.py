"""
    persistor factory
"""
from dimsum.providers.persistor.flatfile_persistor import FlatFilePersistor
from dimsum.providers.persistor.github_persistor import GitHubPersistor
from dimsum.providers.persistor.ibm_object_storage_persistor import IBMObjectStoragePersistor
from dimsum.providers.persistor.watson_knowledge_catalog_persistor import WatsonKnowlegeCatalogPersistor

class PersistorFactory():

    # fabricate persistor
    @staticmethod
    def get_persistor(config):
        if config['type'] == 'flat_file':
            return FlatFilePersistor(config)
        elif config['type'] == 'ibm_object_storage':
            return IBMObjectStoragePersistor(config)
        elif config['type'] == 'ibm_watson_knowledge_catalog':
            return WatsonKnowlegeCatalogPersistor(config)
        elif config['type'] == 'github':
            return GitHubPersistor(config)
        else:
            raise Exception('> persistor provider: %s is not supported' % (config['type']))

    # return supported persistor info
    @staticmethod
    def info():
        return ['flat_file: flat file persistor.', 
                'ibm_object_storage: IBM object storage persistor.',
                'ibm_watson_knowledge_catalog: IBM Watson Knowledge Catalog persistor.',
                'github: GitHub persistor'
                ]