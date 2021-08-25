import argparse
from contextlib import contextmanager
from getpass import getpass
import json
import logging
from pkg_resources import get_distribution
from pathlib import Path, PurePosixPath
import re
from shutil import copy2
import sys
import tarfile
from tempfile import TemporaryDirectory
from uuid import uuid4

import pytest
import yaml
from paramiko.client import SSHClient
from paramiko.sftp_client import SFTPClient
from sshtunnel import open_tunnel

import phantom_dev.dummy
from phantom_dev.app import App
from phantom_dev.dummy import PatchedPath, mock_phantom


logger = logging.getLogger(name=__name__)


DEFAULT_DATA = Path(__file__).absolute().parent.joinpath('default_data')
DEFAULT_CONNECTOR = DEFAULT_DATA.joinpath('connector.py')
DEFAULT_TEST = DEFAULT_DATA.joinpath('test_connector.py')
DEFAULT_REQUIREMENTS = DEFAULT_DATA.joinpath('requirements-whl.txt')
DEFAULT_README = DEFAULT_DATA.joinpath('readme.html')
DEFAULT_VIEWS_DIR = DEFAULT_DATA.joinpath('views')


class RemoteTemporaryFolder:
	def __init__(self, ssh_client: SSHClient):
		self.client = ssh_client
		self.path = None

	def __enter__(self):
		path = PurePosixPath('/').joinpath('tmp', str(uuid4()))
		self.client.exec_command(f'mkdir -p {path}')
		self.path = path
		logger.debug('Created remote temporary directory %r', self.path)
		return self.path

	def __exit__(self, exc_type, exc_info, traceback):
		self.client.exec_command(f'rm -rf {self.path}')
		self.path = None


def package(
		app_directory: Path, destination: Path = None, force: bool = False):
	logger.debug('App directory: %r', app_directory)
	app = App(path=app_directory)
	version = app.get_version()
	version_string = version.replace('.', '_')
	with TemporaryDirectory() as tmp:
		temp_path = Path(tmp)
		with PatchedPath(app_directory):
			build_path = app.build(temp_path)
			default_archive_name = f'{app.package_name}-{version_string}.tgz'

		if destination is None:
			tar_path = Path().joinpath(default_archive_name)
		elif destination.is_dir():
			tar_path = destination.joinpath(default_archive_name)
		else:
			tar_path = destination

		logger.debug('Packaging to destination %r', tar_path)
		mode = 'w:gz' if force else 'x:gz'
		with tarfile.open(tar_path, mode) as tar:
			tar.add(build_path, arcname=build_path.name)

	return tar_path


def create(app_name, destination: Path = None, metadata_file: Path = None):
	app_directory_name = '_'.join(x.lower() for x in app_name.split())
	if destination is None:
		destination = Path().joinpath(app_directory_name)
	elif destination.is_dir():
		destination = destination.joinpath(app_directory_name)

	if metadata_file is None:
		metadata = {'name': app_name, 'id': str(uuid4())}
	else:
		with metadata_file.open() as metadata_yaml:
			metadata = yaml.safe_load(metadata_yaml)

	product_metadata = metadata.setdefault('product', {})
	for product_key in ['vendor', 'name']:
		if product_key in product_metadata:
			continue

		value = input(f'Product {product_key.title()}: ').strip()
		product_metadata[product_key] = value

	for key in ['description', 'publisher', 'license']:
		if key not in metadata:
			metadata[key] = input(f'{key.title()}: ').strip()

	destination.mkdir(exist_ok=False)
	copy2(DEFAULT_CONNECTOR, destination)
	new_metadata = destination.joinpath('metadata.yaml')

	with new_metadata.open('w') as metadata_yaml:
		yaml.safe_dump(metadata, metadata_yaml)

	test_directory = destination.joinpath('tests')
	test_directory.mkdir()
	copy2(DEFAULT_TEST, test_directory)

	copy2(DEFAULT_REQUIREMENTS, destination)

	copy2(DEFAULT_README, destination)

	views_directory = destination.joinpath('views')
	views_directory.mkdir()
	for view_template in DEFAULT_VIEWS_DIR.glob('*.html'):
		copy2(view_template, views_directory)

	return destination


