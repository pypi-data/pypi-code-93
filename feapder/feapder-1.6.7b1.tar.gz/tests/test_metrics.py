from feapder import setting
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

import re
import time
from datetime import datetime, timedelta


def get_value(content, key):
    value = re.search(f"{key}=([^,]+)", content)
    if value:
        return value.group(1)
    else:
        return None


if __name__ == "__main__":
    influxdb_client = InfluxDBClient(
        host=setting.INFLUXDB_HOST,
        port=setting.INFLUXDB_PORT,
        udp_port=setting.INFLUXDB_UDP_PORT,
        database="feapder",
        use_udp=False,
        timeout=10,
        username="root",
        password="root",
    )

    # r = influxdb_client.get_list_measurements()
    # print(r)
    series = influxdb_client.get_list_series(measurement="task_23")

    # 按照_type和classify分类，按照_key分组
    point_classifies = set()
    for serie in series:
        _type = get_value(serie, "_type")
        classify = get_value(serie, "classify")
        point_classifies.add((_type, classify))

    print(point_classifies)

    task_id = 23
    start_time = "{}000000000".format(1629041351)
    end_time = "{}000000000".format(1629041400)
    # end_time = "{}000000000".format(int(time.time()))

    measurement = f"task_{task_id}"

    # point_classifies = [("counter", "document")]

    # datas = [
    #     {
    #         "name": "document",
    #         "series": [
    #             {
    #                 "columns": ["time", "sum"],
    #                 "_key": "TestSpider: download_success",
    #                 "values": [
    #                     ["2021-08-15T15: 29: 00Z", 1],
    #                     ["2021-08-15T15: 30: 00Z", 0],
    #                 ],
    #             }
    #         ],
    #     }
    # ]
    datas = []

    for _type, classify in point_classifies:
        if _type != "counter":
            continue  # 暂时不支持

        if classify:
            sql = f"""
                SELECT sum("_count") FROM "{measurement}" WHERE ("classify" = '{classify}') AND time >= {start_time} and time <= {end_time} GROUP BY time(60s), "_key" fill(0)
            """
        else:
            sql = f"""
                    SELECT sum("_count") FROM "{measurement}" WHERE time >= {start_time} and time <= {end_time} GROUP BY time(60s), "_key" fill(0)
                    """

        data = {}
        data["name"] = classify or ""
        data["series"] = []

        print(sql)
        _points: ResultSet = influxdb_client.query(sql)
        for _serie in _points.raw.get("series"):
            serie = {}

            serie["key"] = _serie.get("tags").get("_key")
            serie["columns"] = _serie.get("columns")
            serie["values"] = []
            # 时间格式化
            for point in _serie.get("values"):
                _time, count = point

                _time = (
                    datetime.strptime(_time, "%Y-%m-%dT%H:%M:%SZ") + timedelta(hours=8)
                ).strftime("%Y-%m-%d %H:%M:%S")

                serie["values"].append([_time, count])

            data["series"].append(serie)

        datas.append(data)

    print(datas)

# [
#   {
#     "name": "document",
#     "series": [
#       {
#         "key": "TestSpider:download_success",
#         "columns": [
#           "time",
#           "sum"
#         ],
#         "values": [
#           [
#             "2021-08-15 23:29:00",
#             1
#           ],
#           [
#             "2021-08-15 23:30:00",
#             0
#           ]
#         ]
#       },
#       {
#         "key": "TestSpider:download_total",
#         "columns": [
#           "time",
#           "sum"
#         ],
#         "values": [
#           [
#             "2021-08-15 23:29:00",
#             1
#           ],
#           [
#             "2021-08-15 23:30:00",
#             0
#           ]
#         ]
#       }
#     ]
#   },
#   {
#     "name": "spider_data",
#     "series": [
#       {
#         "key": "title",
#         "columns": [
#           "time",
#           "sum"
#         ],
#         "values": [
#           [
#             "2021-08-15 23:29:00",
#             1
#           ],
#           [
#             "2021-08-15 23:30:00",
#             0
#           ]
#         ]
#       }
#     ]
#   }
# ]
