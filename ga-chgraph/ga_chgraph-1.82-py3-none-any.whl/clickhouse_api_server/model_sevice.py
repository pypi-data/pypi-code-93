import logging
from graph_add_op import CHGraph
from CKClient import get_client
from graph_op import CHGraph as ch
import Longger_design

# LOG_FORMAT = "%(asctime)s:%(levelname)s:%(name)s:%(funcName)s:%(message)s"
# logging.basicConfig(filename='./CHGraph.log', level=logging.INFO, format=LOG_FORMAT)
# logger = logging.getLogger('ModelService')
logger = Longger_design.get_logger()

operation_dict = {'avg': 'avg', 'sum': 'sum', 'min': 'min', 'max': 'max', 'count': 'count', }

def disconnect_client(client):
    if client:
        client.disconnect()


class ModelService(object):
    # 切换图空间
    def use_graph(self, graph_name, db):
        res = db.use_tables(graph_name)
        print(res)
        if res is None:
            logger.warning("graph name [" + graph_name + "] does not exist")
            return
        else:
            self.graph_name = graph_name
            self.graph_cfg = res
            logger.info("use graph [" + graph_name + "] done")

    # 根据条件过滤查询子图
    def search_subgraph_by_condition(self, data,
                                     config_param):
        if "subGraph" in data.keys():
            graph_name = data["subGraph"]
        else:
            return None
        # if "fieldList" in data.keys():
        #     fieldList = data["fieldList"]
        #     fields = ",".join(fieldList)
        #
        edge_types = None
        if "edgeTypes" in data.keys():
            edge_types = data["edgeTypes"]

        node_types = None
        if "nodeTypes" in data.keys():
            node_types = data["nodeTypes"]

        db = config_param["db"]
        # graph_client = config_param["graphClient"]
        clickhouse_connect = config_param["clickhouse_connect"]
        graph_client = get_client(clickhouse_connect)
        graph = CHGraph(graph_client)
        self.use_graph(graph_name, db)
        ######
        edges = self.graph_cfg["edges"]
        vertexes = self.graph_cfg["vertexes"]

        if "edgeConditions" in data.keys():
            edge_conditions = data["edgeConditions"]
            edge_condition_dict, edge_order_dict, special_sql_dict = ConditionOperation().conditionalOperation(
                edge_conditions, edges)
        else:
            edge_condition_dict, edge_order_dict = {}, {}
        if "nodeConditions" in data.keys():
            node_conditions = data["nodeConditions"]
            node_condition_dict, node_order_dict, special_sql_dict = ConditionOperation().conditionalOperation(
                node_conditions, vertexes)
        else:
            node_condition_dict, node_order_dict = {}, {}

        if "fieldList" in data.keys():
            ext_field_list = data["fieldList"]
        else:
            ext_field_list = None
        if "resultType" in data.keys():
            result_type = data["resultType"]
        else:
            result_type = None
        data = {}
        path_data = {}
        edge_data_list = []
        vertexes_data_list = []

        if edge_types:
            edge_data_list = executeController(edge_types, edges, edge_condition_dict, edge_order_dict, graph, "edge",
                                               ext_field_list, result_type)
        else:
            # edge_data_list = executeController(edges, edges, edge_condition_dict, edge_order_dict, graph, "edge")
            pass
        if node_types:
            vertexes_data_list = executeController(node_types, vertexes, node_condition_dict, node_order_dict, graph,
                                                   "vertexes", ext_field_list, result_type)
        else:
            # vertexes_data_list = executeController(vertexes, vertexes, node_condition_dict, node_order_dict, graph,
            #                                      "vertexes")
            pass

        path_data["graphEdges"] = edge_data_list
        path_data["graphNodes"] = vertexes_data_list
        data["pathList"] = path_data
        # 释放链接
        disconnect_client(graph_client)
        return data

    # 时间轴获取点边的模型
    def time_line_search(self, data, config_param):
        res_data = {}
        if "subGraph" in data.keys():
            graph_name = data["subGraph"]
        else:
            return None
        # if "fieldList" in data.keys():
        #     fieldList = data["fieldList"]
        #     fields = ",".join(fieldList)
        #
        edge_types = None
        if "edgeTypes" in data.keys():
            edge_types = data["edgeTypes"]

        node_types = None
        if "nodeTypes" in data.keys():
            node_types = data["nodeTypes"]

        db = config_param["db"]
        # graph_client = config_param["graphClient"]
        clickhouse_connect = config_param["clickhouse_connect"]
        graph_client = get_client(clickhouse_connect)
        graph = CHGraph(graph_client)
        self.use_graph(graph_name, db)
        ######
        edges = self.graph_cfg["edges"]
        vertexes = self.graph_cfg["vertexes"]
        if "edgeConditions" in data.keys() or "nodeConditions" in data.keys():
            if "edgeConditions" in data.keys():
                edge_conditions = data["edgeConditions"]
                edge_condition_dict, edge_order_dict, special_sql_dict = ConditionOperation().conditionalOperation(
                    edge_conditions, edges)
                if "sql" in special_sql_dict:
                    res = execute_graph_sql(graph, special_sql_dict["sql"])
            if "nodeConditions" in data.keys():
                node_conditions = data["nodeConditions"]
                node_condition_dict, node_order_dict, special_sql_dict = ConditionOperation().conditionalOperation(
                    node_conditions, vertexes)
                if "sql" in special_sql_dict:
                    res = execute_graph_sql(graph, special_sql_dict["sql"])
        if res:
            res_dict = res["data"]
            res_data["columns"] = res_dict["schema"]
            res_data["rowList"] = res_dict["detail"]
        # 释放链接
        disconnect_client(graph_client)
        return res_data

    # 统计任意两点间的边
    def count_src_dst_round(self, data, config_param):
        if "subGraph" in data.keys():
            graph_name = data["subGraph"]
        else:
            return None
        # if "fieldList" in data.keys():
        #     fieldList = data["fieldList"]
        #     fields = ",".join(fieldList)
        #
        edge_types = None
        if "edgeTypes" in data.keys():
            edge_types = data["edgeTypes"]

        db = config_param["db"]
        # graph_client = config_param["graphClient"]
        clickhouse_connect = config_param["clickhouse_connect"]
        graph_client = get_client(clickhouse_connect)
        graph = CHGraph(graph_client)
        self.use_graph(graph_name, db)
        ######
        edges = self.graph_cfg["edges"]

        if "edgeConditions" in data.keys():
            edge_conditions = data["edgeConditions"]
            edge_condition_dict, edge_order_dict, special_sql_dict = ConditionOperation().conditionalOperation(
                edge_conditions, edges)
        else:
            edge_condition_dict, edge_order_dict = {}, {}

        if edge_types:
            edge_data_list = executeController(edge_types, edges, edge_condition_dict, edge_order_dict, graph,
                                               "edgeCount")
        else:
            edge_data_list = executeController(edges.keys(), edges, edge_condition_dict, edge_order_dict, graph,
                                               "edgeCount")
        res_data = {}
        res_list = []
        if edge_data_list:
            for res_dict in edge_data_list:
                res = res_dict["data"]
                res_data["columns"] = res["schema"]
                res_data["rowList"] = res["detail"]
                res_data["type"] = res_dict["type"]
                res_list.append(res_data)
        # 释放链接
        disconnect_client(graph_client)
        return res_list

    # 根据条件过滤查询子图
    def query_subgraph(self, data, config_params):

        if "subGraph" in data.keys():
            graphName = data["subGraph"]
            print(graphName)
        else:
            return None
        # graph = config_params["graph"]
        db = config_params["db"]
        # graph.use_graph(graphName, db)
        # graph_client = config_param["graphClient"]
        clickhouse_connect = config_params["clickhouse_connect"]
        graph_client = get_client(clickhouse_connect)
        graph = ch(graph_client)
        graph.use_graph(graphName, db)
        graph_cfg = db.use_tables(graphName)

        graphNodes = []
        for vertex in graph_cfg["vertexes"]:
            graphNode = {}
            dict1 = graph_cfg["vertexes"][vertex]
            tem = []
            tem.append(dict1["id"])
            tem.append(dict1["label"])
            for field in dict1["fields"]:
                tem.append(field)
                try:
                    vertex_query = graph.query_vertexes(
                        vertex,
                        [""],
                        tem,
                        "df"
                    )
                except Exception as e:
                    print(e)
                    return "vertex query failed"
                graphNode["type"] = vertex
                graphNode["data"] = vertex_query
                graphNodes.append(graphNode)
        graphEdges = []
        for edge in graph_cfg["edges"]:
            graphEdge = {}
            dict2 = graph_cfg["edges"][edge]
            tem = []
            tem.append(dict2["src"])
            tem.append(dict2["dst"])
            tem.append(dict2["rank"])
            for field in dict2["fields"]:
                tem.append(field)
            try:
                edges_result = graph.query_edges(
                    edge,
                    [""],
                    tem,
                    "df"
                )
            except Exception as e:
                print(e)
                return "edge query failed"
        graphEdge["type"] = edge
        graphEdge["data"] = edges_result
        graphEdge["id"] = edge

        graphEdges.append(graphEdge)
        res_list = {}
        res_list["pathList"] = {}
        res_list["pathList"]["graphEdges"] = graphEdges
        res_list["pathList"]["graphNodes"] = graphNodes
        return res_list

    # 统计子图中点或者边的数量
    def statistics_operation_function(self, data, config_param):
        data = dispose_parse_params(data)
        if "subGraph" in data.keys():
            graph_name = data["subGraph"]
        else:
            return None
        edge_types = None
        if "type" in data.keys():
            graph_type = data["type"]
        else:
            graph_type = None
        if "orderTypes" in data.keys():
            orderTypes = data["orderTypes"]
        else:
            orderTypes = ""
        db = config_param["db"]
        clickhouse_connect = config_param["clickhouse_connect"]
        graph_client = get_client(clickhouse_connect)
        graph = CHGraph(graph_client)
        ###处理参数
        operations = {"1": "count"}
        group_field = []
        order_operation = orderTypes
        field_list = []
        self.use_graph(graph_name, db)
        if graph_type:
            schemas = self.graph_cfg[graph_type]
            res = None
            for schema in schemas:
                execute_sql = joinSql(operations, group_field, order_operation,
                                      schema, schemas, field_list, graph_type)
                result_dict = execute_graph_sql(graph, execute_sql)
                res = self.dispose_statistics_operation_res(result_dict, res, schema)
            result = {graph_type: res}

        else:
            edges = self.graph_cfg["edges"]
            vertexes = self.graph_cfg["vertexes"]
            res_edge = None
            res_vertex = None
            for edge in edges:
                execute_sql = joinSql(operations, group_field, order_operation,
                                      edge, edges, field_list, "edges")
                result_dict = execute_graph_sql(graph, execute_sql)
                res_edge = self.dispose_statistics_operation_res(result_dict, res_edge, edge)
            for vertex in vertexes:
                execute_sql = joinSql(operations, group_field, order_operation,
                                      vertex, vertexes, field_list, "vertexes")
                result_dict = execute_graph_sql(graph, execute_sql)
                res_vertex = self.dispose_statistics_operation_res(result_dict, res_vertex, vertex)
            result = {"vertexes": res_vertex, "edges": res_edge}
        return result

    def dispose_statistics_operation_res(self, result_dict, res, type):
        if "typeValue" not in result_dict["data"]["schema"]:
            result_dict["data"]["schema"].append("typeValue")
        result_dict["data"]["detail"][0].append(type)
        if res:
            res["data"]["detail"].append(result_dict["data"]["detail"][0])
        else:
            res = result_dict
        return res

    # 统计子图中点或者边的多个属性
    def statistics_operation_attributes_function(self, data, config_param):
        data = dispose_parse_params(data)
        if "subGraph" in data.keys():
            graph_name = data["subGraph"]
        else:
            return None
        if "type" in data.keys():
            type_value = data["type"]
        else:
            type_value = None
        if "attributes" in data.keys():
            attributes = data["attributes"]
        else:
            return None
        if "orderTypes" in data.keys():
            orderTypes = data["orderTypes"]
        else:
            orderTypes = ""

        # 获取客户端
        db = config_param["db"]
        clickhouse_connect = config_param["clickhouse_connect"]
        graph_client = get_client(clickhouse_connect)
        graph = CHGraph(graph_client)

        # 更新子图
        self.use_graph(graph_name, db)
        edges = self.graph_cfg["edges"]
        vertexes = self.graph_cfg["vertexes"]

        # 处理参数
        attribute_list = attributes.split(",")
        if orderTypes:
            order_list = orderTypes.split(",")
        else:
            order_list = ""
        res_list = []
        for i in range(len(attribute_list)):

            if order_list:
                order_operation = order_list[i]
            else:
                order_operation = ""
            field_list = []
            data_param = {"subGraph": graph_name, "type": type_value, "attribute": attribute_list[i],
                          "orderTypes": order_operation}
            if type_value in edges:
                index = edges[type_value]["fields"].index(attribute_list[i])
                field_type = edges[type_value]["types"][index]
                if field_type == "String":
                    data_param["statistics"] = "count"
                elif field_type == "Date":
                    data_param["statistics"] = "count"

            if type_value in vertexes:
                index = vertexes[type_value]["fields"].index(attribute_list[i])
                field_type = vertexes[type_value]["types"][index]
                if field_type == "String":
                    data_param["statistics"] = "count"
                elif field_type == "Date":
                    data_param["statistics"] = "count"
            res_one = self.statistics_operation_attribute_function(data_param, config_param, graph=graph)
            res_list.append(res_one)

        return res_list

    # 统计点或者边的单个属性
    def statistics_operation_attribute_function(self, data, config_param, label_statistic=None, graph=None):
        data = dispose_parse_params(data)
        if "subGraph" in data.keys():
            graph_name = data["subGraph"]
        else:
            return None
        if "type" in data.keys():
            type_value = data["type"]
        else:
            type_value = None
        attribute = None
        if "attribute" in data.keys():
            attribute = data["attribute"]
        else:
            return None
        if "statistics" in data.keys():
            statistics = data["statistics"]
        else:
            statistics = "def"
        if "orderTypes" in data.keys():
            orderTypes = data["orderTypes"]
        else:
            orderTypes = ''
        # 处理参数
        attribute_arr = attribute.split(",")
        statistics_arr = statistics.split(",")
        if len(statistics_arr) != len(attribute_arr):
            return None
        operations = {}
        for i in range(len(statistics_arr)):
            operations[attribute_arr[i]] = statistics_arr[i]
        if "def" in statistics_arr:
            group_field = None
        else:
            group_field = attribute_arr
        order_operation = orderTypes
        field_list = []
        # 获取客户端
        db = config_param["db"]
        clickhouse_connect = config_param["clickhouse_connect"]
        graph_client = get_client(clickhouse_connect)
        if graph:
            pass
        else:
            graph = CHGraph(graph_client)
        # 更换子图
        self.use_graph(graph_name, db)
        edges = self.graph_cfg["edges"]
        vertexes = self.graph_cfg["vertexes"]
        if type_value in edges:
            edge_schema = edges[type_value]
            if label_statistic:
                group_field = [edge_schema["src"], edge_schema["dst"]]
            execute_sql = joinSql(operations, group_field, order_operation,
                                  type_value, edges, field_list, "edges")
        elif type_value in vertexes:
            vertex_schema = vertexes[type_value]
            if label_statistic:
                group_field = [vertex_schema["id"]]
            execute_sql = joinSql(operations, group_field, order_operation,
                                  type_value, vertexes, field_list, "vertexes")
        else:
            return None
        result_dict = execute_graph_sql(graph, execute_sql)

        return result_dict


