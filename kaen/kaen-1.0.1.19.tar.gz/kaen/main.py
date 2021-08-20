import os
import click
import uuid

from dotenv import dotenv_values

from laai.hpo.mlflow_utils import terminate_parent_run, get_active_run_feature_set_id, get_active_run_params

VERSION = "0.0.1"
IMAGE_NAME = "osipov/laai"
IMAGE_TAG = "latest"
IMAGE = f"{IMAGE_NAME}:{IMAGE_TAG}"

def get_backend_provider(dojo = None, job = None):
	if job:
		job_config = {
			**dotenv_values(f"{os.getcwd()}/.job/.{job}/env.sh")
		}
		dojo_config = {
			**dotenv_values(f"{os.getcwd()}/.dojo/.{job_config['LAAI_DOJO']}/env.sh")
		}
		backend = dojo_config['LAAI_BACKEND']
		provider = dojo_config['LAAI_PROVIDER']
		return backend, provider		
	elif dojo:
		dojo_config = {
			**dotenv_values(f"{os.getcwd()}/.dojo/.{dojo}/env.sh")
		}
		backend = dojo_config['LAAI_BACKEND']
		provider = dojo_config['LAAI_PROVIDER']
		return backend, provider
	else:
		return None

def get_volumes(provider = None):
	volumes = {f"{os.getcwd()}" : {"bind": "/workspace", "mode": "rw"},}
	if provider == 'local':
		volumes = {
			**volumes, 
			**{"/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}}
		}
	return volumes

def assert_aws_credentials():
	assert 'AWS_ACCESS_KEY_ID' in os.environ, "Missing environment variable AWS_ACCESS_KEY_ID"
	assert 'AWS_DEFAULT_REGION' in os.environ, "Missing environment variable AWS_DEFAULT_REGION"
	assert 'AWS_SECRET_ACCESS_KEY' in os.environ, "Missing environment variable AWS_SECRET_ACCESS_KEY"

def prepare_docker():
	import docker
	client = docker.from_env()
	images = client.images.list(IMAGE)
	image = images[0] if len(images) else client.images.pull(IMAGE_NAME, tag = IMAGE_TAG)
	return client


@click.group()
def cli():
	f"""LAAI helps you train distributed PyTorch deep learning models in AWS, Azure, and Google Cloud.

	You are using LAAI version {VERSION}.
	"""
	pass

@cli.command("init")
@click.option('--provider', required=True, type=click.Choice(['aws', 'azure', 'gcp', 'local'], case_sensitive=False))
@click.option('--backend', default='docker', type=click.Choice(['docker', 'k8s'], case_sensitive=False), show_default=True)
@click.option('--worker-instances', default='1', type=int, show_default=True)
@click.option('--worker-instance-type', default='t3.micro', show_default=True)
@click.option('--manager-instances', default='1', type=int, show_default=True)
@click.option('--manager-instance-type', default='t3.micro', show_default=True)
@click.option('--volume-size', default='8', type=int, show_default=True)
@click.option('--ssh-connection-timeout', default='5', type=int, show_default=True)
@click.option('--ssh-connection-attempts', default='1', type=int, show_default=True)
def init(provider, 
			backend, 
			worker_instances, 
			worker_instance_type, 
			manager_instances, 
			manager_instance_type,
			volume_size,
			ssh_connection_timeout,
			ssh_connection_attempts):			
	"""Initialize a training dojo in a specified infrastructure provider."""
	DojoCLI.init(provider, 
			backend, 
			worker_instances, 
			worker_instance_type, 
			manager_instances, 
			manager_instance_type,
			volume_size,
			ssh_connection_timeout,
			ssh_connection_attempts)

class DojoCLI(click.MultiCommand):
	@cli.command("init")
	@click.option('--provider', required=True, type=click.Choice(['aws', 'azure', 'gcp', 'local'], case_sensitive=False))
	@click.option('--backend', default='docker', type=click.Choice(['docker', 'k8s'], case_sensitive=False), show_default=True)
	@click.option('--worker-instances', default='1', type=int, show_default=True)
	@click.option('--worker-instance-type', default='t3.micro', show_default=True)
	@click.option('--manager-instances', default='1', type=int, show_default=True)
	@click.option('--manager-instance-type', default='t3.micro', show_default=True)
	@click.option('--volume-size', default='8', type=int, show_default=True)
	@click.option('--ssh-connection-timeout', default='5', type=int, show_default=True)
	@click.option('--ssh-connection-attempts', default='1', type=int, show_default=True)
	def init(provider, 
				backend, 
				worker_instances, 
				worker_instance_type, 
				manager_instances, 
				manager_instance_type,
				volume_size,
				ssh_connection_timeout,
				ssh_connection_attempts):			
		"""Initialize a training dojo in a specified infrastructure provider."""
		assert provider == 'aws	' or provider == 'local', f"Provider {provider} is not publicly available in version {VERSION}"
		assert backend == 'docker', f"Backend {backend} is not publicly available in version {VERSION}"

		#check for the aws settings
		if (provider == 'aws'):
			assert_aws_credentials()

			# #drop the provider prefix for the instance type, e.g. aws:t3.micro -> t3.micro
			# assert worker_instance_type[:len(provider) + 1] == provider + ":",\
			# 	f"Worker instance type {worker_instance_type} is missing a prefix {provider}:"
			# worker_instance_type = worker_instance_type[len(provider) + 1:]

			# manager_instance_type = manager_instance_type[len(provider) + 1:]

		print(f"Checking for the latest updates...", end='')
		client = prepare_docker()
		print('done')

		dojo = os.environ['LAAI_DOJO'] if 'LAAI_DOJO' in os.environ else None
		while not dojo or dojo[:1].isalpha() is False:
			dojo = uuid.uuid4().hex[:8]
		print(f"Using a dojo store at {os.getcwd()}/.dojo/.{dojo}")

		environment = { "LAAI_DOJO": dojo, 
						"LAAI_VERSION": VERSION,
						"LAAI_BACKEND": backend,
						"LAAI_PROVIDER": provider,
						}

		volumes = {f"{os.getcwd()}" : {"bind": "/workspace", "mode": "rw"},}
		
		if provider == 'local':
			print(f"Preparing a dojo using {backend} on {provider} ...")
			volumes = {
				**volumes, 
				**{"/var/run/docker.sock": {"bind": "/var/run/docker.sock", "mode": "rw"}}
			}
		else:
			environment = { **environment, **{
							"LAAI_DOJO_CONNECT_TIMEOUT": ssh_connection_timeout,
							"LAAI_DOJO_CONNECT_ATTEMPTS": ssh_connection_attempts,
							"AWS_ACCESS_KEY_ID": os.environ['AWS_ACCESS_KEY_ID'],
							"AWS_DEFAULT_REGION": os.environ['AWS_DEFAULT_REGION'],
							"AWS_SECRET_ACCESS_KEY": os.environ['AWS_SECRET_ACCESS_KEY'],
							"TF_VAR_instances": worker_instances,
							"TF_VAR_worker_instance_type": worker_instance_type,
							"TF_VAR_manager_instances": manager_instances,
							"TF_VAR_manager_instance_type": manager_instance_type,
							"TF_VAR_volume_size": volume_size,}
			}		
			print(f"Preparing a dojo using {backend} on {provider} with {worker_instances} worker(s) and {manager_instances} manager(s) ...")

		container = client.containers.run(	image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/dojo_init.sh'",
			volumes = volumes,
			environment = environment,
			auto_remove = True,
			detach=True)
			
		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	

		print(dojo)

	@click.command()	
	@click.argument('dojo')
	def activate(dojo):
		print(f"Activating dojo {dojo}")
		backend, provider = get_backend_provider(dojo)
		if 'aws' == provider:
			assert_aws_credentials()

		client = prepare_docker()
		volumes = get_volumes(provider)

		container = client.containers.run(	
			image = IMAGE, 
			command = f"/bin/bash -c '/opt/laai/{backend}/{provider}/dojo_activate.sh'",
			volumes = volumes ,
			environment = { "LAAI_DOJO": dojo, 
							},
			auto_remove = True,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8'))	

	@click.command()	
	@click.option('--reverse', '-r',  is_flag = True, default = False)
	def ls(reverse):		
		"""Output a list with the training dojo(s) in the current workspace.		
		By default, the dojo that was created first in the workspace is listed first."""

		client = prepare_docker()
		
		environment = {
			"LAAI_DOJO_LS_REVERSE": "" if reverse else "-r"
		}

		container = client.containers.run(	
			image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/dojo_ls.sh'",
			volumes = get_volumes() ,
			environment = environment,
			auto_remove = True,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	

	@click.command()
	def prune():
		client = prepare_docker()
		container = client.containers.run(	
			image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/dojo_prune.sh'",
			volumes = get_volumes() ,
			auto_remove = True,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			s = s.decode('utf-8').strip()
			if len(s):
				print(s)
	
	@click.command()
	@click.argument('dojo')
	def rm(dojo):
		print(f"Removing dojo {dojo} and deactivating store {os.getcwd()}/.dojo/.{dojo}")

		backend, provider = get_backend_provider(dojo)
		environment = {}
		if 'aws' == provider:
			assert_aws_credentials()
			environment = {
				"AWS_ACCESS_KEY_ID": os.environ['AWS_ACCESS_KEY_ID'],
				"AWS_DEFAULT_REGION": os.environ['AWS_DEFAULT_REGION'],
				"AWS_SECRET_ACCESS_KEY": os.environ['AWS_SECRET_ACCESS_KEY'],				
			}
		
		client = prepare_docker()

		volumes = get_volumes(provider)
		
		container = client.containers.run(	
			image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/dojo_rm.sh'",
			volumes = volumes,
			environment = { **{"LAAI_DOJO": dojo,}, 
							**environment,},
			auto_remove = True,
			detach=True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8'))	
	
	@click.command()	
	@click.argument('dojo')
	def inspect(dojo):	
		"""Return key value settings for the specified dojo."""
		backend, provider = get_backend_provider(dojo)
		if 'aws' == provider:
			assert_aws_credentials()

		client = prepare_docker()
		
		container = client.containers.run(	
			image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/dojo_inspect.sh'",
			volumes = get_volumes(provider) ,
			environment = { "LAAI_DOJO": dojo, 
							},
			auto_remove = True,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			s = s.decode('utf-8').strip()
			if len(s):
				print(s)

	def list_commands(self, ctx):
		return ['ls', 'rm', 'prune', 'activate', 'inspect', 'init']

	def get_command(self, ctx, name):
		return {"ls": DojoCLI.ls,
				"rm": DojoCLI.rm,
				"prune": DojoCLI.prune,
				"inspect": DojoCLI.inspect,
				"init": DojoCLI.init,
				'activate': DojoCLI.activate}[name]

@cli.command(cls=DojoCLI)
def dojo():
	"""Manage a dojo training environment."""
	pass

class JobCLI(click.MultiCommand):
	@click.command()
	@click.option('--dojo', required = True)
	@click.option('--image', required = True)
	@click.option('--subnet', required = False)
	@click.option('--manager-ip', required = False)
	def create(image, dojo, subnet, manager_ip):
		"""Create a training job in a specified dojo training environment. 
		The training job must be packaged as a container and available to docker pull 
		command, in other words docker pull <image> must pull the image."""

		if subnet is not None or manager_ip is not None:
			assert subnet is not None and manager_ip is not None, "Both --subnet and --manager-ip must be specified"
			from ipaddress import ip_network, ip_address
			net = ip_network(subnet)
			assert ip_address(manager_ip) in net, f"Manager IP {manager_ip} is not in the CIDR subnet {subnet} range"

		job = None
		while not job or job[:1].isalpha() is False:
			job = uuid.uuid4().hex[:8]			
		print(f"Creating a job {job} using image {image} in dojo {dojo}")

		backend, provider = get_backend_provider(dojo)

		print(f"Checking for the latest version...", end='')
		client = prepare_docker()
		print('done')

		container = client.containers.run(image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/job_create.sh'",
			volumes = get_volumes(provider) ,
			environment = { "LAAI_DOJO": dojo,
							"LAAI_JOB": job,
							"LAAI_JOB_IMAGE": image,
							"LAAI_JOB_SUBNET": subnet if subnet else None,
							"LAAI_JOB_MANAGER_IP": manager_ip if subnet else None,
							},
			auto_remove = True,
			detach=True)
		
		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	
		
		print(job)			

	@click.command()	
	@click.argument('job')
	def inspect(job):
		"""Return key value settings for the specified job."""
		
		client = prepare_docker()
		
		container = client.containers.run(	
			image=IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/job_inspect.sh'",
			volumes = {f"{os.getcwd()}" : {"bind": "/workspace",
											"mode": "rw"}} ,
			environment = { "LAAI_JOB": job, },
			auto_remove = False,
			detach=True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8'))	

	@click.command()
	@click.argument('job')
	@click.option('--replicas', default='1', type=int)
	@click.option('--detach', is_flag = True, default = False)
	@click.option('--port', '-p', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )	
	@click.option('--env', '-e', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )
	def start(job, replicas, detach, port, env):
		"""Start an existing job using the specified number of worker replicas."""

		print(f"Checking for the latest version...", end='')
		client = prepare_docker()
		print('done')

		backend, provider = get_backend_provider(job = job)		

		env = dict({ "LAAI_JOB": job,
					 "LAAI_JOB_REPLICAS": replicas,
					 "LAAI_JOB_CFG_DETACH": 1 if detach else 0,
					 },
					 **{"LAAI_JOB_ARG_" + k : v for k, v in env},
					 **{"LAAI_JOB_PORT_" + k : v for k, v in port})

		vol = get_volumes(provider)

		container = client.containers.run(	image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/job_start.sh'",
			volumes = vol ,
			environment = env,
			auto_remove = True,
			detach = True)

		if not detach:
			logs = container.attach(stream = True, logs = True)
			for s in logs:
				print(s.decode('utf-8').strip())	

	@click.command()	
	@click.option('--reverse', '-r',  is_flag = True, default = False)
	def ls(reverse):		
		"""List existing jobs in the current workspace.
		By default, the dojo that was created first in the workspace is listed first."""

		client = prepare_docker()
		
		env = {
			"LAAI_JOB_LS_REVERSE": "" if reverse else "-r"
		}
		
		container = client.containers.run(	
			image=IMAGE, 
			command=f"/bin/bash -c '/opt/laai/job_ls.sh'",
			environment = env,
			volumes = get_volumes(),
			auto_remove = False,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())

	@click.command()
	@click.argument('job')
	def rm(job):
		"""Remove the specified job and associated resources."""
		client = prepare_docker()
		env = dict({ "LAAI_JOB": job,})

		container = client.containers.run(	
			image=IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/hpo_disable.sh'",
			volumes = {f"{os.getcwd()}" : {"bind": "/workspace",
											"mode": "rw"}} ,
			environment = env,
			auto_remove = False,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())			
		
		container = client.containers.run(	
			image=IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/job_rm.sh'",
			volumes = {f"{os.getcwd()}" : {"bind": "/workspace",
											"mode": "rw"}} ,
			environment = env,
			auto_remove = False,
			detach = True )

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	


	def list_commands(self, ctx):
		return ['ls', 'rm', 'create', 'inspect', 'start']

	def get_command(self, ctx, name):
		return {"ls": JobCLI.ls,
				"rm": JobCLI.rm,
				'create': JobCLI.create,
				'inspect': JobCLI.inspect,
				"start": JobCLI.start}[name]

@cli.command("job", cls=JobCLI)
def job():
	"""Manage jobs in a specific dojo training environment."""
	pass

class HpoCLI(click.MultiCommand):
	def list_commands(self, ctx):
		return ["enable", "disable", 'start', 'stop', 'inspect', 'set']

	def get_command(self, ctx, name):
		return {"enable": HpoCLI.enable,
				"disable": HpoCLI.disable,
				"start": HpoCLI.start,
				"stop": HpoCLI.stop,
				"client": HpoCLI.client,
				'inspect': HpoCLI.inspect,
				'set': HpoCLI._set,
				'kv': HpoCLI.kv}[name]

	@click.command()
	@click.argument('name')
	@click.option('--parent-run', is_flag = True, required = False)
	@click.option('--active-run-params', is_flag = True, required = False)
	@click.option('--hp-set-id', required = False)
	def inspect(name, parent_run, active_run_params, hp_set_id):
		from laai.hpo.mlflow_utils import get_client, get_parent_run, \
			get_active_child_run, get_active_run_params, \
			get_active_run_hp_set_id

		mlflow_tracking_uri = os.environ['MLFLOW_TRACKING_URI'] if 'MLFLOW_TRACKING_URI' in os.environ else None
		client = get_client(mlflow_tracking_uri)
		if parent_run:
			run = get_parent_run(client, name)
			if run is not None:
				for k, v in {"EXPERIMENT_RUN_ID": run.info.run_id, 
							"EXPERIMENT_RUN_STATUS": run.info.status, 
							# **run.data.tags, 
							}.items():
					print(f"LAAI_{k}={v}")
			else:
				return None
		elif active_run_params:
			params = get_active_run_params(mlflow_tracking_uri = mlflow_tracking_uri, mlflow_experiment_name = name)
			if params is not None:
				print(params)
		elif hp_set_id:
			hp_id = get_active_run_hp_set_id(mlflow_experiment_name=name, hp_set_id=hp_set_id)
			print(hp_id)

	@click.command()
	@click.argument('job')
	@click.option('--image', required = True)
	@click.option('--num-runs', required = False, default = 1, show_default=True)
	@click.option('--seed', required = False, default = 42, show_default=True)
	@click.option('--service-prefix', required = False, default = 'laai.hpo.services', show_default=True)
	@click.option('--service-name', required = False, default = 'BaseMLFlowService', show_default=True)
	@click.option('--port', '-p', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )	
	@click.option('--env', '-e', required = False, default = [], multiple = True, type=click.Tuple([str, str]) )
	def enable(job, image, num_runs, seed, service_prefix, service_name, port, env):
		"""Enable hyperparameter optimization(HPO) for a job using
		the HPO service packaged in the specified image."""

		print(f"Checking for the latest version...", end='')
		client = prepare_docker()
		print('done')

		backend, provider = get_backend_provider(job = job)

		env = dict({ "LAAI_JOB": job,
					 "LAAI_HPO_IMAGE": image,
					 "LAAI_HPO_JOB_RUNS": num_runs,
					 "LAAI_HPO_SEED": seed,
					 "LAAI_HPO_SERVICE_PREFIX": service_prefix,
					 "LAAI_HPO_SERVICE_NAME": service_name,
					 },
					 **{"LAAI_JOB_ARG_" + k : v for k, v in env},
					 **{"LAAI_JOB_PORT_" + k : v for k, v in port})

		vol = get_volumes(provider)

		container = client.containers.run(	image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/hpo_enable.sh'",
			volumes = vol,
			environment = env,
			auto_remove = True,
			detach = True)

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	

	@click.command()
	@click.argument('job')
	def disable(job):
		"""Disable hyperparameter optimization(HPO) for a job.
		If a job never had HPO enabled, this command succeeds."""

		print(f"Checking for the latest version...", end='')
		client = prepare_docker()
		print('done')

		backend, provider = get_backend_provider(job = job)

		env = dict({ "LAAI_JOB": job,})
		vol = get_volumes(provider)

		container = client.containers.run(	image = IMAGE, 
			command=f"/bin/bash -c '/opt/laai/{backend}/{provider}/hpo_disable.sh'",
			volumes = vol,
			environment = env,
			auto_remove = True,
			detach = True)

		logs = container.attach(stream = True, logs = True)
		for s in logs:
			print(s.decode('utf-8').strip())	

	@click.command()
	@click.argument('name')
	def _set(name):
		print(get_active_run_feature_set_id(feature_set_id = name))

	@click.command()
	@click.option('--output', default='bash', required = False)
	def kv(output):
  		print(get_active_run_params(output = output))

	@click.command()
	@click.option('--num_runs', required = False, default = 1)
	@click.option('--client_prefix', required = False, default = 'laai.hpo.client')
	@click.option('--client_name', required = False, default = 'BaseMLFlowClient')
	def client(num_runs, client_prefix, client_name):
		"""Execute a run(s) of a hyperparameter optimization service client.
		
		Unless specified otherwise, the client executes a single run. The default
		implementation of the client uses laai.hpo.client.BaseMLFlowClient.
		This implementation simply queries for a seed hyperparameter and reports
		uniform random values in a range [0., 1.) as the values for the loss metric.
		"""
		import importlib.util
		mod = importlib.import_module(client_prefix)
		klass = getattr(mod, client_name)
		client = klass()
		client.run(num_runs = num_runs)

	@click.command()
	@click.option('--name', required = True)
	@click.option('--num_runs', required = False, default = 1)
	@click.option('--hpo_seed', required = False, default = 42)
	@click.option('--service_prefix', required = False, default = 'laai.hpo.services')
	@click.option('--service_name', required = False, default = 'BaseMLFlowService')
	def start(name, num_runs, hpo_seed, service_prefix, service_name):
		import importlib.util
		mod = importlib.import_module(service_prefix)
		klass = getattr(mod, service_name)
		hpo_service = klass()
		hpo_service.run(mlflow_experiment_name = name,
						num_trials = num_runs, 
						hpo_seed = hpo_seed)

	@click.command()
	def stop():
		terminate_parent_run()


@cli.command(cls=HpoCLI)
def hpo():
	"""Manage hyperparameter optimization."""
	pass