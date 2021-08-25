from flask import Flask

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=['POST'])
@app.route("/<path:path>", methods=['POST'])
def unexpected_version_in_response(path):
    malformed_json = """
    {
      "status": "success",
      "data": {
        "version": "0.0",
        "result": [
          {
            "value": 17,
            "confidence": 1.0,
            "grammar_entry": null
          }
        ]
      }
    }"""
    response = app.response_class(response=malformed_json, status=200, mimetype='application/json')
    return response