# 拼接sql,查询表数量
def joinSql(operations, group_field, order_operation,
            type_vertex, schema, field_list, subgraph_type):
    if field_list:
        for operation in operations:
            if operation in field_list:
                pass
            else:
                field_list.append(operation)
    else:
        for operation in operations:
            field_list.append(operation)

    if field_list:
        if group_field:
            for field in group_field:
                if field in field_list:
                    pass
                else:
                    field_list.append(field)
    else:
        for field in group_field:
            field_list.append(field)
    operList = statisticsOperation(operations)
    operStr = ','.join(operList)
    group_s = ""
    operStr_new = operStr
    if group_field:
        group_str = ','.join(group_field)
        operStr_new = group_str + "," + operStr_new
        group_s = " group by " + group_str
    main_sql = mainSqlValue(type_vertex, schema, field_list, subgraph_type)
    if main_sql:
        sql = "select " + operStr_new + " from (" + main_sql + ")" + group_s + " order by " + operStr + "  " + order_operation
        return sql
    else:
        return


# 处理Statistics函数
def statisticsOperation(operations):
    operList = []
    for operation in operations:
        oper = operations[operation]
        if oper in operation_dict:
            operList.append(operation_dict[oper] + '(' + operation + ')')
        else:
            operList.append(operation)
    return operList


