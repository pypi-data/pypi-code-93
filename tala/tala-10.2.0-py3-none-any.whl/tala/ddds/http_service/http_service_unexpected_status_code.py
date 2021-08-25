from flask import Flask, abort

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=['POST'])
@app.route("/<path:path>", methods=['POST'])
def unexpected_status_code(path):
    abort(500)
