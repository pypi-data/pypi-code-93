# run pip install -r requirements.txt
# import glob
import sys
from os import listdir
from os.path import isfile, join
import yaml
from sqlpie.exceptions import MissingModelConfigFile
from pandas.core.common import flatten

class Project:

	@staticmethod
	def models(dynamic_env=None):
		output = {'models': [], 'prep_models': [] }
		if dynamic_env:
			output.update( { 'dynamic_env_prod_index': {} } )
		all_paths = Project._all_model_paths()
		all_models = list(map(lambda path: path.split('/')[-1].split('.')[0] , all_paths))
		for model in all_models:
			if dynamic_env:
				dynamic_env_models = []
				dynamic_env_model = Project.dynamic_env_model(dynamic_env, model)
				output['models'].append( dynamic_env_model )
				prep_model = Project.get_prep_model_name(model)
				dynamic_env_prep_model = Project.get_prep_model_name(model, dynamic_env=dynamic_env)
				output['prep_models'].append( dynamic_env_prep_model )
				output['dynamic_env_prod_index'].update( { dynamic_env_model: model} )
				output['dynamic_env_prod_index'].update( { dynamic_env_prep_model: prep_model } )
			else:
				output['models'].append( model )
				output['prep_models'].append(Project.get_prep_model_name(model))
		return output

	@staticmethod
	def get_prep_model_name(model_name, dynamic_env=None):
		model_config = Project.get_model_config(model_name)
		if model_config and 'prep_schema' in model_config.keys():
			prep_model = model_config['prep_schema']
			if dynamic_env:
				return f"{dynamic_env}_{prep_model}" 					
			else:
				return prep_model
		else:
			if dynamic_env:
				return f"{dynamic_env}_{model_name}_prep"
			else:
				return f"{model_name}_prep"
	
	@staticmethod
	def sources():
		sources_config_file = open("./config/sources.yml", "r")
		sources_conf = yaml.load(sources_config_file, Loader=yaml.FullLoader)
		sources_config_file.close()
		return sources_conf

	@staticmethod
	#rewrite project payload
	def project_payload(**kwargs):
		payload_list = []
		payload = {}
		project_models = Project.models()
		models = project_models['models']
		prep_models = project_models['prep_models']
		if 'dynamic_env' in kwargs.keys():
			for model in models:
				dynamic_env_model_name = Project.dynamic_env_model(kwargs['dynamic_env'], model)
				payload_list.append(dynamic_env_model_name)
			for prep_model in prep_models:
				dynamic_env_prep_model = Project.dynamic_env_model(kwargs['dynamic_env'], prep_model)
				payload_list.append(dynamic_env_prep_model)
		else:
			payload_list.append(models)
			payload_list.append(prep_models)
		payload_list.append(list(Project.sources().keys()))
		return list(flatten(payload_list))

	@staticmethod
	def model_paths():
		all_paths = Project._all_model_paths()
		models_and_paths = list(map(lambda x: {x.split('/')[-1].split('.')[0]: x} , all_paths))
		models_and_paths_list = {}
		for item in models_and_paths:
			model_name = list(item)[0]
			models_and_paths_list[model_name] = item[model_name]
		return models_and_paths_list

	@staticmethod
	def _all_model_paths():
		path = './models/'
		return [join(path, f) for f in listdir(path)]
	
	@staticmethod
	def model_config_path(model):
		return f"./models/{model}/model_config.yml"
	
	@staticmethod
	def get_model_config(model):
		try:
			config_file = open(Project.model_config_path(model), "r")
			model_conf = yaml.load(config_file, Loader=yaml.FullLoader)
			config_file.close()
			if model_conf is None:
				return {}
			else:
				return model_conf
		except FileNotFoundError:
			raise MissingModelConfigFile(MissingModelConfigFile.message(model))
	
	@staticmethod
	def dynamic_env_model(dynamic_env, table_name):
		return f"{dynamic_env}_{table_name}"