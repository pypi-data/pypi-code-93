"""AWS Dynamo DB client."""

import ccalogging

from ccaaws.botosession import BotoSession

log = ccalogging.log


class DynamoDB(BotoSession):

    LCACHE = []

    def __init__(self, **kwargs):
        self.dolcache = False
        if kwargs is not None and "LambdaCache" in kwargs:
            self.dolcache = kwargs["LambdaCache"]
            del kwargs["LambdaCache"]
        super().__init__(**kwargs)
        self.newClient("dynamodb")

    def getAll(self, table):
        if self.dolcache and len(self.LCACHE) > 0:
            return self.LCACHE
        resp = self.client.scan(TableName=table)
        data = resp["Items"]
        while resp.get("LastEvaluatedKey"):
            resp = self.client.scan(
                TableName=table, ExclusiveStartKey=resp["LastEvaluatedKey"]
            )
            data.extend(resp["Items"])
        if self.dolcache:
            self.LCACHE = data
        return data

    def getItem(self, item):
        """Item is a dictionary in dynamodb stylee.

        see:
        https://boto3.readthedocs.io/en/latest/
        reference/services/dynamodb.html#DynamoDB.Client.get_item

        i.e.
        item={
          "TableName"='tablename',
          "Key"={
            'accountname':{
              'S':'connectedhomes-dev',
            },
          }
        }

        Args:
            item: item dictionary
        """
        resp = None
        try:
            resp = self.client.get_item(TableName=item["TableName"], Key=item["Key"])
        except Exception as e:
            log.warning(f"Failed to retrieve item {item}, Exception was {e}")
        return resp

    def putItem(self, item):
        """
        item is a dict in dynamodb style, see link above and check put_item
        """
        resp = None
        try:
            resp = self.client.put_item(TableName=item["TableName"], Item=item["Item"])
        except Exception as e:
            log.warning(f"Failed to put item {item}, Exception was {e}")
        return resp

    def deleteItem(self, item):
        try:
            self.client.delete_item(TableName=item["TableName"], Key=item["Key"])
            log.info(f"deleted: {item}")
        except Exception:
            log.warning(f"Failed to delete {item}")
