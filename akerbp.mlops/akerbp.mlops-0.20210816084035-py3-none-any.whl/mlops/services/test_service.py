"""
test_service.py

Generic test for services (training or prediction). Set up the service folder
(copy model code, download model artifact if necessary), install model
dependencies and set current working directory to service folder, then run:
python -m akerbp.mlops.services.test_service
"""
import sys
import json
from importlib import import_module
import subprocess
from pathlib import Path

from akerbp.mlops.core import config, logger
service_name = config.envs.service_name
logging=logger.get_logger(name='MLOps')


api_keys = config.api_keys


def mock_saver(*args, **kargs):
    pass


def run_tests(test_path, path_type='file'):
    """
    Run tests with pytest
    
    Input
      - test_path: path to tests with pytest (string or a list of strings) All
        should have the same format (see next parameter)
      - path_type: either 'file' (test_path refers then to files/folders) or
        'module' (test_path refers then to modules)
    """
    command = [sys.executable, "-m", "pytest", 
                "--quiet", "--color=no", "-W ignore:numpy.ufunc size changed"]
    if path_type == 'module':
        command.append("--pyargs")
    if isinstance(test_path, str) or isinstance(test_path, Path):
        command.append(test_path)
    elif isinstance(test_path, list):
        command += test_path
    else:
        raise ValueError("Input should be string or list of strings")
    logging.info(f"Run tests: {test_path}")
    subprocess.check_call(command)


def get_model_test_data(test_import_path):
    """
    Read input and validation function from the model test file
    """
    service_test = import_module(test_import_path).ServiceTest()
    input = getattr(service_test, f"{service_name}_input")
    check = getattr(service_test, f"{service_name}_check")
    return input, check


def test_service(input, check):
   """
   Generic service test. Call service with the model's test input data and
   validate the output.
   """
   logging.info(f"Test {service_name} service")
   service = import_module(f"akerbp.mlops.services.{service_name}").service

   if service_name == 'training':
      response = service(data=input, secrets=api_keys, saver=mock_saver)
   elif service_name == 'prediction':
      response = service(data=input, secrets=api_keys)
   else:
      raise Exception("Unknown service name")
   
   assert response['status'] == 'ok'
   assert check(response[service_name])
   

if __name__ == '__main__':
   c = config.read_service_settings()
   run_tests(c.test_file)
   input, check = get_model_test_data(c.test_import_path)
   test_service(input, check)
   print(json.dumps(input))