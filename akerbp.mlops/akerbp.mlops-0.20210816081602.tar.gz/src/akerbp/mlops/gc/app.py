"""
app.py

Web service (training or prediction).

"""

from importlib import import_module

from fastapi import FastAPI
from pydantic import Json, BaseModel

from akerbp.mlops.gc.helpers import access_secret_version
from akerbp.mlops.core import config, logger
logging=logger.get_logger("mlops_gc")
service_name = config.envs.service_name

service = import_module(f"akerbp.mlops.services.{service_name}").service


secrets_string = access_secret_version('mlops-cdf-keys') 
secrets = eval(secrets_string)


app = FastAPI()

class Data(BaseModel):
    data: Json

@app.post("/")
def api(input: Data):
    data = input.data
    logging.debug(f"{data=}")
    try:
        config.update_cdf_keys(secrets)
        return service(data, secrets)
    except Exception as error:
      error_type = type(error).__name__
      service_name = service_name.capitalize()
      error_message = f"{service_name} service failed. {error_type}: {error}"
      logging.critical(error_message)
      return dict(status='error', error_message=error_message)
