from contextlib import suppress
from convisoappsec.flow.util import SourceCodeCompressor
from datetime import datetime
from uuid import uuid4
from .exceptions import *
from threading import Thread
from threading import Lock
import docker
import os
import tempfile
import tarfile

mutex = Lock()
class EventLogging(Thread):

    def __init__(self, logger, events):
        super().__init__(name='Docker-Events', daemon=True)
        self.logger = logger
        self.events = events

    def docker_log(self, event):
        ts = datetime.fromtimestamp(event['time']).strftime('%d/%m/%Y %H:%M:%S')
        message = "{timestamp}|{Type} {Action} on {Actor[ID]}".format(**event, timestamp=ts)
        self.logger.debug(message)

    def run(self):
        for event in self.events:
            if 'flow-cli-' in event['Actor']['ID']:
                self.docker_log(event)
        self.logger.debug('Docker Events closed')
            

class Credentials:

    AUTHS = {}

    def __init__(self, docker, logger):
        self.docker = docker
        self.logger = logger

    def login(self, registry, password, username='AWS'):
        mutex.acquire()
        if not registry in Credentials.AUTHS.keys():
            self.logger.info("   \U0001F511 Checking Authorization for {0}".format(registry))
            login_args = {
                'registry': registry,
                'username': username,
                'password': password,
                'reauth': True,
            }
            try:
                login_result = self.docker.login(**login_args)
                status = login_result['Status']
                self.logger.debug("Login result was {0}".format(login_result))
                if status == 'Login Succeeded':
                    Credentials.AUTHS[registry] = password
                    self.logger.info('   \U0001F513 ' + status)
            except docker.errors.APIError:
                self.logger.debug("Docker API Error")
        mutex.release()


