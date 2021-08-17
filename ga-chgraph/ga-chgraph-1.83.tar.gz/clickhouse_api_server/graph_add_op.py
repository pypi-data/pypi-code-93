import logging

# LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s"
# logging.basicConfig(filename='./CHGraph.log', level=logging.INFO, format=LOG_FORMAT)
# logger = logging.getLogger('CHGraph')
import Longger_design
logger = Longger_design.get_logger()

class CHGraph(object):

    def __init__(self, client):
        self.client = client
        logger.info('CHGraph Start')

    def execute(self, sql):
        res = self.client.query_dataframe(sql)
        return res
