"""
基本知识:
_index:索引(index)类似于关系型数据库里的“数据库”——是存储和索引关联数据的地方

_type:(已停用，不用管)

_score: 词频，一个文章中提到该词频率越高，权重越高

_id:id仅仅是一个字符串，它与_index和_type组合时，就可以在ElasticSearch中唯一标识一个文档。


返回数据样式：

  {'took': 42,  # 耗费时间，毫秒单位
   'timed_out': False,  # 搜索是否超时
   '_shards': {'total': 5, 'successful': 5, 'skipped': 0, 'failed': 0}, # 一共搜索多少分片，成功失败个数
   'hits': {  # 实际搜索结果集
        'total': {'value': 29, 'relation': 'eq'},  # 总命中计数
        'max_score': 1.0,
        'hits': [
            {'_index': 'asset', '_type': '_doc', '_id': 'ZN9B8ncBjFzHMmQJZk60', '_score': 1.0,
             '_source': {'location': {'lat': 32.0617, 'lon': 118.7778},
                    'isp': 'China Mobile communications corporation', 'pro': '江苏省', 'city': '南京',
                    'geo': '中国-江苏省-南京', 'is_online': True, 'ports': [80], 'os': None, 'domains': [],
                    'target_ip': '36.152.44.95', 'type': 'ip', 'ports_detail': [
                {'port': '80', 'type': 'tcp', 'product': 'Apache httpd', 'extrainfo': '', 'version': '',
                 'cpe': 'cpe:/a:apache:http_server', 'reason': 'syn-ack', 'state': 'open', 'name': 'http',
                 'conf': '10'}]}}]}}



语法：
Query。使用Query DSL（Domain Specific Language领域特定语言）定义一条搜索语句。
From/Size。分页搜索，类似sql的limit子句。
Sort。排序，支持一个或多个字段，类似sql的order by子句。
Sourcing Filter。字段过滤，支持通配符，类似sql的select字段。
Script Fields。使用脚本基于现有字段虚构出字段。例如索引里包含first name和second name两个字段，使用Script Fields可以虚构出一个full name是first name和second name的组合。
Doc Value Fields。字段格式化，例如Date格式化成字符串，支持自定义格式化类型。
Highlighting。高亮。
Rescoring。再评分，仅对原始结果的Top N（默认10）进行二次评分。
Explain。执行计划，主要列出文档评分的过程。类似mysql的explain查看执行计划。
Min Score。指定搜索文档的最小分值，实现过滤。
Count。返回符合条件的文档数量。

数据类型：
keyword:不进行分词，直接索引  使用场景: id,存储邮箱号码、url、name、title，手机号码、主机名、状态码、邮政编码、标签、年龄、性别等数据。
        可以通过设置ignore_above指定支持的【字符长度】，超过给定长度后的数据将不被索引，无法通过term精确匹配检索返回结果。
        不进行范围搜索的int也建议使用
text:支持分词，全文检索 使用场景: 存储全文搜索数据, 例如: 邮箱内容、地址、代码块、博客文章内容等。

备注：
1.解决空间不够的问题：
    curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_all/_settings -d '{"index.blocks.read_only_allow_delete": null}'
2.图形化工具:
    kibana



优化策略参考：
4.1 优化索引性能

1、批量写入，看每条数据量的大小，一般都是几百到几千。

2、多线程写入，写入线程数一般和机器数相当，可以配多种情况，在测试环境通过Kibana观察性能曲线。

3、增加segments的刷新时间，通过上面的原理知道，segment作为一个最小的检索单元，比如segment有50个，目的需要查10条数据，但需要从50个segment

分别查询10条，共500条记录，再进行排序或者分数比较后，截取最前面的10条，丢弃490条。在我们的案例中将此 **"refresh_interval": "-1" **，程序批量写入完成后

进行手工刷新(调用相应的API即可)。

4、内存分配方面，很多文章已经提到，给系统50%的内存给Lucene做文件缓存，它任务很繁重，所以ES节点的内存需要比较多(比如每个节点能配置64G以上最好）。

5、磁盘方面配置SSD，机械盘做阵列RAID5 RAID10虽然看上去很快，但是随机IO还是SSD好。

6、 使用自动生成的ID，在我们的案例中使用自定义的KEY，也就是与HBase的ROW KEY，是为了能根据rowkey删除和更新数据，性能下降不是很明显。

7、关于段合并，合并在后台定期执行，比较大的segment需要很长时间才能完成，为了减少对其他操作的影响(如检索)，elasticsearch进行阈值限制，默认是20MB/s，

可配置的参数："indices.store.throttle.max_bytes_per_sec" : "200mb" （根据磁盘性能调整）

合并线程数默认是：Math.max(1, Math.min(4, Runtime.getRuntime().availableProcessors() / 2))，如果是机械磁盘，可以考虑设置为1：index.merge.scheduler.max_thread_count: 1，

在我们的案例中使用SSD，配置了6个合并线程。

4.2 优化检索性能

1、关闭不需要字段的doc values。

2、尽量使用keyword替代一些long或者int之类，term查询总比range查询好 (参考lucene说明 http://lucene.apache.org/core/7_4_0/core/org/apache/lucene/index/PointValues.html)。

3、关闭不需要查询字段的_source功能，不将此存储仅ES中，以节省磁盘空间。

4、评分消耗资源，如果不需要可使用filter过滤来达到关闭评分功能，score则为0，如果使用constantScoreQuery则score为1。

5、关于分页：

（1）**from + size: **

每分片检索结果数最大为 from + size，假设from = 20, size = 20，则每个分片需要获取20 * 20 = 400条数据，多个分片的结果在协调节点合并(假设请求的分配数为5，则结果数最大为 400*5 = 2000条) 再在内存中排序后然后20条给用户。这种机制导致越往后分页获取的代价越高，达到50000条将面临沉重的代价，默认from + size默认如下：

index.max_result_window ： 10000*
(2) search_after: 使用前一个分页记录的最后一条来检索下一个分页记录，在我们的案例中，首先使用from+size，检索出结果后再使用search_after，在页面上我们限制了用户只能跳5页，不能跳到最后一页。

(3) **scroll **用于大结果集查询，缺陷是需要维护scroll_id

6、关于排序：我们增加一个long字段，它用于存储时间和ID的组合(通过移位即可)，正排与倒排性能相差不明显。

7、关于CPU消耗，检索时如果需要做排序则需要字段对比，消耗CPU比较大，如果有可能尽量分配16cores以上的CPU，具体看业务压力。

8、关于合并被标记删除的记录，我们设置为0表示在合并的时候一定删除被标记的记录，默认应该是大于10%才删除： "merge.policy.expunge_deletes_allowed": "0"。

{
    "mappings": {
        "data": {
            "dynamic": "false",
            "_source": {
                "includes": ["XXX"]  -- 仅将查询结果所需的数据存储仅_source中
            },
            "properties": {
                "state": {
                    "type": "keyword",   -- 虽然state为int值，但如果不需要做范围查询，尽量使用keyword，因为int需要比keyword增加额外的消耗。
                    "doc_values": false  -- 关闭不需要字段的doc values功能，仅对需要排序，汇聚功能的字段开启。
                },
                "b": {
                    "type": "long"    -- 使用了范围查询字段，则需要用long或者int之类 （构建类似KD-trees结构）
                }
            }
        }
    },
   "settings": {......}
}


"""

