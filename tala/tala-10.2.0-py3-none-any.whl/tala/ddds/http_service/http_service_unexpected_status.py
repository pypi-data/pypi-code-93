from flask import Flask

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=['POST'])
@app.route("/<path:path>", methods=['POST'])
def unexpected_version_in_response(path):
    malformed_json = """
    {
      "status": "error",
      "message": "an error message",
      "data": {
        "version": "1.0"
      }
    }"""
    response = app.response_class(response=malformed_json, status=200, mimetype='application/json')
    return response