# 点子图主sql
def mainSqlValue(type_value, schema, field_list, subgraph_type):
    if type_value in schema:
        value = schema[type_value]
        if subgraph_type == "vertexes":
            if field_list:
                fields = ",".join(field_list)
                sql = "select distinct " + value["id"] + "," + fields + " from " + value["db"] + "." + value["table"]
            else:
                sql = "select distinct " + value["id"] + "," + " from " + value["db"] + "." + value["table"]
            return sql
        else:
            if field_list:
                fields = ",".join(field_list)
                sql = "select distinct " + value["src"] + "," + value["dst"] + "," + value["rank"] + "," + fields \
                      + " from " + value["db"] + "." + value["table"]
            else:
                sql = "select distinct " + value["src"] + "," + value["dst"] + "," + value["rank"] + "," + " from " \
                      + value["db"] + "." + value["table"]
            return sql

    else:
        return


# 执行多条sql，并拼接返回
def executeController(array, schema, condition_dict, order_dict, graph, type,
                      ext_field_list=None, result_type=None):
    result = []
    for key in array:
        data = schema[key]
        condition = condition_splice(key, condition_dict)
        order = condition_splice(key, order_dict)
        if type == "edge":
            main_sql = edges_splice(data, ext_field_list)
        elif type == "edgeCount":
            main_sql = edges_count_splice(data)
            group_splice = edges_group_splice(data)
        else:
            main_sql = vertexes_splice(data, ext_field_list)
        if main_sql:
            # sql = main_sql + condition + order + " limit 10"
            if type == "edgeCount":
                sql = main_sql + condition + group_splice + order
            else:
                sql = main_sql + condition + order
            vertexes_data = execute_graph_sql(graph, sql, key, result_type)
            result.append(vertexes_data)
    return result


