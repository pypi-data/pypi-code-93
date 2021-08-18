import requests
from datetime import datetime
from intstreamsdk.client import Client
import tldextract
import logging
import copy

LOG = logging.getLogger(__name__)


class Resource(object):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

    def __init__(self, client, endpoint, method=None):
        self.client = client
        self.base = self.client.server_url+"api/"
        self.endpoint= endpoint
        self.request_url = '{base}{endpoint}'.format(base=self.base,
                                                         endpoint=self.endpoint)

        self.method = method
        self.valid_codes = {Resource.GET: [200],
                            Resource.PUT: [200],
                            Resource.POST: [201,200],
                            Resource.DELETE: [204]}
        self.json = None# any json data to send with request
        self.params = {}  # any query string parameters to send with request
        self.headers = {}  # any headers to send with request
        self.files = None

    def full_request(self, raise_exc=True):
        """
        returns response and data for sync requests
        :param rasise_exc: bool
        :return:
        """
        pre_r = self.client.request(method=self.method,
                                headers=self.headers,
                                request_url=self.request_url,
                                params=self.params,
                                json=self.json,
                                files=self.files
                                )
        return self.getdata(pre_r, raise_exc)

    def request(self):
        """
        returns response and data for sync requests
        :param rasise_exc: bool
        :return:
        """
        pre_r = self.client.request(method=self.method,
                                headers=self.headers,
                                request_url=self.request_url,
                                params=self.params,
                                json=self.json,
                                )
        return pre_r

    def getdata(self, pre_r, raise_exc=True):
        """
        Test for html error code and return data
        :param response
        :return:
        """
        r = self.client.get_actual_response(pre_r)
        if raise_exc:
            try:
                r.raise_for_status()
            except requests.HTTPError as e:
                LOG.error(str(r.text))
                raise e
        actual_response = r
        result = {}
        if actual_response.status_code in self.valid_codes[self.method]:
            result["status"] = self.SUCCESS
            result["response_code"] = actual_response.status_code
            format = actual_response.headers.get("Content-Type", None)
            if format == Client.FORMAT_JSON:
                json_response = actual_response.json()
                if isinstance(json_response, list):
                    result["data"] = {"results": json_response}
                else:
                    result["data"] = actual_response.json()

            elif format == Client.FORMAT_XML:
                result["data"]=actual_response.content.decode("utf8")
            else:
                result["data"]=actual_response.content
        else:
            result["status"] = self.FAILED
            result["response_code"] = actual_response.status_code
            result["data"] = actual_response.content.decode('utf8')
        return result

    def filter(self, filter):
        """

        :param filter: dict
        :return:
        """
        self.params = filter
        """
        params = "?"
        count = 0
        for key, value in filter.items():
            if count == 0:
                params += key + "=" + str(value)
            else:
                params += "&" + key + "=" + str(value)
            count +=1

        self.request_url = '{current}{params}'.format(current=self.request_url,
                                                   params=params)
        """

    def id(self, id):
        self.request_url = '{current}{id}/'.format(current=self.request_url,
                                                   id=id)


class ResourcePaged(Resource):

    def __init__(self,client, endpoint, method=Resource.GET):
        super(ResourcePaged,self).__init__(client, endpoint, method)
        self.first=True
        self.next=None #data field with next url
        self.previous=None #data field with previous url
        # for next if null we are done paging

    def __iter__(self):
        return self

    def __next__(self):
        if self.next is not None or self.first is not False:
            self.first=False
            if self.next is not None:
                self.request_url=self.next
            response = super(ResourcePaged,self).full_request()
            self.next = response["data"]["next"]
        else:
            raise StopIteration


class BaseArticle(ResourcePaged):
    def __init__(self, endpoint, client:Client, method=Resource.GET, ):
        super(BaseArticle,self).__init__(client, endpoint, method)

    def article_post(self, title, source_id, filename):
        #set format to multipart
        """
        :param title: str
        :param file_h: file
        :return:
        """
        self.files = {"title": (None, title),
                      "source": (None, source_id),
                      "file": open(filename, "rb")}


class TextArticle(BaseArticle):
    def __init__(self, client:Client, method=Resource.GET):
        super(TextArticle,self).__init__("txtarticles/", client, method)


