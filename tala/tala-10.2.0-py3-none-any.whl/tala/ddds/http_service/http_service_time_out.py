from flask import Flask
import time

app = Flask(__name__)


@app.route("/", defaults={"path": ""}, methods=['POST'])
@app.route("/<path:path>", methods=['POST'])
def wait_more_than_two_seconds(path):
    time.sleep(4)
    return "Hello!"
