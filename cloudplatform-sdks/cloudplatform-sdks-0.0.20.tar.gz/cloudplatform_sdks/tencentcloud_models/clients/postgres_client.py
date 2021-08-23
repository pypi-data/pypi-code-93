from .client import TencentClient
from tencentcloud.postgres.v20170312 import postgres_client as tencent_postgres_client
from tencentcloud.postgres.v20170312 import models


class PostgresClient(TencentClient):
    def __init__(self, *args, **kwargs):
        super(PostgresClient, self).__init__(*args, **kwargs)
        self.client = tencent_postgres_client.PostgresClient(self.cred, self.region)

    def create_db(self, **kwargs):
        req = models.CreateDBInstancesRequest()
        return self.do_request(self.client.CreateDBInstances, req, **kwargs)

    def init_db(self, **kwargs):
        req = models.InitDBInstancesRequest()
        return self.do_request(self.client.InitDBInstances, req, **kwargs)

    def isolate_db(self, **kwargs):
        req = models.IsolateDBInstancesRequest()
        return self.do_request(self.client.IsolateDBInstances, req, **kwargs)

    def dis_isolate_db(self, **kwargs):
        req = models.DisIsolateDBInstancesRequest()
        return self.do_request(self.client.DisIsolateDBInstances, req, **kwargs)

    def delete_db(self, **kwargs):
        req = models.DestroyDBInstanceRequest()
        return self.do_request(self.client.DestroyDBInstance, req, **kwargs)

    def describe_orders(self, **kwargs):
        req = models.DescribeOrdersRequest()
        return self.do_request(self.client.DescribeOrders, req, **kwargs)

    def describe_db_info(self, **kwargs):
        req = models.DescribeDBInstanceAttributeRequest()
        return self.do_request(self.client.DescribeDBInstanceAttribute, req, **kwargs)

    def open_db_extranet(self, **kwargs):
        req = models.OpenDBExtranetAccessRequest()
        return self.do_request(self.client.OpenDBExtranetAccess, req, **kwargs)

    def close_db_extranet(self, **kwargs):
        req = models.CloseDBExtranetAccessRequest()
        return self.do_request(self.client.CloseDBExtranetAccess, req, **kwargs)

    def modify_db_name(self, **kwargs):
        req = models.ModifyDBInstanceNameRequest()
        return self.do_request(self.client.ModifyDBInstanceName, req, **kwargs)

    def upgrade_db(self, **kwargs):
        req = models.UpgradeDBInstanceRequest()
        return self.do_request(self.client.UpgradeDBInstance, req, **kwargs)