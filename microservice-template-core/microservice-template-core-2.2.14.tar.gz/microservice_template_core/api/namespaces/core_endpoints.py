from microservice_template_core.tools.flask_restplus import api
from flask_restx import Resource
from microservice_template_core.tools.logger import get_logger
from microservice_template_core.tools.prometheus_metrics import Prom


logger = get_logger()

ns = api.namespace('core-endpoints', description='Core endpoints')


@ns.route('/health')
class Health(Resource):

    def get(self):
        """
            Return general health check result
        """
        Prom.core_endpoint_get_health_count.inc(1)

        return {"msg": "Healthy"}, 200
