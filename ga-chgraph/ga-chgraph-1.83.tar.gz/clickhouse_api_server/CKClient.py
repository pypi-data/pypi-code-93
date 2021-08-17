from clickhouse_driver import Client


def get_client(clickhouse_connect):
    if "user" in clickhouse_connect and "password" in clickhouse_connect:
        graph_client = Client(host=clickhouse_connect["ip"], port=clickhouse_connect["port"], user=clickhouse_connect["user"],
                              password=clickhouse_connect["password"])
    else:
        graph_client = Client(host=clickhouse_connect["ip"], port=clickhouse_connect["port"])
    graph_client.execute(" set max_query_size=100000000 ")
    return graph_client
