from elasticsearch import Elasticsearch
import os

class ElasticSearchController:
    """ 
    Class that wraps Elasticsearch API import
    """

    def __init__(self,host,stage):
        self.elasticInstance = Elasticsearch(hosts=[host])
        self.url = host
        self.stage = stage

    def query(self,index,query):
        """Performs a query in a given index in elastic search

        Args:
            index (string): name of index to perform query
            query (dict): a valid elastic search query

        Returns:
            dict: response from elastic
        """
        index = "{}-{}".format(index,self.stage)
        return self.elasticInstance.search(body=query, index=index)

    def add_data(self,index,id,document):
        """
        Creates new data in the index

        Args:
            index (string): name of index to perform query
            id (string): the id that the document will have
            document (dict): the json/dict to be saved in elastic

        Returns:
            dict: response from elastic
        """
        index = "{}-{}".format(index,self.stage)
        return self.elasticInstance.create(index=index,id=id,body=document)