def edges_group_splice(edges_schema):
    if "src" in edges_schema:
        src = edges_schema["src"]
    else:
        return

    if "dst" in edges_schema:
        dst = edges_schema["dst"]
    else:
        return
    group_splice = " group by " + src + "," + dst + " "
    return group_splice


# 组合sql执行，返回图对象
def execute_graph_sql(graph, sql, type=None, result_type=None):
    result_dict = {}
    data = {}
    logger.info("sql:" + sql)
    res = graph.execute(sql)
    if result_type:
        result_dict["data"] = res
    else:
        schemas = res.columns.values.tolist()
        field_data = res.values.tolist()
        data["schema"] = schemas
        data["detail"] = field_data
        result_dict["data"] = data
    if type:
        result_dict["type"] = type
    return result_dict


# 拼接条件
def condition_splice(type, condition={}):
    if len(condition) > 0 and type in condition:
        return condition[type]
    return ""


# 拼接点主体查询sql
def vertexes_splice(vertexes_schema, ext_field_list=None):
    if "db" in vertexes_schema:
        db = vertexes_schema["db"]
    else:
        db = "default"

    if "table" in vertexes_schema:
        table = vertexes_schema["table"]
    else:
        return

    if "id" in vertexes_schema:
        id = vertexes_schema["id"]
    else:
        return

    if "label" in vertexes_schema:
        label = vertexes_schema["label"]
    else:
        # label = ""
        return
    ext_field = None
    if ext_field_list:
        pass
    else:
        ext_field_list = vertexes_schema["fields"]
    if id in ext_field_list:
        ext_field_list.remove(id)
    if label in ext_field_list:
        ext_field_list.remove(label)
    if ext_field_list:
        ext_field = ",".join(ext_field_list)
    if ext_field:
        main_sql = "select distinct " + id + "," + label + ", " + ext_field + " from " + db + "." + table
    else:
        main_sql = "select distinct " + id + "," + label + " from " + db + "." + table
    # main_sql = "select " + id + " from " + db + "." + table
    return main_sql


