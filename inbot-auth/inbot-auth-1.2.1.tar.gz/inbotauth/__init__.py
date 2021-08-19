import uuid
import logging
import importlib
from flask import Flask, redirect, request, render_template, url_for, session, current_app as app
from flask.helpers import get_env, get_debug_flag
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from inbotauth.config import BaseConfig
from inbotauth import azure, google

LOGGER = logging.getLogger(__name__)


class FlaskOIDC(Flask):
    def _before_request(self):
        # ToDo: Need to refactor and divide this method in functions.
        # Whitelisted Endpoints i.e., health checks and status url
        LOGGER.info(f"Request Path: {request.path}")
        LOGGER.info(f"Request Endpoint: {request.endpoint}")
        LOGGER.info(f"Whitelisted Endpoint: {BaseConfig.WHITELISTED_ENDPOINTS}")

        if request.path.strip("/") in BaseConfig.WHITELISTED_ENDPOINTS.split(",") or \
                request.endpoint in BaseConfig.WHITELISTED_ENDPOINTS.split(","):
            return

        # If accepting token in the request headers
        token = None
        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            token = request.headers['Authorization'].split(None, 1)[1].strip()
        elif 'access_token' in request.form:
            token = request.form['access_token']
        elif 'access_token' in request.args:
            token = request.args['access_token']
        elif session.get('login_type') == 'microsoft':
            token = azure.get_token_from_cache(self.config['MS_SCOPE'])
        elif session.get('login_type') == 'google':
            token = google.get_token_from_cache()
        if not token:
            return redirect(url_for('login'))

    def __init__(self, *args, **kwargs):
        super(FlaskOIDC, self).__init__(*args, **kwargs)

        # Setup Session Database
        _sql_db = SQLAlchemy(self)
        self.config["SESSION_SQLALCHEMY"] = _sql_db

        auth_models = importlib.import_module(self.config["AUTH_MODELS_MODULE"])
        if self.config['TENANT_BASED_LOGIN']:
            tenant_cls_func = getattr(auth_models, self.config["AUTH_TENANT_CLASS_FUNC"])
            tenant_cls = tenant_cls_func(_sql_db)
        else:
            user_cls_func = getattr(auth_models, self.config["AUTH_USER_CLASS_FUNC"])
            user_cls = user_cls_func(_sql_db)

        # Setup Session Store, that will hold the session information
        # in database. OIDC by default keep the sessions in memory
        _session = Session(self)
        _session.app.session_interface.db.create_all()

        # Register the before request function that will make sure each
        # request is authenticated before processing
        self.before_request(self._before_request)

        self.jinja_env.globals.update(_build_auth_url=azure.build_auth_url)  # Used in template

        @self.route('/login')  # catch_all
        def login():
            return render_template("login.html")

        @self.route('/mslogin')  # catch_all
        def mslogin():
            session["state"] = str(uuid.uuid4())
            # Technically we could use empty list [] as scopes to do just sign in,
            # here we choose to also collect end user consent upfront
            auth_url = azure.build_auth_url(scopes=self.config['MS_SCOPE'], state=session["state"])
            return redirect(auth_url)

        @self.route('/mscallback')  # catch_all
        def mscallback():
            code = request.args.get('code')
            if request.args.get('state') != session.get("state"):
                return redirect(url_for('index'))  # No-OP. Goes back to Index page
            if "error" in request.args:  # Authentication/Authorization failure
                return render_template("auth_error.html", result=request.args)
            if code:
                cache = azure.load_cache()
                redirect_uri = url_for("mscallback", _external=True)
                result = azure.build_msal_app(cache=cache).acquire_token_by_authorization_code(
                    code,
                    scopes=self.config['MS_SCOPE'],  # Misspelled scope would cause an HTTP 400 error here
                    redirect_uri=redirect_uri)
                if "error" in result:
                    return render_template("auth_error.html", result=result)
                user_data = result.get("id_token_claims")
                if not user_data:
                    LOGGER.info("failed to get user info for state {}, code {}".format(
                        request.args.get('state'), code))
                    return render_template("auth_error.html", result=result)

                user_info = azure.query_user_info(cache.find("AccessToken")[0])
                domain = user_info['email'].split('@')[1]
                user_info['domain'] = domain
                user_info['tenant_id'] = user_data.get('tid')

                # the user is authenticated only if successfully adding the user
                user = self.config['PUT_USER_METHOD'](self, user_info)
                if not user:
                    return render_template("auth_error.html", result=request.args)

                # authenticate against database
                if self.config['TENANT_BASED_LOGIN']:
                    # if tenant based login, check if user tenant exists in tenant table
                    has_access = self.authenticate(tenant_cls, domain, result)
                else:
                    # if user based login, check if user exists in user table
                    has_access = self.authenticate(user_cls, user['email'], result)
                if not has_access:
                    return render_template("auth_error.html", result=user_info)

                azure.save_cache(cache)
                session["auth_user"] = user
                session['login_type'] = 'microsoft'
            return redirect(url_for('index'))

        @self.route('/glogin')  # catch_all
        def glogin():
            session["state"] = str(uuid.uuid4())
            # Technically we could use empty list [] as scopes to do just sign in,
            # here we choose to also collect end user consent upfront
            auth_url = google.build_auth_url(scopes=self.config['GOOGLE_SCOPE'], state=session["state"])
            return redirect(auth_url)

        @self.route("/gcallback")
        def gcallback():
            code = request.args.get('code')
            if request.args.get('state') != session.get("state"):
                return redirect(url_for('index'))  # No-OP. Goes back to Index page
            if "error" in request.args:  # Authentication/Authorization failure
                return render_template("auth_error.html", result=request.args)
            if code:
                client = google.get_client()
                client = google.get_token(request, code, client)
                user_info = google.query_user_info(client)
                domain = user_info['hd']
                user_info['domain'] = domain

                # the user is authenticated only if successfully adding the user
                user = self.config['PUT_USER_METHOD'](self, user_info)
                if not user:
                    return render_template("auth_error.html", result=request.args)

                # authenticate against database
                if self.config['TENANT_BASED_LOGIN']:
                    # if tenant based login, check if user domain exists in tenant table
                    has_access = self.authenticate(tenant_cls, domain, user_info)
                else:
                    # if user based login, check if user exists in user table
                    has_access = self.authenticate(user_cls, user['email'], user_info)
                if not has_access:
                    return render_template("auth_error.html", result=user_info)

                session["auth_user"] = user
                session['login_type'] = 'google'
                session['token_cache'] = client.token
            return redirect(url_for('index'))

        @self.route('/logout')  # catch_all
        def logout():
            if session['login_type'] == 'microsoft':
                authority = 'https://login.microsoftonline.com/' + session['auth_user']['tenant_id']
                session.clear()  # Wipe out user and its token cache from session
                return redirect(  # Also logout from your tenant's web session
                    authority + "/oauth2/v2.0/logout" + "?post_logout_redirect_uri=" \
                    + url_for("index", _external=True))
            elif session['login_type'] == 'google':
                session.clear()
                return redirect(url_for('login'))

    def authenticate(self, model_class, key, error_text):
        if model_class.query.get(key) is None:
            LOGGER.info("Authentication failed: {}".format(error_text))
            return False
        return True

    def make_config(self, instance_relative=False):
        """
        Overriding the default `make_config` function in order to support
        Flask OIDC package and all of their settings.
        """
        root_path = self.root_path
        if instance_relative:
            root_path = self.instance_path
        defaults = dict(self.default_config)
        defaults['ENV'] = get_env()
        defaults['DEBUG'] = get_debug_flag()

        # Append all the configurations from the base config class.
        for key, value in BaseConfig.__dict__.items():
            if not key.startswith('__'):
                defaults[key] = value
        return self.config_class(root_path, defaults)
