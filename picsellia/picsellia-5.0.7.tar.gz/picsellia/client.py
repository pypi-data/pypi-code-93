import collections
import json
import os
import sys
import io
import requests
import picsellia
from PIL import Image, ImageDraw, ExifTags
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Value
import picsellia.pxl_multithreading as mlt
import picsellia.pxl_exceptions as exceptions
from pxl_parser import COCOParser, PVOCParser
from uuid import uuid4
from picsellia.pxl_utils import is_uuid, check_status_code
import picsellia.pxl_utils as utils
from picsellia.pxl_urls_v2 import Urls as urls
from picsellia.pxl_requests import pxl_requests
from pathlib import Path
from functools import partial
import subprocess
import threading
from picsellia.pxl_requests import pxl_requests
from beartype import beartype
from typing import Any, List, Union, Optional
from picsellia.decorators import exception_handler
import tqdm
import datetime 
from decorators import retry

class Client:
    
    def __init__(self, api_token=None, organization=None, host="https://app.picsellia.com/sdk/v2/", interactive=True):
        """Initiliaze Picsellia Client connection.

        Args:
            api_token ([uuid4]): [Your api token accessible in Profile Page]
            host (str, optional): [description]. Defaults to "https://app.picsellia.com/sdk/v2".
            interactive (bool, optional): [set verbose mode]. Defaults to True.

        Raises:
            exceptions.NetworkError: [If Platform Not responding]
        """

        if api_token == None:
            if "PICSELLIA_TOKEN" in os.environ:
                token = os.environ["PICSELLIA_TOKEN"]
            else:
                raise Exception("Please set up the PICSELLIA_TOKEN environement variable or specify your token")
        else:
            token = api_token
        self.auth = {"Authorization": "Token " + token}
        self.host = host
        self.requests = pxl_requests(self.auth)
        r = self.requests.get(self.host + 'ping')
        # User Variables 
        self.username = r.json()["username"]
        self.sdk_version = r.json()["sdk_version"]
        if self.sdk_version != picsellia.__version__:  # pragma: no cover
            print("{}You are using an outdated version of the picsellia package ({})\nPlease consider upgrading to {} with pip install picsellia --upgrade{}".format('\033[91m', picsellia.__version__, self.sdk_version, '\033[0m'))
        # Project Variables
        self.project_name_list = None
        self.project_token = None
        self.project_id = None
        self.project_infos = None
        self.project_name = None
        self.project_type = None

        # Dataset Variables 
        self.supported_img_types = ("png", "jpg", "jpeg", "JPG", "JPEG", "PNG")
        # Network Variables
        self.network_names = None
        self.network_id = None
        self.network_name = None
        

        # Directory Variables
        self.png_dir = None
        self.base_dir = None
        self.metrics_dir = None
        self.checkpoint_dir = None
        self.record_dir = None
        self.config_dir = None
        self.results_dir = None
        self.exported_model_dir = None

        # Experiment Variables
        self.experiment_id = None
        self.exp_name = None
        self.exp_description = None 
        self.exp_status = None 
        self.exp_parameters = None
        self.line_nb = 0
        self.annotation_type = None
        self.dict_annotations = {}
        self.train_list_id = None
        self.eval_list_id = None
        self.train_list = None
        self.eval_list = None
        self.index_url = None
        self.label_path = None
        self.label_map = None
        self.urls = urls(self.host, self.auth)
        data = {
            'organization': organization
        }
        r = self.requests.post(self.host + 'get_organization', data=json.dumps(data))
        self.organization_id = r.json()["organization_id"]
        self.organization_name = r.json()["organization_name"]
        self.datalake = self.Datalake(token, organization=organization, host=self.host, ping=True)
        self.network = self.Network(token, organization=organization, host=self.host, ping=True)
        self.project = self.Project(token, organization=organization, host=self.host, ping=True)
        self.experiment = self.Experiment(token, self.host, ping=True)
        self.interactive = interactive
        print("Hi {}, welcome back.".format(self.username))

    def __str__(self) -> str:
        return "Client Initialized for {} organization".format(self.organization_name)

    class Experiment:

        def __init__(self, api_token: str=None, host: str="https://app.picsellia.com/sdk/v2/",
                     project_token: str=None, id: str=None,
                     name: str=None, interactive: bool=True, ping: bool=False):
            """Initialize the instance of the Picsellia server .

            Args:
                api_token (str, optional): [Your API token, find it in your Profile Page]. Defaults to None.
                host (str, optional): [Picsellia host to connect]. Defaults to "https://app.picsellia.com/sdk/v2/".
                project_token (str, optional): [Project ID, find it in your Project Page]. Defaults to None.
                id (str, optional): [Experiment ID to checkout]. Defaults to None.
                name (str, optional): [Name of the Experiment to checkout]. Defaults to None.
                interactive (bool, optional): [Set to False to disable verbosity]. Defaults to True.
                ping (bool, optional): [Set to True if you don't want to ping Picsellia Platform]. Defaults to False.

            Raises:
                Exception: [Wrong TOKEN]
                exceptions.NetworkError: [Picsellia Platform not responding]
            """
            self.host = host
            if not ping:
                if api_token == None:
                    if "PICSELLIA_TOKEN" in os.environ:
                        token = os.environ["PICSELLIA_TOKEN"]
                    else:
                        raise Exception("Please set up the PICSELLIA_TOKEN environement variable or specify your token")
                else:
                    token = api_token
                self.auth = {"Authorization": "Token " + token}
                self.requests = pxl_requests(self.auth)
                r = self.requests.get(self.host + 'ping')
                self.username = r.json()["username"]
                self.sdk_version = r.json()["sdk_version"]
                if self.sdk_version != picsellia.__version__:  # pragma: no cover
                    print("{}You are using an outdated version of the picsellia package ({})\nPlease consider upgrading to {} with pip install picsellia --upgrade{}".format('\033[91m', picsellia.__version__, self.sdk_version, '\033[0m'))
                print("Hi {}, welcome back.".format(self.username))
            else:
                self.auth = {"Authorization": "Token " + api_token}
                self.requests = pxl_requests(self.auth)
        
            self.id = id
            if name is not None:
                self.experiment_name = name
            else:
                self.experiment_name = ""
            self.urls = urls(self.host, self.auth)
            self.interactive = interactive
            self.project_token = project_token
            self.base_dir = self.experiment_name
            self.png_dir = os.path.join(self.base_dir, 'images')
            self.line_nb = 0
            self.buffer_length = 1
            self.run = None
            self.logged_data_names = []
            self.infos = {}
            self.name = ""
            self.date_created = ""
            self.dataset = {}
            self.owner = ""
            self.description = ""
            self.files = []
            self.data = []
            self.status = ""

        def __str__(self) -> str:
            if self.infos == {}:
                return "No experiment, you can retrieve one using checkout() or create() methods"
            else:
                return json.dumps(self.infos, indent=2)

        @exception_handler
        @beartype
        def start_logging_chapter(self, name: str) -> None:
            """Print a log entry to the log .

            Args:
                name (str): [Chapter name]
            """
            assert self.id != None, "Please create or checkout experiment first."
            print('--#--' + name)
            
        @exception_handler
        @beartype
        def start_logging_buffer(self, length: int=1) -> None:
            """Start logging buffer .

            Args:
                length (int, optional): [Buffer length]. Defaults to 1.
            """
            assert self.id!=None, "Please create or checkout experiment first."
            print('--{}--'.format(str(length)))
            self.buffer_length = length

        @exception_handler
        @beartype
        def end_logging_buffer(self,):
            """End the logging buffer .
            """
            assert self.id!=None, "Please create or checkout experiment first."
            print('---{}---'.format(str(self.buffer_length)))

        def send_experiment_logging(self, log: str, part: str, final: bool=False, special: bool=False):
            """Send a logging experiment to the experiment .

            Args:
                log (str): [Log content]
                part (str): [Logging Part]
                final (bool, optional): [True if Final line]. Defaults to False.
                special (bool, optional): [True if special log]. Defaults to False.

            Raises:
                exceptions.NetworkError: [Picsellia Platform not responding]
            """
            assert self.id!=None, "Please create or checkout experiment first."
            to_send = {
                "experiment_id": self.id,
                "line_nb": self.line_nb,
                "log": log,
                "final": final,
                "part": part,
                "special": special
            }
            self.line_nb +=1
            try:
                self.requests.post(self.host + 'experiment/send_experiment_logging', data=json.dumps(to_send), headers=self.auth)
            except Exception:  # pragma: no cover
                raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        
        @exception_handler
        @beartype
        def update_job_status(self, status: str):
            """Update the job status.

            Args:
                status (str): [Status to send]

            Raises:
                exceptions.NetworkError: [Picsellia Platform not responding]
            """
            assert self.id!=None, "Please create or checkout experiment first."
            to_send = {
                "status": status,
            }
            self.requests.post(self.host + 'experiment/{}/update_job_status'.format(self.id), data=json.dumps(to_send))

        @exception_handler
        @beartype
        def checkout(self, name: str=None, id: str=None,  project_token: str=None, tree: bool=False, with_file: bool=False, with_data: bool=False):
            """Checkout an experiment.

            Args:
                name (str, optional): [Name of the Experiment]. Defaults to None.
                id (str, optional): [Id of the experiment to checkout]. Defaults to None.
                project_token (str, optional): [Project ID, find it in your Project Page]. Defaults to None.
                tree (bool, optional): [True if you want to create directory tree]. Defaults to False.
                with_file (bool, optional): [True if you want to download all related files]. Defaults to False.
                with_data (bool, optional): [True if you want to download all related data]. Defaults to False.

            Raises:
                Exception: [Experiment does not exists]

            Returns:
                [Client]: [Return self]
            """
            identifier = None
            if self.id != None:
                identifier = self.id
            elif self.project_token != None:
                if self.experiment_name != "":
                    identifier = self.experiment_name
                elif name != None:
                    identifier = name
                elif id != None:
                    identifier = id
            elif project_token != None:
                self.project_token = project_token
                if self.experiment_name != '':
                    identifier = self.experiment_name
                elif name != None:
                    identifier = name
            if identifier == None:
                raise Exception('No corresponding experiment found, please enter a correct experiment id or a correct experiment name + project token')
            self._get(with_file=with_file, with_data=with_data, identifier=identifier)
            if tree:
                self._setup_dirs()
                if with_file:
                    for f in self.files:
                        object_name = f["object_name"]
                        name = f["name"]
                        filename = f["object_name"].split('/')[-1]
                        if f["large"]:
                            if name == 'checkpoint-data-latest':  # pragma: no cover
                                self._dl_large_file(object_name, os.path.join(self.checkpoint_dir, filename))
                            elif name == 'model-latest':  # pragma: no cover
                                self._dl_large_file(object_name, os.path.join(self.exported_model_dir, filename))
                            else:
                                self._dl_large_file(object_name, os.path.join(self.base_dir, filename))
                        else:
                            if name == 'config':  # pragma: no cover
                                self._dl_file(object_name, os.path.join(self.config_dir, filename))
                            elif name == 'checkpoint-index-latest':  # pragma: no cover
                                self._dl_file(object_name, os.path.join(self.checkpoint_dir, filename))
                            else:
                                self._dl_file(object_name, os.path.join(self.base_dir, filename))
            else:
                if with_file:
                    self.base_dir = self.experiment_name
                    self._create_dir(self.base_dir)
                    for f in self.files:
                        object_name = f["object_name"]
                        filename = f["object_name"].split('/')[-1]
                        if f["large"]:
                            self._dl_large_file(object_name, os.path.join(self.base_dir, filename))
                        else:
                            self._dl_file(object_name, os.path.join(self.base_dir, filename))
            return self

        @exception_handler
        @beartype
        def publish(self, name: str=None):
            """Publish an Experiment to the server.

            Args:
                name (str, optional): [Name to be publish under]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Picsellia Platform is not responding]
            """
            assert self.id != None, "Please checkout an experiment or enter the desired experiment id"
            data = json.dumps({
                "name": name
            })
            self.requests.post(self.host + 'experiment/{}/publish'.format(self.id), data=data)
            print("Model published")

        @exception_handler
        @beartype
        def launch(self, gpus: int=0):  # pragma: no cover
            """Launch a job on OVH GPUs.

            Args:
                gpus (int, optional): [Number of GPUs to allocate]. Defaults to 0.

            Raises:
                exceptions.NetworkError: [Picsellia is not responding]

            Returns:
                [Json]: {"success": "Experiment launched successfully"}
            """
            assert self.id != None, "Please checkout or create an experiment first"
            data = json.dumps({
                "gpus": gpus,
            })
            self.requests.post(self.host + 'experiment/{}/launch'.format(self.id), data=data)
            print("Job launched successfully")

        @exception_handler
        @beartype
        def list(self, project_token: str=None):
            """List all experiments in your project

            Args:
                project_token (str, optional): [Project ID, find it in your Project page]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responsing]

            Returns:
                [Json]: {
                        'experiments': []ExperimentListSerializer
                    }
            """
            assert project_token != None or self.project_token != None, "Please checkout a project or enter your project token on initialization"
            if self.project_token != None:
                token = self.project_token
            elif project_token != None:
                token = project_token
            r = self.requests.get(self.host + 'experiment/{}'.format(token))
            return r.json()["experiments"]

        @exception_handler
        @beartype
        def _get(self, with_file: bool=False, with_data: bool=False, identifier=None):
            """Get a single experiment by identifier.

            Args:
                with_file (bool, optional): [True if download files]. Defaults to False.
                with_data (bool, optional): [True if download data ]. Defaults to False.
                identifier ([str], optional): [ID or name of the experiment]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [Json]: {
                        "name": str,
                        'id': uuid,
                        'date_created': int,
                        'owner': str,
                        'project': bool,
                        'description': str,
                        'status': str,
                        'logging' : {
                            "logs":dict
                        }
                        ,
                        'files' : [
                                {
                                    "date_created": str,
                                    "last_update": str,
                                    "file_name" :str,
                                    "object_name": str
                                }
                        ]
                        },
                        'data' : [
                                {
                                    "date_created": str,
                                    "last_update": str,
                                    "data_name" :str,
                                    "data": dict
                                }
                        ]
                    }
            """
            if not is_uuid(identifier):
                assert self.project_token != None, "Please checkout a project or enter your project token on initialization"
            data = {
                'with_file': with_file,
                'with_data': with_data
            }
            if is_uuid(identifier):
                r = self.requests.get(self.host + 'experiment/{}/{}'.format(self.project_token, identifier), data)
            else:
                r = self.requests.get(self.host + 'experiment/{}/by_name/{}'.format(self.project_token, identifier), data)

            experiment = r.json()["experiment"]
            self.infos = experiment
            self.name = experiment["name"]
            self.date_created = experiment["date_created"]
            self.dataset = experiment["dataset"]
            self.owner = experiment["owner"]
            self.description = experiment["description"]
            self.files = experiment["files"]
            self.status = experiment["status"]
            self.data = experiment["data"]
            self.id = experiment["id"]
            self.experiment_name = experiment["name"]
            self.project_token = experiment["project"]["project_id"]
            return experiment

        @exception_handler
        @beartype  
        def create(self, name: str=None, project_token: str=None, description: str='', previous: str=None, dataset: str=None,
                   source: str=None, with_file: bool=False, with_data: bool=False):
            """Creates a new experiment

            Args:
                name (str, optional): [Experiment name]. Defaults to None.
                description (str, optional): [Experiment description]. Defaults to ''.
                previous (str, optional): [Previous experiment name, if you want to base the new one on it]. Defaults to None.
                dataset (str, optional): [DatasetName/DatasetVersion to attach]. Defaults to None.
                source (str, optional): [Network to use as source (username/networkName)]. Defaults to None.
                with_file (bool, optional): [True if add files from the previous experiment]. Defaults to False.
                with_data (bool, optional): [True if add datas from the previous experiment]. Defaults to False.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [Client]: self
            """
            assert project_token is not None or self.project_token is not None, "Please specify your project token"
            if self.project_token is None:
                self.project_token = project_token
            data = json.dumps({
                "name": name,
                "description": description,
                "previous": previous,
                "dataset": dataset,
                "source": source,
                "with_file": with_file,
                "with_data": with_data
            })
            r = self.requests.post(self.host + 'experiment/{}'.format(self.project_token), data=data)

            experiment = r.json()
            self.infos = experiment
            self.name = experiment["name"]
            self.date_created = experiment["date_created"]
            self.dataset = experiment["dataset"]
            self.owner = experiment["owner"]
            self.description = experiment["description"]
            self.files = experiment["files"]
            self.status = experiment["status"]
            self.data = experiment["data"]
            self.id = experiment["id"]
            self.experiment_name = experiment["name"]
            self.project_token = experiment["project"]["project_id"]

            print("Experiment {} created".format(name))
            return self

        def update(self, **kwargs):
            """Update the experiment's configuration.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [Json]: ExperimentSerializerNoAssets
            """
            assert self.id != None, "Please checkout an experiment or enter the desired experiment id"
            data = json.dumps(kwargs)
            r = self.requests.patch(self.host + 'experiment/{}/{}'.format(self.project_token, self.id), data=data)
            return r.json()

        def delete(self,):
            """Delete the experiment.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [bool]: True if success
            """
            assert self.id != None, "Please checkout an experiment first"
            r = self.requests.delete(self.host + 'experiment/{}/{}'.format(self.project_token, self.id))

        def delete_all(self,):
            """Delete all experiments

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [bool]: [True if success]
            """
            assert self.project_token != None, "Please checkout a project or enter your project token on initialization"
            r = self.requests.delete(self.host + 'experiment/{}'.format(self.project_token))
        
        def list_files(self,):
            """List all uploaded files in the experiment.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [list]: []{
                            "date_created": str,
                            "last_update": str,
                            "file_name" :str,
                            "object_name": str
                        }
            """
            assert self.id != None, "Please checkout or create an experiment first"

            r = self.requests.get(self.host + 'experiment/{}/file'.format(self.id))
            return r.json()["files"]
        
        def delete_all_files(self,):
            """Delete all uploaded files of the checked out experiment.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [bool]: [True if success]
            """
            assert self.id != None, "Please checkout or create an experiment first"
            r = self.requests.delete(self.host + 'experiment/{}/file'.format(self.id))
        
        @exception_handler
        @beartype
        def _create_file(self, name: str="", object_name: str="", large: bool=False):
            """Creates and upload a file in the experiment.

            Args:
                name (str, optional): [Name of the file]. Defaults to "".
                object_name (str, optional): [Object key for S3 storage]. Defaults to "".
                large (bool, optional): [True if file > 5 Mo]. Defaults to False.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [Json]: FileAssetSerializer
            """
            assert self.id != None , "Please checkout or create an experiment first"

            data = json.dumps({ '0': {
                'name': name,
                'object_name': object_name,
                'large': large
            }
            })
            r = self.requests.put(self.host + 'experiment/{}/file'.format(self.id), data=data)
            return r.json()
        
        @exception_handler
        @beartype
        def get_file(self, name: str=None):
            """Get a file from the experiment.

            Args:
                name (str, optional): [Filename]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [dict]: FileAssetSerializer
            """
            assert self.id != None , "Please checkout or create an experiment first"

            assert name != None, "Please enter a valid file name"
            r = self.requests.get(self.host + 'experiment/{}/file/{}'.format(self.id, name))
            if len(r.json()["file"]) > 0:
                return r.json()["file"][0]
            else:
                return []

        @exception_handler
        @beartype
        def delete_file(self, name: str=None):
            """Delete a file from the experiment.

            Args:
                name (str, optional): [Filename]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [bool]: [True is success]
            """
            assert self.id != None, "Please checkout or create an experiment first"
            assert name != None, "Please enter a valid file name"
            self.requests.delete(self.host + 'experiment/{}/file/{}'.format(self.id, name))
        
        @exception_handler
        @beartype
        def update_file(self, file_name: str=None, **kwargs):
            """Update a file in the experiment.

            Args:
                file_name (str, optional): [Filename]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [dic]: FileAssetSerializer
            """
            assert self.id != None, "Please checkout or create an experiment first"
            assert file_name != None, "Please enter a valid file name"

            data = json.dumps(kwargs)
            r = self.requests.patch(self.host + 'experiment/{}/file/{}'.format(self.id, file_name), data=data)
            return r.json()
        
        def list_data(self,):
            """List all the uploaded data for this experiment.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [list]: []{
                            "date_created": str,
                            "last_update": str,
                            "name" :str,
                            "data": str
                        }
            
            """
            assert self.id != None, "Please checkout or create an experiment first"
            r = self.requests.get(self.host + 'experiment/{}/data'.format(self.id))
            return r.json()["data_assets"]
        
        def delete_all_data(self,):
            """Delete all data from the experiment.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [bool]: [True if success]
            """
            assert self.id != None, "Please checkout or create an experiment first"
            self.requests.delete(self.host + 'experiment/{}/data'.format(self.id))
        
        @exception_handler
        @beartype
        def create_data(self, name: str="", data: Any={}, type: str=None):
            """Create data in a experiment.

            Args:
                name (str, optional): [Name of data]. Defaults to "".
                data (dict, optional): [Data content]. Defaults to {}.
                type (str, optional): [Type of data]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [dict]: JsonAssetSerializer
            """
            assert self.id != None, "Please checkout or create an experiment first"

            data = json.dumps({ '0': {
                'name': name,
                'data': data,
                'type': type
            }
            })
            r = self.requests.put(self.host + 'experiment/{}/data'.format(self.id), data=data)
            return r.json()
        
        @exception_handler
        @beartype
        def get_data(self, name: str=None):
            """Get the data asset of the experiment.

            Args:
                name (str, optional): [name of the data to fetch]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [dict]: JsonAssetSerializer.data
            """

            assert self.id != None, "Please checkout or create an experiment first"
            assert name != None, "Please enter a valid data asset name"
            r = self.requests.get(self.host + 'experiment/{}/data/{}'.format(self.id, name))
            data_name = r.json()["data_asset"]["name"]
            if data_name not in self.logged_data_names:
                self.logged_data_names.append(data_name)
            return r.json()["data_asset"]["data"]

        @exception_handler
        @beartype
        def delete_data(self, name: str=None):
            """Delete data asset for this experiment.

            Args:
                name (str, optional): [Name of data to delete]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [bool]: [True if success]
            """
            assert self.id != None, "Please checkout or create an experiment first"
            assert name != None, "Please enter a valid data asset name"
            self.requests.delete(self.host + 'experiment/{}/data/{}'.format(self.id, name))
        
        @exception_handler
        @beartype
        def update_data(self, name: str=None, **kwargs):
            """Update data asset for this experiment.

            Args:
                name (str, optional): [Data name to update]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [dict]: JsonAssetSerializer.data
            """
            assert self.id != None, "Please checkout or create an experiment first"

            assert name != None, "Please enter a valid data asset name"
            data = json.dumps(kwargs)
            r = self.requests.patch(self.host + 'experiment/{}/data/{}'.format(self.id, name), data=data)
            return r.json()

        @exception_handler
        @beartype
        def append_data(self, name: str=None, **kwargs):
            """Appends value to one data file.

            Args:
                name (str, optional): [Data name]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            """
            assert self.id != None, "Please checkout or create an experiment first"

            assert name != None, "Please enter a valid data asset name"
            data = json.dumps(kwargs)
            r = self.requests.post(self.host + 'experiment/{}/data/{}'.format(self.id, name), data=data)
            return r.json()

        @exception_handler
        @beartype
        def _send_large_file(self, path: str=None, name: str=None, object_name: str=None, network_id=None):
            """Uploads a large file to the experiment.

            Args:
                path (str, optional): [Path to the file to upload]. Defaults to None.
                name (str, optional): [Name of the file]. Defaults to None.
                object_name (str, optional): [Key name for S3 storage]. Defaults to None.
                network_id (str, optional): [ID of the network to attach file]. Defaults to None.
            """
            error_message = "Please checkout or create an experiment/network or enter the desired experiment id/network_id"
            assert self.id != None or network_id != None, error_message

            self.urls._init_multipart(object_name)
            parts = self.urls._upload_part(path, object_name)

            if self.urls._complete_part_upload(parts, object_name, None):
                self._create_or_update_file(name, path, object_name=object_name, large=True)

        @exception_handler
        @beartype
        def _send_file(self, path: str=None, name: str=None, object_name: str=None, network_id=None):
            """Uploads a small file to the experiment.

            Args:
                path (str, optional): [Path to the file to upload]. Defaults to None.
                name (str, optional): [Name of the file]. Defaults to None.
                object_name (str, optional): [Key name for S3 storage]. Defaults to None.
                network_id (str, optional): [ID of the network to attach file]. Defaults to None.
            """
            error_message = "Please checkout an experiment/network or enter the desired experiment id/network_id"
            assert self.id != None or network_id != None, error_message

            response = self.urls._get_presigned_url(method='post', object_name=object_name, bucket_model=True)
            try:
                with open(path, 'rb') as f:
                    files = {'file': (path, f)}
                    http_response = requests.post(response['url'], data=response['fields'], files=files)
                if http_response.status_code == 204:
                    self._create_or_update_file(name, path, object_name=object_name, large=False)
            except Exception as e:  # pragma: no cover
                raise exceptions.NetworkError(str(e))

        @exception_handler
        @beartype
        def log(self, name: str="", data: Any={}, type: str=None, replace: bool=False):
            """Logs values to the experiment.

            Args:
                name (str, optional): [Value name]. Defaults to "".
                data (dict, optional): [Data to log]. Defaults to {}.
                type (str, optional): [Type to display (line, bar, etc.)]. Defaults to None.
                replace (bool, optional): [True if you want to replace old value]. Defaults to False.

            Raises:
                Exception: [Impossible to log image]
            """
            assert self.id != None, "Please checkout or create an experiment first"
            try:
                if name not in self.logged_data_names:
                    stored = self.get_data(name)
                else:
                    stored = self.logged_data_names
            except Exception:
                stored = []
            if type == 'value':
                data = {'value': data}
            if type == 'image':
                object_name = os.path.join(self.id, data)
                response = self.urls._get_presigned_url(method='post', object_name=object_name, bucket_model=True)
                with open(data, 'rb') as f:
                    files = {'file': (data, f)}
                    http_response = requests.post(response['url'], data=response['fields'], files=files)
                    if http_response.status_code == 204:
                        data = {'object_name': object_name}
                    else:  # pragma: no cover
                        raise Exception("Impossible to log image, can't upload file, please contact us.")
            if stored == []:
                assert type != None, "Please specify a type for your data vizualization, check the docs to see all available types"
                self.create_data(name, data=data, type=type)
            elif stored is not [] and replace:
                self.update_data(name, data=data, type=type)
            elif stored is not [] and not replace and type is 'line':
                threading.Thread(target=self.append_data, kwargs={'name':name, 'data': data, 'type': type}).start()
            elif stored is not [] and not replace and type is not 'line':
                self.update_data(name, data=data, type=type)
        
        @exception_handler
        @beartype
        def _create_or_update_file(self, file_name: str="", path: str="", **kwargs):
            """Create or update a file in the experiment.

            Args:
                file_name (str, optional): [Filename]. Defaults to "".
                path (str, optional): [Path of file to upload]. Defaults to "".
            """
            assert self.id != None, "Please checkout or create an experiment first"
            stored = self.get_file(file_name)
            if stored == []:
                self._create_file(file_name, kwargs["object_name"], kwargs["large"])
            else:
                self.update_file(file_name=file_name, **kwargs)

        @exception_handler
        @beartype
        def store(self, name: str="", path: str=None, zip: bool=False):
            """Store files to Picsellia.

            Args:
                name (str, optional): [namespace ]. Defaults to "".
                path (str, optional): [path of file to upload]. Defaults to None.
                zip (bool, optional): [True if zip files]. Defaults to False.

            Raises:
                FileNotFoundError: [File does not exist]
                exceptions.ResourceNotFoundError: [Resource does not exist]

            Returns:
                [str]: [object s3 key]
            """
            assert self.id != None, "Please checkout or create an experiment first"

            if path != None:
                if zip:
                    path = utils.zipdir(path)
                filesize = Path(path).stat().st_size
                if filesize < 5*1024*1024:
                    filename = path.split('/')[-1]
                    if name == 'model-latest':  # pragma: no cover
                        object_name = os.path.join(self.id, '0', filename)
                    else:
                        object_name = os.path.join(self.id, filename)
                    self._send_file(path, name, object_name, None)
                else:
                    filename = path.split('/')[-1]
                    if name == 'model-latest':  # pragma: no cover
                        object_name = os.path.join(self.id, '0', filename)
                    else:
                        object_name = os.path.join(self.id, filename)
                    self._send_large_file(path, name, object_name, None)
            else:  # pragma: no cover
                if name == 'config':
                    if not os.path.isfile(os.path.join(self.config_dir, "pipeline.config")):
                        raise FileNotFoundError("No config file found")
                    path = os.path.join(self.config_dir, "pipeline.config")
                    object_name = os.path.join(self.id, "pipeline.config")
                    self._send_file(path, name, object_name, None)
                elif name == 'checkpoint-data-latest':
                    file_list = os.listdir(self.checkpoint_dir)
                    ckpt_id = max([int(p.split('-')[1].split('.')[0]) for p in file_list if 'index' in p])
                    ckpt_data_file = None
                    for f in file_list:
                        if "{}.data".format(ckpt_id) in f:
                            ckpt_data_file = f
                    if ckpt_data_file is None:
                        raise exceptions.ResourceNotFoundError("Could not find matching data file with index")
                    path = os.path.join(self.checkpoint_dir, ckpt_data_file)
                    object_name = os.path.join(self.id, ckpt_data_file)
                    self._send_large_file(path, name, object_name, None)
                elif name == 'checkpoint-index-latest':
                    file_list = os.listdir(self.checkpoint_dir)
                    ckpt_id = max([int(p.split('-')[1].split('.')[0]) for p in file_list if 'index' in p])
                    ckpt_index = "ckpt-{}.index".format(ckpt_id)
                    path = os.path.join(self.checkpoint_dir, ckpt_index)
                    object_name = os.path.join(self.id, ckpt_index)
                    self._send_file(path, name, object_name, None)
                elif name == 'model-latest':  # pragma: no cover
                    file_path = os.path.join(self.exported_model_dir, 'saved_model')
                    path = utils.zipdir(file_path)
                    object_name = os.path.join(self.id, '0', 'saved_model.zip')
                    self._send_large_file(path, name, object_name, None)
            return object_name

        @exception_handler
        @beartype
        def download(self, name: str, path: str='', large: bool=None):
            """Download file to specific path.

            Args:
                name (str): [File's name to download]
                path (str, optional): [Path to download file]. Defaults to ''.
                large (bool, optional): [True if large file]. Defaults to None.
            """
            assert self.id != None, "Please checkout or create an experiment first"
            f = self.get_file(name)
            if f == []:
                print("No file found with name {}".format(name))
            else:
                object_name = f["object_name"]
                if large == None:
                    large = f["large"]
                if large:
                    self._dl_large_file(object_name, os.path.join(path, object_name.split('/')[-1]))
                else:
                    self._dl_file(object_name, os.path.join(path, object_name.split('/')[-1]))
                print('{} downloaded successfully'.format(object_name.split('/')[-1]))

        @exception_handler
        @beartype 
        def _dl_large_file(self, object_name: str, path: str):
            """Downloads a large file from the server.

            Args:
                object_name (str): [Object s3 Key name to download]
                path (str): [Direction to download it]
            """
            url = self.urls._get_presigned_url('get', object_name, bucket_model=True)
            with open(path, 'wb') as handler:
                filename = url.split('/')[-1]
                print("Downloading {}".format(filename))
                print('-----')
                response = requests.get(url, stream=True)
                total_length = response.headers.get('content-length')
                if total_length is None:  # pragma: no cover
                    print("Couldn't download {} file".format(filename.split('?')[0]))
                else:
                    dl = 0
                    count = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=4096):
                        dl += len(data)
                        handler.write(data)
                        done = int(50 * dl / total_length)
                        if self.interactive:
                            sys.stdout.write(f"\r{'=' * done}{' ' * (50 - done)}]")
                            sys.stdout.flush()
                        else:  # pragma: no cover
                            if count%500==0:
                                print('['+'='* done+' ' * (50 - done)+']')
                        count += 1
            print('--*--')
        
        @exception_handler
        @beartype
        def _dl_file(self, object_name: str, path: str):
            """Download a file from S3.

            Args:
                object_name (str): [Object s3 Key name to download]
                path (str): [Direction to download it]
            """
            url = self.urls._get_presigned_url('get', object_name, bucket_model=True)
            with open(path, 'wb') as handler:
                filename = url.split('/')[-1]
                response = requests.get(url, stream=True)
                total_length = response.headers.get('content-length')
                if total_length is None:  # pragma: no cover
                    print("Couldn't download {} file".format(filename))
                else:
                    print("Downloading {}".format(filename.split('?')[0]))
                    for data in response.iter_content(chunk_size=1024):
                        handler.write(data)
        
        def _setup_dirs(self):
            """Create the directories for the project.
            """
            self.base_dir = self.experiment_name
            self.metrics_dir = os.path.join(self.base_dir, 'metrics')
            self.png_dir = os.path.join(self.base_dir, 'images')
            self.checkpoint_dir = os.path.join(self.base_dir, 'checkpoint')
            self.record_dir = os.path.join(self.base_dir, 'records')
            self.config_dir = os.path.join(self.base_dir, 'config')
            self.results_dir = os.path.join(self.base_dir, 'results')
            self.exported_model_dir = os.path.join(self.base_dir, 'exported_model')

            if not os.path.isdir(self.experiment_name):
                print("No directory for this project has been found, creating directory and sub-directories...")
                os.mkdir(self.experiment_name)

            self._create_dir(self.base_dir)
            self._create_dir(self.png_dir)
            self._create_dir(self.checkpoint_dir)
            self._create_dir(self.metrics_dir)
            self._create_dir(self.record_dir)
            self._create_dir(self.config_dir)
            self._create_dir(self.results_dir)
            self._create_dir(self.exported_model_dir)

        @exception_handler
        @beartype
        def _upload_simple_file(self, prefix: str, path: str):
            """Upload a single file to the server .

            Args:
                prefix (str): [Bucket prefix s3]
                path (str): [Absolute path to the file]

            Raises:
                FileNotFoundError: [File does not exists]
                exceptions.NetworkError: [Platform does not respond]

            Returns:
                [tuple]: ([filename], [s3 object key])
            """
            if not os.path.isfile(path):
                raise FileNotFoundError("{} not found".format(path))
            else:
                filesize = Path(path).stat().st_size
                filename = path.split('/')[-1]
                object_name = os.path.join(prefix, filename)
                if filesize < 5*1024*1024:
                    response = self.urls._get_presigned_url(method='post', object_name=object_name, bucket_model=True)
                    try:
                        with open(path, 'rb') as f:
                            files = {'file': (path, f)}
                            http_response = requests.post(response['url'], data=response['fields'], files=files)
                        if not http_response.status_code == 204:  # pragma: no cover
                            raise exceptions.NetworkError("Can't upload {}, please contact support".format(filename))
                    except Exception as e:  # pragma: no cover
                        raise exceptions.NetworkError(str(e))
                else:
                    self.urls._init_multipart(object_name)
                    parts = self.urls._upload_part(path, object_name)
                    if not self.urls._complete_part_upload(parts, object_name, None):  # pragma: no cover
                        raise exceptions.NetworkError("Can't upload {}, please contact support".format(filename))
            return filename, object_name

        @exception_handler
        @beartype
        def _create_dir(self, dir_name: str):
            """Create a directory if it doesn t exist.

            Args:
                dir_name (str): [directory name]
            """
            if not os.path.isdir(dir_name):
                os.mkdir(dir_name)

        @exception_handler
        @beartype
        def dl_annotations(self, option: str="all"):
            """ Download all the annotations made on Picsell.ia Platform for your project.
            Called when checking out a network
            Args:
                option (str): Define what type of annotation to export (accepted or all)

            Returns:
                [dict]: Annotation Dictionnary
            Raises:
                NetworkError: If Picsell.ia server is not responding or host is incorrect.
                ResourceNotFoundError: If we can't find any annotations for that project.
            """

            print("Downloading annotations ...")
            assert self.id != None, "self.id"
            r = self.requests.get(self.host + 'experiment/{}/dl_annotations/{}'.format(self.id, option))
            self.dict_annotations = r.json()
            if len(self.dict_annotations.keys()) == 0:  # pragma: no cover
                raise exceptions.ResourceNotFoundError("You don't have any annotations")
            return self.dict_annotations 

        def dl_pictures(self):
            """Download your training set on the machine (Use it to dl images to Google Colab etc.)
            Save it to /project_id/images/*

            Raises:
                ResourceNotFoundError : If no annotations in the Picsell.ia Client yet or images can't be downloaded"""

            if "images" not in self.dict_annotations.keys():
                raise exceptions.ResourceNotFoundError("Please run dl_annotations function first")

            print("Downloading images ...")

            if not os.path.isdir(self.png_dir):
                os.makedirs(self.png_dir)

            lst = []
            for info in self.dict_annotations["images"]:
                lst.append(info["external_picture_url"])
            t = len(set(lst))
            print('-----')
            nb_threads = 20
            infos_split = list(mlt.chunks(self.dict_annotations["images"], nb_threads))
            counter = Value('i', 0)
            p = Pool(nb_threads, initializer=mlt.pool_init, 
                initargs=(t, self.png_dir, counter,self.interactive,))
            p.map(mlt.dl_list, infos_split)
            print('--*--')
            print("Images downloaded")

        def generate_labelmap(self):
            """
            Generate the labelmap.pbtxt file needed for Tensorflow training at:
                - project_id/
                    label_map.pbtxt
            Raises:
                ResourceNotFoundError : If no annotations in the Picsell.ia Client yet or images can't be downloaded
                                        If no directories have been created first."""

            print("Generating labelmap ...")
            self.label_path = os.path.join(self.base_dir, "label_map.pbtxt")

            if "categories" not in self.dict_annotations.keys():
                raise exceptions.ResourceNotFoundError("Please run dl_annotations() first")

            categories = self.dict_annotations["categories"]
            labels_Network = {}
            try:
                with open(self.label_path, "w+") as labelmap_file:
                    for k, category in enumerate(categories):
                        name = category["name"]
                        labelmap_file.write("item {\n\tname: \"" + name + "\"" + "\n\tid: " + str(k + 1) + "\n}\n")
                        labels_Network[str(k + 1)] = name
                    labelmap_file.close()
                print("Label_map.pbtxt created @ {}".format(self.label_path))

            except Exception:  # pragma: no cover
                raise exceptions.ResourceNotFoundError("No directory found, please call checkout_network() or create_network() function first")

            self.label_map = labels_Network

        @exception_handler
        @beartype
        def train_test_split(self, prop: float=0.8):
            """Split the dataset into training and test sets and send the repartition to Picsellia.

            Args:
                prop (float, optional): [train test split proportion]. Defaults to 0.8.

            Raises:
                exceptions.ResourceNotFoundError: [No annotations downloaded yet]
            """
            if "images" not in self.dict_annotations.keys():
                raise exceptions.ResourceNotFoundError("Please download annotations first")

            self.train_list = []
            self.eval_list = []
            self.train_list_id = []
            self.eval_list_id = []
            self.index_url = utils.train_valid_split_obj_simple(self.dict_annotations, prop)

            total_length = len(self.dict_annotations["images"])
            for info, idx in zip(self.dict_annotations["images"], self.index_url):
                pic_name = os.path.join(self.png_dir, info['external_picture_url'])
                if idx == 1:
                    self.train_list.append(pic_name)
                    self.train_list_id.append(info["internal_picture_id"])
                else:
                    self.eval_list.append(pic_name)
                    self.eval_list_id.append(info["internal_picture_id"])

            print("{} images used for training and {} images used for validation".format(len(self.train_list_id), len(self.eval_list_id)))

            label_train, label_test, cate = utils.get_labels_repartition_obj_detection(self.dict_annotations, self.index_url)
            self.train_repartition = label_train
            self.test_repartition = label_test
            self.categories = cate
        
        @exception_handler
        @beartype
        def init_scan(self, name: str, config: dict, nb_worker: int=1):
            """Init a new scan.

            Args:
                name (str): [Scan's name]
                config (dict): [config dictionnary] -> See full documentation https://docs.picsellia.com/experiments/hyperparameter-tuning/config
                nb_worker (int, optional): [Number of worker to instantiate (if running remote)]. Defaults to 1.

            Raises:
                exceptions.InvalidQueryError: [Bad config format]
                exceptions.NetworkError: [Platform does not respond]

            Returns:
                [Json]: {'success': 'Scan started'}
            """
            assert self.project_token != None, "Please create or checkout experiment first."

            if "script" in config.keys():
                path = config["script"]
                filename, object_name = self._upload_simple_file(self.project_token, path)
            else:
                object_name = None
                filename = None
            
            if "requirements" in config.keys():
                requirements = config["requirements"]
                if isinstance(requirements, str):
                    j = self._generate_requirements_json(requirements)
                    config["requirements"] = j["requirements"]
                
                elif isinstance(requirements, list):
                    for e in requirements:
                        assert isinstance(e, dict), "Requirements must be a list of dict"
                        assert "package" in e.keys(), "The dictionnaries must contain the key package"
                        assert "version" in e.keys(), "The dictionnaries must contain the key version"

                else:
                    raise exceptions.InvalidQueryError("Please remove the key requirements from config dict if you don't want to specify any requirements")
            if "data" in config.keys():
                data_list = config["data"]
                files = []
                assert isinstance(data_list, list), "data must be a list of filenames"
                
                for path in data_list:
                    flnm, objnm = self._upload_simple_file(self.project_token, path)
                    files.append({"filename": flnm, "object_name": objnm})
                
            else:
                files = None
            if files is not None:
                config["data"] = files
            data = json.dumps({
                "name": name,
                "config": config,
                "nb_worker": nb_worker,
                "object_name": object_name,
                "filename": filename,
            })
            r = self.requests.post(self.host + 'scan/{}/launch'.format(self.project_token), data=data)
            return r.json()

        @exception_handler
        @beartype
        def get_next_run(self, name: str):
            """Get the next run.

            Args:
                name (str): [Name of the scan]

            Raises:
                exceptions.NetworkError: [Platform does not respond]

            Returns:
                [dict]: RunSerializer
            """
            assert self.project_token != None, "Please create or checkout experiment first."
            r = self.requests.get(self.host + 'run/{}/{}'.format(self.project_token, name))
            self.run = r.json()
            return r.json()

        @exception_handler
        @beartype
        def get_run(self, id:str):
            """Get run by id.

            Args:
                name (str): [Name of the scan]

            Raises:
                exceptions.NetworkError: [Platform does not respond]

            Returns:
                [dict]: RunSerializer
            """
            r = self.requests.get(self.host + 'run/{}'.format(id))
            self.run = r.json()["run"]
            return r.json()["run"]

        @exception_handler
        @beartype
        def update_run(self, **kwargs):
            """Update the Run object with the given keyword arguments.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [dict]: RunSerializer
            """
            assert self.run['id'] != None, "Please get a run first."
            data = json.dumps(kwargs)
            r = self.requests.patch(self.host + 'run/{}'.format(self.run['id']), data=data)
            self.run = r.json()
            return r.json()

        def end_run(self,):
            """End a run.

            Raises:
                exceptions.NetworkError: [Platform is not responding]
                exceptions.AuthenticationError: [Run does not belong to your project]

            Returns:
                [bool]: [True if success]
            """
            assert self.run['id'] != None, "Please get a run first."
            self.requests.post(self.host + 'run/{}/end'.format(self.run['id']))
            return True

        def download_script(self,):
            """Locally download the script from the run.

            Returns:
                [str]: Filename
            """
            assert self.run['id'] != None, "Please get a run first."
            if "script" in self.run.keys():
                filename = self.run["script"]
                object_name = self.run["script_object_name"]
                try:
                    self._dl_file(object_name, filename)
                except Exception:  # pragma: no cover
                    self._dl_large_file(object_name, filename)
                return filename

        def download_run_data(self,):
            """Download run data from the run.

            Returns:
                [str]: Filename
            """
            assert self.run['id'] != None, "Please get a run first."
            if "data" in self.run["config"].keys():
                data_list = self.run["config"]["data"]
                filename = ""
                for data in data_list:
                    filename = data["filename"]
                    object_name = data["object_name"]
                    try:
                        self._dl_file(object_name, filename)
                    except Exception:  # pragma: no cover
                        self._dl_large_file(object_name, filename)
                return filename

        @exception_handler
        @beartype
        def _generate_requirements_json(self, requirements_path: str):
            """Generate a json file with the requirements from the requirements.txt file

            Args:
                requirements_path ([str]): [absolute path to requirements.txt file]

            Raises:
                exceptions.ResourceNotFoundError: [Filepath does match]
                Exception: [Wrong requirements file]

            Returns:
                [dict]: {
                    'requirements': []{
                        'package': (str) package name,
                        'version': (str) package version
                    }
                }
            """
            js = {"requirements": []}
            try:
                with open(requirements_path, 'r') as f:
                    lines = f.readlines()
            except:
                raise exceptions.ResourceNotFoundError("{} does not exists".format(requirements_path))
            try:
                for line in lines:
                    if line[0] != "#":
                        try:
                            package, version = line.split("==")
                        except:
                            package, version = line, ""
                        tmp = {
                            "package": package.rstrip(),
                            "version": version.rstrip()
                        }
                        js["requirements"].append(tmp)
            except:  # pragma: no cover
                raise Exception("Malformed requirements file")
            return js

        def install_run_requirements(self,):
            """Install requirements from the run requirements dictionnary.
            """
            assert self.run['id'] != None, "Please get a run first."
            req = self.run["requirements"]
            for module in req:
                name = "{}=={}".format(module["package"], module["version"]) if module["version"] != "" else module["package"]
                subprocess.call(['pip', 'install', name])
        

    class Datalake:

        def __init__(self, api_token: str=None, organization: str=None, host: str="https://app.picsellia.com/sdk/v2/", ping: bool=False):
            """Initialize the Datalake class.

            Args:
                api_token (str, optional): [API token, find it in your profile page]. Defaults to None.
                organization (str, optional): [Organization id, if None default to your organization]. Defaults to None.
                host (str, optional): [Host to connect]. Defaults to "https://app.picsellia.com/sdk/v2/".
                ping (bool, optional): [True to ping the platform]. Defaults to False.

            Raises:
                Exception: [No API token found]
                exceptions.NetworkError: [Platform not responding]
            """
            self.host = host
            self.fetched_pictures = []
            if not ping:
                if api_token == None:
                    if "PICSELLIA_TOKEN" in os.environ:
                        api_token = os.environ["PICSELLIA_TOKEN"]
                    else:
                        raise Exception("Please set up the PICSELLIA_TOKEN environement variable or specify your token")
                self.auth = {"Authorization": "Token " + api_token}
                self.requests = pxl_requests(self.auth)
                r = self.requests.get(self.host + 'ping')
                self.sdk_version = r.json()["sdk_version"]
                if self.sdk_version != picsellia.__version__:  # pragma: no cover
                    print("{}You are using an outdated version of the picsellia package ({})\nPlease consider upgrading to {} with pip install picsellia --upgrade{}".format('\033[91m', picsellia.__version__, self.sdk_version, '\033[0m'))
            else:
                self.auth = {"Authorization": "Token " + api_token}
                self.requests = pxl_requests(self.auth)
            data = {
                'organization': organization
            }
            r = self.requests.post(self.host + 'get_organization', data=json.dumps(data))
            self.organization_id = r.json()["organization_id"]
            self.organization_name = r.json()["organization_name"]
            self.picture = self.Picture(api_token=api_token, host=self.host, organization_id=self.organization_id)
            self.dataset = self.Dataset(api_token=api_token, host=self.host, organization_id=self.organization_id)


        def upload(self, name: str=None, version: Optional[str]=None,
                             imgdir: str=None, ann_path: str=None, 
                                ann_format: str=None, tags: Optional[list]=[],
                                    nb_jobs: Optional[int]=5, rectangle: Optional[bool]=False):

            assert name is not None, "Please provide a name for your dataset." 
            if ann_path is not None:
                if not (os.path.isdir(ann_path) or os.path.isfile(ann_path)):
                    raise exceptions.InvalidQueryError('Please provide a valid `ann_path`')
                if ann_format is None:
                    raise exceptions.InvalidQueryError('Please provide an ann_format')
            if imgdir is not None:
                if not os.path.isdir(imgdir):
                    raise exceptions.ResourceNotFoundError('Please provide a valid `imgdir`')

            if tags is None:
                tags = [str(datetime.date.today())]

            if imgdir is None:
                assert name is not None, "You did not provided an imgdir, please provide a `name`"
                self.dataset.fetch(
                    name=name,
                    version=version
                )
                dataset_id = self.dataset.dataset_id

            print("Uploading Images to your Picsellia's Datalake\n")

            if imgdir is not None:
                img_paths = [os.path.join(imgdir, e) for e in os.listdir(imgdir)]
                nb_threads = 20 if nb_jobs == -1 else nb_jobs
                pool = Pool(nb_threads)
                upload = partial(self.picture.upload, tags=tags, source='sdk')
                for _ in tqdm.tqdm(pool.imap_unordered(upload, img_paths), total=len(img_paths)):
                    pass
                print("Migrating these pictures to dataset: {}\n".format(name)) 
                pictures = self.picture.fetch(
                    tags=tags
                )
                dataset = self.dataset.create(
                    name=name, pictures=pictures
                )
                dataset_id = dataset.dataset_id
            print("\nScanning categories ...\n")

            if ann_path is not None:
                if ann_format == "COCO":
                    parser = COCOParser(path=ann_path)
                    dataset_type = parser.find_dataset_type() if not rectangle else "detection"
                    ann_type = "rectangle" if dataset_type == "detection" else "polygon"
                    for label in parser.categories:
                        self.dataset.create_labels(
                            name=label['name'],
                            ann_type=ann_type,
                            verbose=False
                        )

                    print("Uploading annotations ...\n")

                    annotations_list, repartition, nb_annotations, nb_objects = parser.generate_annotations(rectangle=rectangle)
                    nb_threads = 20 if nb_jobs == -1 else nb_jobs
                    pool = Pool(nb_threads)

                    f = partial(self._upload_annotation, True, dataset_id)

                    # pool.map(f, annotations_list)

                    for _ in tqdm.tqdm(pool.imap_unordered(f, annotations_list), total=len(annotations_list)):
                        pass
                    self._update_dataset_stats(dataset_id=dataset_id, repartition=repartition,
                                 nb_annotations=nb_annotations, nb_objects=nb_objects)
                    print("Dataset Uploaded to Picsellia, you can check it on the platform.")

                if ann_format == "PASCAL-VOC":
                    parser = PVOCParser(path=ann_path)
                    # TODO -> Handle segmentation cases. 
                    classes, image_infos, ann_data, repartition, nb_annotations, nb_objects = parser._generate_images_labels_annotations(tags=tags)
                    classes = list(set(classes))

                    for label in classes:
                        self.dataset.create_labels(
                            name=label[0],
                            ann_type="rectangle",
                            verbose=False
                        )
                    nb_threads = 20 if nb_jobs == -1 else nb_jobs
                    pool = Pool(nb_threads)

                    f = partial(self._upload_annotation, True, dataset_id)

                    for _ in tqdm.tqdm(pool.imap_unordered(f, ann_data), total=len(ann_data)):
                        pass
                    # pool.map(f, ann_data)

                    self._update_dataset_stats(dataset_id=dataset_id, repartition=repartition,
                                 nb_annotations=nb_annotations, nb_objects=nb_objects)
                    print("Dataset Uploaded to Picsellia, you can check it on the platform.")
                if ann_format == "PICSELLIA":
                    with open(ann_path, 'rb') as f:
                        dict_annotations = json.load(f)
                    label_to_create = []

                    repartition = collections.Counter()
                    nb_annotations = 0 
                    nb_objects = 0 


                    for annotations in dict_annotations["annotations"]:
                        nb_annotations += 1
                        tmpp = []
                        for ann in annotations["annotations"]:
                            tmpp.append(ann["label"])
                            nb_objects += 1
                            tmp = [ann["type"], ann["label"]]
                            if tmp not in label_to_create:
                                label_to_create.append(tmp)
                        repartition.update(tmpp)
                    for l in label_to_create:
                        self.dataset.create_labels(
                            ann_type=l[0],
                            name=l[1],
                            verbose=False
                        )

                    nb_threads = 20 if nb_jobs == -1 else nb_jobs
                    pool = Pool(nb_threads)
                    upload = partial(
                        self.dataset.add_annotation_legacy, 
                        dataset_id=dataset_id,
                        new_picture=True
                    )
                    list_annotations = list(mlt.chunks(dict_annotations["annotations"], nb_threads))
                    # p2.map(upload, list_annotations)
                    
                    for _ in tqdm.tqdm(pool.imap_unordered(upload, list_annotations), total=len(list_annotations)):
                        pass
                    
                    self._update_dataset_stats(dataset_id=dataset_id, repartition=repartition,
                                 nb_annotations=nb_annotations, nb_objects=nb_objects)
                    print("Dataset Uploaded to Picsellia, you can check it on the platform.")

                    


        def _update_dataset_stats(self, dataset_id: str=None, repartition: dict=None, 
                                        nb_annotations: int=None, nb_objects: int=None):
            r = pxl_requests(self.auth)
            data = {
                'repartition': repartition,
                'nb_annotations': nb_annotations,
                'nb_objects': nb_objects
            }
            rep = r.post(url=self.host + "dataset/{}/update_stats".format(dataset_id),
                        data=json.dumps(data), verbose=False)
            
            return
        def _upload_annotation(self, new_picture: bool=False, dataset_id: str=None, data: tuple=None):  # pragma: no cover
            """Add an annotation to a picture.

            Args:
                picture_id (str, optional): [id of the picture]. Defaults to None.
                new_picture (bool, optional): [True if you want to duplicate the picture]. Defaults to False.
                dataset_id (str, optional): [id of the dataset to attach the picture]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [dict]: {'message': 'annotation saved'}
            """
            try:
                if dataset_id is not None:
                    self.dataset_id = dataset_id
                try:
                    if not new_picture:
                        r = requests.put(self.host + 'annotation/' + self.dataset_id + '/' + data[0], data=json.dumps(data[1]), headers=self.auth)
                    else:
                        r = requests.put(self.host + 'annotation/new/' + self.dataset_id + '/' + data[0], data=json.dumps(data[1]), headers=self.auth)
                except Exception as e:
                    print(e)  # pragma: no cover
                    raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
                
                check_status_code(r)
                return 
            except Exception as e:
                print(e)
                return

        class Picture:

            def __init__(self, api_token: str=None, organization: str=None, host: str="https://app.picsellia.com/sdk/v2/", organization_id: str=None):
                """Initialize the Picture class with the API.

                Args:
                    api_token (str, optional): [API Token, find it in Profile page]. Defaults to None.
                    organization (str, optional): [description]. Defaults to None.
                    host (str, optional): [description]. Defaults to "https://app.picsellia.com/sdk/v2/".
                    organization_id (str, optional): [organization id, if none it's your organization]. Defaults to None.

                Raises:
                    Exception: [No Picsellia Token]
                    exceptions.NetworkError: [Server is not responding]
                """
                self.host = host
                if organization_id is None:
                    if api_token == None:
                        if "PICSELLIA_TOKEN" in os.environ:
                            api_token = os.environ["PICSELLIA_TOKEN"]
                        else:
                            raise Exception("Please set up the PICSELLIA_TOKEN environement variable or specify your token")
                    self.auth = {"Authorization": "Token " + api_token}
                    self.requests = pxl_requests(self.auth)
                    r = self.requests.get(self.host + 'ping')
                    self.sdk_version = r.json()["sdk_version"]
                    if self.sdk_version != picsellia.__version__:  # pragma: no cover
                        print("{}You are using an outdated version of the picsellia package ({})\nPlease consider upgrading to {} with pip install picsellia --upgrade{}".format('\033[91m', picsellia.__version__, self.sdk_version, '\033[0m'))
                    data = {
                        'organization': organization
                    }
                    r = self.requests.post(self.host + 'get_organization', data=json.dumps(data))
                    self.organization_id = r.json()["organization_id"]
                else:
                    self.organization_id = organization_id
                    self.auth = {"Authorization": "Token " + api_token}
                    self.requests = pxl_requests(self.auth)
                self.fetched_pictures = []

            def __str__(self) -> str:
                if self.fetched_pictures == []:
                    return "No assets selected"
                else:
                    return "Number of Assets selected : {} \n".format(len(self.fetched_pictures))

            def status(self):
                """Print number of fetched assets.
                """

                if self.fetched_pictures == []:
                    print("No assets selected")
                else:
                    print("Number of Assets selected : {} \n".format(len(self.fetched_pictures)))

            def list(self):
                """[summary]
                List all the pictures of your organization

                Raises:
                    exceptions.NetworkError: [Server Not responding]
                    exceptions.AuthenticationError: [Token Invalid]

                Returns:
                    [dict]: PictureSerializerDatalake
                """
                r = self.requests.get(self.host + 'datalake/{}'.format(self.organization_id))
                self.fetched_pictures = r.json()['pictures']
                return r.json()

            @exception_handler
            @beartype
            def fetch(self, quantity: int=1, tags: List=[]):
                """Search and Fetch a list of pictures for the given tags.

                Args:
                    quantity (float): [Proportion of images to fetch]. Defaults to None.
                    tags (list): [List of tags to look for]

                Raises:
                    exceptions.NetworkError: [description]

                Returns:
                    [list]: PictureSerializerDatalake 
                """
                data = {
                    'tags': tags,
                    'quantity': quantity
                }

                r = self.requests.post(self.host + 'datalake/search/{}'.format(self.organization_id), data=json.dumps(data))
                self.fetched_pictures = r.json()['pictures']

                if len(self.fetched_pictures) < 1:
                    print("No assets found for tags {}".format(tags))
                return self.fetched_pictures

            @exception_handler
            @beartype
            def delete(self, pictures: List=None):
                """Delete assets from the Datalake.

                Args:
                    pictures (list, optional): [List of picture's id to delete]. Defaults to None.

                Raises:
                    exceptions.NetworkError: [Platform is not responding]

                """
                if pictures is None:
                    pictures= self.fetched_pictures

                if len(pictures) < 1:
                    print("No assets selected, please run Client.Datalake.Pictures.Fetch() first")
                    return 
                else:
                    data = {
                        'to_delete': pictures
                    }
                    r = self.requests.post(self.host + 'datalake/delete/{}'.format(self.organization_id), data=json.dumps(data))

                    print(len(pictures), "assets deleted from Lake")
                    return self

            @exception_handler
            @beartype
            def add_tags(self,pictures: List=None, tags: List=[]):
                """Add tags to the given pictures.

                Args:
                    pictures (list, optional): [list of picture's id to tag]. Defaults to None.
                    tags (list, optional): [list of tag to add]. Defaults to [].

                Raises:
                    exceptions.NetworkError: [Platform is not responding]

                Returns:
                    [type]: [self]
                """
                if pictures is None:
                    pictures= self.fetched_pictures

                if len(pictures) < 1:
                    print("No assets selected, please run Client.Datalake.Pictures.Fetch() first")
                    return 
                elif len(tags) < 1:
                    print("You can't use picture.tag() with an empty tags list")
                    return
                else:
                    data = {
                        'tags': tags,
                        'to_tag': pictures
                    }
                    r = self.requests.post(self.host + 'datalake/tag/{}'.format(self.organization_id), data=json.dumps(data))
                    print(len(tags), " tags added to {} assets ".format(len(pictures)))
                    return self

            @exception_handler
            @beartype
            def remove_tags(self,pictures: List=None, tags: List=[]):
                """Remove tags to the given pictures.

                Args:
                    pictures (list, optional): [list of picture's id to untag]. Defaults to None.
                    tags (list, optional): [list of tag to remove]. Defaults to [].

                Raises:
                    exceptions.NetworkError: [Platform is not responding]

                Returns:
                    [type]: [self]
                """
                if pictures is None:
                    pictures= self.fetched_pictures

                if len(pictures) < 1:
                    print("No assets selected, please run Client.datalake.pictures.fetch() first")
                    return 
                elif len(tags) < 1:
                    print("You can't use picture.remove_tags() with an empty tags list")
                    return
                else:
                    data = {
                        'tags': tags,
                        'to_delete_tag': pictures
                    }
                    r = self.requests.post(self.host + 'datalake/delete_tag/{}'.format(self.organization_id), data=json.dumps(data))
                    print(len(tags), "tags deleted to {} assets ".format(len(pictures)))

                    return self

            def upload(self, filepath: Union[str, List], tags: List=[], source: str='sdk'):
                """Uploads the assets to the datalake.

                Args:
                    filepath (str || list): [path (or list of path) to file to upload]
                    tags (list, optional): [list of tags to add to the uploaded picture]. Defaults to [].
                    source (str, optional): [source of upload]. Defaults to 'sdk'.
                """
                urls_utils = urls(self.host, self.auth)
                    
                try:
                    if isinstance(filepath, list):
                        for path in filepath:
                            internal_key = os.path.join(str(uuid4()))+ '.' + path.split('/')[-1].split('.')[-1]
                            external_url = path.split('/')[-1]   
                            try: 
                                with Image.open(path) as image:
                                    width, height = image.size
                            except Exception as e:  # pragma: no cover
                                print(e)
                                return
                            self._send_to_s3_and_confirm(urls_utils=urls_utils,
                                path=filepath, internal_key=internal_key, external_url=external_url,
                                height=height, width=width, tags=tags, source=source
                            )
                        print("{} Assets uploaded".format(len(filepath)))
                    else:
                        internal_key = os.path.join(str(uuid4()))+ '.' + filepath.split('/')[-1].split('.')[-1]
                        external_url = filepath.split('/')[-1]   
                        try: 
                            with Image.open(filepath) as image:
                                    width, height = image.size
                        except Exception as e:  # pragma: no cover
                            print(e)
                            return
                        self._send_to_s3_and_confirm(urls_utils,
                                path=filepath, internal_key=internal_key, external_url=external_url,
                                height=height, width=width, tags=tags, source=source
                            )
                except Exception as e:  # pragma: no cover
                    print(e)
                    return
        
            @retry((KeyError, ValueError), total_tries=4)
            def _send_to_s3_and_confirm(self, urls_utils, path, 
                    internal_key, external_url, height, width, tags, source):
                response = urls_utils._get_presigned_url("post", object_name=internal_key)
                with open(path, 'rb') as f:
                    r = requests.post(response["url"], data=response["fields"], files = {'file': (internal_key, f)})
                    if r.status_code == 204:
                        data = json.dumps({
                            'internal_key': internal_key,
                            'external_url': external_url,
                            'height': height,
                            'width': width,
                            'tags': tags,
                            'source': source
                        })
                        r = requests.put(self.host + 'picture/upload/{}'.format(self.organization_id), data=data, headers=self.auth)
                        if r.status_code == 208:
                            raise exceptions.PicselliaError("A picture in your Datalake already has this name.")
                        elif r.status_code != 201:
                            check_status_code(r)
                        else:
                            check_status_code(r)
                    else:
                        raise KeyError
        class Dataset:
            
            def __init__(self, api_token: str=None, organization: str=None, host: str="https://app.picsellia.com/sdk/v2/", organization_id: str=None):
                """Initialize the Dataset class.

                Args:
                    api_token (str, optional): [API Token, find it in your Profile page]. Defaults to None.
                    organization (str, optional): [description]. Defaults to None.
                    host (str, optional): [Host to connect]. Defaults to "https://app.picsellia.com/sdk/v2/".
                    organization_id (str, optional): [Organization id, if none default to your organization]. Defaults to None.

                Raises:
                    Exception: [No picsellia token found]
                    exceptions.NetworkError: [Platform does not respond]
                """
                self.host = host
                if organization_id is None:
                    if api_token == None:
                        if "PICSELLIA_TOKEN" in os.environ:
                            api_token = os.environ["PICSELLIA_TOKEN"]
                        else:
                            raise Exception("Please set up the PICSELLIA_TOKEN environement variable or specify your token")
                    self.auth = {"Authorization": "Token " + api_token}
                    self.requests = pxl_requests(self.auth)
                    r = self.requests.get(self.host + 'ping')
                    self.sdk_version = r.json()["sdk_version"]
                    if self.sdk_version != picsellia.__version__:  # pragma: no cover
                        print("{}You are using an outdated version of the picsellia package ({})\nPlease consider upgrading to {} with pip install picsellia --upgrade{}".format('\033[91m', picsellia.__version__, self.sdk_version, '\033[0m'))
                    data = {
                        'organization': organization
                    }
                    r = self.requests.post(self.host + 'get_organization', data=json.dumps(data))
                    self.organization_id = r.json()["organization_id"]
                else:
                    self.organization_id = organization_id
                    self.auth = {"Authorization": "Token " + api_token}
                    self.requests = pxl_requests(self.auth)
                self.dataset_id = None 
                self.fetched_dataset = {}
                self.dataset_list = []
                # self.urls = urls(self.host, self.auth)

            ###########################################
            ###### DATASET ( LIST, GET, CREATE, DELETE)
            ###########################################
            def __str__(self) -> str:
                if self.fetched_dataset == {}:
                    return "No Dataset fetched, you can retrieve one using fetch() or create() methods"
                else:
                    return json.dumps(self.fetched_dataset, indent=2)

            @exception_handler
            @beartype
            def fetch(self, name: str=None, version: Optional[str]=None):
                """Fetch a dataset by name and version

                Args:
                    name (str, optional): [Dataset name]. Defaults to None.
                    version (str, optional): [Dataset version]. Defaults to None.

                Raises:
                    exceptions.NetworkError: [Picsellia does not respond]

                Returns:
                    self
                """
                if name is None:
                    print("Please select a name")
                    return

                if version is None:
                    version = "latest"
                r = self.requests.get(self.host + 'dataset/{}/{}/{}'.format(self.organization_id, name, version))
                print(r.json())
                self.dataset_id = r.json()['dataset']['dataset_id']
                self.fetched_dataset = r.json()['dataset']
                print("Successfully fetched dataset {}".format(self.fetched_dataset["dataset_name"]))
                print(self)
                return self

            def list(self):
                """[summary]
                List all your Datasets

                Raises:
                    exceptions.NetworkError: [Server Not responding]
                    exceptions.AuthenticationError: [Token Invalid]

                Returns:
                    dataset_list
                """
                r = self.requests.get(self.host + 'dataset/{}'.format(self.organization_id), headers=self.auth)
                dataset_list = r.json()['datasets']
                if len(dataset_list) > 5:  # pragma: no cover
                    for ds in dataset_list[:4]:
                        print('Dataset Name: {}\nDataset Version: {}\nNb Assets: {}\n-------------'.format(ds['dataset_name'], ds['version'], ds['size']))
                    last_dataset = dataset_list[-1]
                    print('\n... {}  more...\n'.format(len(dataset_list)-5))
                    print('Dataset Name: {}\nDataset Version: {}\nNb Assets: {}\n-------------'.format(last_dataset['dataset_name'], last_dataset['version'], last_dataset['size']))
                else:
                    for ds in dataset_list:
                        print('Dataset Name: {}\nDataset Version: {}\nNb Assets: {}\n-------------'.format(ds['dataset_name'], ds['version'], ds['size']))
                self.dataset_list = dataset_list
                return self.dataset_list 

            @exception_handler
            @beartype
            def create(self, name: str='', description: str='', private: bool=True, pictures: List=[]):
                """Creates a dataset

                Args:
                    name (str, optional): [Dataset name]. Defaults to ''.
                    description (str, optional): [Dataset description]. Defaults to ''.
                    private (bool, optional): [True if private dataset]. Defaults to True.
                    pictures (list, optional): [List of id to attach to dataset]. Defaults to [].

                Raises:
                    exceptions.NetworkError: [Platform is not responding]

                Returns:
                    self
                """
                data = json.dumps({ 
                    'dataset_name': name,
                    'description': description,
                    'private': private,
                    'pictures': pictures
                
                })
                if len(pictures) < 1:
                    print('Please specify the assets to add to dataset')
                    return 
                r = self.requests.put(self.host + 'dataset/{}'.format(self.organization_id), data=data)
                print(f"Dataset {name} created with {len(pictures)} assets in it")
                self.dataset_id = r.json()["dataset"]["dataset_id"]
                self.fetched_dataset = r.json()["dataset"]
                print(self)
                return self

            @exception_handler
            @beartype
            def new_version(self, name: str='', version: str='', pictures: List=[], from_version: str='latest'):
                """Create a new dataset version.

                Args:
                    name (str, optional): [Dataset name]. Defaults to ''.
                    version (str, optional): [Dataset version name]. Defaults to ''.
                    pictures (list, optional): [List of picture's id to add to version]. Defaults to [].
                    from_version (str, optional): [Version to base new version]. Defaults to 'latest'.

                Raises:
                    exceptions.NetworkError: [Platform is not responding]

                Returns:
                    self
                """
                data = json.dumps({ 
                    'name': name,
                    'version': version,
                    'pictures': pictures,
                    'from_version': from_version
                
                })

                r = self.requests.put(self.host + 'dataset/{}/new_version'.format(self.organization_id), data=data)
                print(f"Version {version} for dataset {name} created with {len(pictures)} assets in it")
                self.dataset_id = r.json()["dataset"]['dataset_id']
                self.fetched_dataset = r.json()["dataset"]
                return self

            @exception_handler
            @beartype
            def add_data(self, name: str='', version: str='latest', pictures: List=[]):
                """Add assets to a dataset

                Args:
                    name (str, optional): [Dataset name]. Defaults to ''.
                    version (str, optional): [Dataset version]. Defaults to 'latest'.
                    pictures (list, optional): [List of picture's id to attach to dataset version]. Defaults to [].

                Raises:
                    exceptions.NetworkError: [Platform is not responding]

                Returns:
                    self
                """


                dataset_id = self.dataset_id if self.dataset_id is not None else ''
                data = json.dumps({ 
                    'name': name,
                    'version': version,
                    'pictures': pictures,
                    'pk': dataset_id
                
                })

                if len(pictures) <1:
                    print('Please specify the assets to add to dataset')
                    return 

                r = self.requests.post(self.host + 'dataset/{}'.format(self.organization_id), data=data)
                print(f"{len(pictures)} assets added to Dataset {name}/{version}")
                return self

            @exception_handler
            @beartype
            def delete(self, name: str, version='latest'):
                """Delete a dataset

                Args:
                    name (str): [Dataset name]
                    version (str, optional): [Dataset version]. Defaults to 'latest'.

                Raises:
                    exceptions.NetworkError: [Platform is not responding]
                """
                r = self.requests.delete(self.host + 'dataset/{}/{}/{}'.format(self.organization_id, name, version))
                print(f"Dataset {name} deleted")
                return 

            @exception_handler
            @beartype
            def download(self, dataset: str=None, folder_name: str=None, nb_threads: int=20):
                """Downloads all the images from a dataset in the specified folder.

                Args:
                    dataset (str, optional): [DatasetName/DatasetVerion]. Defaults to None.
                    folder_name (str, optional): [Directory to download images]. Defaults to None.
                """
                dataset_name, version = dataset.split('/')
                if folder_name is None:
                    if os.path.isdir(dataset_name):
                        if not os.path.isdir(os.path.join(dataset_name, version)):
                            os.mkdir(os.path.join(dataset_name, version))
                    else:
                        os.mkdir(dataset_name)
                        if not os.path.isdir(os.path.join(dataset_name, version)):
                            os.mkdir(os.path.join(dataset_name, version))
                    img_dir = os.path.join(dataset_name, version)
                else:
                    if not os.path.isdir(folder_name):
                        os.mkdir(folder_name)
                    img_dir = folder_name
                r = self.requests.get(self.host + 'dataset/{}/{}/{}/download'.format(self.organization_id, dataset_name, version))
                    
                images = r.json()["images"]
                lst = []
                for info in images:
                    lst.append(info["external_picture_url"])
                t = len(set(lst))
                print('-----')
                nb_threads = nb_threads
                infos_split = list(mlt.chunks(images, nb_threads))
                counter = Value('i', 0)
                p = Pool(nb_threads, initializer=mlt.pool_init, 
                    initargs=(t, img_dir, counter, True,))
                p.map(mlt.dl_list, infos_split)
                print('--*--')
                print("Images downloaded")

            


            #############################################
            ################# PICTURE ( ADD, DELETE )
            ##############################################
            
                
            @exception_handler
            @beartype
            def add_annotation(self, picture_id: str=None, new_picture: bool=False, dataset_id: str=None,  **kwargs ):  # pragma: no cover
                """Add an annotation to a picture.

                Args:
                    picture_id (str, optional): [id of the picture]. Defaults to None.
                    new_picture (bool, optional): [True if you want to duplicate the picture]. Defaults to False.
                    dataset_id (str, optional): [id of the dataset to attach the picture]. Defaults to None.

                Raises:
                    exceptions.NetworkError: [Platform is not responding]

                Returns:
                    [dict]: {'message': 'annotation saved'}
                """
                if dataset_id is not None:
                    self.dataset_id = dataset_id
                if not new_picture:
                    r = self.requests.put(self.host + 'annotation/' + self.dataset_id + '/' + picture_id, data=json.dumps(kwargs))
                else:
                    r = self.requests.put(self.host + 'annotation/new/' + self.dataset_id + '/' + picture_id, data=json.dumps(kwargs))
                return r.json()
            
            def add_annotation_legacy(self, annotation_yield, new_picture: bool=False, dataset_id: str=None):  # pragma: no cover
                """Add annotation to a dataset

                /!\ -> This method will not be supported in the near future. 

                Args:
                    annotation_yield ([type]): [Yiel generator of anntotations]
                    new_picture (bool, optional): [True if create a new picture]. Defaults to False.
                    dataset_id (str, optional): [Dataset id to attach picture and annotation]. Defaults to None.

                Raises:
                    exceptions.NetworkError: [Platform is not responding]
                """

                if dataset_id is not None:
                    self.dataset_id = dataset_id
                for annotations in annotation_yield:
                    picture_id = annotations["external_picture_url"]
                    args= {
                        "picture_id": picture_id,
                        "nb_instances": annotations["nb_labels"],
                        "duration": annotations["time_spent"],
                        "data": annotations["annotations"]
                    }
                    if not new_picture:
                        r = self.requests.put(self.host + 'annotation/new/' + self.dataset_id + '/' + picture_id, data=json.dumps(args))
                    else:
                        r = self.requests.put(self.host + 'annotation/new/' + self.dataset_id + '/' + picture_id, data=json.dumps(args))
            
            @exception_handler
            @beartype
            def delete_annotations(self, dataset_id: str=None, picture_id: str=None, all_annotations: bool=False):  # pragma: no cover
                """Delete annotations from a dataset.

                Args:
                    dataset_id (str, optional): [Dataset's id to delete annotations]. Defaults to None.
                    picture_id (str, optional): [Picture's id to attach annotation]. Defaults to None.
                    all_annotations (bool, optional): [True if delete all annotations in the dataset]. Defaults to False.

                Raises:
                    exceptions.InvalidQueryError: [No dataset Id specified]
                    exceptions.NetworkError: [Platform is not responding]

                Returns:
                    [dict]: {'success': "annotations deleted"}
                """
                if self.dataset_id is None and dataset_id is None:
                    raise exceptions.InvalidQueryError('Please specify a dataset ID or fetch a dataset first')
                
                else:
                    dataset_id = self.dataset_id if self.dataset_id is not None else dataset_id 

                if picture_id is None and not all_annotations:
                    raise exceptions.InvalidQueryError('You did not specify a picture ID and the `all_annotations` parameter is False')

                if picture_id is not None:
                    if is_uuid(dataset_id) and is_uuid(picture_id):
                        r = self.requests.delete(self.host + 'annotation/' + dataset_id + '/' + picture_id, headers=self.auth)
                    else:
                        print("Please provide a valid uuid")
                        return
                else:
                    if is_uuid(dataset_id):
                        r = self.requests.delete(self.host + 'annotation/' + dataset_id, headers=self.auth)
                    else:
                        print("Please provide a valid uuid")
                        return
                return r.json()

            @exception_handler
            @beartype
            def create_labels(self, name: str=None, ann_type: str=None, verbose=True):
                """Create labels for a dataset.

                Args:
                    name (str, optional): [label name]. Defaults to None.
                    ann_type (str, optional): [type of annotation]. Defaults to None.

                Raises:
                    exceptions.NetworkError: [Platform is not responding]
                """
                try:
                    if self.dataset_id is None:
                        raise Exception("Please fetch or create a dataset first.")
                   
                    r = requests.put(self.host + 'label/{}/{}/{}'.format(self.dataset_id, name, ann_type), headers=self.auth)                   
                except Exception:  # pragma: no cover
                    raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
                
                check_status_code(r, verbose=verbose)
            #############################################
            ################# PICTURE ( ADD, DELETE )
            ##############################################
                    
    class Network:
        
        def __init__(self,api_token: str=None, organization: str=None,  host: str="https://app.picsellia.com/sdk/v2/", network_id: str=None, ping: bool=False):
            """Initialize the Network class.

            Args:
                api_token (str, optional): [API token, find it in your profile page]. Defaults to None.
                organization (str, optional): [organization id, if none your organization]. Defaults to None.
                host (str, optional): [Host to connect picsellia client]. Defaults to "https://app.picsellia.com/sdk/v2/".
                network_id (str, optional): [Network id to checkout]. Defaults to None.
                ping (bool, optional): [True if ping picsellia platform]. Defaults to False.

            Raises:
                Exception: [No picsellia token found]
                exceptions.NetworkError: [Platform is not responding]
            """
            self.host = host
            if not ping:
                if api_token == None:
                    if "PICSELLIA_TOKEN" in os.environ:
                        token = os.environ["PICSELLIA_TOKEN"]
                    else:
                        raise Exception("Please set up the PICSELLIA_TOKEN environement variable or specify your token")
                else:
                    token = api_token
                self.auth = {"Authorization": "Token " + token}
                self.requests = pxl_requests(self.auth)
                r = self.requests.get(self.host + 'ping')
                self.username = r.json()["username"]
                self.sdk_version = r.json()["sdk_version"]
                if self.sdk_version != picsellia.__version__:  # pragma: no cover
                    print("{}You are using an outdated version of the picsellia package ({})\nPlease consider upgrading to {} with pip install picsellia --upgrade{}".format('\033[91m', picsellia.__version__, self.sdk_version, '\033[0m'))
                print("Hi {}, welcome back.".format(self.username))
            else:
                self.auth = {"Authorization": "Token " + api_token}
                self.requests = pxl_requests(self.auth)
            data = {
                'organization': organization
            }
            r = self.requests.post(self.host + 'get_organization', data=json.dumps(data))
            self.organization = r.json()["organization_name"]
            self.network_id = network_id
            self.network_name = ""
            self.urls = urls(self.host, self.auth)
            self.infos = {}
            self.network_list = []

        def __str__(self) -> str:
            if self.infos == {}:
                return "No Network fetched, you can retrieve one using get() or create() methods"
            else:
                return json.dumps(self.infos, indent=2)

        def list(self,):
            """List networks in the organization.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                self.network_list
            """
            data = {
                'organization': self.organization
            }
            r = self.requests.get(self.host + 'network/'+self.organization, data=data)
            network_list = r.json()['networks']
            self.network_list = network_list
            if len(network_list) > 5:  # pragma: no cover
                for net in network_list[:4]:
                    print('Network Name: {}\nFramework: {}\nTags: {}\n-------------'.format(net['network_name'], net['framework'], net['tag']))
                last_network = network_list[-1]
                print('\n... {}  more...\n'.format(len(network_list)-5))
                print('Network Name: {}\nFramework: {}\nTags: {}\n-------------'.format(last_network['network_name'], last_network['framework'], last_network['tag']))
            else:
                for net in network_list:
                    print('Network Name: {}\nFramework: {}\nTags: {}\n-------------'.format(net['network_name'], net['framework'], net['tag']))
            return network_list

        @exception_handler
        @beartype
        def get(self, identifier: str=None):
            """Get a network by identifier.

            Args:
                identifier (str, optional): [uuid or name of network to get]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                self
            """
            if self.network_id is not None:
                r = self.requests.get(self.host + 'network/' + self.organization + '/' + self.network_id)
            else:
                if is_uuid(identifier):
                    r = self.requests.get(self.host + 'network/' + self.organization + '/' + identifier)
                else:
                    r = self.requests.get(self.host + 'network/by_name/' + self.organization + '/' + identifier)
            self.network_id = r.json()["model_id"]
            self.network_name = r.json()["network_name"]
            self.files = r.json()["files"]
            self.organization_name = r.json()["organization"]["name"]
            self.infos = r.json()
            print("Successfully fetched network {}".format(self.network_name))
            print(self)
            return self

        @exception_handler
        @beartype
        def create(self, name: str=None, type: str=None):
            """Creates a new network.

            Args:
                name (str, optional): [Network name to create]. Defaults to None.
                type (str, optional): [Network type (classification, detection, etc.)]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                self
            """
            if type is None or type == "":
                raise exceptions.InvalidQueryError("You must specify a non-empty type for your network")
            data = json.dumps({
                "name": name,
                "type": type
            })
            r = self.requests.post(self.host + 'network/'+self.organization, data=data)
            self.network_id = r.json()["model_id"]
            self.network_name = r.json()["network_name"]
            self.files = r.json()["files"]
            self.infos = r.json()
            print("Network {} created.\n".format(r.json()["network_name"]))
            print(self)
            return self

        @exception_handler
        @beartype
        def delete(self,):
            """Delete a network

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                None
            """
            r = self.requests.delete(self.host + 'network/' + self.organization + '/' + self.network_id, headers=self.auth, verbose=False)
            print("Network {} deleted.\n".format(self.infos["network_name"]))
            self.infos = {}
            return

        def update(self, **kwargs):
            """Update the network.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                self
            """
            kwargs["model_id"] = self.network_id
            r = self.requests.patch(self.host + 'network/' + self.organization + '/' + self.network_id, data=json.dumps(kwargs))
            self.infos = r.json()["network"]
            print(f"Network {self.network_name} updated.")
            print(self)
            return self

        @exception_handler
        @beartype
        def _create_or_update_file(self, file_name: str="", path: str="", object_name: str=""):
            """Create or update a file in the Platform.

            Args:
                file_name (str, optional): [filename to upload or update]. Defaults to "".
                path (str, optional): [path to the file]. Defaults to "".
                object_name (str, optional): [s3 object key for storage]. Defaults to "".
            """
            files = self.files
            if file_name in files.keys():
                self.update(files=files)
            else:
                files[file_name] = object_name
                self.update(files=files)

        @exception_handler
        @beartype
        def _send_large_file(self, path: str=None, file_name: str=None, object_name: str=None):
            """Send a large file to the Platform.

            Args:
                file_name (str, optional): [filename to upload or update]. Defaults to "".
                path (str, optional): [path to the file]. Defaults to "".
                object_name (str, optional): [s3 object key for storage]. Defaults to "".
            """
            self.urls._init_multipart(object_name)
            parts = self.urls._upload_part(path, object_name)

            if self.urls._complete_part_upload(parts, object_name, None):
                self._create_or_update_file(file_name, path, object_name=object_name)

        @exception_handler
        @beartype
        def _send_file(self, path: str=None, file_name: str=None, object_name: str=None):
            """Send a file to the Platform.

            Args:
                file_name (str, optional): [filename to upload or update]. Defaults to "".
                path (str, optional): [path to the file]. Defaults to "".
                object_name (str, optional): [s3 object key for storage]. Defaults to "".
            """
            response = self.urls._get_presigned_url(method='post', object_name=object_name, bucket_model=True)
            try:
                with open(path, 'rb') as f:
                    files = {'file': (path, f)}
                    http_response = requests.post(response['url'], data=response['fields'], files=files)
                if http_response.status_code == 204:
                    self._create_or_update_file(file_name, path, object_name=object_name)
            except Exception as e:  # pragma: no cover
                raise exceptions.NetworkError(str(e))
        
        @exception_handler
        @beartype
        def store(self, name: str="", path: str=None, zip: bool=False):
            """Store a file of picsellia.

            Args:
                name (str, optional): [file name]. Defaults to "".
                path (str, optional): [file path]. Defaults to None.
                zip (bool, optional): [True if you want to zip a file]. Defaults to False.
            """
            if path != None:
                if zip:
                    path = utils.zipdir(path)
                filesize = Path(path).stat().st_size
                filename = path.split('/')[-1]
                if name == 'model-latest':
                    object_name = os.path.join(self.network_id, '0', filename)
                else:
                    object_name = os.path.join(self.network_id, filename)
                if filesize < 5*1024*1024:
                    self._send_file(path, name, object_name)
                else:
                    self._send_large_file(path, name, object_name)
                print("File {} stored successfully for network {}".format(name, self.infos["network_name"]))
            else:
                print("Please specify a path")

        @exception_handler
        @beartype
        def update_thumb(self, path: str=None):
            """Updates the network thumbnail.

            Args:
                path (str, optional): [path to the picture to upload as thumbnail]. Defaults to None.

            Raises:
                exceptions.NetworkError: [Platform is not responding]
                exceptions.InvalidQueryError: [Picture file is more than 5Mo]
            """
            if path != None:
                filesize = Path(path).stat().st_size
                if filesize < 5*1024*1024:
                    filename = path.split('/')[-1]
                    object_name = os.path.join(self.network_id, filename)
                    response = self.urls._get_presigned_url(method='post', object_name=object_name, bucket_model=False)
                    try:
                        with open(path, 'rb') as f:
                            files = {'file': (path, f)}
                            http_response = requests.post(response['url'], data=response['fields'], files=files)
                        if http_response.status_code == 204:
                            self.update(thumb_object_name=object_name)
                    except Exception as e:  # pragma: no cover
                        raise exceptions.NetworkError(str(e))
                else:  # pragma: no cover
                    raise exceptions.InvalidQueryError("File too large, must be under 5Mb.")
        
        @exception_handler
        @beartype
        def labels(self, labels: dict):
            """Set labels for this query .

            Args:
                labels ([dict]): [Labelmap of the network to upload]
            """
            self.update(labels=labels)


    class Project:
        
        def __init__(self, api_token: str=None, organization=None, host: str='https://app.picsellia.com/sdk/v2/', project_token: str=None, ping: bool=False):
            """Initialize the Project class.

            Args:
                api_token (str, optional): [API token, find it in your profile page]. Defaults to None.
                host (str, optional): [Host to connect client]. Defaults to 'https://app.picsellia.com/sdk/v2/'.
                project_id (str, optional): [ID of project to checkout]. Defaults to None.
                ping (bool, optional): [True if test platform connection]. Defaults to False.

            Raises:
                Exception: [API token not provided]
                exceptions.NetworkError: [Platform is not responding]
            """
            self.host = host
            if not ping:
                if api_token == None:
                    if "PICSELLIA_TOKEN" in os.environ:
                        token = os.environ["PICSELLIA_TOKEN"]
                    else:
                        raise Exception("Please set up the PICSELLIA_TOKEN environement variable or specify your token")
                else:
                    token = api_token
                self.auth = {"Authorization": "Token " + token}
                self.requests = pxl_requests(self.auth)
                r = self.requests.get(self.host + 'ping')
                self.username = r.json()["username"]
                self.sdk_version = r.json()["sdk_version"]
                if self.sdk_version != picsellia.__version__:  # pragma: no cover
                    print("{}You are using an outdated version of the picsellia package ({})\nPlease consider upgrading to {} with pip install picsellia --upgrade{}".format('\033[91m', picsellia.__version__, self.sdk_version, '\033[0m'))
                print("Hi {}, welcome back.".format(self.username))
            else:
                self.auth = {"Authorization": "Token " + api_token}
                self.requests = pxl_requests(self.auth)
            self.token = api_token
            self.project_token = project_token
            self.name = None
            data = {
                'organization': organization
            }
            r = self.requests.post(self.host + 'get_organization', data=json.dumps(data))
            self.organization_id = r.json()["organization_id"]
            self.organization_name = r.json()["organization_name"]
            self.infos = {}
            self.project_list = []

        def __str__(self) -> str:
            if self.infos == {}:
                return "No Project fetched, you can retrieve one using get() or create() methods"
            else:
                return json.dumps(self.infos, indent=2)

        @exception_handler
        @beartype
        def list(self,):
            """List projects in the organization.

            Args:
                organization (str, optional): [organization id to connect]. Defaults to "null".

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [list]: []ProjectSerializer
            """
            r = self.requests.get(self.host + 'project/'+self.organization_name)
            project_list = r.json()['projects']
            if len(project_list) > 5:  # pragma: no cover
                for project in project_list[:4]:
                    print('Project Name: {}\nDescription: {}\nContributors: {}\nDatasets: {}\n-------------'.format(project['project_name'], project["description"], project['contributors'], project['datasets']))
                last_project = project_list[-1]
                print('\n... {}  more...\n'.format(len(project_list)-5))
                print('Project Name: {}\nDescription: {}\nContributors: {}\nDatasets: {}\n-------------'.format(last_project['project_name'], project["description"], last_project['contributors'], last_project['datasets']))
            else:
                for project in project_list:
                    print('Project Name: {}\nDescription: {}\nContributors: {}\nDatasets: {}\n-------------'.format(project['project_name'], project["description"], project['contributors'], project['datasets']))
            self.project_list = project_list
            return project_list

        @exception_handler
        @beartype
        def get(self, name: str=""):
            """Get a project by name.

            Args:
                name (str): [project name]
                organization (str, optional): [organization id, if null it's your organization]. Defaults to "null".

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                self
            """
            self.organization_name != None, "Please specify an organization first."
            r = self.requests.get(self.host + 'project/by_name/{}/{}'.format(self.organization_name, name))
            project = r.json()
            self.infos = project
            self.name = project["project_name"]
            self.project_token = project["project_id"]
            self.worker = self.Worker(host=self.host, api_token=self.token, project_token=self.project_token, ping=True)
            print("Successfully fetched project {}".format(self.infos["project_name"]))
            print(self)
            return self

        @exception_handler
        @beartype
        def create(self, name: str="", **kwargs):
            """Creates a new project.

            Args:
                name (str, required): The name of your new project, can't be empty
                organization (str, optional): [organization id, if null it's your organization]. Defaults to "null".

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                self
            """
            if name == "":
                raise exceptions.InvalidQueryError("Project name can't be empty")
            kwargs["project_name"] = name
            r = self.requests.put(self.host + 'project/'+self.organization_name, data=json.dumps(kwargs))
            project = r.json()
            self.infos = project
            self.name = project["project_name"]
            self.project_token = project["project_id"]
            self.worker = self.Worker(api_token=self.token, host=self.host, project_token=self.project_token, ping=True)
            print(f"Project {self.name} created successfully.")
            print(self)
            return self

        def update(self, **kwargs):
            """Update this project.
            docs : https://docs.picsellia.com
            Returns:
                self
            """
            assert self.name != None and self.organization_name != None, "Please get a project first"
            r = self.requests.patch(self.host + 'project/by_name/{}/{}'.format(self.organization_name, self.name), data=json.dumps(kwargs))
            project = r.json()["project"]
            self.infos = project
            self.name = project["project_name"]
            print(f"Project {self.name} updated.")
            print(self)
            return self
        
        def delete(self,):
            """Delete a project.

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                [dict]: {'success': "project deleted"}
            """
            assert self.name != None and self.organization_name != None, "Please get a project first"
            r = self.requests.delete(self.host + 'project/by_name/{}/{}'.format(self.organization_name, self.name), verbose=False)
            print("Project {} deleted.\n".format(self.name))
            self.infos = {}
            self.name = ""
            self.project_token = ""
            return
        
        @exception_handler
        @beartype
        def attach_dataset(self, dataset: str=""):
            """Attach a dataset to a project

            Args:
                dataset (str): [DatasetName/DatasetVersion of the dataset to attach]

            Raises:
                exceptions.NetworkError: [Platform is not responding]

            Returns:
                None
            """
            assert self.project_token != None and self.project_token != "", "Please get a project first"
            split = dataset.split('/')
            if len(split) != 2:
                raise exceptions.InvalidQueryError("You must specify the dataset like this -> <dataset_name>/<version>")
            dataset_name = split[0]
            version = split[1]
            data = json.dumps({
                'dataset_name': dataset_name,
                'version': version
            })
            r = self.requests.post(self.host + 'project/attach_dataset/{}'.format(self.project_token), data=data, verbose=False)
            print("Dataset {}/{} successfully attached to project {}".format(dataset_name, version, self.name))
            return 

        class Worker:

            def __init__(self, api_token: str=None, host: str='https://app.picsellia.com/sdk/v2/', project_token: str=None, ping: bool=False):
                """Initialize the Worker class.

                Args:
                    api_token (str, optional): [API Token, find it in you profile page]. Defaults to None.
                    host (str, optional): [Host to connect client]. Defaults to 'https://app.picsellia.com/sdk/v2/'.
                    project_token (str, optional): [Project id, find it in your project page]. Defaults to None.
                    ping (bool, optional): [True if you want to ping platform]. Defaults to False.

                Raises:
                    Exception: [Picsellia token not found]
                    exceptions.NetworkError: [Platform is not responding]
                """
                self.host = host
                if project_token is None:
                    raise Exception("Please specify the project token to access workers")
                if not ping:
                    if api_token == None:
                        if "PICSELLIA_TOKEN" in os.environ:
                            token = os.environ["PICSELLIA_TOKEN"]
                        else:
                            raise Exception("Please set up the PICSELLIA_TOKEN environement variable or specify your token")
                    else:
                        token = api_token
                    self.auth = {"Authorization": "Token " + token}
                    self.requests = pxl_requests(self.auth)
                    r = self.requests.get(self.host + 'ping', headers=self.auth)
                    self.sdk_version = r.json()["sdk_version"]
                    if self.sdk_version != picsellia.__version__:  # pragma: no cover
                        print("{}You are using an outdated version of the picsellia package ({})\nPlease consider upgrading to {} with pip install picsellia --upgrade{}".format('\033[91m', picsellia.__version__, self.sdk_version, '\033[0m'))
                else:
                    self.auth = {"Authorization": "Token " + api_token}
                    self.requests = pxl_requests(self.auth)
                self.project_token = project_token

            def list(self,):
                """List all worker info

                Raises:
                    exceptions.NetworkError: [Platform is not responding]

                Returns:
                    [list]: []WorkerSerializer
                """
                r = self.requests.get(self.host + 'worker/' + self.project_token)
                return r.json()