# 拼接边主体查询sql
def edges_splice(edges_schema, ext_field_list=None):
    if "db" in edges_schema:
        db = edges_schema["db"]
    else:
        db = "default"

    if "table" in edges_schema:
        table = edges_schema["table"]
    else:
        return

    if "src" in edges_schema:
        src = edges_schema["src"]
    else:
        return

    if "dst" in edges_schema:
        dst = edges_schema["dst"]
    else:
        return
    if "rank" in edges_schema:
        rank = edges_schema["rank"]
    else:
        return
    ext_field = None
    if ext_field_list:
        pass
    else:
        ext_field_list = edges_schema["fields"]
    if src in ext_field_list:
        ext_field_list.remove(src)
    if dst in ext_field_list:
        ext_field_list.remove(dst)
    if rank in ext_field_list:
        ext_field_list.remove(rank)
    if ext_field_list:
        ext_field = ",".join(ext_field_list)
    if ext_field:
        main_sql = "select distinct " + src + ", " + dst + "," + rank + " ," + ext_field + "  from  " + db + "." + table
    else:
        main_sql = "select distinct " + src + ", " + dst + "," + rank + "  from  " + db + "." + table
    return main_sql


# 拼接边主体查询sql
def edges_count_splice(edges_schema):
    if "db" in edges_schema:
        db = edges_schema["db"]
    else:
        db = "default"

    if "table" in edges_schema:
        table = edges_schema["table"]
    else:
        return

    if "src" in edges_schema:
        src = edges_schema["src"]
    else:
        return

    if "dst" in edges_schema:
        dst = edges_schema["dst"]
    else:
        return
    if "rank" in edges_schema:
        rank = edges_schema["rank"]
    else:
        return
    main_sql = "select " + src + ", " + dst + ", count(1) count  from  " + db + "." + table
    return main_sql


# 拼接order by
def orderAttributeOperation(orderAttribute):
    if orderAttribute:
        order = ",".join(orderAttribute)
        return "order by " + order


# 拼接group by
# 暂时不用，没有处理聚合函数
def groupAttributeOperation(groupAttribute):
    if groupAttribute:
        group = ",".join(groupAttribute)
        return "group by " + group


# 遍历字符串并加上单引号
def foreachStringArray2String(array=[]):
    if array:
        str = None
        for tmp in array:
            if str:
                str = str + "'" + tmp + "',"
            else:
                str = "'" + tmp + "',"
        return str[0:len(str)]
    return


# 处理parse.parse_qs方法获取的get参数
def dispose_parse_params(data):
    for key in data.keys():
        if isinstance(data[key], list):
            data[key] = data[key][0]
    return data


