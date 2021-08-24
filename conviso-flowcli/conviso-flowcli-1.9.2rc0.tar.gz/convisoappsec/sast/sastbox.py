from contextlib import suppress
from pathlib import Path
import tempfile
import tarfile
import docker
import os

bitbucket = os.getenv('BITBUCKET_CLONE_DIR')

class SASTBox(object):
    REGISTRY = 'docker.convisoappsec.com'
    REPOSITORY_NAME = 'sastbox'
    DEFAULT_TAG = 'latest'
    CONTAINER_REPORTS_DIR = '/reports'
    CONTAINER_CODE_DIR = bitbucket or '/code'
    WORKSPACE_REPORT_PATH = ["reports"]
    JSON_REPORT_PATTERN = '*.jsonreporter*.json'
    SUCCESS_EXIT_CODE = 0
    USER_ENV_VAR = "USER"

    def __init__(self, registry=None, repository_name=None, tag=None):
        self.docker = docker.from_env(
            version="auto"
        )
        self.container = None
        self.registry = registry or self.REGISTRY
        self.repository_name = repository_name or self.REPOSITORY_NAME
        self.tag = tag or self.DEFAULT_TAG

    def login(self, password, username='AWS'):
        login_args = {
            'registry': self.REGISTRY,
            'username': username,
            'password': password,
            'reauth': True,
        }

        login_result = self.docker.login(**login_args)
        return login_result

    def run_scan_diff(
        self, code_dir, current_commit, previous_commit, log=None
    ):
        return self._scan_diff(
            code_dir, current_commit, previous_commit, log
        )

    @property
    def size(self):
        try:
            registry_data = self.docker.images.get_registry_data(
                self.image
            )
            descriptor = registry_data.attrs.get('Descriptor', {})
            return descriptor.get('size') * 1024 * 1024
        except docker.errors.APIError:
            return 6300 * 1024 * 1024

    def pull(self):
        '''
        {
            'status': 'Downloading',
            'progressDetail': {'current': int, 'total': int},
            'id': 'string'
        }
        '''
        size = self.size
        layers = {}
        for line in self.docker.api.pull(
            self.repository, tag=self.tag, stream=True, decode=True
        ):
            status = line.get('status', '')
            detail = line.get('progressDetail', {})

            if status == 'Downloading':
                with suppress(Exception):
                    layer_id = line.get('id')
                    layer = layers.get(layer_id, {})
                    layer.update(detail)
                    layers[layer_id] = layer

                    for layer in layers.values():
                        current = layer.get('current')
                        total = layer.get('total')

                        if (current/total) > 0.98 and not layer.get('done'):
                            yield current
                            layer.update({'done': True})

        yield size

    def _scan_diff(self, code_dir, current_commit, previous_commit, log):
        environment = {
            'PREVIOUS_COMMIT': previous_commit,
            'CURRENT_COMMIT': current_commit,
            'SASTBOX_REPORTS_DIR': self.CONTAINER_REPORTS_DIR,
            'SASTBOX_REPORT_PATTERN': '/tmp/sastbox_workspace*/output/reports/*.jsonreporter*.json',  # noqa: E501
            'SASTBOX_CODE_DIR': self.CONTAINER_CODE_DIR,
        }

        command = '''
            ruby main.rb -c $SASTBOX_CODE_DIR --diff=$PREVIOUS_COMMIT,$CURRENT_COMMIT -q -a && \
            mkdir -p $SASTBOX_REPORTS_DIR && \
            cp $(find $SASTBOX_REPORT_PATTERN) $SASTBOX_REPORTS_DIR
        '''  # noqa: E501

        create_args = {
            'image': self.image,
            'entrypoint': ['bash', '-c'],
            'command': [command],
            'tty': True,
            'detach': True,
            'environment': environment,
        }

        self.container = self.docker.containers.create(**create_args)
        # previously create source code tar ball
        source_code_tarball_file = tempfile.TemporaryFile()
        source_code_tarball = tarfile.open(
            mode="w|gz", fileobj=source_code_tarball_file
        )

        source_code_tarball.add(
            name=code_dir,
            arcname=self.CONTAINER_CODE_DIR,
        )

        source_code_tarball.close()

        source_code_tarball_file.seek(0)
        self.container.put_archive("/", source_code_tarball_file)
        source_code_tarball_file.close()
        self.container.start()

        for line in self.container.logs(stream=True):
            if log:
                log(line, new_line=False)

        wait_result = self.container.wait()
        status_code = wait_result.get('StatusCode')

        if not status_code == self.SUCCESS_EXIT_CODE:
            raise RuntimeError(
                'SASTBox exiting with error status code'
            )

        chunks, _ = self.container.get_archive(
            self.CONTAINER_REPORTS_DIR
        )

        reports_tarball_file = tempfile.TemporaryFile()

        for chunk in chunks:
            reports_tarball_file.write(chunk)

        tempdir = tempfile.mkdtemp()
        reports_tarball_file.seek(0)
        reports_tarball = tarfile.open(mode="r|", fileobj=reports_tarball_file)
        reports_tarball.extractall(path=tempdir)
        reports_tarball.close()
        reports_tarball_file.close()

        return self._list_reports_paths(tempdir)

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

    def __del__(self):
        with suppress(Exception):
            self.container.remove(v=True, force=True)

    @classmethod
    def _list_reports_paths(cls, root_dir):
        sastbox_reports_dir = Path(root_dir, *cls.WORKSPACE_REPORT_PATH)

        for report in sastbox_reports_dir.glob(cls.JSON_REPORT_PATTERN):
            yield report