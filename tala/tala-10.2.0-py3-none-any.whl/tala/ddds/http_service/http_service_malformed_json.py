from flask import Flask

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=['POST'])
@app.route("/<path:path>", methods=['POST'])
def malformed_json_response(path):
    malformed_json = """
    {
        "grammar_entry": "mock_grammar_entry" **
        "sort": "mock_sort" **
        "value": "mock_value"
    }"""
    response = app.response_class(response=malformed_json, status=200, mimetype='application/json')
    return response
