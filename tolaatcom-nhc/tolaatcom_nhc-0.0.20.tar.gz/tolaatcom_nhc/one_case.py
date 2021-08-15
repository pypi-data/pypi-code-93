import time
import threading
import json
import logging

from tolaatcom_nhc import boto3factory
from tolaatcom_nhc import nethamishpat


class OneCase:

    def __init__(self, master_table=None, config=None):
        self.config = config or {}
        self.master = master_table or 'master_table'
        self.bucket = 'cloud-eu-central-1-q97dt1m5d4rndek'
        self.prefix = 'documents_v2/decision_documents'
        self.local = threading.local()
        self.nhc = None
        self.default_storage = 'ONEZONE_IA'
        self.storage = self.config.get('storage_class', self.default_storage)

        #
        # Means we are doing mass scrape
        #
        self.logger = logging.getLogger('onecase')


    def map_to_dynamo(self, m):
        d = {}
        for k, v in m.items():
            if v:
                d[k] = {'S': str(v)}
        return {'M': d}

    def list_to_dynamo(self, l):
        dl = []
        for s in l:
            del s['__type']
            dl.append(self.map_to_dynamo(s))

        return {'L': dl}


    def upload_decisions(self, caseid, type, decisions):
        s3 = boto3factory.client('s3')
        st = self.storage
        for index, decision in enumerate(decisions):
            i = str(index).zfill(3)

            if decision.get('not-scraped'):
                self.logger.info('Not scraped')
                continue

            if 'images' in decision:
                key = f'{self.prefix}/{caseid}/{type}/{i}.json'
                j = json.dumps(decision['images'])
                self.logger.info('Writing to s3://%s/%s', self.bucket, key)
                s3.put_object(Bucket=self.bucket, Key=key, ContentType='application/json', Body=j, StorageClass=st)
                del decision['images']

            if 'pdf' in decision:
                key = f'{self.prefix}/{caseid}/{type}/{i}.pdf'
                self.logger.info('Writing to s3://%s/%s', self.bucket, key)
                s3.put_object(Bucket=self.bucket, Key=key, ContentType='application/pdf', Body=decision['pdf'],
                              StorageClass=st)
                decision['pdf'].close()
                del decision['pdf']

    def get_nhc(self):
        if not self.nhc:
            self.nhc = nethamishpat.NethamishpatApiClient(config=self.config)

        return self.nhc

    def remove_nhc(self):
        if self.nhc:
            del self.nhc

    def init_permissions(self, key):
        dynamo = boto3factory.client('dynamodb')
        dynamo.update_item(TableName=self.master, Key=key, UpdateExpression='SET #p = if_not_exists(#p, :empty)',
                           ExpressionAttributeNames={'#p': 'permissions'},
                           ExpressionAttributeValues={':empty': {'M': {}}})

    def set_permissions(self, key, permission_name, reason):
        dynamo = boto3factory.client('dynamodb')

        self.init_permissions(key)

        value = {'M': {'ts': {'N': str(int(time.time()))}, 'reason': {'S': reason}}}

        dynamo.update_item(TableName=self.master, Key=key,
                                UpdateExpression='SET #ps.#p=:v',
                                ExpressionAttributeNames={'#ps': 'permissions', '#p': permission_name},
                                ExpressionAttributeValues={':v': value})

    def can_scrape(self, key):
        dynamo = boto3factory.client('dynamodb')
        fields = ('api', 'permissions')
        attribute_names = {f'#{attr}': attr for attr in fields}
        projection_expr_list = [f'#{attr}' for attr in fields]
        projection_expr = ', '.join(projection_expr_list)
        r = dynamo.get_item(TableName=self.master, Key=key,
                            ProjectionExpression=projection_expr,
                            ExpressionAttributeNames=attribute_names)
        if 'Item' not in r:
            return True

        item = r['Item']
        return 'api' not in item and 'permissions' not in r


    def mark_unavailable(self, case):
        case_id = case['CaseDisplayIdentifier']
        keys = [{'case_id': {'S': f'{t}:{case_id}'}} for t in ('n', 't')]
        dynamo = boto3factory.client('dynamodb')

        r= dynamo.batch_get_item(RequestItems={self.master: {'Keys': keys}})
        for item in r['Responses'][self.master]:
            title = item['title']['S']
            if title.strip() == case['Title'].strip():
                key = {'case_id': item['case_id']}

                self.set_permissions(key, 'deleted', 'missing_in_api')


    def mass_scrape(self, case):
        case_number = case['CaseDisplayIdentifier']
        t = case['CaseType']
        key = {'case_id': {'S': f'{t}:{case_number}'}}
        if not self.can_scrape(key):
            return

        self.handle(case)


    def handle(self, by_date):
        n = by_date['CaseDisplayIdentifier']

        nhc = self.get_nhc()

        r = nhc.parse_everything(by_date)

        if r is None:
            #self.mark_unavailable(by_date)
            return "deleted"

        if r['type'] == 'court':
            t = 'n'
        elif r['type'] == 'transport':
            t = 't'
        elif r['type'] == 'old':
            t = 'o'
            case_id = by_date['CaseDisplayIdentifier']
            court = by_date['CourtName']
            case_type = by_date['CaseTypeShortName']
            n = f'{case_type} {case_id} {court}'

        else:
            raise Exception()

        case_id = r['case']['CaseID']

        for what in 'decisions', 'verdicts':
            self.upload_decisions(case_id, what, r[what])

        sittings = self.list_to_dynamo(r['sittings'])
        decisions = self.list_to_dynamo(r['decisions'])
        verdicts = self.list_to_dynamo(r['verdicts'])

        if 'case' in r:
            case = self.map_to_dynamo(r['case'])
        else:
            case = {'M': {}}

        by_date = self.map_to_dynamo(by_date)

        ts = {'S': str(int(time.time()))}

        m = {'ts': ts,
             'case': case,
             'type': {'S': r['type']},
             'sittings': sittings,
             'decisions': decisions,
             'verdicts': verdicts}

        object = {'M': m}
        k = f'{t}:{n}'
        key = {'case_id': {'S': k}}
        dynamo = boto3factory.client('dynamodb')
        dynamo.update_item(
            TableName=self.master,
            Key=key,
            UpdateExpression='Set #api=:api, #by_date=:by_date',
            ExpressionAttributeNames={'#api': 'api', '#by_date': 'by_date'},
            ExpressionAttributeValues={':api': object, ':by_date': by_date}
        )

    def close(self):
        self.get_nhc().close()
        self.remove_nhc()


if __name__=='__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('botocore').setLevel(logging.WARN)
    logging.getLogger('urllib3').setLevel(logging.WARN)

    o=OneCase()
    o.handle({'CaseType': 'n', 'CaseDisplayIdentifier': '3851-03-17'})

    exit(30)
    o.mass_scrape('n', '67104-01-20')
    exit(0)
    r = o.can_scrape({'case_id': {'S': 'n:67104-01-20'}})
    print(r)
    exit(0)
    o.handle({'Title': title, 'CaseDisplayIdentifier': '46542-04-16'})
