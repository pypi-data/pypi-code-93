from flask import Flask

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=['POST'])
@app.route("/<path:path>", methods=['POST'])
def schema_violated_json_response(path):
    schema_violated_json = """
    {
        "schema": 781.0,
        "violation": []
    }"""
    response = app.response_class(response=schema_violated_json, status=200, mimetype='application/json')
    return response