class SCSCommon:

    # General Settings
    DEFAULT_REGISTRY = 'docker.convisoappsec.com'
    DEFAULT_TAG = 'latest'
    DEFAULT_CONTAINER_CODE_DIR = '/code'
    SUCCESS_EXIT_CODE = 0
    DOCKER_CLIENT = None
    DOCKER_CREDENTIALS = None
    DOCKER_EVENTS = None
    DOCKER_EVENTS_THREAD = None
    TEMPDIR = None

    def __init__(self, tag=None, registry=None, repository_name=None, token=None, logger=None, command=None, repository_dir=None):
        self.logger = logger
        self.token = token
        uuid = str(uuid4())
        self.docker = self._get_docker_client()
        self.__container_name = "flow-cli-{0}".format(uuid)
        self.__docker_events = self._get_docker_events()
        self.__docker_events_thread = self._get_docker_events_thread()
        self.__credentials = self._get_docker_credentials()
        self.__source_code_volume_name = "flow-cli-{0}".format(uuid)

        self.container = None
        self.tag = tag or self.DEFAULT_TAG
        self.registry = registry or self.DEFAULT_REGISTRY 
        self.repository_name = repository_name
        self.command = command
        self.repository_dir = repository_dir
        if token:
            self._login(self.token)
    
    def _get_docker_client(self):
        mutex.acquire()
        if not SCSCommon.DOCKER_CLIENT:
            SCSCommon.DOCKER_CLIENT = docker.from_env(
                version="auto"
            )
        mutex.release()
        return SCSCommon.DOCKER_CLIENT

    def _get_docker_credentials(self):
        mutex.acquire()
        if not SCSCommon.DOCKER_CREDENTIALS:
            SCSCommon.DOCKER_CREDENTIALS = Credentials(
                docker=self.docker,
                logger=self.logger
            )
        mutex.release()
        return SCSCommon.DOCKER_CREDENTIALS

    def _get_docker_events(self):
        mutex.acquire()
        if not SCSCommon.DOCKER_EVENTS:
            SCSCommon.DOCKER_EVENTS = self.docker.events(decode=True)
        mutex.release()
        return SCSCommon.DOCKER_EVENTS

    def _get_docker_events_thread(self):
        mutex.acquire()
        if not SCSCommon.DOCKER_EVENTS_THREAD:
            SCSCommon.DOCKER_EVENTS_THREAD = EventLogging(
                logger=self.logger,
                events=self.__docker_events,
            )
            SCSCommon.DOCKER_EVENTS_THREAD.start()
        mutex.release()
        return SCSCommon.DOCKER_EVENTS_THREAD

    def _login(self, password, username='AWS'):
        self.__credentials.login(
            registry=self.registry,
            password=password,
        )
    
    def _get_tmpdir(self):
        if not SCSCommon.TEMPDIR:
            SCSCommon.TEMPDIR = tempfile.mkdtemp(prefix='conviso-sca-', dir=self.repository_dir)
        self.logger.debug("Created artifacts directory at {}".format(
            SCSCommon.TEMPDIR
        ))
        return SCSCommon.TEMPDIR

    @property
    def size(self):
        registry_data = self.docker.images.get_registry_data(
            self.image
        )

        descriptor = registry_data.attrs.get('Descriptor', {})
        return descriptor.get('size') * 1024 * 1024

    def run(self):
        container = self.__create_container()
        self.__load_source_code(container)
        container.start()

        container_stderr = container.logs(
            stream=True,
            stdout=False,
            stderr=True
        )

        container_stdout = container.logs(
            stream=True,
            stdout=True,
            stderr=False,
        )

        for message in container_stdout:
            self.logger.debug(message)


    def wait(self):
        wait_result = self.__container.wait()
        status_code = wait_result.get('StatusCode')
        
        if not status_code == self.SUCCESS_EXIT_CODE:
            raise CommonException()
        
        return status_code

    def __has_method(self, method_name):
        return hasattr(self, method_name)

    def pull(self):
        '''
        {
            'status': 'Downloading',
            'progressDetail': {'current': int, 'total': int},
            'id': 'string'
        }
        '''
        self.logger.debug("Pulling scanner image {}. It might takes some minutes.".format(self.repository_name))
        if self.has_pre_pull:
            self._pre_pull()
            self.logger.debug("End of pre_pull method.")
        try:
            return self.docker.images.pull(
            repository=self.repository, 
            tag=self.tag
            )
        except docker.errors.ImageNotFound:
            self.logger.debug("Image {} not found on registry".format(self.image))
            return False

    def __get_container(self):
        return self.docker.containers.get(
            self.__container_name
        )

    @property
    def __container(self):
        try:
            return self.__get_container()
        except:
            return self.__create_container()

    def __create_container(self):
        self.logger.debug("Creating Container {0}".format(self.__container_name))
        return self.docker.containers.create(
            self.image,
            name=self.__container_name,
            volumes=self.volumes,
            detach=True,
            command=self.command
        )

    @property
    def repository(self):
        return "{registry}/{repository_name}".format(
            registry=self.registry,
            repository_name=self.repository_name,
        )

    @property
    def image(self):
        return "{repository}:{tag}".format(
            repository=self.repository,
            tag=self.tag,
        )

    @property
    def has_pre_pull(self):
        return self.__has_method('_pre_pull')

    @property
    def has_read_scan_stdout(self):
        return self.__has_method('_read_scan_stdout')

    @property
    def has_read_scan_stderr(self):
        return self.__has_method('_read_scan_stderr')

    @property
    def volumes(self):
        return {
            self.__source_code_volume_name:{
                'bind': SCSCommon.DEFAULT_CONTAINER_CODE_DIR,
                'mode': 'rw',
            }
        }

    @property
    def name(self):
        return self.__container_name

    def __del__(self):
        self.logger.debug("Removing container {0}".format(self.__container_name))
        with suppress(Exception):
            self.container.remove(v=True, force=True)

    def __load_source_code(self, container):
        try:
            self.logger.debug("Loading Source code into {0}".format(self.__container_name))
            with tempfile.TemporaryFile() as fileobj:
                compressor = SourceCodeCompressor(
                    self.repository_dir
                )

                compressor.write_to(fileobj)
                fileobj.seek(0)

                container.put_archive(
                    SCSCommon.DEFAULT_CONTAINER_CODE_DIR,
                    fileobj
                )
        except Exception as e:
            self.logger.error(e)

    def collect_artifacts(self):
        artifact_path = "/{}.json".format(
            self.repository_name
        )
        self.logger.debug("Collecting Artifacts from {0}".format(self.__container_name))
        try:
            container = self.__container
            chunks, _ = container.get_archive(
                artifact_path
            )
            tempdir = self._get_tmpdir()
            reports_tarball_file = tempfile.TemporaryFile()
            for chunk in chunks:
                reports_tarball_file.write(chunk)
            reports_tarball_file.seek(0)
            reports_tarball = tarfile.open(mode="r|", fileobj=reports_tarball_file)
            reports_tarball.extractall(path=tempdir)
            reports_tarball.close()
            reports_tarball_file.close()
            self.logger.debug("artifact from {} saved to {}{}".format(
                self.__container_name, 
                tempdir,
                artifact_path
                )
            )
            return tempdir+artifact_path
        except docker.errors.NotFound:
            self.logger.debug("{} does not detected issues, continuing...".format(
                self.repository_name
            ))
        except Exception as e:
            self.logger.error(e)