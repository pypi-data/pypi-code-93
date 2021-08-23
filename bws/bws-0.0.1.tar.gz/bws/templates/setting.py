template = """
# generado automaticamente
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager, Command
from flask import Flask, Blueprint, url_for, jsonify
from bws.admin.json import JSONEncoderCurstom

def create_app():
    app = Flask(__name__, static_folder="../static")
    app.config.from_pyfile("config.py")

    return app


app = create_app()
db = SQLAlchemy(app)
app.json_encoder = JSONEncoderCurstom

api = Blueprint('api', __name__)
app.register_blueprint(api)
cmd = Manager(app)
migrate = Manager(app)

cmd.Command = Command
migrate.Command = Command

migrate.add_option("--dev", dest="dev", required=False, action='store_true')
cmd.add_option("--dev", dest="dev", required=False, action='store_true')


def has_no_empty_params(rule):
    defaults = rule.defaults if rule.defaults is not None else ()
    arguments = rule.arguments if rule.arguments is not None else ()
    return len(defaults) >= len(arguments)


@app.route("/site-map")
def site_map():
    links = []
    for rule in app.url_map.iter_rules():
        # Filter out rules we can't navigate to in a browser
        # and rules that require parameters
        if "GET" in rule.methods and has_no_empty_params(rule):
            url = url_for(rule.endpoint, **(rule.defaults or {}))
            links.append((url, rule.endpoint))
    # links is now a list of url, endpoint tuples
    return jsonify(links)


"""