def deploy(package_path: Path, phantom_location: str, python_version: str):
	with phantom_ssh_connection(location=phantom_location) as ssh_client:
		phantom_home = _get_phantom_home(ssh_client)
		with RemoteTemporaryFolder(ssh_client=ssh_client) as tmp:
			remote_path = tmp.joinpath(package_path.name)
			with SFTPClient.from_transport(ssh_client.get_transport()) as sftp:
				sftp.put(str(package_path), str(remote_path))

			if python_version == '3':
				python_command = 'python3'

				# The Python 3 complition script was moved in 4.10
				phantom_settings = _get_phantom_settings(
					ssh_client, phantom_home)
				version_string = phantom_settings['phantom_version']
				major, minor = (
					int(x) for x in version_string.split('.')[:2])
				if (major, minor) < (4, 10):
					script_path = f'{phantom_home}/bin/py3/compile_app.pyc'
				else:
					script_path = f'{phantom_home}/bin/compile_app.pyc'
			else:
				python_command = 'python2'
				script_path = f'{phantom_home}/bin/py2/compile_app.pyc'

			commands = [
				f'cd {tmp}',
				f'tar -zxvf {package_path.name}',
				f'cd $(ls --ignore={package_path.name})',
				f'phenv {python_command} {script_path} -i',
			]

			command_text = ';\n'.join(x.strip() for x in commands)
			logger.debug('Running commands: %r', command_text)

			stdin, stdout, stderr = ssh_client.exec_command(command_text)
			for line in stdout:
				print(line, end='')


def push(app_directory: Path, phantom_location: str):
	python_version = App(app_directory).metadata.get('python_version', '3')
	with TemporaryDirectory() as tmp_str:
		tmp = Path(tmp_str).absolute()
		package_path = package(app_directory, tmp)
		return deploy(
			package_path=package_path,
			phantom_location=phantom_location,
			python_version=python_version,
		)


@mock_phantom
def test(app_directory: Path, pytest_args):
	try:
		first_arg = pytest_args[0]
	except IndexError:
		args = []
	else:
		if first_arg == '--':
			args = pytest_args[1:]
		else:
			args = pytest_args

	logger.debug('Running pytest with args: %r', args)
	with PatchedPath(app_directory):
		exit_code = pytest.main(args=args)

	exit(exit_code)


def debug(
		app_directory: Path,
		phantom_location: str,
		action: str,
		local_debug_port: int,
		remote_debug_port: int,
		phantom_home: PurePosixPath,
):
	app = App(path=app_directory)
	installation_folder = phantom_home.joinpath(
		'apps', f'{app.package_name}_{app.id}')
	PYTHON_PATH_ENTRIES = [
		installation_folder,
		installation_folder.joinpath('dependencies'),
	]
	PYTHON_PATH = ':'.join(str(x) for x in PYTHON_PATH_ENTRIES)
	connector_script = installation_folder.joinpath(app.main_module)
	create_action_script = phantom_home.joinpath('bin', 'py3', 'create_tj.pyc')
	create_action_command = (
		f'phenv python3 {create_action_script} {json.dumps(action)}')
	with phantom_ssh_connection(location=phantom_location) as ssh_client:
		# Create the action JSON file
		stdin, stdout, stderr = ssh_client.exec_command(create_action_command)
		lines = []
		for line in (l for l in stdout if l):
			print(line, end='')
			lines.append(line)

		# Strip the generated JSON file path out of the command output
		final_line: str = lines[-1].strip()
		quoted_dest = final_line.split(maxsplit=5)[-1]
		action_file = quoted_dest.strip("'")

		# Don't know why, but phenv uses PYTHON_PATH instead of PYTHONPATH
		run_debug_command = (
			f'PYTHON_PATH={PYTHON_PATH}:$PYTHON_PATH phenv python3 -m debugpy'
			f' --listen localhost:{remote_debug_port} --wait-for-client'
			f' {connector_script} {action_file}'
		)

		# Open an SSH tunnel for the debugger connection
		with phantom_ssh_tunnel(
				location=phantom_location,
				local_port=local_debug_port,
				remote_port=remote_debug_port,
		):
			logger.debug('Running command: %r', run_debug_command)
			stdin, stdout, stderr = ssh_client.exec_command(run_debug_command)
			for line in stdout:
				print(line, end='')


def tail(
		app_directory: Path,
		phantom_location: str,
		path: PurePosixPath,
		tail_args=tuple(),
):
	app = App(path=app_directory)
	with phantom_ssh_connection(location=phantom_location) as ssh_client:
		if path.is_absolute():
			log_path = path
		else:
			logger.debug('Inferring log path from relative path %r', path)
			phantom_home = _get_phantom_home(ssh_client)
			log_path = phantom_home.joinpath(
				'local_data', 'app_states', app.id, 'logs', path)

		args = ['tail', *tail_args, str(log_path)]
		logger.debug('Running command args: %r', args)
		_, stdout, stderr = ssh_client.exec_command(' '.join(args))
		try:
			for line in stdout:
				print(line, end='')
		except KeyboardInterrupt:
			logger.debug('Interrupted')
			return

		exit_status = stdout.channel.exit_status
		if exit_status != 0:
			message = stderr.read().decode()
			raise RuntimeError(message)


