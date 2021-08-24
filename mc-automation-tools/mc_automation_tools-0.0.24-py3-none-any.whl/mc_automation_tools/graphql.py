"""
This module wrap and provide pytonic client interface to integrate with graphql server
"""
from mc_automation_tools.configuration import config
from mc_automation_tools import common
# from graphqlclient import GraphQLClient

from python_graphql_client import GraphqlClient


class GqlClient:
    """This class wrapping and provide access into gql server"""
    def __init__(self, host):
        self.client = GraphqlClient(endpoint=host)

    def execute_free_query(self, query=None, variables=None):
        """
        This method will send query by providing entire query and variables -> variables by default <None>
        """
        res = self.client.execute(query=query, variables=variables)
        return res

    def get_jobs_tasks(self, query=config.JOB_TASK_QUERY, variables=None):
        retry = 3
        for i in range(retry):
            try:
                res = self.client.execute(query=query, variables=variables)
                return res
            except Exception as e:
                continue
            time.sleep(3)
        raise Exception(f'Failed access to gql after {i+1} / {retry} tries')
        # return res
