# The MIT License (MIT)
#
# Copyright (c) 2021 Scott Lau
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from gevent.pywsgi import WSGIServer
from sc_utilities import log_init

log_init()

from sc_gz_dashboard.flask.data.v1_0_0.dashboard_data_view import *
from .utils import ConfigUtils
from flask_restful import Api
from sc_gz_dashboard.flask.data.v1_0_0 import *
from .flask import app


class Runner(metaclass=Singleton):

    def __init__(self):
        pass

    def run(self):
        config = ConfigUtils.get_config()
        host = config.get("server.host")
        port = config.get("server.port")
        logging.getLogger(__name__).info("Flask运行于：{}:{}".format(host, port))

        self.add_api_resources(app)

        log_obj = logging.getLogger(__name__)
        server = WSGIServer((host, port), app, log=log_obj, error_log=log_obj)
        server.serve_forever()
        return 0

    def add_api_resources(self, app_obj):
        api = Api(app_obj)
        # 数字看板相关
        api.add_resource(GetAvailableYears, '/api/gz-dashboard/v1.0.0/getAvailableYears')
        api.add_resource(GetYearReportTime, '/api/gz-dashboard/v1.0.0/getYearReportTime/<year>')
        api.add_resource(GetDashboardData, '/api/gz-dashboard/v1.0.0/getData/<year>')
        # 指标数据管理
        api.add_resource(IndicatorHistoryList, '/api/gz-dashboard/v1.0.0/indicatorHistoryData')
        api.add_resource(IndicatorHistoryItem, '/api/gz-dashboard/v1.0.0/indicatorHistoryData/<id>')
        api.add_resource(IndicatorItemList, '/api/gz-dashboard/v1.0.0/indicatorItemData')
        api.add_resource(IndicatorItemFilter, '/api/gz-dashboard/v1.0.0/getIndicatorItemFilterData')


def main():
    try:
        state = Runner().run()
    except Exception as e:
        logging.getLogger(__name__).exception('An error occurred.', exc_info=e)
        return 1
    else:
        return state


if __name__ == '__main__':
    main()
