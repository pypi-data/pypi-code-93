import json

from flask import Flask, request
from flask_cors import CORS

from multiprocessing import Process, Manager

from fathom_lib.workflow import run_workflow, validate_pipeline_fake_data

app = Flask(__name__)
CORS(app)


def validate_parameters(data, params):
    if data is None:
        return "Not a valid request"
    for param in params:
        if param not in data:
            return f"Missing {param}"
    return None


@app.route("/executor/health")
def validate_pipeline():
    return "OK"


def validation_worker(return_dict, graph_details):
    return_dict["log"] = validate_pipeline_fake_data(graph_details)


@app.route("/executor/validate_pipeline", methods=["POST"])
def validate_pipeline_endpoint():
    data = request.get_json()
    validation_error = validate_parameters(data, ["graph_details"])
    if validation_error is not None:
        return validation_error
    manager = Manager()
    return_dict = manager.dict()
    run_process = Process(
        target=validation_worker,
        args=(
            return_dict,
            data["graph_details"],
        ),
    )
    run_process.start()
    run_process.join()
    return json.dumps(return_dict["log"])


@app.route("/executor/run_workflow", methods=["POST"])
def run_workflow_endpoint():
    data = request.get_json()
    validation_error = validate_parameters(data, ["graph_details", "data_source"])
    if validation_error is not None:
        return validation_error
    run_process = Process(
        target=run_workflow,
        args=(
            data["graph_details"],
            data["data_source"],
        ),
    )
    run_process.start()
    return json.dumps({"message": "Workflow started running..."})
