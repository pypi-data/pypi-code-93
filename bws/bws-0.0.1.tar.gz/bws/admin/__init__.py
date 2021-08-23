from flask import send_from_directory, current_app, send_file
from flask_admin import expose, AdminIndexView
import flask_admin
import logging
import requests as http
from .urls import *
from .view import *
# import importlib
import tarfile
import os, io
import inspect

logger = logging.getLogger("Boot Admin")


def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

# Create customized index view class that handles login & registration
class IndexView(AdminIndexView):
    
    @expose_json('/')
    def index(self):
        # app = importlib.import_module("app").app
        return {
            "success": True,
            "message": current_app.config["NAME"]
        }
    
    @expose('/dev')
    def get_dev(self):
        return """<pre>Jose Angel Delgado.
       _           _____  ___
      (_)___ _____/ /__ \<  /
     / / __ `/ __  /__/ // / 
    / / /_/ / /_/ // __// /  
 __/ /\__,_/\__,_//____/_/   
/___/                        </pre>      
<style>body{ text-align: center; margin-top: 20% }</style>   
"""

    @expose('/tar/static/dist/<path:url>')
    def get_tar(self, url):
        filename = f"static/dist/{url}"
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            tar.add(filename, arcname=os.path.basename(filename))
        buffer.seek(0)
        return send_file(buffer,  mimetype="application/tar+gzip")

    @expose('/wiki.md')
    def get_wiki(self):
        return """ Metodo reservado para responder la wiki. de los servicios """
    
    @expose('/reload')
    def get_reload(self):
        try:
            app = current_app
            print(app.config["frontviews"])
            res = http.post(app.config["REGISTER"], json=app.config["frontviews"], verify=False)
            logger.info(res.content)
            return res.content
        except Exception as e:
            logger.exception(e)
            return "No se pudo registrar"
    
    @expose_json('/🥚')
    def get_egg(self):
        app = current_app
        return app.config["frontviews"]
        

class Admin(flask_admin.Admin):
    def register_frontend(self, view, endpoint=""):
        app = self.app

        frontviews = app.config.get("frontviews", [])
        if inspect.isclass(view):
            view = view(endpoint=endpoint, name=endpoint)

        endpoint = view.endpoint or endpoint or endpoint.__class__.__name__.lower()
        
        if endpoint.endswith("/"):
            endpoint = endpoint[:-1]
        
        logger.info("endpoint: %s" % endpoint)
        logger.info("register: %s" % app.config["REGISTER"])
        self.add_view(view)
        try:
            setup = {
                "host": app.config["MS_HOST"],
                "name": view.name,
                "ico": view.ico,
                "endpoint": {
                    "frontend": view.endpoint_frontend,
                    "api": view.endpoint_api or '/',
                    "js": f"{endpoint}/js",
                    "css": f"{endpoint}/css",
                    "ctx": f"{endpoint}/ctx",

                }
            }
            frontviews += [setup]
            res = http.post(app.config["REGISTER"], json=[setup], verify=False)
            logger.info(res.content)
        except Exception as e:
            logger.exception(e)
            print("No se pudo registrar")
        
        app.config["frontviews"] = frontviews 

    def register_api(self, view, endpoint="", *args, **kargs):
        endpoint = endpoint or endpoint.__class__.__name__.lower()
        if inspect.isclass(view):
            view = view(endpoint=endpoint, *args, **kargs)
        self.add_view(view)


def create_admin(app):
    # Create admin
    return Admin(app, 'MS',
                url="/",
                endpoint="index",
                  index_view=IndexView(url="/", endpoint="/"),
                )
