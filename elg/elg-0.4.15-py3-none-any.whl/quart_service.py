import inspect
import json
from collections.abc import AsyncIterable
from pathlib import Path
from typing import Dict, List

from loguru import logger

try:
    import aiohttp
    import docker
    from quart import Quart, make_response
    from quart import request as input_request
    from requests_toolbelt import MultipartDecoder
except:
    raise ImportError(
        "Extra dependencies need to be install to use the QuartService class. Please run: `pip install elg[quart]`."
    )

from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from .model import (AudioRequest, Failure, Progress, ResponseObject,
                    StructuredTextRequest, TextRequest)
from .utils.docker import COPY_FOLDER, DOCKERFILE, ENTRYPOINT_QUART


class ProcessingError(Exception):
    def __init__(self, status_code, code, text, *params):
        self.status_code = status_code
        self.code = code
        self.text = text
        self.params = params

    @staticmethod
    def InternalError(text):
        return ProcessingError(500, "elg.service.internalError", "Internal error during processing: {0}", text)

    @staticmethod
    def InvalidRequest():
        return ProcessingError(400, "elg.request.invalid", "Invalid request message")

    @staticmethod
    def TooLarge():
        return ProcessingError(413, "elg.request.too.large", "Request size too large")

    @staticmethod
    def UnsupportedMime(mime):
        return ProcessingError(
            400, "elg.request.text.mimeType.unsupported", "MIME type {0} not supported by this service", mime
        )

    @staticmethod
    def UnsupportedType(request_type):
        return ProcessingError(
            400, "elg.request.type.unsupported", "Request type {0} not supported by this service", request_type
        )

    def to_json(self):
        return {
            "failure": {
                "errors": [
                    {
                        "code": self.code,
                        "text": self.text,
                        "params": self.params,
                    }
                ]
            }
        }


