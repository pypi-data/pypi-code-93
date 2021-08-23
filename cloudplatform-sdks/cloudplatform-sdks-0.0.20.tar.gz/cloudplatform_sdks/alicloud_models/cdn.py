from .clients import cdn_client


class AliCdnDomain:
    def __init__(self, object):
        self.object = object

    @classmethod
    def list(cls, query_params=None):
        domains = cdn_client.describe_user_domains(query_params).get('Domains', {}).get('PageData')
        return [cls(domain) for domain in domains]

    @classmethod
    def get(cls, query_params=None):
        domain = cdn_client.describe_user_domains(query_params).get('Domains', {}).get('PageData')
        if len(domain) > 0:
            return cls(domain[0])
        else:
            return None

    def fresh(self):
        query_params = {
            "DomainName": self.name
        }
        new_object = cdn_client.describe_user_domains(query_params).get('Domains', {}).get('PageData')[0]
        self.object = new_object

    @staticmethod
    def fresh_cache(query_params):
        return cdn_client.fresh_object_cache(query_params)

    @staticmethod
    def push_cache(query_params):
        return cdn_client.push_object_cache(query_params)

    @staticmethod
    def describe_tasks(query_params):
        tasks = cdn_client.describe_tasks(query_params)
        return [Task(task_info) for task_info in tasks]

    def start(self):
        query_params = {
            "DomainName": self.name
        }
        return cdn_client.start_cdn_domain(query_params)

    def stop(self):
        query_params = {
            "DomainName": self.name
        }
        return cdn_client.stop_cdn_domain(query_params)

    def delete(self):
        query_params = {
            "DomainName": self.name
        }
        return cdn_client.delete_cdn_domain(query_params)

    @property
    def status(self):
        return self.object.get('DomainStatus')

    @property
    def name(self):
        return self.object.get('DomainName')

    @property
    def cname(self):
        return self.object.get('Cname')

    @property
    def type(self):
        return self.object.get('CdnType')

    @property
    def sources(self):
        return self.object.get('Sources')

    @property
    def description(self):
        return self.object.get('Description')

    @property
    def created_time(self):
        return self.object.get('GmtCreated').replace("T", " ").replace("Z", "")

    @property
    def modified_time(self):
        return self.object.get('GmtModified').replace("T", " ").replace("Z", "")

    def __repr__(self):
        return "<AliCdnDomain object:{}>".format(self.name)


class Task:
    FINISHED_STATUS = ['Failed', 'Complete']
    SUCCESS_STATUS = ['Complete']

    def __init__(self, object):
        self.object = object

    @property
    def id(self):
        return self.object.get('TaskId')

    @property
    def status(self):
        return self.object.get('Status')

    @property
    def type(self):
        return self.object.get('ObjectType')

    @property
    def object_path(self):
        return self.object.get('ObjectPath')

    @property
    def process(self):
        return self.object.get('Process')

    @property
    def description(self):
        return self.object.get('Description')

    @property
    def is_finished(self):
        return self.status in self.FINISHED_STATUS

    @property
    def is_success(self):
        return self.status in self.SUCCESS_STATUS

    def __repr__(self):
        info = "Status: {} Process: {} Type: {} ObjectPath: {} Description: {}".format(self.status, self.process,
                                                                                       self.type, self.object_path,
                                                                                       self.description)
        return info
