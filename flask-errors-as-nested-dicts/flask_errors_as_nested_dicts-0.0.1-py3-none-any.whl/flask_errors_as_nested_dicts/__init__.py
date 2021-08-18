__version__ = "0.0.1"
EXTENSION_NAME = "flask-errors-as-nested-dicts"


class ErrorsAsNestedDicts(object):
    """Wrapper class that integrates JWT Errors as Nested Dicts Flask application.

    This extension was developed for personal use and changes standard flask and jwt
    errors from something like::

        {
            "code": 404,
            "status": "Not Found"
        }

    to::

        {
            "errors": {
                "json": {
                    "url": [
                        "Does not exist."
                    ]
                }
            }
        }

    To use it, instantiate with an application::

        from flask import Flask
        from flask_jwt_extended import JWTManager

        app = Flask(__name__)
        jwt = JWTManager(app)
        ErrorsAsNestedDicts(app, jwt)

    :param app: The Flask application object.
    :param (optional) jwt: A JWTManager object from flask_jwt_extended lib.
    """

    def __init__(self, app=None, jwt=None, rollback_on_500=False):
        if app is not None:
            self.init_app(app, jwt, rollback_on_500)

    def init_app(self, app, jwt, rollback_on_500):
        """Initializes the application with the extension.

        :param Flask app: The Flask application object.
        """
        app.extensions = getattr(app, "extensions", {})
        app.extensions[EXTENSION_NAME] = self
        self._error_responses_to_nested_dicts(app, jwt, rollback_on_500)

    def _error_responses_to_nested_dicts(self, app, jwt, rollback_on_500):
        @app.errorhandler(404)
        def not_found_error(error):
            return {"errors": {"json": {"url": ["Does not exist."]}}}, 404

        @app.errorhandler(405)
        def not_allowed_error(error):
            return {"errors": {"json": {"url": ["Method not allowed."]}}}, 405

        @app.errorhandler(500)
        def internal_error(error):
            if rollback_on_500:
                self.db.session.rollback()
            return {"errors": {"json": {"server": ["Internal error."]}}}, 500

        if jwt is not None:
            @jwt.unauthorized_loader
            def unauthorized_callback(unauthorized_token):
                return {"errors": {"json": {"token": ["Authorization token is missing."]}}}, 401

            @jwt.revoked_token_loader
            def revoked_token_callback(jwt_header, jwt_payload):
                return {"errors": {"json": {"token": ["Your token is invalid."]}}}, 401

            @jwt.invalid_token_loader
            def invalid_token_callback(invalid_token):
                return {"errors": {"json": {"token": ["Your token is invalid."]}}}, 401

            @jwt.expired_token_loader
            def expired_token_callback(jwt_header, jwt_payload):
                return {"errors": {"json": {"token": ["Your token has expired."]}}}, 401