class QuartService:
    """
    Class to help the creation of an ELG compatible service from a python model using Quart.
    Extra dependencies need to be install to use the QuartService class. Please run: `pip install elg[quart]`.
    """

    requirements = ["elg[quart]"]

    def __init__(self, name: str, request_size_limit: int = None):
        """
        Init function of the QuartService

        Args:
            name (str): Name of the service. It doesn't have any importance.
        """
        self.name = name
        self.app = Quart(name)
        # Don't add an extra "status" property to JSON responses - this would break the API contract
        self.app.config["JSON_ADD_STATUS"] = False
        # Don't sort properties alphabetically in response JSON
        self.app.config["JSON_SORT_KEYS"] = False

        if request_size_limit is not None:
            self.app.config["MAX_CONTENT_LENGTH"] = request_size_limit

        # Exceptions handling
        self.app.register_error_handler(ProcessingError, self.error_message)
        self.app.register_error_handler(BadRequest, lambda err: self.error_message(ProcessingError.InvalidRequest()))
        self.app.register_error_handler(
            RequestEntityTooLarge, lambda err: self.error_message(ProcessingError.TooLarge())
        )

        self.app.before_serving(self.setup)
        self.app.after_serving(self.shutdown)

        self.app.add_url_rule("/health", "health", self.health, methods=["GET"])
        self.app.add_url_rule("/process", "process", self.process, methods=["POST"])

    def run(self):
        """
        Method to start the app.
        """
        self.app.run()

    @staticmethod
    def error_message(err):
        return err.to_json(), err.status_code

    async def setup(self):
        """
        One-time setup tasks that must happen before the first request is
        handled, but require access to the event loop so cannot happen at the top
        level.
        """
        # Create the shared aiohttp session
        self.session = aiohttp.ClientSession()
        # or you may wish to configure things like default headers, e.g.
        # session = aiohttp.ClientSession(headers = {'X-API-Key':os.environ.get('APIKEY')})

    async def shutdown(self):
        """
        Logic that must run at shutdown time, after the last request has been
        handled.
        """
        if self.session is not None:
            await self.session.close()

    def health(self):
        return {"alive": True}

    async def process(self):
        """
        Main request processing logic - accepts a JSON request and returns a JSON response.
        """
        logger.info("Process request")
        even_stream = True if "text/event-stream" in input_request.accept_mimetypes else False
        logger.debug(f"Accept MimeTypes: {input_request.accept_mimetypes}")
        logger.info(f"Accept even-stream: {even_stream}")
        if "application/json" in input_request.content_type:
            data = await input_request.get_json()
        elif "multipart/form-data" in input_request.content_type:
            input_request_data = await input_request.get_data()
            decoder = MultipartDecoder(input_request_data, input_request.content_type)
            data = {}
            for part in decoder.parts:
                headers = {k.decode(): v.decode() for k, v in part.headers.items()}
                if "application/json" in headers["Content-Type"]:
                    for k, v in json.loads(part.content.decode()).items():
                        data[k] = v
                elif "audio" in headers["Content-Type"]:
                    data["content"] = part.content
                else:
                    raise ProcessingError.UnsupportedType(str(headers["Content-Type"]))
        else:
            raise ProcessingError.UnsupportedType(input_request.content_type)

        logger.debug(f"Data type: {data.get('type')}")
        if data.get("type") == "audio":
            request = AudioRequest(**data)
        elif data.get("type") == "text":
            request = TextRequest(**data)
        elif data.get("type") == "structuredText":
            request = StructuredTextRequest(**data)
        else:
            raise ProcessingError.InvalidRequest()
        logger.info(f"Call with the input: {request}")
        logger.info("Await for the coroutine...")
        try:
            response = await self.process_request(request)
        except:
            raise ProcessingError.InvalidRequest()
        if isinstance(response, Failure):
            logger.info(f"Get error message: {response}")
            response = {"failure": response.dict(by_alias=True)}
            logger.info(f"Return: {response}")
        elif isinstance(response, ResponseObject):
            logger.info(f"Get response: {response}")
            response = {"response": response.dict(by_alias=True)}
            logger.info(f"Return: {response}")
            return response
        elif isinstance(response, AsyncIterable):
            logger.info(f"Get async iterable response")
            if even_stream:
                response = await make_response(
                    self.generator_mapping(response), 200, {"Content-Type": "text/event-stream"}
                )
                # Quart will by default time-out long responses, may be necessary to disable that
                # or at least set a longer timeout than usual
                response.timeout = None
                return response
            else:
                response = await self.get_response_from_generator(response)
                logger.info(f"Get response: {response}")
                if isinstance(response, ResponseObject):
                    response = {"response": response.dict(by_alias=True)}
                elif isinstance(response, Failure):
                    response = {"failure": response.dict(by_alias=True)}
                else:
                    raise ProcessingError.InvalidRequest()
                logger.info(f"Return: {response}")
                return response
        else:
            raise ProcessingError.InvalidRequest()

    async def process_request(self, request):
        """
        Method to process the request object. This method only calls the right process method regarding the type of the request.
        """
        if request.type == "text":
            logger.debug("Process text")
            try:
                return await self.process_text(request)
            except:
                return self.process_text(request)
        if request.type == "structuredText":
            logger.debug("Process structured text")
            try:
                return await self.process_structured_text(request)
            except:
                return self.process_structured_text(request)
        if request.type == "audio":
            logger.debug("Process audio")
            try:
                return await self.process_audio(request)
            except:
                return self.process_audio(request)
        raise ProcessingError.InvalidRequest()

    async def process_text(self, request: TextRequest):
        """
        Method to implement if the service takes text as input.

        Args:
            request (TextRequest): TextRequest object.
        """
        raise ProcessingError.UnsupportedType()

    async def process_structured_text(self, request: StructuredTextRequest):
        """
        Method to implement if the service takes structured text as input.

        Args:
            request (StructuredTextRequest): StructuredTextRequest object.
        """
        raise ProcessingError.UnsupportedType()

    async def process_audio(self, request: AudioRequest):
        """
        Method to implement if the service takes audio as input.

        Args:
            request (AudioRequest): AudioRequest object.
        """
        raise ProcessingError.UnsupportedType()

    @staticmethod
    async def generator_mapping(generator):
        end = False
        try:
            async for message in generator:
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
    async def get_response_from_generator(generator):
        response = None
        async for message in generator:
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
            f.write(ENTRYPOINT_QUART.format(service_script=service_script).encode("utf-8"))
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
        Class method to do `docker build ...` in python. Better to use the docker cli instead of this method.
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
        Class method to do `docker push ...` in python. Better to use the docker cli instead of this method.
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
