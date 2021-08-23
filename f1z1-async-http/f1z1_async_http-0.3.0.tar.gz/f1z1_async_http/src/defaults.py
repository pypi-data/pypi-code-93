# @Time     : 2021/8/23
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from httpx import Limits, Timeout

DEFAULT_LIMITS = Limits(max_connections=100, max_keepalive_connections=20)
DEFAULT_TIMEOUT = Timeout(3600)