class ConditionOperation(object):
    singular = ["=", ">", "<", "like"]
    allCondition = ["in"]
    twoCondition = ["between"]
    special = ["timeType"]
    attribute_type_num = "num"
    attribute_type_time = "time"

    # 合并conditional条件
    def conditionalOperation(self, typeConditions, schemas={}):

        typeConditionDict = {}
        typeOrderDict = {}
        typeSpecialSql = {}
        if typeConditions:
            for typeCondition in typeConditions:
                val = None
                type = typeCondition["type"]
                schema = schemas[type]

                if "srcNodes" in typeCondition:
                    srcNodes = typeCondition["srcNodes"]
                    if srcNodes:
                        if "src" in schema:
                            if schema["src_data_type"] == self.attribute_type_num:
                                src_node = ",".join(srcNodes)
                            else:
                                src_node = foreachStringArray2String(srcNodes)
                            if val:
                                val = val + schema["src"] + " in(" + src_node + ") and "
                            else:
                                val = " where " + schema["src"] + " in(" + src_node + ") and "

                if "destNodes" in typeCondition:
                    destNodes = typeCondition["destNodes"]
                    if destNodes:
                        if "dst" in schema:
                            if schema["dst_data_type"] == self.attribute_type_num:
                                dest_node = ",".join(destNodes)
                            else:
                                dest_node = foreachStringArray2String(destNodes)
                            if val:
                                val = val + schema["dst"] + " in(" + dest_node + ") and "
                            else:
                                val = " where " + schema["dst"] + " in(" + dest_node + ") and "
                if "id" in typeCondition:
                    srcNodes = typeCondition["id"]
                    if srcNodes:
                        if "id" in schema:
                            if schema["id_data_type"] == self.attribute_type_num:
                                ids = ",".join(srcNodes)
                            else:
                                ids = foreachStringArray2String(srcNodes)
                            if val:
                                val = val + schema["id"] + " in(" + ids + ") and "
                            else:
                                val = " where " + schema["id"] + " in(" + ids + ") and "
                if "conditions" in typeCondition:
                    conditions = typeCondition["conditions"]
                    val_sql = val
                    val_dict = self.splice_condition(conditions, schema, val_sql)
                    if "sql" in val_dict:
                        typeSpecialSql["sql"] = val_dict["sql"]
                    val = val_dict["val"]

                if val:
                    typeConditionDict[type] = val + " 1=1"

                if "orderAttribute" in typeCondition:
                    type_order = typeCondition["orderAttribute"]
                    order_val = orderAttributeOperation(type_order)
                    typeOrderDict[type] = order_val
            return typeConditionDict, typeOrderDict, typeSpecialSql

        return

    # 拼接条件
    def splice_condition(self, conditions, schema, val_sql=None):
        if conditions:
            tem_dict = {}
            if val_sql:
                val = val_sql
            else:
                val = " where "
            for condition in conditions:
                symbol = condition["symbol"]
                attribute_type = condition["type"]
                if symbol in self.singular:
                    if attribute_type == self.attribute_type_num:
                        val = val + condition["attribute"] + condition["symbol"] \
                              + condition["conditional"][0] + " and "
                    elif attribute_type == self.attribute_type_time:
                        val = val + " formatDateTime(" + condition["attribute"] + ",'%F %T') " + condition["symbol"] \
                              + " '" + condition["conditional"][0] + "' and "
                    else:
                        val = val + condition["attribute"] + condition["symbol"] \
                              + "'" + condition["conditional"][0] + "' and "

                if symbol in self.allCondition:
                    if attribute_type == self.attribute_type_num:
                        val = val + condition["attribute"] + condition["symbol"] + "(" \
                              + ",".join(condition["conditional"]) + ")" + " and "
                    else:
                        val = val + condition["attribute"] + condition["symbol"] + "(" \
                              + foreachStringArray2String(condition["conditional"]) + ")" + " and "
                if symbol in self.twoCondition:
                    if attribute_type == self.attribute_type_num:
                        val = val + condition["attribute"] + " between " \
                              + condition["conditional"][0] + " and " \
                              + condition["conditional"][1] + " and "
                    elif attribute_type == self.attribute_type_time:
                        val = val + " formatDateTime(" + condition["attribute"] + ",'%F %T') " + condition["symbol"] \
                              + " '" + condition["conditional"][0] + "' and "
                    else:
                        val = val + condition["attribute"] + " between '" \
                              + condition["conditional"][0] + "' and '" \
                              + condition["conditional"][1] + "' and "
                if symbol in self.special:
                    sql = self.time_line_count_sql(condition, schema, val_sql)
                    tem_dict["sql"] = sql
            tem_dict["val"] = val
            return tem_dict

    # 处理特殊sql的拼接
    def time_line_count_sql(self, condition, schema, val_sql):
        if "id" in schema and "label" in schema:
            attribute = schema["id"] + " , " + schema["label"]
        else:
            attribute = schema["src"] + " , " + schema["dst"] + " , " + schema["rank"]
        if val_sql:
            val_sql = val_sql + " 1=1 "
        else:
            val_sql = " where 1=1 "
        if condition["conditional"][0] == "year":
            sql = "select toYear(" + condition["attribute"] + ") year,count(1) count from ( select distinct " \
                  + attribute + "," + condition["attribute"] + " from " + schema["db"] + "." + schema[
                      "table"] + val_sql + " ) group by year order by year "
        elif condition["conditional"][0] == "quarter":
            sql = "select concat(toString(year),\' \',toString(quarter)) yearQuarter ,count from (select toYear(" + \
                  condition["attribute"] + ") year,toQuarter(" + condition["attribute"] \
                  + ") quarter ,count(1) count from   ( select distinct  " + attribute + "," + condition[
                      "attribute"] + " from " \
                  + schema["db"] + "." + schema["table"] \
                  + val_sql \
                  + " )  group by year,quarter order by year,quarter) "
        elif condition["conditional"][0] == "month":
            sql = "select concat(toString(year),\' \',toString(month)) yearMonth, count from ( select toYear(" + \
                  condition["attribute"] + ") year,toMonth(" + condition["attribute"] \
                  + ") month ,count(1) count from  ( select distinct " + attribute + "," + condition[
                      "attribute"] + " from " \
                  + schema["db"] + "." + schema["table"] \
                  + val_sql \
                  + " )group by year,month order by year,month)"
        elif condition["conditional"][0] == "week":
            sql = "select concat(toString(yw),\' \',toString(week)) ywWeek, count from (select toYearWeek(" + \
                  condition[
                      "attribute"] + ") yw, toDayOfWeek(" + condition["attribute"] + \
                  ") week ,count(1) count from   ( select distinct  " + attribute + "," + condition[
                      "attribute"] + " from " \
                  + schema["db"] + "." + schema["table"] \
                  + val_sql \
                  + ") group by yw,week order by yw,week )"
        elif condition["conditional"][0] == "day":
            sql = "select formatDateTime(" + condition[
                "attribute"] + ",'%F') day ,count(1) count from  ( select distinct  " \
                  + attribute + "," + condition["attribute"] + " from " \
                  + schema["db"] + "." + schema["table"] + val_sql + " ) group by day order by day"
        elif condition["conditional"][0] == "hours":
            sql = "select formatDateTime(" + condition[
                "attribute"] + ",'%F %H') h ,count(1) count from ( select distinct  " \
                  + attribute + "," + condition["attribute"] + " from " \
                  + schema["db"] + "." + schema["table"] + val_sql + " )group by h order by h"
        elif condition["conditional"][0] == "minute":
            sql = "select formatDateTime(" + condition[
                "attribute"] + ",'%F %R') m ,count(1) count from  ( select distinct  " \
                  + attribute + "," + condition["attribute"] + " from " \
                  + schema["db"] + "." + schema["table"] + val_sql + " )group by m order by m"
        else:
            sql = "select formatDateTime(" + condition[
                "attribute"] + ",'%F') day ,count(1) count from  ( select distinct  " \
                  + attribute + "," + condition["attribute"] + " from " \
                  + schema["db"] + "." + schema["table"] + val_sql + " )group by day order by day"

        #     if condition["conditional"][0] == "year":
        #         sql = "select toYear(" + condition["attribute"] + ") year,count(1) count from ( select distinct " \
        #              + attribute + "," + condition["attribute"] + " from " + schema["db"] + "." + schema["table"] + val_sql + " ) group by year order by year "
        #     elif condition["conditional"][0] == "quarter":
        #         sql = "select concat(toString(year),\' \',toString(quarter)) yearQuarter ,count from (select toYear(" + \
        #               condition["attribute"] + ") year,toQuarter(" + condition["attribute"] \
        #               + ") quarter ,count(1) count from   ( select distinct  " + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] \
        #               + val_sql \
        #               + " )  group by year,quarter order by year,quarter) "
        #     elif condition["conditional"][0] == "month":
        #         sql = "select concat(toString(year),\' \',toString(month)) yearMonth, count from ( select toYear(" + \
        #               condition["attribute"] + ") year,toMonth(" + condition["attribute"] \
        #               + ") month ,count(1) count from  ( select distinct " + attribute + "," + condition["attribute"] + " from "\
        #               + schema["db"] + "." + schema["table"] \
        #               + val_sql \
        #               + " )group by year,month order by year,month)"
        #     elif condition["conditional"][0] == "week":
        #         sql = "select concat(toString(yw),\' \',toString(week)) ywWeek, count from (select toYearWeek(" + \
        #               condition[
        #                   "attribute"] + ") yw, toDayOfWeek(" + condition["attribute"] + \
        #               ") week ,count(1) count from   ( select distinct  " + attribute + "," + condition["attribute"] + " from "\
        #               + schema["db"] + "." + schema["table"] \
        #               + val_sql \
        #               + ") group by yw,week order by yw,week )"
        #     elif condition["conditional"][0] == "day":
        #         sql = "select formatDateTime(" + condition["attribute"] + ",'%F') day ,count(1) count from  ( select distinct  " \
        #               + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] + val_sql + ") group by day order by day"
        #     elif condition["conditional"][0] == "hours":
        #         sql = "select formatDateTime(" + condition["attribute"] + ",'%F %H') h ,count(1) count from ( select distinct  " \
        #               + schema["db"] + "." + schema["table"] + val_sql + " group by h order by h"
        #     elif condition["conditional"][0] == "minute":
        #         sql = "select formatDateTime(" + condition["attribute"] + ",'%F %R') m ,count(1) count from  ( select distinct  " \
        #               + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] + val_sql + " )group by m order by m"
        #     else:
        #         sql = "select formatDateTime(" + condition["attribute"] + ",'%F') day ,count(1) count from  ( select distinct  " \
        #               + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] + val_sql + " )group by day order by day"
        # else:
        #     if condition["conditional"][0] == "year":
        #         sql = "select toYear(" + condition["attribute"] + ") year,count(1) count from ( select distinct " \
        #              + attribute + "," + condition["attribute"] + " from " + schema["db"] + "." + schema["table"] + " ) group by year order by year "
        #     elif condition["conditional"][0] == "quarter":
        #         sql = "select concat(toString(year),\' \',toString(quarter)) yearQuarter ,count from (select toYear(" + \
        #               condition["attribute"] + ") year,toQuarter(" + condition["attribute"] \
        #               + ") quarter ,count(1) count from   ( select distinct  " + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] \
        #               + " )  group by year,quarter order by year,quarter) "
        #     elif condition["conditional"][0] == "month":
        #         sql = "select concat(toString(year),\' \',toString(month)) yearMonth, count from ( select toYear(" + \
        #               condition["attribute"] + ") year,toMonth(" + condition["attribute"] \
        #               + ") month ,count(1) count from  ( select distinct " + attribute + "," + condition["attribute"] + " from "\
        #               + schema["db"] + "." + schema["table"] \
        #               + " )group by year,month order by year,month)"
        #     elif condition["conditional"][0] == "week":
        #         sql = "select concat(toString(yw),\' \',toString(week)) ywWeek, count from (select toYearWeek(" + \
        #               condition[
        #                   "attribute"] + ") yw, toDayOfWeek(" + condition["attribute"] + \
        #               ") week ,count(1) count from   ( select distinct  " + attribute + "," + condition["attribute"] + " from "\
        #               + schema["db"] + "." + schema["table"] \
        #               + ") group by yw,week order by yw,week )"
        #     elif condition["conditional"][0] == "day":
        #         sql = "select formatDateTime(" + condition["attribute"] + ",'%F') day ,count(1) count from  ( select distinct  " \
        #               + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] + ") group by day order by day"
        #     elif condition["conditional"][0] == "hours":
        #         sql = "select formatDateTime(" + condition["attribute"] + ",'%F %H') h ,count(1) count from ( select distinct  " \
        #               + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] + " )group by h order by h"
        #     elif condition["conditional"][0] == "minute":
        #         sql = "select formatDateTime(" + condition["attribute"] + ",'%F %R') m ,count(1) count from  ( select distinct  " \
        #               + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] + " )group by m order by m"
        #     else:
        #         sql = "select formatDateTime(" + condition["attribute"] + ",'%F') day ,count(1) count from  ( select distinct  " \
        #               + attribute + "," + condition["attribute"] + " from " \
        #               + schema["db"] + "." + schema["table"] + " )group by day order by day"
        # if condition["conditional"][0] == "year":
        #     sql = "select toYear(" + condition["attribute"] + ") year,count(1) count from " \
        #           + schema["db"] + "." + schema["table"] + " group by year order by year "
        # elif condition["conditional"][0] == "quarter":
        #     sql = "select concat(toString(year),\' \',toString(quarter)) yearQuarter ,count from (select toYear(" + \
        #           condition["attribute"] + ") year,toQuarter(" + condition["attribute"] \
        #           + ") quarter ,count(1) count from " + schema["db"] + "." + schema["table"] \
        #           + " group by year,quarter order by year,quarter) "
        # elif condition["conditional"][0] == "month":
        #     sql = "select concat(toString(year),\' \',toString(month)) yearMonth, count from ( select toYear(" + \
        #           condition["attribute"] + ") year,toMonth(" + condition["attribute"] \
        #           + ") month ,count(1) count from " + schema["db"] + "." + schema["table"] \
        #           + " group by year,month order by year,month)"
        # elif condition["conditional"][0] == "week":
        #     sql = "select concat(toString(yw),\' \',toString(week)) ywWeek, count from (select toYearWeek(" + \
        #           condition[
        #               "attribute"] + ") yw, toDayOfWeek(" + condition["attribute"] + \
        #           ") week ,count(1) count from " + schema["db"] + "." + schema["table"] \
        #           + " group by yw,week order by yw,week )"
        # elif condition["conditional"][0] == "day":
        #     sql = "select formatDateTime(" + condition["attribute"] + ",'%F') day ,count(1) count from " \
        #           + schema["db"] + "." + schema["table"] + " group by day order by day"
        # elif condition["conditional"][0] == "hours":
        #     sql = "select formatDateTime(" + condition["attribute"] + ",'%F %H') h ,count(1) count from " \
        #           + schema["db"] + "." + schema["table"] + " group by h order by h"
        # elif condition["conditional"][0] == "minute":
        #     sql = "select formatDateTime(" + condition["attribute"] + ",'%F %R') m ,count(1) count from " \
        #           + schema["db"] + "." + schema["table"] + " group by m order by m"
        # else:
        #     sql = "select formatDateTime(" + condition["attribute"] + ",'%F') day ,count(1) count from " \
        #           + schema["db"] + "." + schema["table"] + " group by day order by day"
        return sql