def main():
	package_name, *_ = __name__.split('.', 1)
	package_version = get_distribution(package_name).version
	root_parser = argparse.ArgumentParser(
		description='A Splunk>Phantom app development utility')
	root_parser.add_argument(
		'-V', '--version',
		action='version',
		version=f'%(prog)s {package_version}',
	)
	root_parser.add_argument('-l', '--log-level', default='INFO')
	root_parser.add_argument(
		'--dummy_path',
		action='store_true',
		help='show the path of the dummy phantom module and exit'
	)

	subparsers = root_parser.add_subparsers(
		title='Sub-commands',
		description=(
			'For more information on a sub-command, invoke it with `--help`'),
	)

	# package command
	package_parser = subparsers.add_parser(
		name='package',
		description=(
			'Build an installable package from an app project directory'),
	)

	app_directory_help = 'App project directory path'
	package_parser.set_defaults(function=package)
	package_parser.add_argument(
		'app_directory', type=Path, help=app_directory_help)
	package_parser.add_argument(
		'-f', '--force',
		action='store_true',
		help=('Overwrite any existing files with the same name as the output')
	)
	package_parser.add_argument(
		'-o', '--output',
		type=Path,
		dest='destination',
		help=(
			'Output package path. If this is an existing directory, the'
			' package will be placed inside.'
		)
	)

	# create command
	create_parser = subparsers.add_parser(
		'create', description='Create a new Splunk>Phantom app project')
	create_parser.set_defaults(function=create)
	create_parser.add_argument('app_name', help='The name of the new app')
	create_parser.add_argument(
		'-d', '--destination',
		type=Path,
		help=(
			'The path to the new project directory. If this is an existing'
			' directory, the app directory will be placed inside.'
		),
	)
	create_parser.add_argument(
		'-m', '--metadata',
		type=Path,
		dest='metadata_file',
		help=(
			'The path to a YAML file containing metadata values for the new'
			' app'
		),
	)

	# deploy command
	deploy_parser = subparsers.add_parser(
		'deploy',
		description=(
			'Install a local app package on a remote Splunk>Phantom instance'),
	)
	deploy_parser.set_defaults(function=deploy)
	deploy_parser.add_argument(
		'package_path', type=Path, help='Local package path')

	phantom_location_help = (
			'Splunk>Phantom server location taking the form'
			' [username[:password]@]host'
	)
	deploy_parser.add_argument('phantom_location', help=phantom_location_help)
	deploy_parser.add_argument(
		'--python_version',
		help='Python version used by app (default=3)',
		default='3',
	)

	# push command
	push_parser = subparsers.add_parser(
		'push',
		description=(
			'Combine `package` and `deploy` operations to build a package from'
			' the specified app project directory and install it on a remote'
			' Splunk>Phantom instance'
		),
	)
	push_parser.set_defaults(function=push)
	push_parser.add_argument(
		'app_directory', type=Path, help=app_directory_help)
	push_parser.add_argument('phantom_location', help=phantom_location_help)

	# test command
	test_parser = subparsers.add_parser('test')
	test_parser.set_defaults(function=test)
	test_parser.add_argument(
		'app_directory', type=Path, help=app_directory_help)
	test_parser.add_argument('pytest_args', nargs=argparse.REMAINDER)

	# debug command
	debug_parser = subparsers.add_parser(
		'debug',
		description=(
			'Run the specified action in a debugging session through an SSH'
			' tunnel.'
			' An action JSON file will be generated and passed to the'
			' installed app connector, which will wait for a debugger '
			' connection on the specified port to begin execution.'
			' An SSH tunnel will be opened forwarding connections on the'
			' specified local port to the remote debugging port.'
			' Designed to integrate with Visual Studio Code and debugpy.'
		),
	)
	debug_parser.set_defaults(function=debug)
	debug_parser.add_argument(
		'app_directory', type=Path, help=app_directory_help)
	debug_parser.add_argument('phantom_location', help=phantom_location_help)
	debug_parser.add_argument(
		'action', help='The action to test (e.g. "dummy action")')
	debug_parser.add_argument(
		'--local_debug_port', type=int, default=8869)
	debug_parser.add_argument(
		'--remote_debug_port', type=int, default=8869)
	debug_parser.add_argument(
		'--phantom_home',
		type=PurePosixPath,
		default=PurePosixPath('/opt/phantom'),
	)

	# tail command
	tail_parser = subparsers.add_parser(
		'tail',
		description=(
			'Run the tail command on the remote app log file.'
			' Options for the tail command can be passed as positional'
			' arguments.'
		),
	)
	tail_parser.set_defaults(function=tail)
	tail_parser.add_argument(
		'app_directory', type=Path, help=app_directory_help)
	tail_parser.add_argument(
		'phantom_location', help=phantom_location_help)
	tail_parser.add_argument(
		'path',
		nargs='?',
		help=(
			'Either an absolute path, or the relative path to a log file from'
			' the app state logs directory (default=connector.log)'
		),
		type=PurePosixPath,
		default=PurePosixPath('connector.log')
	)
	tail_parser.add_argument('tail_args', nargs='*')

	namespace, unknown = root_parser.parse_known_args(sys.argv[1:])
	log_level = namespace.log_level
	logging.basicConfig(level=log_level.upper())
	logger.debug('namespace: %r', namespace)

	if unknown:
		logger.debug('Unknown arguments: %r', unknown)
		if namespace.function is tail:
			namespace.tail_args = unknown
		else:
			root_parser.parse_args(sys.argv[1:])

	arguments = vars(namespace)
	log_level = arguments.pop('log_level')

	show_dummy = arguments.pop('dummy_path')
	if show_dummy:
		path, = phantom_dev.dummy.__path__
		print(path)
		return

	try:
		command_function = arguments.pop('function')
	except KeyError:
		root_parser.print_usage()
		return

	logger.debug(
		'Calling %r with keyword arguments %r', command_function, arguments)

	result = command_function(**arguments)
	if result is not None:
		print(result)


