from .clients import dns_client

DOMAIN_RECORD_OFF_SET = 0  # 记录开始的偏移, 第一条记录为 0
DOMAIN_RECORD_LIMIT = 3000  # 单次查询的记录数量, 最大为3000


class TencentDnsDomain:
    def __init__(self, object):
        self.object = object

    @classmethod
    def list(cls, **kwargs):
        domains = dns_client.describe_domain_list(**kwargs).get('DomainList')
        return [cls(domain) for domain in domains]

    @classmethod
    def get(cls, domain_name):
        domains = dns_client.describe_domain_list(Keyword=domain_name).get('DomainList')
        if not domains:
            return None
        for domain in domains:
            if domain.get("Name") != domain_name:
                continue
            return cls(domain)
        return None

    @property
    def domain_records(self):
        return TencentDnsRecord.list(self.name, self.ns_records)

    @property
    def registration_date(self):
        return self.object.get("CreatedOn")

    def create_record(self, **kwargs):
        record_id = TencentDnsRecord.create(Domain=self.name, **kwargs)
        return record_id

    def delete_record(self, record_id):
        TencentDnsRecord.get(self.name, record_id).delete()

    def modify_record(self, record_id, **kwargs):
        record_id = TencentDnsRecord.get(self.name, record_id).modify(**kwargs)
        return record_id

    @property
    def status(self):
        return self.object.get('Status')

    @property
    def name(self):
        return self.object.get('Name')

    @property
    def ns_records(self):
        return self.object.get('EffectiveDNS') or []

    def __repr__(self):
        return "<TencentDnsDomain object:{}>".format(self.name)


class TencentDnsRecord:
    def __init__(self, domain, object):
        self.object = object
        self.domain = domain

    @classmethod
    def list(cls, domain, ns_records):
        off_set = DOMAIN_RECORD_OFF_SET
        records = list()
        while True:
            try:
                resp = dns_client.describe_record_list(Domain=domain, Limit=DOMAIN_RECORD_LIMIT, Offset=off_set)
            except BaseException as e:
                if "ResourceNotFound.NoDataOfRecord" in e.args:
                    break
                else:
                    raise
            records.extend(resp.get("RecordList"))
            off_set += DOMAIN_RECORD_LIMIT
        record_objs = []
        for record in records:
            if record.get("Value")[:-1] in ns_records and record.get("Name") == "@" and record.get("Type") == "NS":
                continue
            record_objs.append(cls(domain, record))
        return record_objs

    @classmethod
    def get(cls, domain, record_id):
        res = dns_client.describe_record(Domain=domain, RecordId=int(record_id)).get("RecordInfo")
        if not res:
            return None
        record = {
            "Value": res.get("Value"),
            "Status": "ENABLE" if res.get("Enabled") else "DISABLE",
            "UpdatedOn": res.get("UpdatedOn"),
            "Name": res.get("SubDomain"),
            "Line": res.get("RecordLine"),
            "LineId": res.get("RecordLineId"),
            "Type": res.get("RecordType"),
            "Weight": res.get("Weight"),
            "MonitorStatus": res.get("MonitorStatus"),
            "Remark": res.get("Remark"),
            "RecordId": res.get("Id"),
            "TTL": res.get("TTL"),
            "MX": res.get("MX")
        }
        return cls(domain, record)

    @classmethod
    def create(self, **kwargs):
        record_id = dns_client.create_record(**kwargs).get('RecordId')
        return record_id

    def delete(self):
        dns_client.delete_record(Domain=self.domain, RecordId=self.external_id)

    def modify(self, **kwargs):
        record_id = dns_client.modify_record(Domain=self.domain, RecordId=self.external_id, **kwargs).get('RecordId')
        return record_id

    @property
    def attributes(self):
        return {
            "DomainName": self.domain,
            "Status": self.object.get("Status"),
            "Weight": self.object.get("Weight"),
            "RR": self.object.get("Name"),
            "RecordId": self.object.get("RecordId"),
            "Value": self.object.get("Value"),
            "Line": self.object.get("Line"),
            "Type": self.object.get("Type"),
            "TTL": self.object.get("TTL"),
        }

    @property
    def external_id(self):
        return self.object.get('RecordId')

    def __repr__(self):
        return "<TencentDnsRecord object:{}>".format(self.external_id)
