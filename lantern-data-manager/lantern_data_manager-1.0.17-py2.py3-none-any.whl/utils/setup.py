import os
import boto3
from moto import mock_sqs
# from lantern_data_manager.utils.logger import logger

# register variables in environment
def register_environment( variables ):
    """ register dictionary of variables in environment/memory variables """
    for key in variables.keys():
        os.environ[key] = variables[key]

# creates dynamodb table
def create_tables(instance,tables):
    for table in tables:
        # dynamodb = boto3.resource('dynamodb', region_name=table["region_name"], endpoint_url=table["endpoint_url"])
        params = {
            "TableName": table["table_name"],
            "KeySchema": [{'AttributeName': x["name"], 'KeyType': x["key_type"] } for x in table["keys"]],
            "AttributeDefinitions": [{'AttributeName': x["name"], 'AttributeType': x["type"]} for x in table["columns"]],
            "ProvisionedThroughput": { 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10 }
        }
        # adding indexes
        indexes = []
        if "indexes" in table:
            for index in table["indexes"]:
                indexes.append({
                    "IndexName": index["name"],
                    "KeySchema": [{  "AttributeName": x["name"], "KeyType": x["key_type"]} for x in index["keys"]],
                    "Projection": { "ProjectionType": "ALL" },
                    "ProvisionedThroughput": { 'ReadCapacityUnits': 10, 'WriteCapacityUnits': 10 }
                })
        if len(indexes):
            params["GlobalSecondaryIndexes"] = indexes
        
        # Creating table with defined parameters
        try:
            table = instance.create_table(**params)
        except Exception as e:
            logger.warning("warning creating table with message: {}".format(e))