def parse_phantom_location(location: str):
	try:
		credentials, phantom_location = location.split('@')
	except ValueError:
		phantom_location = location
		username = None
		password = None
	else:
		try:
			username, password = credentials.split(':')
		except ValueError:
			username = credentials
			password = getpass(f'SSH password for {username}:')
		else:
			password = None if not password else password

	return phantom_location, username, password


@contextmanager
def phantom_ssh_tunnel(location: str, local_port: int, remote_port: int):
	phantom_location, username, password = parse_phantom_location(
		location=location)
	try:
		with open_tunnel(
				phantom_location,
				ssh_username=username,
				ssh_password=password,
				local_bind_address=('localhost', local_port),
				remote_bind_address=('localhost', remote_port)
		) as tunnel:
			logger.info(
				'Opened SSH tunnel (localhost:%r -> %s:%r)',
				local_port,
				phantom_location,
				remote_port,
			)
			yield tunnel
	finally:
		logger.info('Closed SSH Tunnel')


@contextmanager
def phantom_ssh_connection(location: str):
	phantom_location, username, password = parse_phantom_location(
		location=location)

	with SSHClient() as ssh_client:
		ssh_client.load_system_host_keys()
		ssh_client.connect(
			phantom_location, username=username, password=password)

		yield ssh_client


# Captures the phantom home location on 4.8 - 4.10
_PHENV_HOME_REGEX = re.compile(
	r'^Usage:\s+(?P<home>/.*)/bin/phenv\b', flags=re.M)


def _get_phantom_home(ssh_client: SSHClient):
	_, stdout, stderr = ssh_client.exec_command('phenv')
	error_text = stderr.read()
	if error_text:
		logger.debug('phenv stderr: %r', error_text)

	stdout_text = stdout.read().decode()
	logger.debug('phenv stdout: %r', stdout_text)

	home_match, = _PHENV_HOME_REGEX.finditer(stdout_text)
	home_string = home_match['home']
	logger.debug('Found phantom home: %r', home_string)
	return PurePosixPath(home_string)


def _get_phantom_settings(ssh_client: SSHClient, phantom_home: PurePosixPath):
	settings_path = phantom_home.joinpath('etc', 'settings.json')
	command = f'cat {settings_path}'
	_, stdout, stderr = ssh_client.exec_command(command)
	error_text = stderr.read()
	if error_text:
		logger.debug('%r stderr: %r', command, error_text)

	stdout_text = stdout.read().decode()
	logger.debug('%r stdout: %r', command, stdout_text)
	return json.loads(stdout_text)


if __name__ == '__main__':
	main()
