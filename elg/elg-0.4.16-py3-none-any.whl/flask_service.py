import inspect
import json
import re
from collections.abc import Iterable
from pathlib import Path
from typing import Dict, List

from loguru import logger

try:
    import docker
    from flask import Flask
    from flask import request as flask_request
    from flask_json import JsonError
    from requests_toolbelt import MultipartDecoder
except:
    raise ImportError(
        "Extra dependencies need to be install to use the FlaskService class. Please run: `pip install elg[flask]`."
    )

from .model import (AudioRequest, Failure, Progress, ResponseObject,
                    StructuredTextRequest, TextRequest)
from .utils.docker import COPY_FOLDER, DOCKERFILE, ENTRYPOINT_FLASK


class FlaskService:
    """
    Class to help the creation of an ELG compatible service from a python model.
    Extra dependencies need to be install to use the FlaskService class. Please run: `pip install elg[flask]`.
    """

    requirements = ["gunicorn", "elg[flask]"]

    def __init__(self, name: str):
        """
        Init function of the FlaskService

        Args:
            name (str): Name of the service. It doesn't have any importance.
        """
        self.name = name
        self.app = Flask(name)
        # Don't add an extra "status" property to JSON responses - this would break the API contract
        self.app.config["JSON_ADD_STATUS"] = False
        # Don't sort properties alphabetically in response JSON
        self.app.config["JSON_SORT_KEYS"] = False
        self.app.add_url_rule("/process", "process", self.process, methods=["POST"])

    def run(self):
        """
        Method to start the flask app.
        """
        self.app.run()

    def process(self):
        """
        Main request processing logic - accepts a JSON request and returns a JSON response.
        """
        logger.info("Process request")
        even_stream = True if "text/event-stream" in flask_request.accept_mimetypes else False
        logger.debug(f"Accept MimeTypes: {flask_request.accept_mimetypes}")
        logger.info(f"Accept even-stream: {even_stream}")
        if "application/json" in flask_request.content_type:
            data = flask_request.get_json()
        elif "multipart/form-data" in flask_request.content_type:
            decoder = MultipartDecoder(flask_request.get_data(), flask_request.content_type)
            data = {}
            for part in decoder.parts:
                headers = {k.decode(): v.decode() for k, v in part.headers.items()}
                if "application/json" in headers["Content-Type"]:
                    for k, v in json.loads(part.content.decode()).items():
                        data[k] = v
                elif "audio" in headers["Content-Type"]:
                    data["content"] = part.content
                else:
                    raise ValueError("Unknown Content-Type in multipart request")
        else:
            raise ValueError()

        logger.debug(f"Data type: {data.get('type')}")
        if data.get("type") == "audio":
            request = AudioRequest(**data)
        elif data.get("type") == "text":
            request = TextRequest(**data)
        elif data.get("type") == "structuredText":
            request = StructuredTextRequest(**data)
        else:
            self.invalid_request_error()
        logger.info(f"Call with the input: {request}")
        try:
            response = self.process_request(request)
        except:
            logger.debug("Error during the request processing.")
            response = Failure(
                errors=[
                    {"code": "elg.internalError", "text": "Internal error during processing", "params": ["message"]}
                ]
            )
        if isinstance(response, Failure):
            logger.info(f"Get error message: {response}")
            response = {"failure": response.dict(by_alias=True)}
            logger.info(f"Return: {response}")
        elif isinstance(response, ResponseObject):
            logger.info(f"Get response: {response}")
            response = {"response": response.dict(by_alias=True)}
            logger.info(f"Return: {response}")
            return response
        elif isinstance(response, Iterable):
            logger.info(f"Get iterable response")
            if even_stream:
                return self.app.response_class(self.generator_mapping(response), mimetype="text/event-stream")
            else:
                response = self.get_response_from_generator(response)
                logger.info(f"Get response: {response}")
                response = {"response": response.dict(by_alias=True)}
                logger.info(f"Return: {response}")
                return response
        else:
            raise ValueError("Unknown returned type")

    def invalid_request_error(self):
        """
        Generates a valid ELG "failure" response if the request cannot be parsed
        """
        raise JsonError(
            status_=400, failure={"errors": [{"code": "elg.request.invalid", "text": "Invalid request message"}]}
        )

    def process_request(self, request):
        """
        Method to process the request object. This method only calls the right process method regarding the type of the request.
        """
        if request.type == "text":
            logger.info("Process text request")
            return self.process_text(request)
        elif request.type == "structuredText":
            return self.process_structured_text(request)
        elif request.type == "audio":
            return self.process_audio(request)
        self.invalid_request_error()

    def process_text(self, request: TextRequest):
        """
        Method to implement if the service takes text as input.

        Args:
            request (TextRequest): TextRequest object.
        """
        raise NotImplementedError()

    def process_structured_text(self, request: StructuredTextRequest):
        """
        Method to implement if the service takes structured text as input.

        Args:
            request (StructuredTextRequest): StructuredTextRequest object.
        """
        raise NotImplementedError()

    def process_audio(self, request: AudioRequest):
        """
        Method to implement if the service takes audio as input.

        Args:
            request (AudioRequest): AudioRequest object.
        """
        raise NotImplementedError()

    @staticmethod
    def generator_mapping(generator):
        end = False
        try:
            for message in generator:
                if end == True:
                    logger.warning(
                        (
                            "The service has already returned a ResponseObject or Failure message but continue to return the following message:\n"
                            f"{message.dict(by_alias=True)}\nThis message will be ignored and not returned to the user."
                        )
                    )
                    continue
                if isinstance(message, Failure):
                    logger.info(f"Get failure: {message}")
                    message = json.dumps({"failure": message.dict(by_alias=True)})
                    end = True
                elif isinstance(message, Progress):
                    logger.info(f"Get progress: {message}")
                    message = json.dumps({"progress": message.dict(by_alias=True)})
                elif isinstance(message, ResponseObject):
                    logger.info(f"Get response: {message}")
                    message = json.dumps({"response": message.dict(by_alias=True)})
                    end = True
                yield f"data:{message}\r\n\r\n"
        except:
            message = json.dumps(
                {
                    "failure": Failure(
                        errors=[
                            {
                                "code": "elg.internalError",
                                "text": "Internal error during processing",
                                "params": ["message"],
                            }
                        ]
                    ).dict(by_alias=True)
                }
            )
            yield f"data:{message}\r\n\r\n"

    @staticmethod
    def get_response_from_generator(generator):
        response = None
        for message in generator:
            if response is not None:
                logger.warning(
                    (
                        "The service has already returned a ResponseObject or Failure message but continue to return the following message:\n"
                        f"{message.dict(by_alias=True)}\nThis message will be ignored and not returned to the user."
                    )
                )
                continue
            if isinstance(message, (ResponseObject, Failure)):
                response = message
        if response is None:
            return Failure(
                errors=[{"code": "elg.response.invalid", "text": "Invalid response message", "params": ["message"]}]
            )
        return response

    @classmethod
    def create_requirements(cls, requirements: List = [], path: str = None):
        """
        Class method to create the correct requirements.txt file.

        Args:
            requirements (List, optional): List of required pip packages. Defaults to [].
            path (str, optional): Path where to generate the file. Defaults to None.
        """
        if path == None:
            path = Path(inspect.getsourcefile(cls))
        else:
            path = Path(path)
        requirements = cls.requirements + requirements
        with open(path.parent / "requirements.txt", "w") as f:
            f.write("\n".join(set(requirements)))

    @classmethod
    def create_docker_files(
        cls,
        required_files: List[str] = [],
        required_folders: List[str] = [],
        commands: List[str] = [],
        base_image: str = "python:slim",
        path: str = None,
    ):
        """Class method to create the correct Dockerfile.

        Args:
            required_files (List[str], optional): List of files needed for the service. Defaults to [].
            required_folders (List[str], optional): List of folders needed for the service. Defaults to [].
            commands (List[str], optional): List off additional commands to run in the Dockerfile. Defaults to [].
            base_image (str, optional): Name of the base Docker image used in the Dockerfile. Defaults to 'python:slim'.
            path (str, optional): Path where to generate the file. Defaults to None.
        """
        if path == None:
            path = Path(inspect.getsourcefile(cls))
        else:
            path = Path(path)
        required_files = [path.name] + required_files
        required_folders = "\n".join(
            [COPY_FOLDER.format(folder_name=str(Path(folder))) for folder in required_folders]
        )
        commands = ["RUN " + cmd for cmd in commands]
        service_script = path.name[:-3]  # to remove .py
        # The docker-entrypoint file is a Linux shell script so _must_ be
        # written with Unix-style line endings, even if the build is being done
        # on Windows.  To ensure this we write in binary mode.
        with open(path.parent / "docker-entrypoint.sh", "wb") as f:
            f.write(ENTRYPOINT_FLASK.format(service_script=service_script).encode("utf-8"))
        with open(path.parent / "Dockerfile", "w") as f:
            f.write(
                DOCKERFILE.format(
                    base_image=base_image,
                    required_files=" ".join(required_files),
                    required_folders=required_folders,
                    commands="\n".join(commands),
                )
            )

    @classmethod
    def docker_build_image(cls, tag: str, pull: bool = True, path: str = None, **kwargs):
        """
        Class method to do `docker build ...` in python.
        """
        if path == None:
            path = Path(inspect.getsourcefile(cls))
        else:
            path = Path(path)
        client = docker.from_env()
        image, _ = client.images.build(path=str(path.parent), tag=tag, pull=pull, **kwargs)
        return image

    @classmethod
    def docker_push_image(cls, repository: str, tag: str, username: str = None, password: str = None, **kwargs):
        """
        Class method to do `docker push ...` in python.
        """
        client = docker.from_env()
        if username is not None and password is not None:
            auth_config = {"username": username, "password": password}
            client.images.push(repository=repository, tag=tag, auth_config=auth_config, stream=True, **kwargs)
        client.images.push(repository=repository, tag=tag, stream=True, **kwargs)
        return

    @classmethod
    def docker_build_push_image(
        cls,
        repository: str,
        tag: str,
        pull: bool = True,
        username: str = None,
        password: str = None,
        build_kwargs: Dict = {},
        push_kwargs: Dict = {},
    ):
        cls.docker_build_image(tag=f"{repository}:{tag}", pull=pull, **build_kwargs)
        cls.docker_push_image(repository=repository, tag=tag, username=username, password=password, **push_kwargs)
        return None
