from .clients import cdn_client


class TencentCdnDomain:
    def __init__(self, object):
        self.object = object

    @classmethod
    def list(cls, **kwargs):
        domains = cdn_client.list_domains(**kwargs).get('Domains')
        return [cls(domain) for domain in domains]

    @classmethod
    def get(cls, domain_name):
        params = {
            "Filters": [
                {
                    "Name": "domain",
                    "Value": [domain_name]
                }
            ]
        }
        domains = cdn_client.list_domains(**params).get('Domains')
        if domains and len(domains) > 0:
            return cls(domains[0])
        else:
            return None

    @staticmethod
    def fresh_urls_cache(**kwargs):
        return cdn_client.refresh_urls_cache(**kwargs)

    @staticmethod
    def fresh_path_cache(**kwargs):
        return cdn_client.refresh_path_cache(**kwargs)

    @staticmethod
    def push_urls_cache(**kwargs):
        return cdn_client.push_urls_cache(**kwargs)

    @staticmethod
    def describe_push_tasks(**kwargs):
        resp = cdn_client.describe_push_tasks(**kwargs)
        return resp.get("PushLogs")

    @staticmethod
    def describe_fresh_tasks(**kwargs):
        resp = cdn_client.describe_refresh_tasks(**kwargs)
        return resp.get("PurgeLogs")

    @staticmethod
    def describe_task_status(task_type, **kwargs):
        if task_type == "push":
            resp = cdn_client.describe_push_tasks(**kwargs).get("PushLogs")
            if not resp:
                return ""
            return resp[0].get("Status")
        elif task_type == "fresh":
            resp = cdn_client.describe_refresh_tasks(**kwargs).get("PurgeLogs")
            if not resp:
                return ""
            return resp[0].get("Status")

    def start(self):
        params = {
            "Domain": self.name
        }
        return cdn_client.start_cdn_domain(**params)

    def stop(self):
        params = {
            "Domain": self.name
        }
        return cdn_client.stop_cdn_domain(**params)

    def delete(self):
        params = {
            "Domain": self.name
        }
        return cdn_client.delete_cdn_domain(**params)

    @property
    def status(self):
        return self.object.get('Status')

    @property
    def id(self):
        return self.object.get('ResourceId')

    @property
    def name(self):
        return self.object.get('Domain')

    @property
    def cname(self):
        return self.object.get('Cname')

    @property
    def type(self):
        return self.object.get('ServiceType')

    @property
    def created_time(self):
        return self.object.get('CreateTime')

    @property
    def modified_time(self):
        return self.object.get('UpdateTime')

    def __repr__(self):
        return "<TencentCdnDomain object:{}>".format(self.name)