from typing import Any, MutableMapping, Optional, Type, Union, Collection
from elasticsearch import Elasticsearch, Transport


class ES(Elasticsearch):
    """
    创建 index : es.indices.create(index="test", body=body)
    删除 index : es.indices.delete(index='test')
    插入数据: es.create(index="test", id=4, body={"name": "JOJO"})
    删除指定数据: es.delete(index='test', id=1)
    修改字段: es.update(index="test", id=1, body={"doc": {"name": "张三",'sex':'男'}})
    获取数据: res = es.get(index="test", id=1)
    查找所有数据: res = es.search(index='test', size=20)
    根据条件查找数据:
        1.匹配查询 （核心查询）:
            body = {"query": {"match": {"name": "JOJO"}}}
            res = es.search(index="test", body=match)
        2.词条查询,注意只能查询内容是'被分析(analyzed)'的,查询前不会再对搜索词进行分词
            单匹配 body = {"query": {'term': {'id': 1}}}
            多条件匹配 body = {"query": {'terms': {'id': [1,2]}}}
        3.range查询:
            gt :: 大于 gte:: 大于等于
            lt :: 小于 lte:: 小于等于
            body = {"range":{"id":{"gt":2,"lt":10}}}
        4.exists查询:
            允许查询必须存在某个字段，且不为null body = {"query": {'exists': {'field': "sex"}}}
        4.bool查询，由一个或多个类型化的bool子句构成:
            must:and关系，影响评分
            must not：与must作用相反，且不会影响评分
            filter: 不会对评分有影响
            should: 如果Bool Query包含must或filter子句，则该子句主要用于评分；否则用于搜索命中文档，可以带有minimum_should_match（至少匹配几个条件）参数控制该行为


            body =  {"query": {"bool": {"should": [{"match": {"content": "{}".format(keywords)}}, {"match": {"title": "{}".format(keywords)}}]}}}


        res = es.search(index="test", body=body)
    查看分词:
        对于词条查询，必须查询对象是已经分词过的内容，所以需要知道目前的分词情况
        res = es.termvectors(index='test', id=9, body={"fields": ['ChineseName']})

    批量操作:
        bulk会把将要处理的数据载入内存中，所以数据量是有限制的，最佳的数据量不是一个确定的数值，它取决于你的硬件，你的文档大小以及复杂性，你的索引以及搜索的负载。
        大小建议是5-15MB，默认不能超过100M
        from elasticsearch.helpers import async_bulk, bulk
        actions = []
        for i in range(3):
            action = {'_op_type': 'index',  # 操作 index update create delete
                      '_index': 'test',  # index
                      '_source': {'level': i}}
            actions.append(action)
        # 使用bulk方法
        bulk(client=es, actions=actions)
        # 使用异步bulk方法
        async def main():
            await async_bulk(es, data)


    查看所有索引:http://192.168.1.100:9210/_cat/indices?v

    """

    def __init__(self, **kwargs: Any):
        self._es = super(ES, self).__init__(**kwargs)

    def build_host_index(self):
        create_body = {
            "settings": {
                "number_of_shards": 5,  # 每个索引主分片数，创建后无法修改
                "number_of_replicas": 2,  # 每个主分片的副本数，对于索引库，这个配置可以随时修改
                "blocks.read_only_allow_delete": False,  # 防止磁盘使用率大导致的文件写入失败
                "analysis": {
                    "analyzer": {
                        "ik_smart_pinyin": {
                            "type": "custom",
                            "tokenizer": "ik_smart",
                            "filter": ["my_pinyin", "word_delimiter"]
                        },
                        "ik_max_word_pinyin": {
                            "type": "custom",
                            "tokenizer": "ik_max_word",
                            "filter": ["my_pinyin", "word_delimiter"]
                        }
                    },
                    "filter": {
                        "my_pinyin": {
                            "type": "pinyin",
                            "keep_separate_first_letter": False,
                            "keep_full_pinyin": True,
                            "keep_original": True,
                            "limit_first_letter_length": 16,
                            "lowercase": True,
                            "remove_duplicated_term": True
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "location": {  # 地理信息
                        "type": "geo_point"
                    },
                    "isp": {  # 公司名
                        "type": "text",
                        "analyzer": "ik_max_word"  # 考虑到公司名可能会有中文，所以用ik分词器
                    },
                    "pro": {
                        "type": "text",
                        "analyzer": "ik_smart_pinyin"
                        #  "doc_values": False  # 关闭不需要字段的doc values功能，仅对需要排序，汇聚功能的字段开启。

                    },
                    "city": {
                        "type": "text",
                        "analyzer": "ik_smart_pinyin"
                    },
                    "geo": {
                        "type": "text",
                        "analyzer": "ik_smart_pinyin"
                    },
                    "is_online": {
                        "type": 'boolean'
                    },
                    "is_ipv6": {
                        "type": 'boolean'
                    },
                    "ports_detail": {
                        "type": "nested",  # 定义嵌套类型的数据
                        "properties": {
                            "port": {
                                "type": "integer",
                            },
                            "conf": {
                                "type": "integer"
                            },
                            "state": {
                                "type": "keyword"
                            },
                            "extrainfo": {
                                "type": "text"
                            },
                            "product": {
                                "type": "text"
                            },
                            "reason": {
                                "type": "keyword"
                            },
                            "version": {
                                "type": "text"
                            }
                        }
                    },
                    "os": {
                        "type": 'text'
                    },
                    "ip": {
                        "type": 'ip'
                    },
                    "target": {
                        "type": 'keyword'
                    },
                    "type": {
                        "type": "keyword"
                    },
                    "timestamp": {
                        "type": "date",
                        "format": 'yyyy-MM-dd HH:mm:ss'
                    }
                }
            }
        }
        res = self.indices.create(index='asset', body=create_body)
        print(res)

    def build_web_index(self):
        create_body = {
            "settings": {
                "number_of_shards": 5,  # 每个索引主分片数，创建后无法修改
                "number_of_replicas": 2,  # 每个主分片的副本数，对于索引库，这个配置可以随时修改
                "blocks.read_only_allow_delete": False,  # 防止磁盘使用率大导致的文件写入失败
                "analysis": {
                    "analyzer": {
                        "ik_smart_pinyin": {
                            "type": "custom",
                            "tokenizer": "ik_smart",
                            "filter": ["my_pinyin", "word_delimiter"]
                        },
                        "ik_max_word_pinyin": {
                            "type": "custom",
                            "tokenizer": "ik_max_word",
                            "filter": ["my_pinyin", "word_delimiter"]
                        },
                        "domain_name_analyzer": {
                            "filter": "lowercase",
                            "tokenizer": "domain_name_tokenizer",
                            "type": "custom"
                        },
                        "ik_html": {
                            "tokenizer": "ik_smart",
                            "char_filter": ["html_strip"]
                        }
                    },
                    "tokenizer": {
                        "domain_name_tokenizer": {
                            "type": "PathHierarchy",
                            "delimiter": ".",
                            "reverse": True
                        }
                    },
                    "filter": {
                        "my_pinyin": {
                            "type": "pinyin",
                            "keep_separate_first_letter": False,
                            "keep_full_pinyin": True,
                            "keep_original": True,
                            "limit_first_letter_length": 16,
                            "lowercase": True,
                            "remove_duplicated_term": True
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "title": {  # 网页名
                        "type": "text",
                        "analyzer": "ik_max_word"  # 考虑到公司名可能会有中文，所以用ik分词器
                    },
                    "status_code": {
                        "type": "integer",
                    },
                    "target": {
                        "type": "text",
                        "analyzer": "domain_name_analyzer"
                    },
                    "domain_ip": {
                        "type": "ip",
                    },
                    "html": {
                        "type": 'text',
                        "analyzer": "ik_html"
                    },
                    "fingerprints": {
                        "type": "nested",  # 定义嵌套类型的数据
                        "properties": {
                            "name": {
                                "type": "keyword",
                            },
                            "confidence": {
                                "type": "integer"
                            },
                            "version": {
                                "type": "text"
                            },
                            "cpe": {
                                "type": "text"
                            },
                            "categories": {
                                "type": "nested",
                                "properties": {
                                    "id": {'type': 'keyword'},
                                    "name": {'type': 'keyword'}
                                }
                            }
                        }
                    }
                }
            }
        }
        res = self.indices.create(index='web', body=create_body)
        print(res)

    def insert_data(self, index, body):
        res = self.index(index=index, body=body)
        return True if res['result'] == 'created' else False

    def test_search(self, body={}):
        # body = {"query": {"match": {"name": 'X11:5'}}}
        if not body:
            body = {"query": {
                "nested": {
                    "path": 'ports',
                    "query": {
                        "match": {
                            "ports.name": 'ssh'
                        }
                    }
                }
            }}
        res = self.search(index="asset", body=body)
        # return res['hits']['hits']
        return res

    def insert_web_demo(self):
        body = {
            "title": "Adet Söktürücü Çay - Adet Ağrısı İçin Bitkisel Çay",
            "status_code": 200,
            "target": "https://51.222.183.68:443",
            "domain_ip": "51.222.183.68",
            "cert": {
                "source": "openssl",
                "MD5": "8959740FF2047EEF090B547FA195BD1F",
                "SHA1": "B2335FE65D2BA39F13C79B8651A75EA4D78A6319",
                "SHA-256": "2EBBC4395FDE53E9DEF162C3E7EB10EBD9F6C4D183AD671CB76F4D67073AC51E",
                "Public_Key_Modulus": "EC:E6:4E:69:75:63:10:DA:74:85:CC:52:27:C1:31:B7:C7:7A:55:44:37:B3:38:D8:E2:DA:8C:B3:FB:C1:E7:42:06:BF:A4:93:2E:2A:41:FF:59:3C:85:06:D7:96:0F:64:A8:D0:90:EF:9F:2E:9F:E5:80:1B:5E:92:13:09:DC:9E:C4:8C:AE:99:87:14:64:7B:E9:DC:E3:3D:17:D9:3B:E4:5A:AA:04:20:AA:E7:9C:5B:38:E5:3D:DE:3C:B2:DC:20:92:AB:C7:0D:BD:6D:A5:73:90:12:21:BC:8C:3E:81:48:7F:E9:5E:A7:CE:93:D8:89:02:9B:B8:13:ED:7F:36:F7:76:70:81:57:C5:4B:69:9A:B2:29:7C:16:B1:DA:71:30:FC:FB:AB:71:99:47:2B:9F:DD:46:04:CC:0A:E1:B6:39:AD:7E:AA:3D:98:07:63:12:AA:E5:13:E4:73:F8:F2:2A:FB:78:0D:60:B2:42:E3:42:AD:E5:8C:59:F5:14:E6:17:67:2E:C2:01:18:AA:4E:C6:70:88:5C:02:B4:4E:A9:9E:21:2A:75:AD:9C:AD:25:27:84:02:BB:E2:40:06:5C:E2:DC:E6:E3:BB:4B:88:B1:AB:E3:E7:F1:9B:73:60:1B:61:45:45:17:37:43:B2:5E:41:6E:18:64:07:88:10:6F:D5",
                "DNS_Names": [
                    "adetsokturucucay.com",
                    "www.adetsokturucucay.com"
                ],
                "Names": "www.adetsokturucucay.com",
                "Version": "v3",
                "Serial_Number": "299514511984207870179040579824374379494664",
                "Serial_Hex": "0x37031acbdab11a68af40e29bc6bda80bd08",
                "Signature_Algorithm": "sha256WithRSAEncryption",
                "Country": "US",
                "Organization": "Let\"s Encrypt",
                "CommonName": "R3",
                "Not_Before": "2021-01-04 12:05:24 UTC",
                "Not_After": "2021-04-04 12:05:24 UTC",
                "Is_Expired": False,
                "Public_Key_Bits": 2048,
                "Public_Key": "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7OZOaXVjENp0hcxSJ8Ex\nt8d6VUQ3szjY4tqMs/vB50IGv6STLipB/1k8hQbXlg9kqNCQ758un+WAG16SEwnc\nnsSMrpmHFGR76dzjPRfZO+RaqgQgquecWzjlPd48stwgkqvHDb1tpXOQEiG8jD6B\nSH/pXqfOk9iJApu4E+1/Nvd2cIFXxUtpmrIpfBax2nEw/PurcZlHK5/dRgTMCuG2\nOa1+qj2YB2MSquUT5HP48ir7eA1gskLjQq3ljFn1FOYXZy7CARiqTsZwiFwCtE6p\nniEqda2crSUnhAK74kAGXOLc5uO7S4ixq+Pn8ZtzYBthRUUXN0OyXkFuGGQHiBBv\n1QIDAQAB\n-----END PUBLIC KEY-----\n",
                "CA": True,
                "is_effective": False
            },
            "html": "",
            "headers": {
                "Connection": "keep-alive",
                "Content-Type": "text/html; charset=UTF-8",
                "X-Redirect-By": "WordPress",
                "Location": "https://adetsokturucucay.com/",
                "X-LiteSpeed-Cache": "hit",
                "Content-Length": "0",
                "Date": "Fri, 12 Mar 2021 07:05:56 GMT",
                "Server": "cloudflare",
                "Alt-Svc": "h3-27=\":443\"; ma=86400, h3-28=\":443\"; ma=86400, h3-29=\":443\"; ma=86400",
                "Transfer-Encoding": "chunked",
                "Set-Cookie": "__cfduid=dea74bbe5f7da7f16547e544f53bf92241615532755; expires=Sun, 11-Apr-21 07:05:55 GMT; path=/; domain=.adetsokturucucay.com; HttpOnly; SameSite=Lax",
                "Link": "<https://adetsokturucucay.com/wp-json/>; rel=\"https://api.w.org/\", <https://adetsokturucucay.com/>; rel=shortlink",
                "Vary": "Accept-Encoding",
                "X-Turbo-Charged-By": "LiteSpeed",
                "CF-Cache-Status": "DYNAMIC",
                "cf-request-id": "08c6daa39d000042ea093e0000000001",
                "Expect-CT": "max-age=604800, report-uri=\"https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct",
                "Report-To": "{\"group\":\"cf-nel\",\"endpoints\":[{\"url\":\"https:\\/\\/a.nel.cloudflare.com\\/report?s=2F%2FVLB0gSe9Ldf1yGlMn4CGaO5S14%2F4KLCHzGdBZ8TpUccJmNb6lCOJcQ9joLW3dtPYFOQTqGJkCNpChGfGXgPNaUvxrYkVctaPzDKtbPkr7WCWIyw%3D%3D\"}],\"max_age\":604800}",
                "NEL": "{\"max_age\":604800,\"report_to\":\"cf-nel\"}",
                "CF-RAY": "62eb2d4c2ced42ea-LAX",
                "Content-Encoding": "gzip"
            },
            "fingerprints": [
                {
                    "slug": "wordpress",
                    "name": "WordPress",
                    "confidence": 100,
                    "version": "5.2.9",
                    "cpe": "cpe:/a:wordpress:wordpress",
                    "categories": [
                        {
                            "id": 1,
                            "slug": "cms",
                            "name": "CMS"
                        },
                        {
                            "id": 11,
                            "slug": "blogs",
                            "name": "Blogs"
                        }
                    ]
                },
                {
                    "slug": "mysql",
                    "name": "MySQL",
                    "confidence": 100,
                    "version": None,
                    "cpe": "cpe:/a:mysql:mysql",
                    "categories": [
                        {
                            "id": 34,
                            "slug": "databases",
                            "name": "Databases"
                        }
                    ]
                },
                {
                    "slug": "php",
                    "name": "PHP",
                    "confidence": 100,
                    "version": None,
                    "cpe": "cpe:/a:php:php",
                    "categories": [
                        {
                            "id": 27,
                            "slug": "programming-languages",
                            "name": "Programming languages"
                        }
                    ]
                },
                {
                    "slug": "litespeed-cache",
                    "name": "Litespeed Cache",
                    "confidence": 100,
                    "version": None,
                    "cpe": None,
                    "categories": [
                        {
                            "id": 23,
                            "slug": "caching",
                            "name": "Caching"
                        }
                    ]
                },
                {
                    "slug": "all-in-one-seo-pack",
                    "name": "All in One SEO Pack",
                    "confidence": 100,
                    "version": "3.1.1",
                    "cpe": "cpe:/a:semperfiwebdesign:all_in_one_seo_pack",
                    "categories": [
                        {
                            "id": 54,
                            "slug": "seo",
                            "name": "SEO"
                        }
                    ]
                },
                {
                    "slug": "google-font-api",
                    "name": "Google Font API",
                    "confidence": 100,
                    "version": None,
                    "cpe": None,
                    "categories": [
                        {
                            "id": 17,
                            "slug": "font-scripts",
                            "name": "Font scripts"
                        }
                    ]
                },
                {
                    "slug": "font-awesome",
                    "name": "Font Awesome",
                    "confidence": 100,
                    "version": None,
                    "cpe": None,
                    "categories": [
                        {
                            "id": 17,
                            "slug": "font-scripts",
                            "name": "Font scripts"
                        }
                    ]
                },
                {
                    "slug": "jquery-migrate",
                    "name": "jQuery Migrate",
                    "confidence": 100,
                    "version": "1.4.1",
                    "cpe": None,
                    "categories": [
                        {
                            "id": 59,
                            "slug": "javascript-libraries",
                            "name": "JavaScript libraries"
                        }
                    ]
                },
                {
                    "slug": "jquery",
                    "name": "jQuery",
                    "confidence": 100,
                    "version": "1.12.4",
                    "cpe": "cpe:/a:jquery:jquery",
                    "categories": [
                        {
                            "id": 59,
                            "slug": "javascript-libraries",
                            "name": "JavaScript libraries"
                        }
                    ]
                },
                {
                    "slug": "google-analytics",
                    "name": "Google Analytics",
                    "confidence": 100,
                    "version": None,
                    "cpe": None,
                    "categories": [
                        {
                            "id": 10,
                            "slug": "analytics",
                            "name": "Analytics"
                        },
                        {
                            "id": 61,
                            "slug": "saas",
                            "name": "SaaS"
                        }
                    ]
                },
                {
                    "slug": "cloudflare",
                    "name": "Cloudflare",
                    "confidence": 100,
                    "version": None,
                    "cpe": None,
                    "categories": [
                        {
                            "id": 31,
                            "slug": "cdn",
                            "name": "CDN"
                        }
                    ]
                }
            ]
        }
        res = self.index(index='web', body=body)
        return True if res['result'] == 'created' else False

    def delete_all(self):
        self.delete_by_query(index='asset', body={"query": {"match_all": {}}}, timeout=100)


if __name__ == '__main__':
    es = ES(host="localhost", port=9200)
    es.build_web_index()
    # es.insert_web_demo()
    es.build_host_index()
    # print(es.test_search())
    # es.delete(index='asset',id='3N_57HcBjFzHMmQJCEhN')
    # es.delete_all()

    # body = { # 更新表结构，但是我不知道怎么用python去进行更新
    #     "properties": {
    #         "ChineseName": {
    #             "type": "text",
    #             "analyzer": "ik_max_word"
    #         }}}
    # res = es.termvectors(index='test', id=11, body={"fields": ['ChineseName']})
    # print(res)
    # # 滚动分页的func，第四块部分 分页查询中 说明
    # es.scroll(scroll_id="scroll_id", scroll="5m")
