from copy import deepcopy

from common.logging_config import logger
from common.rest_extend.response import Results, PageTypeResults, SERVER_ERROR_CODE
from elasticsearch import Elasticsearch
from common.utility.args_parsing import BaseArgsParsing


class ESClient(BaseArgsParsing):
    LIST_KEYWORD = ["must", "should"]
    RANGE = "range"

    def conn(self, host=None, port=None, username=None, password=None):
        if username and password:
            self.es = Elasticsearch(f"http://{host}/", port=port, http_auth=(username, password))
        else:
            self.es = Elasticsearch(f"http://{host}/", port=port)
        return self.es

    def transform(self, data):
        body = {}
        for key in data:
            if (not key) or (not data.get(key)):
                continue
            values = data.get(key)
            if key in self.RESERVED_FIELD:
                continue
            itme = key.split("_")
            if len(itme) > 1:
                real_key = "_".join(itme[:-1])
                keyword = itme[-1].lower()
                if keyword in self.SUFFIX_KEYWORD:
                    self.build_suffix_keyword_args(body, real_key, keyword, data.get(key))
                    continue

            page, size = self.get_page_and_size(data)

    def build_suffix_keyword_args(self, body, key, keyword, value):
        if keyword == self.GT or keyword == self.GTE or keyword == self.LT or keyword == self.LTE:
            if "query" in body.keys():
                pass
            else:
                body["query"] = {
                    "range": {
                        key: {
                            "gt": "2021-07-26T10:00:00Z",
                            "lt": "2021-07-26T10:02:00Z",
                        }
                    }
                }

    def build(self, body, keys, field, vaule):
        if body is None:
            body = {}
        if "." in keys:
            itme = keys.split(".")
            key = itme[0]
            if isinstance(body, dict):
                if key in body.keys():
                    body[key] = self.build(body[key], ".".join(itme[1:]), field, vaule)
                    return body
                else:
                    child_body = [] if key in self.LIST_KEYWORD else {}
                    body[key] = self.build(child_body, ".".join(itme[1:]), field, vaule)
                    return body
            else:
                if key == self.RANGE:
                    for range_item in body:
                        if key in range_item.keys():
                            if itme[1] in range_item[key].keys():
                                range_item[key][itme[1]] = self.build(range_item[key], ".".join(itme[1:]), field, vaule)
                                return body
                else:
                    for item in body:
                        if key in item.keys():
                            item[key] = self.build(item[key], ".".join(itme[1:]), field, vaule)
                            break
                    else:
                        body.append({key: self.build({}, ".".join(itme[1:]), field, vaule)})
                return body

        else:
            key = keys
            if isinstance(body, dict):
                if key in body.keys():
                    body[key][field] = vaule
                    return body[key]
                else:
                    return {key: {field: vaule}}
            else:
                body.append({key: {field: vaule}})
                return body

    def build_range(self, body, real_field, kw, vaule):
        if body:
            pass
        return body

    def build2(self, body, keys, field, vaule):
        if body is None:
            body = {}
        if "." in keys:
            itme = keys.split(".")
            key = itme[0]
            if key in body.keys():
                body[key] = self.build(body[key], ".".join(itme[1:]), field, vaule)
                return body
            else:
                child_body = [] if key in self.LIST_KEYWORD else {}
                body[key] = self.build(child_body, ".".join(itme[1:]), field, vaule)
                return body

        else:
            key = keys
            if isinstance(body, dict):
                if key in body.keys():
                    body[key][field] = vaule
                    return body[key]
                else:
                    return {key: {field: vaule}}
            else:
                body.append({key: {field: vaule}})
                return body

    def sort_(self, key, value, body=None):
        if not body:
            body = {}
        sort_data = {key: {"order": value}}
        if "sort" in body.keys():
            body["sort"].append(sort_data)
        else:
            body["sort"] = [sort_data]
        return body

    def and_(self, key, value, body=None):

        # body = self.build(body, 'query.bool.must.match_phrase', key, value)
        body = self.build(body, "query.bool.must.match_phrase", key, value)
        return body

    def or_(self, key, value, body=None):

        # body = self.build(body, 'query.bool.should.match_phrase', key, value)
        body = self.build(body, "query.bool.should.match_phrase", key, value)
        return body

    def range_(self, key, kw, value, body=None):
        # body = self.build(body, 'query.bool.must.range.' + key, kw, value)
        body = self.build(body, "query.bool.must.range." + key, kw, value)
        return body

    def not_(self, key, value, body=None):
        body = self.build(body, "query.bool.must_not.match_phrase", key, value)
        return body

    def must_and_should(self, key, *, values: list = None, body=None):
        if not values:
            raise ValueError("'values' is none!!!")
        for value in values:
            if value:
                body = self.build(body, "query.bool.must.bool.should.match_phrase", key, value)
        return body

    def search(self, body, index, page=1, size=20, all_result=False):
        if all_result:
            results = self.es.search(body=body, index=index, size=10000)
        else:
            from_ = (page - 1) * size
            if page * size > 10000:
                raise ValueError(f"'page'*'size'不能大于10000，当前 {page * size}")
            results = self.es.search(body=body, index=index, size=size, from_=from_)
        return results

    def to_results(self, es_results, page, size, results: Results = None):
        if not results:
            results = Results()
        results.code = 200
        page_type_results = PageTypeResults()
        results.data = page_type_results
        try:
            for item in es_results["hits"]["hits"]:
                try:
                    _source = item["_source"]
                    page_type_results.result.append(_source)
                except Exception as e:
                    logger.exception(e)
            page_type_results.page = page
            page_type_results.size = size
            page_type_results.total = es_results["hits"]["total"]["value"]
            results.data_length = len(page_type_results.result)
        except Exception as e:
            logger.exception(e)
            results.code = SERVER_ERROR_CODE
            results.describe = str(e)

        return results

    def index(self, index, body, id=None):
        if not body:
            return

        self.es.index(index, body=body, id=id)


if __name__ == "__main__":
    es_client = ESClient()
    body = es_client.and_("series", "P")
    es = es_client.conn(
        host="config.esmeas.host",
        port="config.esmeas.port",
        username="config.esmeas.username",
        password="config.esmeas.password",
    )
    es.index()
