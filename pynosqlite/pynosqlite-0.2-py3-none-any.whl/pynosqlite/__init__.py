from pathlib import Path
from time import time as utc_timestamp
import json
from typing import Any, Dict, List
from filelock import FileLock, Timeout


class PyNoSQLite:

	__content = {'info': {'last_id': 0, 'created_at': int(utc_timestamp())},'data': {}}
	__file = None
	__file_lock = None

	def __init__(self, file='db.json', indent=4):
		self.__file_lock = FileLock(f'{file}.lock', timeout=5)
		self.__file = file
		self.indent = indent
		if Path(file).is_file():
			self.__load_db_from_file()
		else:
			self.__create_db()

	def __del__(self):
		self.__dump_db_into_file()
		if self.__file_lock != None:
			self.__file_lock.release()
	
	def __create_db(self):
		if not Path(self.__file).is_file():
			self.__dump_db_into_file()
			return True
		return False
	
	def __load_db_from_file(self):
		try:
			self.__file_lock.acquire()
			with open(self.__file, 'r') as fp:
				content = json.load(fp)
			assert all(key in content for key in ['data','info'])
			assert all(key in content['info'] for key in ['last_id','created_at'])
			self.__content = content
		except Exception as e:
			if type(e).__name__ == 'Timeout':
				exit('Error: database file is currently in used by another object')
			elif type(e).__name__ in ['AssertionError', 'JSONDecodeError']:
				exit(f'Error: file {self.__file} already exist, but data is corrupted.')
			else:
				raise e
		finally:
			self.__file_lock.release()

	def __dump_db_into_file(self):
		self.__file_lock.acquire()
		with open(self.__file, 'w') as fp:
			fp.write(json.dumps(self.__content, indent=self.indent))
		self.__file_lock.release()

	def info(self):
		self.__load_db_from_file()
		info = {'total': len(self.__content['data'])}
		info.update(self.__content['info'])
		return info
	
	def insert(self, new_data: Dict) -> int:
		self.__load_db_from_file()
		new_id = self.__content['info']['last_id'] + 1
		self.__content['data'][str(new_id)] = new_data
		self.__content['info']['last_id'] = new_id
		self.__dump_db_into_file()
		return new_id

	def insert_many(self, new_data_list: List[Dict]) -> List[int]:
		new_ids = []
		for new_data in new_data_list:
			id = self.insert(new_data)
			new_ids.append(id)
		return new_ids

	def delete(self, id: int) -> Any:
		id = str(id)
		self.__load_db_from_file()
		if id in self.__content['data']:
			del self.__content['data'][id]
			self.__dump_db_into_file()
			return True
		return None
	
	def delete_many(self, ids: List[int]) -> List[int]:
		deleted = []
		for id in ids:
			if self.delete(id) == True:
				deleted.append(id)
		return deleted

	def find(self, id: int) -> Dict:
		id = str(id)
		self.__load_db_from_file()
		if id in self.__content['data']:
			return self.__content['data'][id]
		return None

	def search(self, query: Dict):
		print('Not implemented yet')

	def all(self):
		self.__load_db_from_file()
		return self.__content['data']




