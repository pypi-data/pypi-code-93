import pathlib
from eventlet.green import subprocess

from flask import Flask, app, render_template
from flask_cors import CORS

from openfabric_pysdk.manifest import manifest
from openfabric_pysdk.service import OpenfabricService

app = Flask(__name__, template_folder=f"{pathlib.Path(__file__).parent}/templates")
CORS(app)


@app.route("/")
def index():
    return render_template("index.html", manifest=manifest.all())


class OpenfabricStarter:

    @staticmethod
    def ignite(debug, host):
        service = OpenfabricService(app)
        service.install_rest('/app')
        service.install_socket('/app')
        # service.run(debug=debug, host=host)
