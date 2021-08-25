from sqlpie.client import Sqlpie
from sqlpie.project import Project
from sqlpie.exceptions import BadInputError, UnknownSourceError
import yaml
import json

class DynamicEnv:
	def __init__(self, **kwargs):
		self.version_diff = self.extract_version_diff(kwargs['dynamic_env'], kwargs['prod_version'], kwargs['branch_version'])
		inital_dynamic_env = Sqlpie(vars_payload={"dynamic_env": kwargs['dynamic_env']})		
		if self.version_diff:
			inital_dynamic_env.render_from_tables(self.version_diff)
			self.diff_lineage = inital_dynamic_env.from_tables_dag.topological_sort()
			self.version = Sqlpie(vars_payload={"dynamic_env": kwargs['dynamic_env'], 'dynamic_env_diff': self.diff_lineage})
			self.version.render_from_tables(self.diff_lineage)
			self.version.api_data['version_diff_dag'] = self.version.api_data.pop('from_tables_dag')
		else:
			self.version = inital_dynamic_env
	
	def extract_version_diff(self, dynamic_env, prod_version , branch_version):
		diff = []
		prod_models = list(prod_version.keys())
		branch_models = list(branch_version.keys())
		all_models = prod_models + branch_models
		for model in all_models:
			if model in prod_version.keys():
				prod_version_keys = list(prod_version[model]['rendered_model'].keys())
			else:
				prod_version_keys = []
			if model in branch_version.keys():
				branch_version_keys = list(branch_version[model]['rendered_model'].keys())
			else:
				branch_version_keys = []
			all_keys = list(set(dict.fromkeys(prod_version_keys+branch_version_keys))) 
			lenl = len(all_keys)
			for i in range(lenl):
				if all_keys[i] not in prod_version_keys or all_keys[i] not in branch_version_keys or prod_version[model]['rendered_model'][all_keys[i]] != branch_version[model]['rendered_model'][all_keys[i]]:
					if all_keys[i] in branch_version_keys:
						diff.append(f"{dynamic_env}_{all_keys[i]}")
		return list(set(diff))