from __future__ import print_function

from abc import ABC

import tornado.ioloop
import tornado.web
import ujson, json
import logging
import sys

import os

curPath = os.path.abspath(os.path.dirname(__file__))

rootPath = os.path.split(curPath)

sys.path.append(rootPath[0])
sys.path.append(rootPath[0] + "/" + rootPath[1])

from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor
from model import model_service_graph_search_one_hop, \
    model_service_graph_search_multi_hop, \
    model_service_graph_search_multi_hop_multi_edge, \
    model_service_graph_search_one_hop_multi_edge, \
    model_service_graph_search_multi_hop_common_vertexes, \
    model_service_graph_search_match_edge, \
    model_service_graph_search_match_vertex, \
    model_service_graph_search_multi_hop_multi_edge_common_vertexes, \
    model_service_graph_search_find_path, \
    model_service_register_graph, \
    model_service_delete_graph, \
    model_service_show_graph, \
    model_service_insert_edge, \
    model_service_insert_vertex, \
    model_service_summary_graph, \
    model_service_description_graph, \
    model_service_path_finding, \
    model_service_create_subgraph, \
    model_service_update_subgraph_by_multi_hop_multi_edge, \
    model_service_update_subgraph_by_match_edge, \
    model_service_update_subgraph_by_find_path_multi_edge, \
    model_service_destroy_subgraph, \
    model_service_metric_indegree, \
    model_service_metric_outdegree, \
    model_service_metric_degree, \
    model_service_metric_pagerank, \
    model_service_edge_match_property, \
    model_service_vertex_match_property, \
    model_service_query_edges, \
    model_service_query_vertexes, \
    model_service_time_static_subgraph, \
    model_service_graph, \
    model_service_graph_insert, \
    model_service_graph_delete, \
    model_service_graph_update, \
    model_service_ga_build

import datetime
from data_load_config import load_config
from tornado_swagger.setup import setup_swagger
from tornado_swagger.setup import export_swagger
from tornado_swagger.model import register_swagger_model

from model_sevice import ModelService

import traceback
import time
import Longger_design
from urllib import parse

# LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s"
# logging.basicConfig(filename='./CHGraph.log', level=logging.INFO, format=LOG_FORMAT)
# logger = logging.getLogger()
logger = Longger_design.get_logger()

