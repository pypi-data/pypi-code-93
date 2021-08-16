from flask import Blueprint
from init import app

remote = Blueprint('remote', __name__, )


@remote.errorhandler(Exception)
def default_error_handler(error):
    app.log.exception('error 500: %s', error)
    import traceback
    trac = traceback.format_exc()
    response = {"status": False, "message": str(error), "track": trac}

    return jsonify(response), 500, {'Content-Type': 'application/json'}

from .ActuatorRemote import *
from .TriggerRemoteActor import *
from .LogReadRemoteService import *
from .AsyncResponseRestService import *
from .PrometheusMetricsRemoteService import *