class HtmlArticle(BaseArticle):
    def __init__(self, client:Client, method=Resource.GET):
        super(HtmlArticle,self).__init__("htmlarticles/", client, method)


class PDFArticle(BaseArticle):
    def __init__(self, client:Client, method=Resource.GET):
        super(PDFArticle,self).__init__("pdfarticles/", client, method)


class WordDocxArticle(BaseArticle):
    def __init__(self, client:Client, method=Resource.GET):
        super(WordDocxArticle, self).__init__("pdfarticles/", client, method)


class RawArticle(ResourcePaged):
    def __init__(self, client:Client, method=Resource.GET):
        super(RawArticle,self).__init__(client, "rawarticles/", method)

    def article_post(self, title, source_id, text):
        """
        :param title: str
        :param source_id: int
        :param text: str
        :return:
        """
        self.json = {"title": title,
                     "source": source_id,
                     "text": text}


class UserInfo(ResourcePaged):
    def __init__(self, client:Client, method=Resource.GET):
        super(UserInfo, self).__init__(client, "userinfo/", method)


class Indicator(ResourcePaged):
    def indicators_post(self, indicators):
        """

        :param indicators: list[str]
        :return:
        """
        self.json = [{"value": i} for i in indicators]

    def indicators_put(self, info):
        self.json = info


class IndicatorBase(Indicator):

    def __init__(self, client:Client, method=Resource.GET):
        super(IndicatorBase, self).__init__(client, "indicatorbase/", method)


class MD5(Indicator):

    def __init__(self, client:Client, method=Resource.GET):
        super(MD5,self).__init__(client, "indicatormd5/", method)


class SHA1(Indicator):

    def __init__(self, client:Client, method=Resource.GET):
        super(SHA1,self).__init__(client, "indicatorsha1/", method)


class SHA256(Indicator):

    def __init__(self, client:Client, method=Resource.GET):
        super(SHA256,self).__init__(client, "indicatorsha256/", method)


class Email(Indicator):

    def __init__(self, client:Client, method=Resource.GET):
        super(Email, self).__init__(client, "indicatoremail/", method)


class IPV4(Indicator):

    def __init__(self, client:Client, method=Resource.GET):
        super(IPV4, self).__init__(client, "indicatoripv4/", method)


class IPV6(Indicator):

    def __init__(self, client:Client, method=Resource.GET):
        super(IPV6, self).__init__(client, "indicatoripv6/", method)


class PartsNetLoc(object):
    def __init__(self, subdomain, domain, suffix_id):
        """

        :param subdomain: str
        :param domain: str
        :param suffix_id: int
        """
        self.subdomain = subdomain
        self.domain = domain
        self.suffix_id = suffix_id


class PartsNetLocValue(object):
    def __init__(self, subdomain=None, domain=None, suffix__value=None):
        """

        :param subdomain: str
        :param domain: str
        :param suffix_id: int
        """
        self.subdomain = subdomain
        self.domain = domain
        self.suffix__value = suffix__value

    def full_domain(self):
        if self.subdomain is not None:
            self.subdomain += self.subdomain + "."
        else:
            self.subdomain = ""
        return self.subdomain + self.domain + "." + self.suffix__value


class NetLoc(Indicator):
    def __init__(self, client:Client, method=Resource.GET):
        super(NetLoc, self).__init__(client, "indicatornetloc/", method)

    def indicators_post(self, indicators):
        """

        :param indicators: list[PartsNetLoc]
        :return:
        """

        self.json = [{"subdomain": i.subdomain,
                      "domain": i.domain,
                      "suffix": i.suffix_id} for i in indicators]


class Suffix(Indicator):
    def __init__(self, client:Client, method=Resource.GET):
        super(Suffix, self).__init__(client, "indicatorsuffix/", method)


class IntstreamSDKException(Exception):
    pass


class NoTLD(IntstreamSDKException):
    pass


class ColumnNotFound(IntstreamSDKException):
    pass


