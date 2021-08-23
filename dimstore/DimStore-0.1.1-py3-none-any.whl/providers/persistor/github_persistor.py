"""
"   Use Github as persist layer
" docu: https://docs.github.com/en/rest
" docu: https://pygithub.readthedocs.io/en/latest/introduction.html
"""
from sys import version

from yaml import dump
from dimsum.core.feature_metadata import FeatureOperation
from dimsum.providers.persistor.persistor_base import PersistorBase
from dimsum.utility.github_client import GitHubClient

class GitHubPersistor(PersistorBase):

    def __init__(self, config):
        self.config = config
        self.username = config['username']
        self.token = config['token']
        self.repo_name = config['repository_name']
        self.branch = config['branch']
        self.enterprise_name = config['enterprise_hostname']
        self.client = self.__get_github_client__()
    
    """
    "
    " create a new file in github reposiory from feature dumps and metadata
    "
    """

    def write(self, feature, dumps, **kwargs):
        """ 
        @param::feature: instance of Feature class
        @param::dumps: the byte codes of pipeline dumps
        @param::kwargs: name parameter list
        return none
        """
        operation_list = kwargs.get('supported_operation')
        try:                      
            if FeatureOperation.CREATE_NEW_VERSION in operation_list :
                self.client.update(feature.uid, f"updated file: {feature.uid}", dumps)
            else:
                self.client.create(feature.uid, dumps, f"created file: {feature.uid}")
            feature.latest_version = self.client.version_count(feature.uid)
        except Exception as e:
            print('> github client create failed!', e)
            raise

    """
    "
    " read the feature file from github repository and extract the byte dumps
    "
    """
    def read(self, uid, **kwargs):
        """ 
        @param::uid: symbolic string name used to identify the feature
        @param string::version: version number of file
        @param::kwargs: named parameter list
        return the byte dumps of feature asset
        """
        try:
            version = kwargs.get('version')
            content = self.client.read(uid, version)
            return content
        except Exception as e:
            print('> github client read failed! \n',e)
            raise

    def delete(self, uid, **kwargs):
        """
        @param::uid: symbolic string name used to identify the feature
        @param::kwargs: named parameter list
        return none
        """
        try:
            self.client.delete(uid, f"deleted file: {uid}")
        except Exception as e:
            print('> github client delete failed! \n',e)
            raise

    def __get_github_client__(self):
        """
        @param::none:
        return the github client instance
        """
        client = None
        try:
            client = GitHubClient(self.username, self.token, self.repo_name, self.branch, self.enterprise_name)
        except Exception as e:
            print('> github client initialization failed! \n', e)
            raise

        return client