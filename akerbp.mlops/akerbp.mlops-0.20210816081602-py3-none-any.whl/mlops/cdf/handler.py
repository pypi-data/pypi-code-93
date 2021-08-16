# handler.py
import traceback
from importlib import import_module
import warnings
warnings.simplefilter("ignore")

import akerbp.mlops.cdf.helpers as cdf
from akerbp.mlops.core import logger, config
service_name = config.envs.service_name
logging=logger.get_logger("mlops_cdf")

service = import_module(f"akerbp.mlops.services.{service_name}").service


def handle(data, secrets, function_call_info):
   try:
      if data:
         output = service(data, secrets)
      else:
         output = dict(status='ok')
      cdf.api_keys = secrets
      cdf.set_up_cdf_client(context='deploy')
      metadata = cdf.get_function_metadata(function_call_info["function_id"])
      output.update(dict(metadata=metadata))
      return output
   except Exception:
      trace = traceback.format_exc()
      error_message = f"{service_name} service failed.\n{trace}"
      logging.critical(error_message)
      return dict(status='error', error_message=error_message)