def main():
    from clickhouse_driver import Client
    graphClient = Client(host="10.202.255.93", port="9090", user="default", password="root")
    from graph_op import CHGraph
    graph = CHGraph(graphClient)
    res = graph.execute("select * from anti_money_launder.transactions limit 10")
    list = res.columns.values.tolist();
    print(res.values.tolist())
    print(list)


def test():
    import data_load_config as config
    config_params = config.load_config()
    str(config_params["db"])
    print(str(config_params["db"]))
    dict_data = {"subGraph": "anti_money_launder"}
    model_service = ModelService()
    result_dict = model_service.search_subgraph_by_condition(dict_data, config_params)
    print(result_dict)


def test_function():
    import data_load_config as config
    config_params = config.load_config()
    str(config_params["db"])
    print(str(config_params["db"]))
    # dict_data = {"subGraph": "0b58bfda_7bf5_4661_ae21_5079057afe49", "type": "xiqianvertex",
    #              "attribute": "initial_deposit", "statistics": ""}
    # model_service = ModelService()
    # result_dict = model_service.statistics_operation_attribute_function(dict_data, config_params)
    # print(result_dict)
    # dict_data = {"subGraph": "0b58bfda_7bf5_4661_ae21_5079057afe49"}
    # model_service = ModelService()
    # res = model_service.statistics_operation_function(dict_data, config_params)
    # print(res)
    dict_data = {"subGraph": "0b58bfda_7bf5_4661_ae21_5079057afe49", "type": "xiqianvertex",
                 "attributes": "type,acct_stat"}
    model_service = ModelService()
    result_dict = model_service.statistics_operation_attributes_function(dict_data, config_params)
    print(result_dict)


if __name__ == '__main__':
    # main()
    test_function()
