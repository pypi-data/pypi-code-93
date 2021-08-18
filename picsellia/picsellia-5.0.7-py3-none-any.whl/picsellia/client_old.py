import json
import os
import sys
import io
import picsellia_training.pxl_utils as utils
from picsellia_training.pxl_urls import Urls as urls
import picsellia_training.pxl_multithreading as mlt
import requests
from PIL import Image, ImageDraw, ExifTags
import picsellia_training.pxl_exceptions as exceptions
import numpy as np
import cv2
from multiprocessing.pool import ThreadPool
from multiprocessing import Pool, Value
import time
import zipfile


class Client:
    """
    The Picsell.ia Client is used to connect to the Picsell.ia platform.
    It provides functions to :
        - format data for training
        - dl annotations & images
        - send training logs
        - send examples
        - save weights and SavedModel to Picsell.ia server."""

    def __init__(self, api_token, host="http://localhost:8000/sdk/", interactive=True):
        """ Creates and initializes a Picsell.ia Client.
        Args:
            api_token (str): api_token key, given on the platform.
            host (str): URL of the Picsell.ia server to connect to.
        Raises:
            NetworkError: if server is not responding or host is incorrect.
        """

        #Global Variables
        self.supported_img_types = ("png", "jpg", "jpeg", "JPG", "JPEG", "PNG")
        self.OBJECT_NAME = None
        self.uploadId = None
        self.auth = {"Authorization": "Bearer " + api_token}
        self.host = host

        try:
            r = requests.get(self.host + 'ping', headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")  

        # User Variables 
        self.username = r.json()["username"]

        # Project Variables
        self.project_name_list = r.json()["project_list"]
        self.project_token = None
        self.project_id = None
        self.project_infos = None
        self.project_name = None
        self.project_type = None

        # Dataset Variables 

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
        self.exp_id = None
        self.exp_name = None
        self.exp_description = None 
        self.exp_status = None 
        self.exp_parameters = None
        self.line_nb = 0
        self.training_id = None
        self.annotation_type = None
        self.dict_annotations = {}
        self.train_list_id = None
        self.eval_list_id = None
        self.train_list = None
        self.eval_list = None
        self.index_url = None
        self.checkpoint_index = None
        self.checkpoint_data = None
        self.config_file = None
        self.model_selected = None
        self.label_path = None
        self.label_map = None
        self.urls = urls(self.host, self.auth)
        self.dataset = self.Dataset(self.host, self.auth)
        
        self.interactive = interactive
        print(f"Welcome {self.username}, glad to have you back")


    def checkout_project(self, project_token, png_dir=None):
        """ Attach the Picsell.ia Client to the desired project.
                Args:
                    project_token (str): project_token key, given on the platform.
                    png_dir (str): path to your images, if None you can download the pictures with dl_pictures()
                Raises:
                    NetworkError: If Picsell.ia server not responding or host is incorrect.
                    AuthenticationError: If token does not match the provided token on the platform.
                    NotImplementedError: If there are files in the png_dir with unsupported types (png, jpeg, jpg)
        """
        to_send = {"project_token": project_token}
        try:
            r = requests.get(self.host + 'init_project', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        if r.status_code != 200:
            raise exceptions.AuthenticationError('The project_token provided does not match any of the known project_token for your profile.')

        self.project_token = project_token
        self.project_id = r.json()["project_id"]
        self.project_infos = r.json()["infos"]
        self.project_name = r.json()["project_name"]
        self.project_type = r.json()["project_type"]
        self.network_names = r.json()["network_names"]

        if png_dir is None:
            self.png_dir = os.path.join(self.project_name, 'images')
        else:
            print(f"You have provided a path to your training data directory ... \n")
            self.png_dir = png_dir
            print(f"Looking for images at {self.png_dir}...")
            if not len(os.listdir(self.png_dir)) != 0:
                raise exceptions.ResourceNotFoundError(f"Can't find images at {self.png_dir}")

            for filename in os.listdir(self.png_dir):
                ext = filename.split('.')[-1]
                if ext not in self.supported_img_types:
                    raise NotImplementedError(f"Found a non supported filetype {filename.split('.')[-1]} in your png_dir, \
                                    supported filetype are : {self.supported_img_types}, please move {filename} elsewhere")

    def init_experiment(self, name):
        assert isinstance(name, str), f"model name must be string, got {type(name)}"
        assert name!="", "Experiment name's length can't be 0"
        assert self.project_token!=None, "Please create or checkout project first."
        to_send = {
            "project_token": self.project_token,
            "name": name,
        }
        try:
            r = requests.post(self.host + 'init_experiment', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        if r.status_code!=200:
            raise exceptions.AuthenticationError(r.text)
        response = r.json()
        if response["name"]!=name:
            print("{} experiment name was already taken, we have renamed it to {}".format(name,response["name"]))
        self.exp_id = response["experiment_id"]
        print("Experiment created successfully.")
        return self.exp_id

    def fetch_experiment_parameters(self, experiment_id):
        to_send = {
            "experiment_id": experiment_id,
        }
        try:
            r = requests.get(self.host + 'get_experiment_parameters', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        response = r.json()
        if not response["exp_available"]:
            raise exceptions.ResourceNotFoundError("Experiment Not Found, please check your experiment_id")
        self.exp_id = experiment_id
        self.exp_name = response["name"]
        self.exp_description = response["description"]
        self.exp_status = response["status"]
        self.exp_parameters = response["parameters"]
        self.project_token = response["project_token"]
        if self.exp_status == 'waiting':
            print("Experiment {} found, ready for training. \n".format(self.exp_name))
            self.update_experiment_status("launched")
        else:
            print("Experiment {} found with status '{}'\n".format(self.exp_name, self.exp_status))
        
        return self.project_token, self.exp_parameters
    
    def update_experiment_status(self, status):
        assert status!="", "Experiment status's length can't be 0"
        assert self.exp_id!=None, "Please create or checkout experiment first."
        to_send = {
            "experiment_id": self.exp_id,
            "status": status,
        }
        try:
            r = requests.post(self.host + 'update_experiment_status', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        if r.status_code!=200:
            raise exceptions.AuthenticationError(r.text)
        
    def send_experiment_logging(self, log, part, final=False, special=False):
        assert self.exp_id!=None, "Please create or checkout experiment first."
        to_send = {
            "experiment_id": self.exp_id,
            "line_nb": self.line_nb,
            "log": log,
            "final": final,
            "part": part,
            "special": special
        }
        self.line_nb +=1
        try:
            r = requests.post(self.host + 'send_experiment_logging', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")

    def create_network(self, network_name, orphan=False):
        """ Initialise the model instance on Picsell.ia server.
            If the model name exists on the server for this project, you will create a new version of your training.
            Create all the repositories for your training with this architecture :
              your_code.py
              - project_id
                    - images/
                    - network_id/
                        - training_version/
                            - logs/
                            - checkpoints/
                            - records/
                            - config/
                            - results/
                            - exported_model/
        Args:
            network_name (str): It's simply the name you want to give to your model
                              For example, SSD_Picsellia

        Raises:
            AuthenticationError: If `project_token` does not match the provided project_token on the platform.
            NetworkError: If Picsell.ia server not responding or host is incorrect.
        """

        assert isinstance(network_name, str), f"model name must be string, got {type(network_name)}"

        if self.network_names is None:
            self.network_names = []

        if network_name in self.network_names:
            raise exceptions.InvalidQueryError("The Network name you provided already exists for this project")

        to_send = {"model_name": network_name, "project_token": self.project_token}

        try:
            r = requests.get(self.host + 'init_model', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")

        if r.status_code == 400:
            raise exceptions.AuthenticationError('The project_token provided does not match any of the known project_token for profile.')

        self.network_id = r.json()["network_id"]
        self.training_id = r.json()["training_id"]
        self.network_name = network_name
        self.dict_annotations = {}

        if orphan is not True:
            self.setup_dirs()
        else:
            self.base_dir = os.path.join(self.project_name, self.network_name, str(self.training_id))
            self.metrics_dir = os.path.join(self.base_dir, 'metrics')
            self.checkpoint_dir = os.path.join(self.base_dir, 'checkpoint')
            self.record_dir = os.path.join(self.base_dir, 'records')
            self.config_dir = os.path.join(self.base_dir, 'config')
            self.results_dir = os.path.join(self.base_dir, 'results')
            self.exported_model_dir = os.path.join(self.base_dir, 'exported_model')

        print("New network has been created")

    def checkout_network(self, network_name, training_id=None, prop=0.8):
        """ Attach the Picsell.ia Client to the desired Network.
            If the model name exists on the server for this project, you will create a new version of your training.

            Create all the repositories for your training with this architecture :

              your_code.py
              - project_id
                    - images/
                    - network_id/
                        - training_version/
                            - logs/
                            - checkpoints/
                            - records/
                            - config/
                            - results/
                            - exported_model/

        Args:
            network_name (str): It's simply the name you want to give to your model
                              For example, SSD_Picsellia

        Raises:
            AuthenticationError: If `project_token` does not match the provided project_token on the platform.
            NetworkError: If Picsell.ia server not responding or host is incorrect.
        """

        assert isinstance(network_name, str), f"model name must be string, got {type(network_name)}"

        if network_name not in self.network_names:
            raise exceptions.ResourceNotFoundError("The Network name you provided does not exists for this project")

        to_send = {"model_name": network_name, "project_token": self.project_token}

        try:
            r = requests.get(self.host + 'init_model', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")

        if r.status_code == 400:
            raise exceptions.AuthenticationError('The project_token provided does not match any of the known project_token for this profile.')

        response = r.json()
        self.network_id = response["network_id"]
        self.training_id = response["training_id"]
        if training_id is not None:
            self.training_id = training_id
        self.network_name = network_name
        self.dict_annotations = {}
        if "index_object_name" in response["checkpoints"].keys():
            self.checkpoint_index = response["checkpoints"]["index_object_name"]
        else:
            self.checkpoint_index = None

        if "data_object_name" in response["checkpoints"].keys():
            self.checkpoint_data = response["checkpoints"]["data_object_name"]

        else:
            self.checkpoint_data = None

        if "config_file" in response["checkpoints"].keys():
            self.config_file = response["checkpoints"]["config_file"]
        else:
            self.config_file = None
        self.setup_dirs()
        self.model_selected = self.dl_checkpoints()

        if not os.path.isfile(os.path.join(self.project_name, self.network_name, "annotations.json")):
            self.dl_annotations()
            with open(os.path.join(self.project_name, self.network_name, "annotations.json"), "w") as f:
                json.dump(self.dict_annotations, f)
        else:
            with open(os.path.join(self.project_name, self.network_name, "annotations.json"), "r") as f:
                self.dict_annotations = json.load(f)
        self.generate_labelmap()
        self.send_labelmap()
        self.dl_train_test_split(prop=prop)
        return self.model_selected

    def configure_network(self, project_type):

        supported_type = ["classification", "detection", "segmentation"]
        if project_type not in supported_type:
            trigger = False
            while not trigger:
                a = input(f"Please provide a supported project type : {supported_type}")
                if a in supported_type:
                    if a == "classification" and self.project_type != "classification":
                        print(f"You tried to configure you project with an incompatible project type, you project type is {self.project_type}")
                    else:
                        trigger = True
            to_send = {"network_id": self.network_id, "type": a}
        else:
            to_send = {"network_id": self.network_id, "type": project_type}

        try:
            r = requests.post(self.host + 'configure_network', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")

        if not r.status_code == 200:
            raise exceptions.ResourceNotFoundError("Invalid network to configure")

        if project_type == "classification":
            self.annotation_type = "label"
        elif project_type == "detection":
            self.annotation_type = "rectangle"
        elif project_type == "segmentation":
            self.annotation_type = "polygon"
    
    def reset_network(self, network_name):
        """ Reset your training checkpoints to the origin.
        Args:
            network_name (str): It's simply the name you want to give to your model
                              For example, SSD_Picsellia
        Raises:
            AuthenticationError: If `project_token` does not match the provided project_token on the platform.
            NetworkError: If Picsell.ia server not responding or host is incorrect.
        """
        assert isinstance(network_name, str), f"model name must be string, got {type(network_name)}"

        print("We'll reset your project to the origin checkpoint")
        if network_name not in self.network_names:
            raise exceptions.ResourceNotFoundError("The Network name you provided does not exists for this project")

        to_send = {"model_name": network_name, "project_token": self.project_token, "reset": True}

        try:
            r = requests.get(self.host + 'init_model', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")

        if r.status_code == 400:
            raise exceptions.AuthenticationError('The project_token provided does not match any of the known project_token for profile.')

        response = r.json()
        self.network_id = response["network_id"]
        self.training_id = response["training_id"]
        self.network_name = network_name
        self.dict_annotations = {}
        self.setup_dirs()
        if "index_object_name" in response["checkpoints"].keys():
            self.checkpoint_index = response["checkpoints"]["index_object_name"]
        else:
            self.checkpoint_index = None

        if "data_object_name" in response["checkpoints"].keys():
            self.checkpoint_data = response["checkpoints"]["data_object_name"]

        else:
            self.checkpoint_data = None

        if "config_file" in response["checkpoints"].keys():
            self.config_file = response["checkpoints"]["config_file"]
        else:
            self.config_file = None
        self.model_selected = self.dl_checkpoints(reset=True)
        return self.model_selected

    def setup_dirs(self):

        self.base_dir = os.path.join(self.project_name, self.network_name, str(self.training_id))
        self.metrics_dir = os.path.join(self.base_dir, 'metrics')
        self.checkpoint_dir = os.path.join(self.base_dir, 'checkpoint')
        self.record_dir = os.path.join(self.base_dir, 'records')
        self.config_dir = os.path.join(self.base_dir, 'config')
        self.results_dir = os.path.join(self.base_dir, 'results')
        self.exported_model_dir = os.path.join(self.base_dir, 'exported_model')

        if not os.path.isdir(self.project_name):
            print("No directory for this project has been found, creating directory and sub-directories...")
            os.mkdir(self.project_name)

        self._create_dir(os.path.join(self.project_name, self.network_name))
        self._create_dir(self.base_dir)
        self._create_dir(self.png_dir)
        self._create_dir(self.checkpoint_dir)
        self._create_dir(self.metrics_dir)
        self._create_dir(self.record_dir)
        self._create_dir(self.config_dir)
        self._create_dir(self.results_dir)
        self._create_dir(self.exported_model_dir)

    def _create_dir(self, dir_name):
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)

    def generate_labelmap(self):
        """THIS FUNCTION IS MAINTAINED FOR TENSORFLOW 1.X
        ----------------------------------------------------------
        Genrate the labelmap.pbtxt file needed for Tensorflow training at:
            - project_id/
                network_id/
                    training_id/
                        label_map.pbtxt
        Raises:
            ResourceNotFoundError : If no annotations in the Picsell.ia Client yet or images can't be downloaded
                                    If no directories have been created first."""

        print("Generating labelmap ...")
        if not hasattr(self, "dict_annotations") or not hasattr(self, "base_dir"):
            raise exceptions.ResourceNotFoundError("Please run create_network() or checkout_network() then dl_annotations()")

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
                    if self.project_type == 'classification':
                        labels_Network[str(k)] = name
                    else:
                        labels_Network[str(k + 1)] = name
                labelmap_file.close()
            print(f"Label_map.pbtxt created @ {self.label_path}")

        except Exception:
            raise exceptions.ResourceNotFoundError("No directory found, please call checkout_network() or create_network() function first")

        self.label_map = labels_Network
        
    # Downloaders 

    def dl_checkpoints(self, checkpoint_path=None, reset=False):

        if checkpoint_path is not None:
            if not os.path.isdir(checkpoint_path):
                raise exceptions.ResourceNotFoundError(f"No directory @ {checkpoint_path}")
            return checkpoint_path

        if (self.checkpoint_index is None) or (self.checkpoint_data is None):
            print("You are working with a custom model")
            return None

        # list all existing training id
        if not reset:
            training_ids = sorted([int(t_id) for t_id in os.listdir(os.path.join(self.project_name, self.network_name))
                                   if os.path.isdir(os.path.join(self.project_name, self.network_name, t_id))], reverse=True)
            print("Available trainings : ", *training_ids)

            index_path = ""
            data_path = ""
            config_path = ""
            a = 0
            for _id in training_ids:
                path = os.path.join(self.project_name, self.network_name, str(_id), "checkpoint")
                if utils.is_checkpoint(path, self.project_type):
                    if self.interactive:
                        while (a not in ["y", "yes", "n", "no"]):
                            a = input(f"Found checkpoint for training {_id}, do you want to use this checkpoint ? [y/n] ")
                        if a.lower() == 'y' or a.lower() == 'yes':
                            p = os.path.join(self.project_name, self.network_name, str(self.training_id), "checkpoint")
                            print(f"Your next training will use checkpoint: {p}")
                            return path
                        else:
                            continue
                    else:
                        return path
                else:
                    path_deep = os.path.join(self.project_name, self.network_name, str(_id), "checkpoint", "origin")
                    if utils.is_checkpoint(path_deep, self.project_type):
                        if self.interactive:
                            while (a not in ["y", "yes", "n", "no"]):
                                a = input(f"Found origin checkpoint from training {_id}, do you want to use this checkpoint ? [y/n] ")
                            if a.lower() == 'y' or a.lower() == 'yes':
                                p = os.path.join(self.project_name, self.network_name, str(self.training_id), "checkpoint")
                                print(f"Your next training will use checkpoint: {p}")
                                return path_deep
                            else:
                                continue
                        else:
                            return path_deep
                    else:
                        continue
        else:
            try:
                path_to_look_0 = os.path.join(self.project_name, self.network_name, "0", "checkpoint", "origin")
                path_to_look_1 = os.path.join(self.project_name, self.network_name, "1", "checkpoint", "origin")
                if os.path.isdir(path_to_look_0):
                    if utils.is_checkpoint(path_to_look_0, self.project_type):
                        print(f"Found original checkpoint: {path_to_look_0}")
                        return path_to_look_0
                if os.path.isdir(path_to_look_1):
                    if utils.is_checkpoint(path_to_look_1, self.project_type):
                        print(f"Found origin checkpoint: {path_to_look_1}")
                        return path_to_look_1
            except Exception:
                pass

        path_to_origin = os.path.join(self.checkpoint_dir, "origin")

        if not os.path.isdir(path_to_origin):
            os.makedirs(path_to_origin)

        for fpath in os.listdir(path_to_origin):
            os.remove(os.path.join(path_to_origin, fpath))
        url_index = self.urls._get_presigned_url('get', self.checkpoint_index, bucket_model=True)
        checkpoint_file = os.path.join(path_to_origin, self.checkpoint_index.split('/')[-1])

        with open(checkpoint_file, 'wb') as handler:
            response = requests.get(url_index, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None:  # no content length header
                print("couldn't download checkpoint index file")
                self.checkpoint_index = None
            else:
                print(f"Downloading {self.checkpoint_index}")
                for data in response.iter_content(chunk_size=1024):
                    handler.write(data)

        url_config = self.urls._get_presigned_url('get', self.config_file, bucket_model=True)
        config_file = os.path.join(path_to_origin, self.config_file.split('/')[-1])

        with open(config_file, 'wb') as handler:
            print(f"Downloading {self.config_file}")
            response = requests.get(url_config, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None:
                total_length = int(total_length)
                print("Couldn't download config file")
            else:
                for data in response.iter_content(chunk_size=1024):
                    handler.write(data)

        url_data = self.urls._get_presigned_url('get', self.checkpoint_data, bucket_model=True)
        checkpoint_file = os.path.join(path_to_origin, self.checkpoint_data.split('/')[-1])
        
        with open(checkpoint_file, 'wb') as handler:
            print(f"Downloading {self.checkpoint_data}")
            print('-----')    
            response = requests.get(url_data, stream=True)
            total_length = response.headers.get('content-length')
            if total_length is None:  # no content length header
                print("Couldn't download checkpoint data file")
                self.checkpoint_data = None
            else:
                dl = 0
                count = 0
                total_length = int(total_length)
                for data in response.iter_content(chunk_size=4096):
                    dl += len(data)
                    handler.write(data)
                    done = int(50 * dl / total_length)
                    if self.interactive:
                        sys.stdout.write(f"\r[{'=' * done}{' ' * (50 - done)}]")
                        sys.stdout.flush()
                    else:
                        if count%500==0:
                            print('['+'='* done+' ' * (50 - done)+']')
                    count += 1
        print('--*--')
        return path_to_origin

    def dl_train_test_split(self, prop):
        ''' Download, if it exists, the train_test_split for this training.'''
        to_send = {"project_token": self.project_token, "network_id": self.network_id, "training_id": self.training_id}
        if not self.dict_annotations:
            raise exceptions.ResourceNotFoundError("Dict annotations not found")
        try:
            r = requests.post(self.host + "get_repartition", data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        if r.status_code != 400:
            data = r.json()
            self.train_list_id = data["train"]["train_list_id"]
            self.eval_list_id = data["test"]["eval_list_id"]
            self.train_list = []
            self.eval_list = []
            for info in self.dict_annotations["images"]:
                pic_name = os.path.join(self.png_dir, info['external_picture_url'])
                if info["internal_picture_id"] in self.eval_list_id:
                    self.eval_list.append(pic_name)
                elif info["internal_picture_id"] in self.train_list_id:
                    self.train_list.append(pic_name)
            print("Datasplit retrieved from the platform")
        else:
            if r.text == "Could not find datasplit":
                print(f"{r.text} for the training_id {self.training_id}, splitting the dataset now with a {prop} proportion")
                self.train_test_split(prop=prop)
            else:
                raise exceptions.NetworkError(r.text)

    def dl_annotations(self, option="all"):
        """ Download all the annotations made on Picsell.ia Platform for your project.
            Called when checking out a network
            Args:
                option (str): Define what type of annotation to export (accepted or all)

            Raises:
                NetworkError: If Picsell.ia server is not responding or host is incorrect.
                ResourceNotFoundError: If we can't find any annotations for that project.
            """

        print("Downloading annotations ...")

        try:
            to_send = {"project_token": self.project_token, "type": option}
            r = requests.get(self.host + 'annotations', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Server is not responding, please check your host or Picsell.ia server status on twitter")
        if r.status_code != 200:
            raise exceptions.ResourceNotFoundError("No annotations were found for this project")

        self.dict_annotations = r.json()

        if len(self.dict_annotations.keys()) == 0:
            raise exceptions.ResourceNotFoundError("You don't have any annotations")

    def dl_latest_saved_model(self, path_to_save=None):
        """ Pull the latest  Picsell.ia Platform for your project.

                    Args:
                        option (str): Define what time of annotation to export (accepted or all)

                    Raises:
                        AuthenticationError: If `project_token` does not match the provided project_token on the platform.
                        NetworkError: If Picsell.ia server not responding or host is incorrect.
                        ResourceNotFoundError: If we can't find any annotations for that project."""

        if path_to_save is None:
            raise exceptions.InvalidQueryError("Please precise where you want to save .pb file.")
        if not os.path.isdir(path_to_save):
            os.makedirs(path_to_save)
        if not hasattr(self, "training_id"):
            raise exceptions.ResourceNotFoundError("Please init model first")

        if not hasattr(self, "auth"):
            raise exceptions.ResourceNotFoundError("Please init client first")

        to_send = {"project_token": self.project_token, "network_id": self.network_id}
        try:
            r = requests.get(self.host + 'get_saved_model_object_name', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Could not connect to Picsell.ia Backend")

        object_name = r.json()["object_name"]
        if object_name == 0:
            raise ValueError("There is no saved model on our backend for this project")

        url = self.urls._get_presigned_url("get", object_name, bucket_model=True)

        with open(os.path.join(path_to_save, 'saved_model.pb'), 'wb') as handler:
            print("Downloading exported model...")
            response = requests.get(url, stream=True)
            total_length = response.headers.get('content-length')
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                handler.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write(f"\r[{'=' * done}{' ' * (50 - done)}]")
                sys.stdout.flush()
            print(f'Exported model downloaded @ {path_to_save}')

    def dl_pictures(self):
        """Download your training set on the machine (Use it to dl images to Google Colab etc.)
           Save it to /project_id/images/*
           Perform train_test_split & send the repartition to Picsell.ia Platform

        Raises:
            ResourceNotFoundError : If no annotations in the Picsell.ia Client yet or images can't be downloaded"""

        if not hasattr(self, "dict_annotations"):
            raise exceptions.ResourceNotFoundError("Please dl_annotations model with dl_annotations()")

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
        #print(f"\n{cnt} images have been downloaded")

    def train_test_split(self, prop=0.8):

        if not hasattr(self, "dict_annotations"):
            raise exceptions.ResourceNotFoundError("Please download annotations first")

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

        print(f"{len(self.train_list_id)} images used for training and {len(self.eval_list_id)} images used for validation")

        label_train, label_test, cate = utils.get_labels_repartition_obj_detection(self.dict_annotations, self.index_url)

        to_send = {"project_token": self.project_token,
                   "train": {"train_list_id": self.train_list_id, "label_repartition": label_train, "labels": cate},
                   "eval": {"eval_list_id": self.eval_list_id, "label_repartition": label_test, "labels": cate},
                   "network_id": self.network_id, "training_id": self.training_id}

        try:
            r = requests.post(self.host + 'post_repartition', data=json.dumps(to_send), headers=self.auth)
            if r.status_code != 201:
                raise exceptions.NetworkError('Can not send repartition to Picsell.ia Backend')
            print("Repartition sent ..")
        except Exception:
            raise exceptions.NetworkError('Can not send repartition to Picsell.ia Backend')

    # Exporters 

    def send_logs(self, logs=None, logs_path=None):
        """Send training logs to Picsell.ia Platform
        Args:
            logs (dict): Dict of the training metric (Please find Getting Started Picsellia Docs to see how to get it)
        Raises:
            NetworkError: If it impossible to initialize upload
            ResourceNotFoundError: If no saved_model saved"""

        if not hasattr(self, "training_id") or not hasattr(self, "network_id") or not hasattr(self, "host") or not hasattr(self, "project_token"):
            raise exceptions.ResourceNotFoundError("Please initialize model with init_model()")

        if logs_path is not None:
            if not os.path.isfile(logs_path):
                raise FileNotFoundError("Logs file not found")
            with open(logs_path, 'r') as f:
                logs = json.load(f)

        if logs is None and logs_path is None:
            raise exceptions.ResourceNotFoundError("No log dict or path to logs .json given")

        try:
            to_send = {"project_token": self.project_token, "training_id": self.training_id, "logs": logs,
                       "network_id": self.network_id}
            r = requests.post(self.host + 'post_logs', data=json.dumps(to_send), headers=self.auth)
            if r.status_code != 201:
                raise exceptions.NetworkError(f"The logs have not been sent because {r.text}")

            print("Training logs have been sent to Picsell.ia Platform...\nYou can now inspect them on the platform.")

        except Exception:
            raise exceptions.NetworkError("Could not connect to Picsell.ia Server")

    def send_metrics(self, metrics=None, metrics_path=None):
        """Send evalutation metrics to Picsell.ia Platform

        Args:
            metrics (dict): Dict of the evaluation metrics (Please find Getting Started Picsellia Docs to see how to get it)
        Raises:
            NetworkError: If it impossible to initialize upload
            ResourceNotFoundError: If no saved_model saved

        """
        if not hasattr(self, "training_id") or not hasattr(self, "network_id") or not hasattr(self, "host") or not hasattr(self, "project_token"):
            raise exceptions.ResourceNotFoundError("Please initialize model first")

        if metrics_path is not None:
            if not os.path.isfile(metrics_path):
                raise FileNotFoundError("Metrics file not found")
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)

        if metrics is None and metrics_path is None:
            raise exceptions.ResourceNotFoundError("No metrics dict or path to metrics.json given")

        try:
            to_send = {"project_token": self.project_token, "training_id": self.training_id, "metrics": metrics,
                       "network_id": self.network_id}
            r = requests.post(self.host + 'post_metrics', data=json.dumps(to_send), headers=self.auth)
            if r.status_code != 201:
                raise exceptions.NetworkError(f"The evaluation metrics have not been sent because {r.text}")

            print("Evaluation metrics have been sent to Picsell.ia Platform...\nYou can now inspect them on the platform.")

        except Exception:
            raise exceptions.NetworkError("Could not connect to Picsell.ia Server")

    def send_results(self, _id=None, example_path_list=None):
        """Send Visual results to Picsell.ia Platform

        Args:
            _id (int): id of the training
        Raises:
            NetworkError: If impossible to connect to Picsell.ia Backend
            FileNotFoundError:
            ResourceNotFoundError:
        """

        if _id is None and example_path_list is None:
            results_dir = self.results_dir
            list_img = os.listdir(results_dir)
            assert len(list_img) != 0, 'No infered images found'

        elif _id is not None and example_path_list is None:
            base_dir = os.path.join(self.project_name, self.network_name)
            if str(_id) in os.listdir(base_dir):
                results_dir = os.path.join(base_dir, str(_id), 'results')
                list_img = os.listdir(results_dir)
                assert len(list_img) != 0, 'No example have been created'
            else:
                raise FileNotFoundError(os.path.join(base_dir, str(_id) + '/results'))

        elif (_id is None and example_path_list is not None) or (_id is not None and example_path_list is not None):
            for f in example_path_list:
                if not os.path.isfile(f):
                    raise FileNotFoundError(f"file not found @ {f}")
            list_img = example_path_list
            results_dir = ""

        object_name_list = []
        for img_path in list_img[:4]:
            file_path = os.path.join(results_dir, img_path)
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Can't locate file @ {file_path}")
            if _id is None and example_path_list is not None:
                OBJECT_NAME = os.path.join(self.project_id, self.network_id, str(self.training_id), "results", file_path.split('/')[-1])
            elif _id is not None and example_path_list is not None:
                OBJECT_NAME = os.path.join(self.project_id, self.network_id, str(_id), "results", file_path.split('/')[-1])
            else:
                OBJECT_NAME = file_path

            response = self.urls._get_presigned_url('post', OBJECT_NAME)
            to_send = {"project_token": self.project_token, "object_name": OBJECT_NAME}

            try:
                with open(file_path, 'rb') as f:
                    files = {'file': (OBJECT_NAME, f)}
                    http_response = requests.post(response['url'], data=response['fields'], files=files)
                    print('http:', http_response.status_code)
                if http_response.status_code == 204:
                    object_name_list.append(OBJECT_NAME)
            except Exception:
                raise exceptions.NetworkError("Could not upload examples to s3")

        to_send2 = {"project_token": self.project_token, "network_id": self.network_id, "training_id": self.training_id, "urls": object_name_list}
        try:
            r = requests.post(self.host + 'post_preview', data=json.dumps(to_send2), headers=self.auth)
            if r.status_code != 201:
                raise ValueError(f"Errors {r.text}")
            print("Your images have been uploaded to the platform")
        except Exception:
            raise exceptions.NetworkError("Could not upload to Picsell.ia Backend")

    def send_model(self, file_path=None):
        """Send frozen graph for inference to Picsell.ia Platform
        Raises:
            NetworkError: If it impossible to initialize upload
            ResourceNotFoundError: If no visual results saved in /project_id/network_id/training_id/results/"""

        if not hasattr(self, "training_id") or not hasattr(self, "network_id") or not hasattr(self, "host") or not hasattr(self, "project_token"):
            raise exceptions.ResourceNotFoundError("Please initialize model with init_model()")

        if file_path is not None:
            if not os.path.isdir(file_path):
                raise FileNotFoundError("You have not exported your model")

            trigger = False
            for fp in os.listdir(file_path):
                if fp.endswith('.pb'):
                    trigger = True
                    break
            if not trigger:
                raise exceptions.InvalidQueryError("wrong file type, please send a .pb file")

            file_path = utils.zipdir(file_path)
            self.OBJECT_NAME = os.path.join(self.network_id, str(self.training_id), file_path.split('/')[-1])

        else:
            if os.path.isdir(os.path.join(self.exported_model_dir, 'saved_model')):
                file_path = os.path.join(self.exported_model_dir, 'saved_model')
                trigger = False
                for fp in os.listdir(file_path):
                    if fp.endswith('.pb'):
                        trigger = True
                        break
                if not trigger:
                    raise exceptions.InvalidQueryError("Wrong file type, please send a .pb file")

                self.OBJECT_NAME = os.path.join(self.network_id, str(self.training_id), 'saved_model.zip')
                file_path = utils.zipdir(file_path)
            else:
                file_path = self.exported_model_dir
                trigger = False
                liste = os.listdir(file_path)

                if "variables" in liste and "saved_model.pb" in liste:
                    trigger = True

                if not trigger:
                    raise exceptions.InvalidQueryError("wrong file type, please send a .pb file")

                self.OBJECT_NAME = os.path.join(self.network_id, str(self.training_id), 'saved_model.zip')
                file_path = utils.zipdir(file_path)

        self.urls._init_multipart(self.OBJECT_NAME)
        parts = self.urls._upload_part(file_path, self.OBJECT_NAME, self.project_token)

        if self.urls._complete_part_upload(parts, self.OBJECT_NAME, 'model',
             self.project_token, self.network_id, self.training_id):
            print("Your exported model has been successfully uploaded to the platform.")

    def send_checkpoints(self, index_path=None, data_path=None, config_path=None):
        """Send training weights to the Picsell.ia platform
        Raises:
            NetworkError: If it impossible to initialize upload
            ResourceNotFoundError: If no visual results saved in /project_id/network_id/training_id/results/"""

        if not hasattr(self, "training_id") or not hasattr(self, "network_id") or not hasattr(self, "host") or not hasattr(self, "project_token"):
            raise exceptions.ResourceNotFoundError("Please initialize the client first")
        file_list = os.listdir(self.checkpoint_dir)
        if (index_path is not None) and (data_path is not None) and (config_path is not None):
            if not os.path.isfile(index_path):
                raise FileNotFoundError(f"{index_path}: no such file")
            if not os.path.isfile(data_path):
                raise FileNotFoundError(f"{data_path}: no such file")
            if not os.path.isfile(config_path):
                raise FileNotFoundError(f"{config_path}: no such file")

            ckpt_index_object = os.path.join(self.checkpoint_dir, index_path.split('/')[-1])
            ckpt_data_object = os.path.join(self.checkpoint_dir, data_path.split('/')[-1])
            self.OBJECT_NAME = ckpt_data_object
            if self.project_type != "classification":
                config_object = os.path.join(self.checkpoint_dir, config_path.split('/')[-1])

        elif (index_path is None) and (data_path is None) and (config_path is None):
            ckpt_id = max([int(p.split('-')[1].split('.')[0]) for p in file_list if 'index' in p])
            ckpt_index = f"model.ckpt-{ckpt_id}.index"  # TODO: what is this ?
            ckpt_index_object = os.path.join(self.checkpoint_dir, ckpt_index)
            index_path = ckpt_index_object

            ckpt_data = None
            for e in file_list:
                if f"{ckpt_id}.data" in e:
                    ckpt_data = e

            if ckpt_data is None:
                raise exceptions.ResourceNotFoundError("Could not find matching data file with index")

            ckpt_data_object = os.path.join(self.checkpoint_dir, ckpt_data)
            self.OBJECT_NAME = ckpt_data_object
            data_path = ckpt_data_object
            if self.project_type != "classification":
                if not os.path.isfile(os.path.join(self.checkpoint_dir, "pipeline.config")):
                    raise FileNotFoundError("No config file found")
                config_object = os.path.join(self.checkpoint_dir, "pipeline.config")
                config_path = config_object
        else:
            raise ValueError("checkpoint index, data and config files must be sent together to ensure compatibility")

        self.send_checkpoint_index(index_path, ckpt_index_object)
        print("Checkpoint index saved")

        if self.project_type != "classification":
            self.send_config_file(config_path, config_object)
        print("Config file saved")

        self.urls._init_multipart(self.OBJECT_NAME)
        parts = self.urls._upload_part(data_path, self.OBJECT_NAME, self.project_token)

        if self.urls._complete_part_upload(parts, ckpt_data_object, 'checkpoint',
             self.project_token, self.network_id, self.training_id):
            print("Your checkpoint has been successfully uploaded to the platform.")

    def send_checkpoint_index(self, filename, object_name):
        response = self.urls._get_presigned_url(method='post', object_name=object_name, bucket_model=True)
        try:
            with open(filename, 'rb') as f:
                files = {'file': (filename, f)}
                http_response = requests.post(response['url'], data=response['fields'], files=files)
                print('http:', http_response.status_code)
            if http_response.status_code == 204:
                index_info = {"project_token": self.project_token, "object_name": object_name,
                              "network_id": self.network_id}
                r = requests.post(self.host + 'post_checkpoint_index', data=json.dumps(index_info), headers=self.auth)
                if r.status_code != 201:
                    raise ValueError(f"Errors {r.text}")
        except Exception:
            raise exceptions.NetworkError("Could not upload checkpoint to s3")

    def send_config_file(self, filename, object_name):
        response = self.urls._get_presigned_url('post', object_name, bucket_model=True)
        try:
            with open(filename, 'rb') as f:
                files = {'file': (filename, f)}
                http_response = requests.post(response['url'], data=response['fields'], files=files)
                print('http:', http_response.status_code)
            if http_response.status_code == 204:
                index_info = {"project_token": self.project_token, "object_name": object_name, "network_id": self.network_id}
                r = requests.post(self.host + 'post_config', data=json.dumps(index_info), headers=self.auth)
                if r.status_code != 201:
                    raise ValueError(f"Errors {r.text}")
        except Exception:
            raise exceptions.NetworkError("Could not upload config to s3")

    def send_labelmap(self, label_path=None):
        """Attach to network, it allow nicer results visualisation on hub playground
        """

        if label_path is not None:
            if not os.path.isfile(label_path):
                raise FileNotFoundError(f"label map @ {label_path} doesn't exists")
            with open(label_path, 'r') as f:
                label_map = json.load(f)

        if not hasattr(self, "label_map") and label_path is None:
            raise ValueError("Please Generate label map first")

        if label_path is not None:
            to_send = {"project_token": self.project_token, "labels": label_map, "network_id": self.network_id}
        else:
            to_send = {"project_token": self.project_token, "labels": self.label_map, "network_id": self.network_id}

        try:
            r = requests.get(self.host + 'attach_labels', data=json.dumps(to_send), headers=self.auth)
        except Exception:
            raise exceptions.NetworkError("Could not connect to picsellia backend")
        if r.status_code != 201:
            raise ValueError(f"Could not upload label to server because {r.text}")

    def send_everything(self, training_logs=None, metrics=None):
        '''Wrapper function to send data from the training'''

        self.send_labelmap()

        if training_logs:
            self.send_logs(training_logs)
        if metrics:
            self.send_metrics(metrics)
        try:
            self.send_checkpoints()
        except Exception as e:
            print(f"The training checkpoint wasn't uploaded because: {e}")
        try:
            self.send_results()
        except Exception as e:
            print(f"The results were not uploaded because: {e}")
        try:
            self.send_model()
        except Exception as e:
            print(f"The exported model wasn't uploaded because: {e}")

    # Uploaders

    def upload_annotations(self, annotations, _format='picsellia'):
        """ Upload annotation to Picsell.ia Backend
        Please find in our Documentation the annotations format accepted to upload
        Args :
            annotation (dict)
            _format (str) : Chose between train & test

        Raises:
            ValueError
            NetworkError: If impossible to upload to Picsell.ia server"""

        if not isinstance(_format, str):
            raise ValueError(f'format must be a string not {type(_format)}')

        if _format != 'picsellia':
            if not isinstance(annotations, dict):
                raise ValueError(f'dict of annotations in images must be a dict_annotations not {type(annotations)}')

            print("Chunking your annotations ...")
            all_chunk = []
            for im in annotations["images"]:
                chunk_tmp = []
                for ann in annotations["annotations"]:
                    if ann["image_id"] == im["id"]:
                        chunk_tmp.append(ann)
                all_chunk.append({
                    "images": [im],
                    "annotations": chunk_tmp,
                    "categories": annotations["categories"]
                })
            print("Upload starting ..")
            self.urls.project_token = self.project_token
            self.urls.project_type = self.project_type
            pool = ThreadPool(processes=8)
            pool.map(self.urls._send_chunk_custom, all_chunk)
    
    class Dataset:

        def __init__(self, host, auth):
            self.host = host
            self.auth = auth 
            self.urls = urls(self.host, self.auth)
        def get_dataset_list(self):
            r = requests.get(self.host + 'get_dataset_list', headers=self.auth)
            dataset_names = r.json()["dataset_names"]
            print(dataset_names)
            return dataset_names

        def create_dataset(self, dataset_name):
            if not isinstance(dataset_name, str):
                raise ValueError(f'dataset_name must be a string not {type(dataset_name)}')
            dataset_info = {"dataset_name": dataset_name}
            r = requests.get(self.host + 'create_dataset', data=json.dumps(dataset_info), headers=self.auth)
            new_dataset = r.json()["new_dataset"]
            if not new_dataset:
                dataset_names = r.json()["dataset_names"]
                raise ValueError("You already have a dataset with this name, please pick another one")
            else:
                dataset_id = r.json()["dataset_id"]
                print(f"Dataset {dataset_name} created successfully")
                return dataset_id

        def send_dataset_thumbnail(self, dataset_name, img_path):
            if not isinstance(dataset_name, str):
                raise ValueError(f'dataset_name must be a string not {type(dataset_name)}')
            data = {"dataset_name": dataset_name}
            with open(img_path, 'rb') as f:
                files = {'file': (img_path, f)}
                http_response = requests.post(self.host + 'send_dataset_thumbnail', data=data, files=files, headers=self.auth)
                if http_response.status_code == 200:
                    print(http_response.text)
                else:
                    raise exceptions.NetworkError("Could not upload thumbnail")

        def create_and_upload_dataset(self, dataset_name, path_to_images):
            """ Create a dataset and upload the images to Picsell.ia
            Args :
                dataset_name (str)
                path_to_images (str)
            Raises:
                ValueError
                NetworkError: If impossible to upload to Picsell.ia server"""

            if not isinstance(dataset_name, str):
                raise ValueError(f'dataset_name must be a string not {type(dataset_name)}')

            if not isinstance(path_to_images, str):
                raise ValueError(f'path_to_images must be a string not {type(path_to_images)}')

            if not os.path.isdir(path_to_images):
                raise FileNotFoundError(f'{path_to_images} is not a directory')

            dataset_id = self.create_dataset(dataset_name)
            print("Dataset created, starting upload...")
            image_list = os.listdir(path_to_images)
            thumb_path = os.path.join(path_to_images, image_list[0])
            self.send_dataset_thumbnail(dataset_name, thumb_path)
            if len(image_list) > 0:
                object_name_list = []
                image_name_list = []
                sizes_list = []
                for img_path in image_list:
                    file_path = os.path.join(path_to_images, img_path)
                    if not os.path.isfile(file_path):
                        raise FileNotFoundError(f"Can't locate file @ {file_path}")
                    OBJECT_NAME = os.path.join(dataset_id, img_path)

                    response = self.urls._get_presigned_url(method='post', object_name=OBJECT_NAME)

                    try:
                        im = Image.open(file_path)
                        width, height = im.size
                        with open(file_path, 'rb') as f:
                            files = {'file': (OBJECT_NAME, f)}
                            http_response = requests.post(response['url'], data=response['fields'], files=files)
                            print('http:', http_response.status_code)
                        if http_response.status_code == 204:
                            object_name_list.append(OBJECT_NAME)
                            image_name_list.append(img_path)
                            sizes_list.append([width, height])
                    except Exception:
                        raise exceptions.NetworkError("Could not upload to the Picsell.ia platform")

                to_send2 = {"dataset_id": dataset_id,
                            "object_list": object_name_list,
                            "image_list": image_list,
                            "sizes_list": sizes_list}
                try:
                    r = requests.post(self.host + 'create_pictures_for_dataset', data=json.dumps(to_send2), headers=self.auth)
                    if r.status_code != 200:
                        raise ValueError("Errors.")
                    print("Images have been uploaded to the Picsell.ia platform")
                except Exception:
                    raise exceptions.NetworkError("Could not upload to the Picsell.ia platform")