from prometheus_client import multiprocess, start_http_server, Gauge, Counter, Summary, Histogram, Info, Enum


class Prom:
    core_endpoint_get_health_count = Counter('my_start', 'Description of counter')
