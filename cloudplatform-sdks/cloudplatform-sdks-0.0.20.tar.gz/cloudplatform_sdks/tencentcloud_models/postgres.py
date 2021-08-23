from .clients import postgres_client


class TencentPostgreSQL:
    def __init__(self, obj):
        self.obj = obj

    @property
    def external_id(self):
        return self.obj.get('DBInstanceId')

    @property
    def external_name(self):
        return self.obj.get('DBInstanceName')

    @classmethod
    def get(cls, db_id):
        resp = postgres_client.describe_db_info(DBInstanceId=db_id).get('DBInstance')
        return cls(resp)

    @classmethod
    def create(cls, **kwargs):
        return postgres_client.create_db(**kwargs)

    @classmethod
    def init_instance(cls, **kwargs):
        return postgres_client.init_db(**kwargs)

    @classmethod
    def delete(cls, db_id):
        return postgres_client.delete_db(DBInstanceId=db_id)

    @classmethod
    def stop(cls, db_id):
        return postgres_client.isolate_db(DBInstanceIdSet=[db_id])

    @classmethod
    def start(cls, db_id):
        return postgres_client.dis_isolate_db(DBInstanceIdSet=[db_id])

    @classmethod
    def get_status(cls, db_id):
        db_instance = cls.get(db_id).obj
        return db_instance.get('DBInstanceStatus')

    @classmethod
    def get_order_info(cls, order_id):
        return postgres_client.describe_orders(DealNames=[order_id]).get('Deals')[0]

    @classmethod
    def open_extranet(cls, db_id):
        return postgres_client.open_db_extranet(DBInstanceId=db_id)

    @classmethod
    def close_extranet(cls, db_id):
        return postgres_client.close_db_extranet(DBInstanceId=db_id)