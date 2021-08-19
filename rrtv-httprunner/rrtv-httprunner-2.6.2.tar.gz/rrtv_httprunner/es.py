# @author: chenfanghang

from elasticsearch5 import Elasticsearch, Transport
from loguru import logger


class ESHandler(Elasticsearch):
    def __init__(self, hosts=None, transport_class=Transport, **kwargs):
        """
        :arg hosts: list of nodes we should connect to. Node should be a
            dictionary ({"host": "localhost", "port": 9200}), the entire dictionary
            will be passed to the :class:`~elasticsearch.Connection` class as
            kwargs, or a string in the format of ``host[:port]`` which will be
            translated to a dictionary automatically.  If no value is given the
            :class:`~elasticsearch.Urllib3HttpConnection` class defaults will be used.

        :arg transport_class: :class:`~elasticsearch.Transport` subclass to use.

        :arg kwargs: any additional arguments will be passed on to the
            :class:`~elasticsearch.Transport` class and, subsequently, to the
            :class:`~elasticsearch.Connection` instances.
        """
        if "index" in kwargs and kwargs["index"] is not None:
            self.index_name = kwargs["index"]
        else:
            self.index_name = "cms_season_test"
        super().__init__(hosts, transport_class, **kwargs)

    def term_search(self, condition):
        """
        精确查询
        """
        body = {
            "query": {
                "term": condition
            }
        }
        result = self.search(index=self.index_name, body=body)
        return result

    def match_search(self, condition):
        """
        匹配查询
        """
        body = {
            "query": {
                "match": condition
            }
        }
        result = self.search(index=self.index_name, body=body)
        logger.debug(result)
        return result

    def searchById(self, id):
        """
        查询指定ID数据
        """
        body = {
            "query": {
                "ids": {
                    "type": "_doc",
                    "values": [
                        id
                    ]
                }
            }
        }
        return self.search(index=self.index_name, body=body)

    def term_delete(self, condition):
        """
        精确删除
        """
        body = {
            "query": {
                "term": condition
            }
        }
        result = self.delete_by_query(index=self.index_name, body=body)
        logger.debug(result)
        return result

    def match_delete(self, condition):
        """
        匹配删除
        """
        body = {
            "query": {
                "match": condition
            }
        }
        result = self.delete_by_query(index=self.index_name, body=body)
        logger.debug(result)
        if result["deleted"] == 0:
            logger.warning("删除失败")
        return result

    def deleteById(self, id):
        """
        删除指定ID数据
        """
        body = {
            "query": {
                "ids": {
                    "type": "_doc",
                    "values": [
                        id
                    ]
                }
            }
        }
        result = self.delete_by_query(index=self.index_name, body=body)
        logger.debug(result)
        return result

    def term_update(self, condition, field, value):
        """
        精确更新
        """
        body = {
            "query": {
                "term": condition
            }
        }
        data = self.term_search(body)
        if not data["hits"]["hits"]:
            raise Exception("hits为空") from None
        id = data["hits"]["hits"][0]["_id"]
        source = data["hits"]["hits"][0]["_source"]
        expr = f"""content{field} =value"""
        exec(expr, {'content': source, "value": value})
        result = self.update(index=self.index_name, doc_type='_doc', id=id, body={"doc": source})
        logger.debug(result)
        if result["_shards"]["successful"] == 0:
            logger.warning("更新失败")
        return result

    def updateById(self, id, field, value):
        """
        通过指定id更新
        """
        data = self.searchById(id)
        if not data["hits"]["hits"]:
            raise Exception("hits为空") from None
        id = data["hits"]["hits"][0]["_id"]
        source = data["hits"]["hits"][0]["_source"]
        expr = f"""content{field} =value"""
        exec(expr, {'content': source, "value": value})
        result = self.update(index=self.index_name, doc_type='_doc', id=id, body={"doc": source})
        logger.debug(result)
        if result["_shards"]["successful"] == 0:
            logger.warning("更新失败")
        return result


if __name__ == '__main__':
    hosts = ['10.97.12.207:9200', '10.97.12.194:9200', '10.97.12.59:9200']
    es = ESHandler(hosts, index="cms_season_test")
    body = {
        "query": {
            "term": {
                "drama_id": 40435
            }
        }
    }
    print(es.match_search({"drama_id": 40435}))
    # body = {
    #     "query": {
    #         "match": {
    #             "name.ik": "apitest"
    #         }
    #     }
    # }
    # body = {
    #     "query": {
    #         "ids": {
    #             "type": "_doc",
    #             "values": [
    #                 "40241"
    #             ]
    #         }
    #     }
    # }
    # print(es.updateById(40241, "['enable']", False))
    # print(es.searchById(40241))
    # print(es.search(index="cms_season_test", body=body))
    # print(es.search(index='cms_season_test', body=body))
    # es.search()
    # data = es.term_search({"drama_id": 40241})
    # id = data["hits"]["hits"][0]["_id"]
    # source = data["hits"]["hits"][0]["_source"]
    # source["enable"] = True
    # print(id)
    # print(source)
    # print(es.update(index='cms_season_test', doc_type='_doc', id=id, body={"doc": source}))
    # print(es.term_search({"drama_id": 40435}))
    # print(es.match_search({"name": "测试"}))
    # print(es.delete_by_query(index="cms_season_test", body=body))
    # result = es.delete_by_query(index="megacorp", body=query)
    # print(es.match_delete({"name.ik": "apitest"}))