config_location = {"version": "0.0.1", "begin_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


def get_pack_time():
    with open("./../env/pack_time.txt") as f:
        line = f.read()
        config_location["begin_time"] = line.strip()


#get_pack_time()


class get_info_data(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        result = {
            "build": {
                "name": "CHGraph",
                "time": config_location["begin_time"],
                "version": config_location["version"],
            }
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


class get_health_data(tornado.web.RequestHandler, ABC):
    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        result = {"status": "UP"}
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


class dataServiceConfigLoad(object):
    def __init__(self):
        print("clickhouse config load start")

    def load_config(self):
        return load_config()


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


class gaBuildHandler(tornado.web.RequestHandler):
    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(50)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        logger.info(data_json["sql"])
        try:
            result_list = self.model.model_operation(data_json, self.config_params)
            res = success_request(result_list, {})
        except Exception as e:
            logger.error(e)
            print(e.args)
            print(str(e))
            traceback.print_exc()
            res = fail_request({}, {}, e)
        result = res
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class model_serviceGABuild(object):
    def __init__(self):
        print("model_service_ga_build model start")

    def model_operation(self, data, config_params):
        return model_service_ga_build(data, config_params)


class graphHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceGraph(object):
    def __init__(self):
        print("model_service_graph model start")

    def model_operation(self, data, config_params):
        return model_service_graph(data, config_params)


class graphInsertHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceGraphInsert(object):
    def __init__(self):
        print("model_service_graph_insert model start")

    def model_operation(self, data, config_params):
        return model_service_graph_insert(data, config_params)


class graphDeleteHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceGraphDelete(object):
    def __init__(self):
        print("model_service_graph_delete model start")

    def model_operation(self, data, config_params):
        return model_service_graph_delete(data, config_params)


class graphUpdateHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceGraphUpdate(object):
    def __init__(self):
        print("model_service_graph_update model start")

    def model_operation(self, data, config_params):
        return model_service_graph_update(data, config_params)


# one pop

@register_swagger_model
class modelServiceGraphSearchOneHop(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_one_hop(data, config_params)


class graphSearchOneHopHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
        Description end-point
        ---
        tags:
        - graphSearchOneHop
        summary: Create user
        description: This is one hop algorithm.
        operationId: examples.api.api.createUser
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Created user object
          required: false
          schema:
            type: object
            properties:
              step:
                type: integer
                format: int64
              start_vertex_list:
                type:
                  - "list"
              edge_name_list:
                type: list
              graph_dir:
                type: string
              direction:
                type: string
              edge_con_list:
                type: list
              userStatus:
                type: integer
                format: int32
                description: User Status
        responses:
        "201":
          description: successful operation
        """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# multi pop
@register_swagger_model
class modelServiceGraphSearchMultiHop(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_multi_hop(data, config_params)


class graphSearchMultiHopHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
        Description end-point
        ---
        tags:
        - graphSearchMultiHop
        summary: Create user
        description: This can only be done by the logged in user.
        operationId: examples.api.api.createUser
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Created user object
          required: false
          schema:
            type: object
            properties:
              step:
                type: integer
                format: int64
              start_vertex_list:
                type:
                  - "list"
              edge_name_list:
                type: list
              graph_dir:
                type: string
              direction:
                type: string
              edge_con_list:
                type: list
              userStatus:
                type: integer
                format: int32
                description: User Status
        responses:
        "201":
          description: successful operation
        """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# multi pop multi edge

@register_swagger_model
class modelServiceGraphSearchMultiHopMultiEdge(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_multi_hop_multi_edge(data, config_params)


class graphSearchMultiHopMultiEdgeHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                       Description end-point
                       ---
                       tags:
                       - Vertex/Edge-Wise Operation:Search
                       summary: Multi-Hop
                       description: This is the multi-hop service.
                       operationId: examples.api.api.Multi-Hop
                       produces:
                       - application/json
                       parameters:
                       - in: body
                         name: body
                         description: multi-hop
                         required: false
                         schema:
                           type: object
                           properties:
                             step:
                               type: integer
                               default: 1
                             start_vertex_list:
                               type: list
                               default: ['10.73.28.115','10.78.55.20']
                             edge_name_list:
                               type: list
                               default: ["tcpflow", "flow"]
                             graph_name:
                               type: string
                               default: "cyber"
                             direction:
                               type: string
                               default: "forward"
                             edge_con_list_list:
                               type: list
                               default: [["downlink_length>10000", "protocol='http'"], ["record_date='2019-04-15'"]]
                             target_field_list:
                               type: list
                               default: ["record_time"]
                             only_last_step:
                               type: boolean
                               default: true
                             plus_last_vertexes:
                               type: boolean
                               default: false
                       responses:
                       "201":
                         description: successful operation
               """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# one pop multi edge
@register_swagger_model
class modelServiceGraphSearchOneHopMultiEdge(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_one_hop_multi_edge(data, config_params)


class graphSearchOneHopMultiEdgeHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                               Description end-point
                               ---
                               tags:
                               - Vertex/Edge-Wise Operation:Search
                               summary: One Hop
                               description: This is the one hop service.
                               operationId: examples.api.api.OneHop
                               produces:
                               - application/json
                               parameters:
                               - in: body
                                 name: body
                                 description: one hop
                                 required: false
                                 schema:
                                   type: object
                                   properties:
                                     start_vertex_list:
                                       type: list
                                       default: ['10.73.28.115', '10.78.55.20']
                                     edge_name_list:
                                       type: list
                                       default: ["tcpflow", "flow"]
                                     graph_name:
                                       type: string
                                       default: "cyber"
                                     direction:
                                       type: string
                                       default: "forward"
                                     edge_con_list_list:
                                       type: list
                                       default: [["downlink_length>10000", "protocol='http'"], ["record_date='2019-04-15'"]]
                                     target_field_list:
                                       type: list
                                       default: ["record_time"]
                               responses:
                               "201":
                                 description: successful operation
                       """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# multi_hop_common_vertexes

@register_swagger_model
class modelServiceGraphSearchMultiHopCommonVertexes(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_multi_hop_common_vertexes(data, config_params)


class graphSearchMultiHopCommonVertexesHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# one pop multi edge
@register_swagger_model
class modelServiceGraphSearchMatchEdge(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_match_edge(data, config_params)


class graphSearchMatchEdgeHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                               Description end-point
                               ---
                               tags:
                               - Vertex/Edge-Wise Operation:Search
                               summary: edge matching
                               description: This is the edge matching service.
                               operationId: examples.api.api.EdgeMatching
                               produces:
                               - application/json
                               parameters:
                               - in: body
                                 name: body
                                 description: edge
                                 required: false
                                 schema:
                                   type: object
                                   properties:
                                     edge_name:
                                       type: string
                                       default: "tcpflow"
                                     graph_name:
                                       type: string
                                       default: "cyber"
                                     edge_con_list:
                                       type: list
                                       default: ["downlink_length>100000000"]
                                     target_field_list:
                                       type: list
                                       default: ['record_time', 'downlink_length']
                               responses:
                               "201":
                                 description: successful operation
                       """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# one pop multi edge

@register_swagger_model
class modelServiceGraphSearchMatchVertex(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_match_vertex(data, config_params)


class graphSearchMatchVertexHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                       Description end-point
                                       ---
                                       tags:
                                       - Vertex/Edge-Wise Operation:Search
                                       summary: vertices matching
                                       description: This is the vertices matching service.
                                       operationId: examples.api.api.VerticesMatching
                                       produces:
                                       - application/json
                                       parameters:
                                       - in: body
                                         name: body
                                         description: vertices
                                         required: false
                                         schema:
                                           type: object
                                           properties:
                                             vertex_name:
                                               type: string
                                               default: "ip"
                                             graph_name:
                                               type: string
                                               default: "cyber_plus"
                                             vertex_con_list:
                                               type: list
                                               default: ["speed>2","service_date=='2021-01-05'"]
                                             target_field_list:
                                               type: list
                                               default: ["service_date","speed"]
                                       responses:
                                       "201":
                                         description: successful operation
                               """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# one pop multi edge
@register_swagger_model
class modelServiceGraphSearchMultiHopMultiEdgeCommonVertexes(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_multi_hop_multi_edge_common_vertexes(data, config_params)


class graphSearchMultiHopMultiEdgeCommonVertexesHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                      Description end-point
                                      ---
                                      tags:
                                      - Vertex/Edge-Wise Operation:Search
                                      summary: Multi-Hop Common Vertices
                                      description: This is the multi-hop common vertices service.
                                      operationId: examples.api.api.Multi_HopCommonVertices
                                      produces:
                                      - application/json
                                      parameters:
                                      - in: body
                                        name: body
                                        description: multi-hop common vertices
                                        required: false
                                        schema:
                                          type: object
                                          properties:
                                            step:
                                              type: integer
                                              default: 1
                                            start_vertex_list:
                                              type: list
                                              default: ['10.73.28.115', '10.78.55.20']
                                            edge_name_list:
                                              type: list
                                              default: ["tcpflow", "flow"]
                                            graph_name:
                                              type: string
                                              default: "cyber"
                                            direction:
                                              type: string
                                              default: "forward"
                                            edge_con_list_list:
                                              type: list
                                              default: [["protocol='http'"], ["record_date='2019-04-15'"]]
                                      responses:
                                      "201":
                                        description: successful operation
                              """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# one pop multi edge
@register_swagger_model
class modelServiceGraphSearchMultiHopMultiEdgeCommonVertexes(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_multi_hop_multi_edge_common_vertexes(data, config_params)


class graphSearchFindPathHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                             Description end-point
                                             ---
                                             tags:
                                             - Vertex/Edge-Wise Operation:Search
                                             summary: Path Finding
                                             description: This is path finding service.
                                             operationId: examples.api.api.PathFinding
                                             produces:
                                             - application/json
                                             parameters:
                                             - in: body
                                               name: body
                                               description: path
                                               required: false
                                               schema:
                                                 type: object
                                                 properties:
                                                   step_limit:
                                                     type: integer
                                                     default: 2
                                                   start_vertex:
                                                     type: string
                                                     default: '10.73.28.115'
                                                   end_vertex:
                                                     type: string
                                                     default: "10.78.55.20"
                                                   graph_name:
                                                     type: string
                                                     default: "cyber"
                                                   target_field_list:
                                                     type: list
                                                     default: ["record_time", "downlink_length"]
                                                   edge_con_list_list:
                                                     type: list
                                                     default: [["downlink_length>10000", "protocol='http'"], ["record_date='2019-04-15'"]]
                                                   edge_name_list:
                                                     type: list
                                                     default: ["tcpflow", "flow"]
                                             responses:
                                             "201":
                                               description: successful operation
                                     """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceGraphSearchFindPath(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_graph_search_find_path(data, config_params)


class RegisterGraphHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Graph-Wise Operation
                                                     summary: Register Graph
                                                     description: This is the graph registering service.
                                                     operationId: examples.api.api.RegisterGraph
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: graph registering
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           graph_name:
                                                             type: string
                                                             default: "cyber"
                                                           graph_cfg:
                                                             type: string
                                                             default: '{"edges":{"tcpflow":{"db":"graph","table":"tcpflow","src":"source_ip","dst":"destination_ip","fields":["record_date","record_time","protocol","destination_port","uplink_length","downlink_length"]      },"flow":{"db":"graph","table":"flow","src":"source_ip","dst":"destination_ip","fields":["record_date","record_time","destination_port","uri"]} },"vertexes":{}}'
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceRegisterGraph(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_register_graph(data, config_params)


class DeleteGraphHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def delete(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceDeleteGraph(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_delete_graph(data, config_params)


class ShowGraphHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Graph-Wise Operation
                                                     summary: Show Graph
                                                     description: This is the graph showing service.
                                                     operationId: examples.api.api.ShowGraph
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: graph showing
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceShowGraph(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_show_graph(config_params)


class InsertEdgeHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Vertex/Edge-Wise Operation:Insert
                                                     summary: Insert Edge
                                                     description: This is the edge inserting service.
                                                     operationId: examples.api.api.InsertEdge
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: insert edge
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           edge_name:
                                                             type: string
                                                             default: "tcpflow"
                                                           graph_name:
                                                             type: string
                                                             default: "cyber_plus"
                                                           edge_schema:
                                                             type: list
                                                             default: ["record_time", "record_date", "source_ip", "destination_ip", "protocol", "destination_port", "uplink_length", "downlink_length"]
                                                           edge_data:
                                                             type: list
                                                             default: [["2019-04-11 18:48:59", "2019-04-11", "10.66.18.32", "184.173.90.200", "http", "80", 14725, 3116]]
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceInsertEdge(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_insert_edge(data, config_params)


class InsertVertexHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Vertex/Edge-Wise Operation:Insert
                                                     summary: Insert Vertex
                                                     description: This is the vertex inserting service.
                                                     operationId: examples.api.api.InsertVertex
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: insert vertex
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           vertex_name:
                                                             type: string
                                                             default: "ip"
                                                           graph_name:
                                                             type: string
                                                             default: "cyber_plus"
                                                           vertex_schema:
                                                             type: list
                                                             default: ["service_date", "ip", "host", "speed"]
                                                           vertex_data:
                                                             type: list
                                                             default: [["2021-01-04","1.1.1.1","p47708v.hulk.shbt.qihoo.net","2"],["2021-01-05","1.1.1.2","p47709v.hulk.shbt.qihoo.net","3"]] 
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceInsertVertex(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_insert_vertex(data, config_params)


class SummaryGraphHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, graph_name):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Graph-Wise Operation
                                                     summary: Summary Graph
                                                     description: This is the graph summary service.
                                                     operationId: examples.api.api.SummaryGraph
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: graph summary
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           graph_name:
                                                             type: string
                                                             default: "cyber"
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """
        res = yield self.data_process_and_model(graph_name)
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self, graph_name):
        # data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(graph_name, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceSummaryGraph(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_summary_graph(data, config_params)


class DescriptionGraphHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, graph_name):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Graph-Wise Operation
                                                     summary: Description Graph
                                                     description: This is the graph description service.
                                                     operationId: examples.api.api.DescriptionGraph
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: graph description
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           graph_name:
                                                             type: string
                                                             default: "cyber"
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model(graph_name)
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self, graph_name):
        # data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(graph_name, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceDescriptionGraph(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_description_graph(data, config_params)


class HealthServiceHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
               Description end-point
                ---
                tags:
                - health
                summary: health
                description: This is the health
                operationId: examples.api.api.health
                produces:
                - application/json
                parameters:
                - in: body
                  name: body
                  description: health
                  required: false
                  schema:
                    type: object
                    properties:
                      health:
                        type: str
                        default:  "health"
                responses:
                "201":
                  description: successful operation
        """
        res = yield self.data_process_and_model()
        self.write(ujson.dumps(res, ensure_ascii=False))
        self.finish("")

    @run_on_executor
    def data_process_and_model(self):
        json_datas = self.request.body.decode('utf8')
        result = {}
        result["status"] = "UP"
        return result


class InfoServiceHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
               Description end-point
                ---
                tags:
                - info
                summary: info
                description: This is the info
                operationId: examples.api.api.info
                produces:
                - application/json
                parameters:
                - in: body
                  name: body
                  description: info
                  required: false
                  schema:
                    type: object
                    properties:
                      info:
                        type: str
                        default:  "info"
                responses:
                "201":
                  description: successful operation
        """
        res = yield self.data_process_and_model()
        self.write(ujson.dumps(res, ensure_ascii=False))
        self.finish("")

    @run_on_executor
    def data_process_and_model(self):
        json_datas = self.request.body.decode('utf8')
        result = {}
        build = {}
        build["name"] = "graph-operation"
        build["time"] = "2021-01-29T20:20:41.578Z"
        build["version"] = "0.0.1-SNAPSHOT"
        result["build"] = build
        return result


class FindPathHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Vertex/Edge-Wise Operation: Path
                                                     summary: Path
                                                     description: This is the path service.
                                                     operationId: examples.api.api.Path
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: path
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           step_limit:
                                                             type: integer
                                                             default: "2"
                                                           graph_name:
                                                             type: string
                                                             default: "cyber_plus"
                                                           start_vertex_list:
                                                             type: list
                                                             default: ["1000007","100000","100"]
                                                           end_vertex_list:
                                                             type: list
                                                             default: ["343965","131254","51242","343965"]
                                                           edge_name_list:
                                                             type: list
                                                             default: ["userid_adgroup","adgroup_customer"]
                                                           edge_con_list_list:
                                                             type: list
                                                             default: [["record_date='2097-5-13'"],["record_date='2017-5-9'"]]
                                                           target_field_list:
                                                             type: list
                                                             default: [["record_date='2097-5-13'"],["record_date='2017-5-9'"]]
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServicePathFinding(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_path_finding(data, config_params)


class SubgraphCreationHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Subgraph
                                                     summary: Subgraph Creation
                                                     description: This is the subgraph creation service.
                                                     operationId: examples.api.api.SubgraphCreation
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: path
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           subgraph_name:
                                                             type: string
                                                             default: "taobao_sub"
                                                           graph_name:
                                                             type: string
                                                             default: "taobao"
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceSubgraphCreation(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_create_subgraph(data, config_params)


class MultiHopSubgraphUpdateHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
                               Description end-point
                               ---
                               tags:
                               - Subgraph
                               summary: Subgraph Update Multi-Hop
                               description: This is the multi-hop subgraph update service.
                               operationId: examples.api.api.SubgraphUpdateMultiHop
                               produces:
                               - application/json
                               parameters:
                               - in: body
                                 name: body
                                 description: subgraph update multi-hop
                                 required: false
                                 schema:
                                   type: object
                                   properties:
                                     step:
                                       type: integer
                                       default: 1
                                     start_vertex_list:
                                       type: list
                                       default: ['10.73.28.115','10.78.55.20']
                                     edge_name_list:
                                       type: list
                                       default: ["tcpflow", "flow"]
                                     graph_name:
                                       type: string
                                       default: "taobao"
                                     subgraph_name:
                                       type: string
                                       default: "taobao_sub"
                                     direction:
                                       type: string
                                       default: "forward"
                                     edge_con_list_list:
                                       type: list
                                       default: [["downlink_length>10000", "protocol='http'"], ["record_date='2019-04-15'"]]
                               responses:
                               "201":
                                 description: successful operation
                       """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceMultiHopSubgraphUpdate(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_update_subgraph_by_multi_hop_multi_edge(data, config_params)


class PathSubgraphUpdateHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
                                                             Description end-point
                                                             ---
                                                             tags:
                                                             - Subgraph
                                                             summary: Subgraph Update Path
                                                             description: This is the path subgraph update service.
                                                             operationId: examples.api.api.SubgraphUpdatePath
                                                             produces:
                                                             - application/json
                                                             parameters:
                                                             - in: body
                                                               name: body
                                                               description: path
                                                               required: false
                                                               schema:
                                                                 type: object
                                                                 properties:
                                                                   step_limit:
                                                                     type: integer
                                                                     default: "2"
                                                                   graph_name:
                                                                     type: string
                                                                     default: "taobao"
                                                                   subgraph_name:
                                                                     type: string
                                                                     default: "taobao_sub"
                                                                   start_vertex_list:
                                                                     type: list
                                                                     default: ["1000007","100000","100"]
                                                                   end_vertex_list:
                                                                     type: list
                                                                     default: ["343965","131254","51242","343965"]
                                                                   edge_name_list:
                                                                     type: list
                                                                     default: ["userid_adgroup","adgroup_customer"]
                                                                   edge_con_list_list:
                                                                     type: list
                                                                     default: [["record_date='2097-5-13'"],["record_date='2017-5-9'"]]
                                                             responses:
                                                             "201":
                                                               description: successful operation
                                                     """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServicePathSubgraphUpdate(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_update_subgraph_by_find_path_multi_edge(data, config_params)


class EdgeSubgraphUpdateHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
                                       Description end-point
                                       ---
                                       tags:
                                       - Subgraph
                                       summary: Subgraph Update Edge
                                       description: This is the edge subgraph update service.
                                       operationId: examples.api.api.SubgraphUpdateEdge
                                       produces:
                                       - application/json
                                       parameters:
                                       - in: body
                                         name: body
                                         description: subgraph update edge
                                         required: false
                                         schema:
                                           type: object
                                           properties:
                                             edge_name:
                                               type: string
                                               default: "tcpflow"
                                             graph_name:
                                               type: string
                                               default: "taobao"
                                             subgraph_name:
                                               type: string
                                               default: "taobao_sub"
                                             edge_con_list:
                                               type: list
                                               default: ["downlink_length>100000000"]
                                       responses:
                                       "201":
                                         description: successful operation
                               """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceEdgeSubgraphUpdate(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_update_subgraph_by_match_edge(data, config_params)


class SubgraphDestroyHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Subgraph
                                                     summary: Subgraph Destroy
                                                     description: This is the subgraph destroy update service.
                                                     operationId: examples.api.api.SubgraphDestroy
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: Subgraph Destroy
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           subgraph_name:
                                                             type: string
                                                             default: "taobao_sub"
                                                           graph_name:
                                                             type: string
                                                             default: "taobao"
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceSubgraphDestroy(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_destroy_subgraph(data, config_params)


class MetricIndegreeHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - vertex/edge-wise operation: metric
                                                     summary: Metric Indegree
                                                     description: This is the metric indegree service.
                                                     operationId: examples.api.api.MetricIndegree
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: Metric Indegree
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           edge_name:
                                                             type: string
                                                             default: "user_adgroup"
                                                           graph_name:
                                                             type: string
                                                             default: "taobao"
                                                           if_sort:
                                                             type: boolean
                                                             default: False
                                                           topk:
                                                             type: integer
                                                             default: -1
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceMetricIndegree(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_metric_indegree(data, config_params)


class MetricOutdegreeHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - vertex/edge-wise operation: metric
                                                     summary: Metric Outdegree
                                                     description: This is the metric outdegree service.
                                                     operationId: examples.api.api.MetricOutdegree
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: Metric Outdegree
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           edge_name:
                                                             type: string
                                                             default: "user_adgroup"
                                                           graph_name:
                                                             type: string
                                                             default: "taobao"
                                                           if_sort:
                                                             type: boolean
                                                             default: False
                                                           topk:
                                                             type: integer
                                                             default: -1
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceMetricOutdegree(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_metric_outdegree(data, config_params)


class MetricDegreeHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - vertex/edge-wise operation: metric
                                                     summary: Metric Degree
                                                     description: This is the metric degree service.
                                                     operationId: examples.api.api.MetricDegree
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: Metric Degree
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           edge_name:
                                                             type: string
                                                             default: "user_adgroup"
                                                           graph_name:
                                                             type: string
                                                             default: "taobao"
                                                           if_sort:
                                                             type: boolean
                                                             default: False
                                                           topk:
                                                             type: integer
                                                             default: -1
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceMetricDegree(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_metric_degree(data, config_params)


class MetricPagerankHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - vertex/edge-wise operation: metric
                                                     summary: Metric Pagerank
                                                     description: This is the metric pagerank service.
                                                     operationId: examples.api.api.MetricPagerank
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: Metric Pagerank
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           edge_name:
                                                             type: string
                                                             default: "user_adgroup"
                                                           graph_name:
                                                             type: string
                                                             default: "taobao"
                                                           if_sort:
                                                             type: boolean
                                                             default: False
                                                           topk:
                                                             type: integer
                                                             default: -1
                                                           d:
                                                             type: float
                                                             default: 0.85
                                                           num_iter:
                                                             type: integer
                                                             default: 10
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceMetricPagerank(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_metric_pagerank(data, config_params)


class EdgeMatchPropertyHandler(tornado.web.RequestHandler):

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Vertex/Edge-Wise Operation:Match
                                                     summary: Match Edge Property
                                                     description: This is the edge Property matching service.
                                                     operationId: examples.api.api.EdgePropertyMatching
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: edge property matching
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           edge_name:
                                                             type: string
                                                             default: "transactions"
                                                           graph_name:
                                                             type: string
                                                             default: "anti_money_launder"
                                                           start_vertex_list:
                                                             type: list
                                                             default: ["770305"]
                                                           end_vertex_list:
                                                             type: list
                                                             default: ["402592"]
                                                           egde_con_list:
                                                             type: list
                                                             default: ["record_date < \'2017-05-11\'"]
                                                           target_field_list:
                                                             type: list
                                                             default: []
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceEdgeMatchProperty(object):
    def __init__(self):
        print("query edge prop model start")

    def model_operation(self, data, config_params):
        return model_service_edge_match_property(data, config_params)


class VertexMatchPropertyHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Vertex/Edge-Wise Operation:Match
                                                     summary: Match Vertex Property
                                                     description: This is the vertex property matching service.
                                                     operationId: examples.api.api.VertexPropertyMatching
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: vertex property matching
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           vertex_name:
                                                             type: string
                                                             default: "account"
                                                           graph_name:
                                                             type: string
                                                             default: "anti_money_launder"
                                                           vertex_id_list:
                                                             type: list
                                                             default: ['119309','151550']
                                                           vertex_con_list:
                                                             type: list
                                                             default: ["record_date < \'2017-05-11\'"]
                                                           target_field_list:
                                                             type: list
                                                             default: None
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceVertexMatchProperty(object):
    def __init__(self):
        print("query vertex prop model start")

    def model_operation(self, data, config_params):
        return model_service_vertex_match_property(data, config_params)


class EdgeQueryHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Vertex/Edge-Wise Operation:Match
                                                     summary: Match Edge Property
                                                     description: This is the edge Property matching service.
                                                     operationId: examples.api.api.EdgePropertyMatching
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: edge property matching
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           edge_name:
                                                             type: string
                                                             default: "transactions"
                                                           graph_name:
                                                             type: string
                                                             default: "anti_money_launder"
                                                           edge_con_list:
                                                             type: list
                                                             default: ["record_date < \'2017-05-11\'"]
                                                           target_field_list:
                                                             type: list
                                                             default: []
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceQueryEdge(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_query_edges(data, config_params)


class VertexQueryHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Vertex/Edge-Wise Operation:Match
                                                     summary: Match Vertex Property
                                                     description: This is the vertex property matching service.
                                                     operationId: examples.api.api.VertexPropertyMatching
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: vertex property matching
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           vertex_name:
                                                             type: string
                                                             default: "account"
                                                           graph_name:
                                                             type: string
                                                             default: "anti_money_launder"
                                                           vertex_con_list:
                                                             type: list
                                                             default: ["record_date < \'2017-05-11\'"]
                                                           target_field_list:
                                                             type: list
                                                             default: None
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceQueryVertex(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_query_vertexes(data, config_params)


class TimeStaticSubgraphHandler(tornado.web.RequestHandler):
    """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
    """

    def initialize(self, model_service, config_params):
        self.model = model_service
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        """
                                                     Description end-point
                                                     ---
                                                     tags:
                                                     - Vertex/Edge-Wise Operation:Statistic
                                                     summary: Time Static Subgraph
                                                     description: This is the time static subgraph service.
                                                     operationId: examples.api.api.TimeStaticSubgraph
                                                     produces:
                                                     - application/json
                                                     parameters:
                                                     - in: body
                                                       name: body
                                                       description: time static subgraph
                                                       required: false
                                                       schema:
                                                         type: object
                                                         properties:
                                                           edge_name:
                                                             type: string
                                                             default: "account"
                                                           graph_name:
                                                             type: string
                                                             default: "anti_money_launder"
                                                           subgraph_name:
                                                             type: string
                                                             default: "sub_anti_money_laundry2"
                                                           edge_con_list:
                                                             type: list
                                                             default: ["record_date < '2017-05-11'"]
                                                           time_dimention:
                                                             type: string
                                                             default: "Minute"
                                                     responses:
                                                     "201":
                                                       description: successful operation
                                             """

        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        result_list = self.model.model_operation(data_json, self.config_params)
        result = {
            "result": result_list
        }
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


@register_swagger_model
class modelServiceTimeStaticSubgraph(object):
    def __init__(self):
        print("clickhouse model start")

    def model_operation(self, data, config_params):
        return model_service_time_static_subgraph(data, config_params)


# 获取子图带条件
class gain_subgraph(tornado.web.RequestHandler):

    # def __init__(self,config_params):
    #     self.config_params = config_params

    def initialize(self, config_params):
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        # data = data_json["countParams"]
        # result_list = ModelService().search_subgraph_by_condition(data, self.config_params)
        try:
            data = data_json["countParams"]
            result_list = ModelService().search_subgraph_by_condition(data, self.config_params)
            res = success_request(result_list, {})
        except Exception as e:
            res = fail_request({}, {}, e)
            print(e.args)
            print(str(e))
            traceback.print_exc()
        result = res
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# 获取时间线统计接口
class gain_time_line_count(tornado.web.RequestHandler):

    # def __init__(self,config_params):
    #     self.config_params = config_params

    def initialize(self, config_params):
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        data = data_json["countParams"]
        try:
            data = data_json["countParams"]
            result_list = ModelService().time_line_search(data, self.config_params)
            res = success_request(result_list, {})
        except Exception as e:
            res = fail_request({}, {}, e)
            print(e.args)
            print(str(e))
            traceback.print_exc()
        result = res
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# 获取时间线统计接口
class gain_sub_query(tornado.web.RequestHandler):

    # def __init__(self,config_params):
    #     self.config_params = config_params

    def initialize(self, config_params):
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        try:
            data = data_json["requestParams"]
            result_list = ModelService().query_subgraph(data, self.config_params)
            res = success_request(result_list, {})
        except Exception as e:
            res = fail_request({}, {}, e)
            print(e.args)
            print(str(e))
            traceback.print_exc()
        result = res
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# 获取时间线统计接口
class gain_count_edges(tornado.web.RequestHandler):

    # def __init__(self,config_params):
    #     self.config_params = config_params

    def initialize(self, config_params):
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        data_json = ujson.loads(self.request.body)
        data = data_json["countParams"]
        try:
            data = data_json["countParams"]
            result_list = ModelService().count_src_dst_round(data, self.config_params)
            res = success_request(result_list, {})
        except Exception as e:
            res = fail_request({}, {}, e)
            print(e.args)
            print(str(e))
            traceback.print_exc()
        result = res
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# 获取子图不同类型的统计接口
class gain_graph_type_count(tornado.web.RequestHandler):

    # def __init__(self,config_params):
    #     self.config_params = config_params

    def initialize(self, config_params):
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        uri = self.request.uri
        params = parse.parse_qs(parse.urlparse(self.request.uri).query)
        # data_json = ujson.loads(self.request.body)
        # data = data_json["countParams"]
        try:
            # data = data_json["countParams"]
            result_list = ModelService().statistics_operation_function(params, self.config_params)
            res = success_request(result_list, {})
        except Exception as e:
            res = fail_request({}, {}, e)
            print(e.args)
            print(str(e))
            traceback.print_exc()
        result = res
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# 统计子图点或者边的多个属性接口
class gain_graph_type_set(tornado.web.RequestHandler):

    def initialize(self, config_params):
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        uri = self.request.uri
        params = parse.parse_qs(parse.urlparse(self.request.uri).query)
        # data_json = ujson.loads(self.request.body)
        # data = data_json["countParams"]
        try:
            # data = data_json["countParams"]
            result_list = ModelService().statistics_operation_attributes_function(params, self.config_params)
            res = success_request(result_list, {})
        except Exception as e:
            res = fail_request({}, {}, e)
            print(e.args)
            print(str(e))
            traceback.print_exc()
        result = res
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


# 统计子图点或者边的单个属性接口
class gain_graph_type_function(tornado.web.RequestHandler):

    def initialize(self, config_params):
        self.config_params = config_params

    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        res = yield self.data_process_and_model()
        self.write(json.dumps(res, cls=DateEncoder))
        self.finish()

    @run_on_executor
    def data_process_and_model(self):
        uri = self.request.uri
        params = parse.parse_qs(parse.urlparse(self.request.uri).query)
        # data_json = ujson.loads(self.request.body)
        # data = data_json["countParams"]
        try:
            # data = data_json["countParams"]
            result_list = ModelService().statistics_operation_attribute_function(params, self.config_params,
                                                                                 label_statistic="y")
            res = success_request(result_list, {})
        except Exception as e:
            res = fail_request({}, {}, e)
            print(e.args)
            print(str(e))
            traceback.print_exc()
        result = res
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        return result


class Application(tornado.web.Application):
    data_service = dataServiceConfigLoad()

    config_params = data_service.load_config()

    model_serviceGABuild = model_serviceGABuild()

    model_serviceGraphInsert = modelServiceGraphInsert()

    model_serviceGraphDelete = modelServiceGraphDelete()

    model_serviceGraphUpdate = modelServiceGraphUpdate()

    model_serviceGraph = modelServiceGraph()

    model_serviceGraphSearchOnePop = modelServiceGraphSearchOneHop()

    model_serviceGraphSearchMultiHopMultiEdge = modelServiceGraphSearchMultiHopMultiEdge()

    model_serviceGraphSearchMultiHop = modelServiceGraphSearchMultiHop()

    model_serviceGraphSearchOneHopMultiEdge = modelServiceGraphSearchOneHopMultiEdge()

    model_serviceGraphSearchMultiHopCommonVertexes = modelServiceGraphSearchMultiHopCommonVertexes()

    model_serviceGraphSearchMatchEdge = modelServiceGraphSearchMatchEdge()

    model_serviceGraphSearchMatchVertex = modelServiceGraphSearchMatchVertex()

    model_serviceGraphSearchMultiHopMultiEdgeCommonVertexes = modelServiceGraphSearchMultiHopMultiEdgeCommonVertexes()

    model_serviceGraphSearchFindPath = modelServiceGraphSearchFindPath()

    model_serviceRegisterGraph = modelServiceRegisterGraph()

    model_serviceDeleteGraph = modelServiceDeleteGraph()

    model_serviceShowGraph = modelServiceShowGraph()

    model_serviceInsertEdge = modelServiceInsertEdge()

    model_serviceInsertVertex = modelServiceInsertVertex()

    model_serviceSummaryGraph = modelServiceSummaryGraph()

    model_serviceDescriptionGraph = modelServiceDescriptionGraph()

    model_serviceFindPath = modelServicePathFinding()

    model_serviceSubgraphCreation = modelServiceSubgraphCreation()

    model_serviceMultiHopSubgraphUpdate = modelServiceMultiHopSubgraphUpdate()

    model_servicePathSubgraphUpdate = modelServicePathSubgraphUpdate()

    model_serviceEdgeSubgraphUpdate = modelServiceEdgeSubgraphUpdate()

    model_serviceSubgraphDestroy = modelServiceSubgraphDestroy()

    model_serviceMetricIndegree = modelServiceMetricIndegree()

    model_serviceMetricOutdegree = modelServiceMetricOutdegree()

    model_serviceMetricDegree = modelServiceMetricDegree()

    model_serviceMetricPagerank = modelServiceMetricPagerank()

    model_serviceEdgeMatchProperty = modelServiceEdgeMatchProperty()

    model_serviceVertexMatchProperty = modelServiceVertexMatchProperty()

    model_serviceQueryEdge = modelServiceQueryEdge()

    model_serviceQueryVertex = modelServiceQueryVertex()

    model_serviceTimeStaticSubgraph = modelServiceTimeStaticSubgraph()

    _routes = [
        tornado.web.url(r"/chgraph/api/v1/info", get_info_data),
        tornado.web.url(r"/chgraph/api/v1/health", get_health_data),
        tornado.web.url(r"/graph-db/api/v1/ga-build", gaBuildHandler,
                        {"model_service": model_serviceGABuild, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph", graphHandler,
                        {"model_service": model_serviceGraph, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph-insert", graphInsertHandler,
                        {"model_service": model_serviceGraphInsert, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph-delete", graphDeleteHandler,
                        {"model_service": model_serviceGraphDelete, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph-update", graphUpdateHandler,
                        {"model_service": model_serviceGraphUpdate, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/multi-hop", graphSearchMultiHopMultiEdgeHandler,
                        {"model_service": model_serviceGraphSearchMultiHopMultiEdge, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/one-hop", graphSearchOneHopMultiEdgeHandler,
                        {"model_service": model_serviceGraphSearchOneHopMultiEdge, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/edges", graphSearchMatchEdgeHandler,
                        {"model_service": model_serviceGraphSearchMatchEdge, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/vertices", graphSearchMatchVertexHandler,
                        {"model_service": model_serviceGraphSearchMatchVertex, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/multi-hop-common-vertices",
                        graphSearchMultiHopMultiEdgeCommonVertexesHandler,
                        {"model_service": model_serviceGraphSearchMultiHopMultiEdgeCommonVertexes,
                         "config_params": config_params}),
        # tornado.web.url(r"/graph-db/api/v1/paths", graphSearchFindPathHandler,{"model_service": model_serviceGraphSearchFindPath,"config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph-registration", RegisterGraphHandler,
                        {"model_service": model_serviceRegisterGraph, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph-deletion", DeleteGraphHandler,
                        {"model_service": model_serviceDeleteGraph, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph-show", ShowGraphHandler,
                        {"model_service": model_serviceShowGraph, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph-summary/(?P<graph_name>\S*)", SummaryGraphHandler,
                        {"model_service": model_serviceSummaryGraph, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/graph-description/(?P<graph_name>\S*)", DescriptionGraphHandler,
                        {"model_service": model_serviceDescriptionGraph, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/edge-insertion", InsertEdgeHandler,
                        {"model_service": model_serviceInsertEdge, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/vertex-insertion", InsertVertexHandler,
                        {"model_service": model_serviceInsertVertex, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/health", HealthServiceHandler),
        tornado.web.url(r"/graph-db/api/v1/info", InfoServiceHandler),
        tornado.web.url(r"/graph-db/api/v1/path", FindPathHandler,
                        {"model_service": model_serviceFindPath, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-creation", SubgraphCreationHandler,
                        {"model_service": model_serviceSubgraphCreation, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-update-multi-hop", MultiHopSubgraphUpdateHandler,
                        {"model_service": model_serviceMultiHopSubgraphUpdate, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-update-path", PathSubgraphUpdateHandler,
                        {"model_service": model_servicePathSubgraphUpdate, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-update-edge", EdgeSubgraphUpdateHandler,
                        {"model_service": model_serviceEdgeSubgraphUpdate, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-destruction", SubgraphDestroyHandler,
                        {"model_service": model_serviceSubgraphDestroy, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/metric-indegree", MetricIndegreeHandler,
                        {"model_service": model_serviceMetricIndegree, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/metric-outdegree", MetricOutdegreeHandler,
                        {"model_service": model_serviceMetricOutdegree, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/metric-degree", MetricDegreeHandler,
                        {"model_service": model_serviceMetricDegree, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/metric-pagerank", MetricPagerankHandler,
                        {"model_service": model_serviceMetricPagerank, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/vertex-property", VertexMatchPropertyHandler,
                        {"model_service": model_serviceVertexMatchProperty, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/edge-property", EdgeMatchPropertyHandler,
                        {"model_service": model_serviceEdgeMatchProperty, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/vertex-query", VertexQueryHandler,
                        {"model_service": model_serviceQueryVertex, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/edge-query", EdgeQueryHandler,
                        {"model_service": model_serviceQueryEdge, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-time-statistic", TimeStaticSubgraphHandler,
                        {"model_service": model_serviceTimeStaticSubgraph, "config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-filtration-statistic", gain_subgraph,
                        {"config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/time-line-count", gain_time_line_count,
                        {"config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/round-edges-count", gain_count_edges,
                        {"config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-query", gain_sub_query,
                        {"config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-type-statistics", gain_graph_type_count,
                        {"config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-type-statistics-set", gain_graph_type_set,
                        {"config_params": config_params}),
        tornado.web.url(r"/graph-db/api/v1/subgraph-type-statistics-function", gain_graph_type_function,
                        {"config_params": config_params}),
    ]

    def get_routes(self):
        return self._routes

    def __init__(self):
        settings = {"debug": True}
        # setup_swagger(self._routes,
        #               swagger_url='/doc',
        #               api_base_url='/',
        #               description='',
        #               api_version='1.0.0',
        #               title='Journal API',
        #               contact='name@domain',
        #               schemes=['https'],
        #               security_definitions={
        #                   'ApiKeyAuth': {
        #                       'type': 'apiKey',
        #                       'in': 'header',
        #                       'name': 'X-API-Key'
        #                   }
        #               })
        super(Application, self).__init__(self._routes, **settings)


class response_encapsulation():
    def __init__(self, args):
        if "massage" in args:
            self.massage = args["massage"]
        if "code" in args:
            self.code = args["code"]
        if "reason" in args:
            self.reason = args["reason"]
        if "timestamp" in args:
            self.timestamp = args["timestamp"]


def success_request(data, response):
    res = {}
    if data:
        res["data"] = data
    else:
        res["data"] = {}
    if response:
        res["context"] = response
    else:
        res["context"] = {"code": 200, "timestamp": time.time()}
    return res


def fail_request(data, response, e):
    res = {}
    if data:
        res["data"] = data
    else:
        res["data"] = {}
    if response:
        res["context"] = response
    else:
        if e:
            res["context"] = {"code": 500, "timestamp": time.time(), "massage": str(e)}
        else:
            res["context"] = {"code": 500, "timestamp": time.time(), "massage": "系统异常"}

    return res


def main():
    App = Application()
    App.get_routes()
    App.listen(10110)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