class DomainExtractor(object):
    def __init__(self, url, client:Client, raise_exc=True):
        """
        :param client:
        :param url:
        """
        self.subdomain, self.domain, self.suffix = tldextract.extract(url)
        if (self.suffix is None or self.suffix == "") and raise_exc:
            raise NoTLD
        resource = Suffix(client)
        resource.filter(filter={"value":self.suffix})
        r = resource.full_request(raise_exc=raise_exc)
        suffix_id="NA"
        if r["status"] == Resource.SUCCESS:
            suffix_id = r["data"]["results"][0]["id"]
        self.net_loc = PartsNetLoc(subdomain=self.subdomain,
                                  domain=self.domain,
                                  suffix_id=suffix_id)


class DomainLoader(object):
    def __init__(self, urls, client:Client,):
        """
        :param urls: list[str]
        :param client: Client
        :param raise_exc: bool
        """
        self.urls = urls
        self.client = client

    def _get_perform(self, method, update=True):
        """

        :param method: str
        :return: list[dict]
        """
        new_net_locs = []
        existing = []
        all_data = []
        for i in self.urls:
            extractor = DomainExtractor(i, self.client,)
            resource_get = NetLoc(self.client, method=Resource.GET)
            filter = {
                "subdomain":extractor.net_loc.subdomain,
                "domain":extractor.net_loc.domain,
                "suffix":extractor.net_loc.suffix_id
            }
            resource_get.filter(filter=filter)
            r = resource_get.full_request()
            if r["status"] == Resource.SUCCESS and r["data"]["count"] == 0:
                new_net_locs.append(extractor.net_loc)
            else:
                existing.extend(r["data"]["results"])
                all_data.extend(existing)
        if update and len(existing) > 0:
            # update indicators to kick off indicator jobs on intstream
            for i in copy.deepcopy(existing):
                resource = NetLoc(self.client, method=Resource.PUT)
                resource.id(i["id"])
                del i["id"]
                del i["value"]
                resource.indicators_put(i)
                res = resource.full_request()
                all_data.extend([res["data"]])

        if len(new_net_locs) > 0:
            resource = NetLoc(self.client, method=Resource.POST)
            resource.indicators_post(new_net_locs)
            res = resource.full_request()
            all_data.extend(res["data"]["results"])
        return all_data

    def upload(self):
        """
        :return: list[dict]
        """
        res = self._get_perform(method=Resource.POST)
        return res

    def delete(self):
        """
        :return: list[dict]
        """
        res = self._get_perform(method=Resource.DELETE)
        return res


class Link(Indicator):

    def __init__(self, client:Client, method=Resource.GET, article_id=None, indicator_ids=None):
        endpoint = "articles/{id}/link/".format(id=article_id)
        super(Link, self).__init__(client, endpoint, method)
        self.json = {
            "indicator_ids": [i for i in indicator_ids]
        }


class IndicatorAction(object):
    def __init__(self, client):
        self.client = client

    def check_delete(self, indicators, resource_class):
        resource_get = resource_class(client=self.client, method=Resource.GET)
        filter = {"value__in": ",".join(indicators)}
        resource_get.filter(filter)
        response_get = resource_get.full_request()
        existing = [i["id"] for i in response_get["data"]["results"]]
        for i in existing:
            resource_del = resource_class(client=self.client, method=Resource.DELETE)
            resource_del.id(i)
            resource_del.full_request()

    def check_upload(self,
                     indicators,
                     resource_class,
                     update=True
                     ):
        """
        check upload for all indicator types except NetLoc; use DomainLoader instead
        :param indicators:
        :param resource_class:
        :param update: bool. set to True if you want tasks to run for each indicator
        whether or not it already exists in the database
        :return:
        """
        resource_get = resource_class(client=self.client, method=Resource.GET)
        filter = {"value__in": ",".join(indicators)}
        resource_get.filter(filter)
        response_get = resource_get.full_request()
        existing = [i["value"] for i in response_get["data"]["results"]]
        existing_obj = response_get["data"]["results"]
        not_existing = set(indicators).difference(existing)
        all_data = existing_obj
        if len(not_existing) > 0:
            resource_post = resource_class(client=self.client, method=Resource.POST)
            resource_post.indicators_post(not_existing)
            response_post = resource_post.full_request()
            all_data = response_get["data"]["results"]
            all_data.extend(response_post["data"]["results"])
        if update:
            if len(existing_obj) > 0:
                # update indicator to kick off indicator tasks.
                for i in copy.deepcopy(existing_obj):
                    resource_put = resource_class(client=self.client, method=Resource.PUT)
                    resource_put.id(i["id"])
                    resource_put.indicators_put(i)
                    response_put = resource_put.full_request()
                    all_data.extend(response_put["data"])

        return all_data


