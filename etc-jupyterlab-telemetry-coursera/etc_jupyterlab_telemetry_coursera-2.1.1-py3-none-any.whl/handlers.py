# import logging, os
# logger = logging.getLogger('etc_jupyterlab_telemetry_coursera')
# logger.propagate = False
# fhandler = logging.FileHandler(filename=os.getcwd() + '/debug.log', mode='a')
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fhandler.setFormatter(formatter)
# logger.addHandler(fhandler)
# logger.setLevel(logging.DEBUG)


from requests import Session, Request
from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import os, json, concurrent, tornado
from jupyter_core.paths import jupyter_config_path
from pathlib import Path
import urllib.request

def get_config():

    try: 
        HERE = Path(__file__).parent.resolve()

        with (HERE / "labextension" / "package.json").open() as fid:
            data = json.load(fid)

        CONFIG_FILE_NAME = data['jupyterlab']['discovery']['server']['base']['name'] + '.json'
    except:
        raise Exception('The extension failed to obtain a base extension name in package.json. \
            The base extension name should be at jupyterlab.discovery.server.base.name in package.json.')

    config = None

    config_dirs = jupyter_config_path()
    config_dirs.reverse()
    for config_dir in config_dirs:

        path = os.path.join(config_dir, CONFIG_FILE_NAME)

        if os.path.isfile(path):
            with open(path) as f:
                config = json.load(f)
            break

    if not config:
        raise Exception('The ' + CONFIG_FILE_NAME + ' configuration file is missing in one of: ' + ', '.join(config_dirs))

    return config

CONFIG = get_config()

class RouteHandler(APIHandler):

    executor = concurrent.futures.ThreadPoolExecutor(5)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    # The following decorator should be present on all verb methods (head, get, post,
    # patch, put, delete, options) to ensure only authorized user can request the
    # Jupyter server
    @tornado.web.authenticated
    def get(self, resource):

        try:
            if resource == 'id':
                self.finish(
                    json.dumps(
                        os.getenv('WORKSPACE_ID') if os.getenv('WORKSPACE_ID') is not None else 'UNDEFINED'
                        )
                    )

            elif resource == 'config':

                    if CONFIG:
                        self.finish(json.dumps(CONFIG))
                    else:
                        self.set_status(404)
            else:
                self.set_status(404)

        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps(str(e)))

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, resource):
        try:

            if resource == 's3':

                result = yield self.process_request()

                self.finish(json.dumps(result))

            else:
                self.set_status(404)

        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps(str(e)))

    @tornado.concurrent.run_on_executor 
    def process_request(self):

        data = self.request.body

        url = CONFIG['url']
        bucket = CONFIG['bucket']
        path = CONFIG['path']

        url = '/'.join([url, bucket, path])
        
        with Session() as s:

            headers = {
                'Content-Type': 'application/json'
            }

            req = Request('POST', url, data=data, headers=headers)

            prepped = s.prepare_request(req)

            res = s.send(prepped, proxies=urllib.request.getproxies())

            return {'url': res.url, 'status_code': res.status_code}


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "etc-jupyterlab-telemetry-coursera", "(.*)")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)