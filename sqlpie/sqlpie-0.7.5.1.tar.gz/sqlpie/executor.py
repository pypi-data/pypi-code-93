from concurrent.futures import ThreadPoolExecutor
from sqlpie.client import Sqlpie
from time import sleep
import random
import time  

class Executor:

	def __init__(self, account_id, version, status_endpoint=None):
		self.version = version
		self.queue = []
		self.results = {}
		ind_nodes = self.version['dag']['ind_nodes']
		self.append_to_queue(ind_nodes)
		print(self.queue)
		self.run()
	
	def run_task(self, payload):
		if payload['node'] not in self.results.keys():
			self.results[payload['node']] = {}
		self.results[payload['node']]['status'] = 'running'
		self.results[payload['node']]['count'] = 0
		print('='*50)
		print('running')
		print('node name - ', payload['node'])
		print('query - ', payload['rendered_query'])
		secs = random.randint(1,10)
		sleep(3) ##run_query
		self.results[payload['node']]['status'] = 'completed'
		self.results[payload['node']]['count'] += 1 
		print(f"took {secs} seconds")
		print('completed')
		print('='*50)
		print('Appending downstreams - ', payload['downstreams'])
		self.append_to_queue(payload['downstreams'])
		self.run()

	def get_upstream_statuses(self,payload):
		return list(filter(None,set(list(map(lambda upstream: self.results[upstream]['status'] if upstream in self.results.keys() else None, payload['upstreams'])))))

	def execute_task(self, payload):
		if payload in self.queue:
			self.queue.remove(payload)
		print('upstreams', payload['upstreams'])
		print('results - ', self.results.keys())			
		if payload['upstreams']:
			upstream_statuses =	self.get_upstream_statuses(payload)
			print('reduced upstream statuses', upstream_statuses)
			if upstream_statuses == ['completed']:
				print('dependecies completed - starting task')
				if payload['node'] in self.results.keys():
					print(f"Task {self.results[payload['node']]['status']}")
				else:
					self.run_task(payload)
				return True
			else:
				print('not starting - waiting for dependecies to complete')
				print('task statuses - ', self.results)
				if payload not in self.queue:
					self.queue.append(payload)
				return False																
		else:
			print('no dependecies - starting task')
			self.run_task(payload)
			return True

	def append_to_queue(self, nodes):		
		for node in nodes:
			print(node, self.version['table_index'][node]['source_type'])
			if self.version['table_index'][node]['source_type'] in ('model', 'prep'):
				self.queue.append(self.build_payload(node))
			else:
				downstream_nodes = self.version['dag']['dag_index'][node]['downstreams']
				self.append_to_queue(downstream_nodes)

	def build_payload(self, node):
		model_name = self.version['table_index'][node]['schema']
		print('model_name', model_name)
		if '_prep' in model_name:
			model_name = model_name.replace('_prep', '')
		payload = self.version['models'][model_name]['rendered_model'][node]

		payload['node'] = node
		payload['downstreams'] = self.version['dag']['dag_index'][node]['downstreams']
		payload['upstreams'] = self.version['dag']['dag_index'][node]['predecessors']
		return payload

	def run(self):
		print('queue lenght-', len(self.queue))		
		with ThreadPoolExecutor(max_workers = 5) as executor:
			results = executor.map(self.execute_task, self.queue)
		for result in results:
			print(result)
		print(self.results)