class ValueDelete(IndicatorAction):
    """
    deprecated
    """
    def __init__(self, client):
        super(ValueDelete, self).__init__(client)


class Uploader(IndicatorAction):
    """
    deprecated
    """
    def __init__(self, client):
        super(Uploader, self).__init__(client)


class Source(ResourcePaged):
    def __init__(self, client:Client, method=Resource.GET):
        super(Source, self).__init__(client, "sources/", method)

    def source_post(self, name):
        self.json = {"name": name}


class CustomField(Resource):
    """
    abstract class
    """
    def __init__(self, client:Client, endpoint, method=Resource.GET):
        super(CustomField, self).__init__(client, endpoint, method)

    def col_value_put(self, id, name, value, indicator_id):
        self.request_url += str(id) + "/"
        self.json = {"name": name, "value": value,"indicator": indicator_id}

    def col_value_post(self, name, value, indicator_id):
        self.json = {"name": name, "value": value, "indicator": indicator_id}

    def getIndicatorColumns(self, indicator_id):
        # retrieve id
        res_col_get = CustomField(self.client, endpoint=self.endpoint, method=Resource.GET)
        res_col_get.filter({"indicator": indicator_id})
        r = res_col_get.full_request()
        return r["data"]["results"]


class IndicatorNumericField(CustomField):
    def __init__(self, client:Client, method=Resource.GET):
        super(IndicatorNumericField, self).__init__(client, "indicatornumericfield/", method)


class IndicatorTextField(CustomField):
    def __init__(self, client:Client, method=Resource.GET):
        super(IndicatorTextField, self).__init__(client, "indicatortextfield/", method)


class ColumnGetPerform(object):
    def __init__(self, client):
        self.client = client

    def upsert(self, col_class,  name, value, indicator_id):
        """

        :param col_class: CustomField child class
        :param name:
        :param value:
        :param indicator_id: int
        :return:
        """
        res_get = col_class(self.client, method=Resource.GET)
        res_get.filter({"name":name, "indicator": indicator_id})
        r = res_get.full_request()
        if len(r["data"]["results"]) == 0:
            res_put = col_class(self.client, method=Resource.POST)
            res_put.col_value_post(name=name, value=value, indicator_id=indicator_id)
            res_put.full_request()

        else:
            id = r["data"]["results"][0]["id"]
            res_put = col_class(self.client, method=Resource.PUT)
            res_put.col_value_put(id=id, name=name, value=value, indicator_id=indicator_id)
            res_put.full_request()


class IndicatorJob(ResourcePaged):
    def __init__(self, client:Client, method=Resource.GET):
        super(IndicatorJob, self).__init__(client, "indicatorjob/", method)

    def job_post(self, name,
                 indicator_type_ids,
                 user,
                 arguments="",
                 timeout=600,
                 active=True):
        """

        :param name: str
        :param indicator_type_ids: list[int]
        :param python_version: str
        :param arguments
        :param user: str
        :param timeout: int
        :param active: boolean
        :return:
        """
        self.json = {"name": name,
                     "indicator_types": indicator_type_ids,
                     "arguments": arguments,
                     "user": user,
                     "timeout": timeout,
                     "active": active}


class IndicatorJobVersion(ResourcePaged):
    def __init__(self, client:Client, method=Resource.GET):
        super(IndicatorJobVersion, self).__init__(client, "indicatorjobversion/", method)

    def job_version_post(self, indicator_job_id,
                         version,
                         filename):
        """

        :param indicator_job_id:
        :param version:
        :param filename:
        :return:
        """
        self.files = {"job": (None, indicator_job_id),
                      "version": (None, version),
                      "zip": open(filename, "rb")}


class IndicatorType(ResourcePaged):
    def __init__(self, client:Client, method=Resource.GET):
        super(IndicatorType, self).__init__(client, "indicatortype/", method)

