from gadgethiServerUtils.db_operations import *
from gadgethiServerUtils.db_basics import *
from gadgethiServerUtils.time_basics import *
from gadgethiServerUtils.encryption import *
from gadgethiServerUtils.file_basics import *
from DodayUtils.menu.MenuUtils import *
import json

import copy
import yaml
import boto3

class MenuInfo():
	"""
	Menu Info expects to turn database information into different existing menu type
	Now we supports 3 version of menu 1. Uber 2. Doday 3. Pcube
	We only support from database -> Uber, Doday, Pcube
	In the future we might support from different menu to database type
	=================
	The following are the guide to all public functions.
	1. add_item() -> use to add one item in the database
	2. delete_item() -> use to delete one item in the database
	3. update_item() -> use to update information in the database
	4. select_item() -> use to select one item out
	5. connect_item() -> use to create connection
	6. disconnect_item() -> use to delete connection 
	=================
	Database strucute looks like this
	_id: postgres default
	brand_id: Doday
	store_id: DDA
	key: SHA256(level+name+create_time)
	level: menu=1,category=2,item=3,choice_group=4
	image_url: "http://......." str
	description: ""  str 
	name: str
	price: int
	suspend: int
	delivery_price int *
	other_information_dict: {}
	time: create_time
	dependency: ["key","key","key"]

	"""
	def __init__(self,store_id):
		self.brand_id = ""
		self.store_id = store_id
		self.Encrypt = GadgetEncryption('','')
		self._renew_menu_data()

	def add_item(self,item_input,**kwargs):
		"""
		use to add one item in the database
		Input
			- list dict type [{},{},{}]
				- level type int *
				- name str *
				- price int *
				- suspend int *
				- other_information_dict type dict *
				- delivery_price int *
		Output
			- add database succeed or not
		"""
		# check list type
		self._isinstance_list(item_input)
		insert_list,save_check = [],[]
		for item in item_input:
			self._isinstance_dict(item)
			self._item_check(item)
			item.update({
				'brand_id': self.brand_id,
				'store_id': self.store_id,
				'dependency': '[]',
				'time': int(serverTime()),
				'key' : self.Encrypt.sha256encrypt_string(str(item['level'])+item['name']+str(int(serverTime())))})
			save_check.append(item['key'])
			insert_list.append(item)
		self._list_duplicate_check(save_check)
		_ = add_to_table('menu',insert_list)
		self._renew_menu_data()
		return {"indicator":True,"message":"add_to_table"}

	def delete_item(self,delete_item_input,**kwargs):
		"""
		use to delete one item in the database
		Input
			- list type
				- key ['','','']
		Output
				- key
		In the same time, I will disconnect the item by calling disconnect item
		"""
		final_update_list = []
		self._isinstance_list(delete_item_input)
		for delete_item in delete_item_input:
			self.disconnect_item(delete_item)
			final_update_list.append({"store_id":"abandone","brand_id":"abandone","key":delete_item})
		_ = edit_on_table('menu',final_update_list,["key"])
		self._renew_menu_data()
		return {"indicator":True,"message":"delete_item"}


	def update_item(self,update_item_input,**kwargs):
		"""
		update one item in the database
		Input
			- key [{},{}]
		Output
			- {} dictionary type 

		"""
		final_update_list = []
		self._isinstance_list(item_input)
		for update_item in update_item_input:
			self._isinstance_dict(update_item)
			self._update_item_check(update_item)
			update_item = self._update_information_prepare(update_item)
			final_update_list.append(update_item)
		_ = edit_on_table('menu',final_update_list,["key"])
		self._renew_menu_data()
		return {"indicator":True,"message":"update_item"}


	def select_item(self,argument='',level=0,level_search=False,normal_mode=True,multicontraint=False,**kwargs):
		"""
		use to select one item in the database
		Input
			normal_mode:
			- level
			- argument item ''
			or
			- key item '' 
		Output
			- return an item [{}] or [{},{}]
		"""		
		if level_search:
			data = self._level_mode_search(level)
		elif normal_mode:
			data = self._normal_mode_search(level,argument,multicontraint)
		else:
			data = self._specific_mode_search(argument)
		return data



	def connect_item(self,argument_list,normal_mode=True,**kwargs):
		"""
		connect item to make dependency
		Input:[{"name":"","level":2,"connected_name":,"connected_level":1},{},{},{}s]
			normal mode:
			- name item
			- level int
			- name one you would like to connect
			---> if there is more than one duplicate name the normal mode is prohibited
			---> 1 -> 2, 2 -> 3, 3 -> 4, 4 -> 3 only these connection is allowed
			specific mode:
			[{"key":"","connected_key":{}},{},{},{}s]
			- key item
			- key the one you would like to connect
			---> no name contraint but have level contraint
			---> 1 -> 2, 2 -> 3, 3 -> 4, 4 -> 3 only these connection is allowed

		Output:
			- add database succeed or not
		"""
		update_dict,final_update_list = {},[]
		if normal_mode:
			for connect_element in argument_list:
				self._check_level(connect_element)
				# check whether two items are all unique
				subitem = self.select_item(connect_element['name'],connect_element['level'],multicontraint=True) 
				mainitem = self.select_item(connect_element['connected_name'],connect_element['connected_level'],multicontraint=True)
				print("subitem",subitem,mainitem)
				subitem,mainitem = self.item_data_test(subitem),self.item_data_test(mainitem)
				update_dict = self._update_connect_item(subitem,mainitem,update_dict)

				# connect dependency
		else:
			for connect_element in argument_list:
				subitem = self.select_item(connect_element['key'],normal_mode=False)
				mainitem = self.select_item(connect_element['connected_key'],normal_mode=False)
				subitem,mainitem = self.item_data_test(subitem),self.item_data_test(mainitem)
				update_dict = self._update_connect_item(subitem,mainitem,update_dict)

		for i in update_dict.keys():
			update_dict[i]["dependency"] = json.dumps(update_dict[i]["dependency"])
			final_update_list.append(update_dict[i])
		_ = edit_on_table('menu',final_update_list,["key"])
		self._renew_menu_data()
		return {"indicator":True,"message":"connected"}




	def disconnect_item(self,key,specific_key='',**kwargs):
		"""
		disconnect item to delete dependency
		2 -> 1, 3 -> 2 4 -> 3 3 -> 4
		Input
			- key item ''
		Output
			- modify database succeed or not
		"""
		final_update_list = []
		if specific_key == '':
			subitem = self.select_item(key,level_search=False,normal_mode=False) 
			subitem = self.item_data_test(subitem)
			if subitem['level'] == MenuLevel.item.value:
				mainitem = self.select_item(level=MenuLevel.category.value,level_search=True,normal_mode=False)
				mainitem2 = self.select_item(level=MenuLevel.modifier_group.value,level_search=True,normal_mode=False)
				mainitem += mainitem2
			else:
				mainitem = self.select_item(level=(subitem['level']-1),level_search=True,normal_mode=False)
		else:
			subitem = self.select_item(key,level_search=False,normal_mode=False) 
			mainitem = self.select_item(specific_key,level_search=False,normal_mode=False) 
			subitem,mainitem = self.item_data_test(subitem),self.item_data_test(mainitem)
			self._check_level({"level":subitem['level'],"connected_level":mainitem['level']})
			# make data type consistent with if case
			mainitem = [mainitem]

		for items in mainitem:
			dependency = json.loads(items['dependency'])
			if subitem['key'] in dependency:
				dependency.remove(subitem['key'])
				items['dependency'] = json.dumps(dependency)
			final_update_list.append({"key":items['key'],"dependency":items['dependency']})

		_ = edit_on_table('menu',final_update_list,['key'])
		self._renew_menu_data()
		return {"indicator":True,"message":"disconnected"}



	def Export_To_Doday_Format(self,menu):
		"""
		Input
			- None
		Output
			- dictionary just like yaml
		2. Find the menu you would like to export
		3. Remove the Item which the time is larger than the time now
		4. Compress all the information together
		5. Make final adjustment
		6. Export
		"""
		mapping_table = self._mapping_table

		for i in self.menu_data:
			if i['name'] == menu:
				level2_dependency = json.loads(i['dependency'])

		menu_dict = {}

		for level2 in level2_dependency:
			# level2 -> 系列
			level3_dependency = json.loads(mapping_table[level2]['dependency'])
			serial_dict = {}
			for level3 in level3_dependency:
				# level3 -> 品項
				level4_dependency = json.loads(mapping_table[level3]['dependency'])
				# generate {"addons":......}
				addons = self._doday_addons_helper(level4_dependency)
				desc = mapping_table[level3]['description']
				price = "NT$ "+str(mapping_table[level3]['price'])
				img = mapping_table[level3]['image_url']
				delivery_price = mapping_table[level3]['delivery_price']
				conditional_dict = json.loads(mapping_table[level3]['other_information_dict'])
				name = mapping_table[level3]['name']
				try:
					conditional = conditional_dict['doday']['conditional']
					serial_dict[name] = {"desc":desc,"price":price,"delivery_price":delivery_price,"img":img,"addons":addons,"conditional":conditional}
				except:
					serial_dict[name] = {"desc":desc,"price":price,"delivery_price":delivery_price,"img":img,"addons":addons}
			name = mapping_table[level2]['name']
			menu_dict[name] = serial_dict

		doday_module = {"store_id":self.store_id,"category":menu_dict}
		print("doday_module",json.dumps(doday_module))
		return doday_module

	def Export_To_Uber_Format(self):
		"""
		This function turns the data into Uber compatiable version
		Input -
			No Required
		Output -
			Uber Json format
		1. get all the data down
		2. rearrange into specific order menu -> categories -> item -> modifier group
		3. UBER will needs some specific information, the items would be stored in other information tag 
		like {"uber":{},"doday":{},"pcube":{}}, other public information will be provided in Uber Class Enum
		4. Uber Json Format
		"""
		mapping_table = self._mapping_table
		# menus part ============
		menus = []
		for data in self.menu_data:
			if self._equal_level(data,1):
				_id,title = self._uber_must_element(data)
				# print("_id,title",_id,title)
				category_ids = json.loads(data['dependency'])
				other_information_dict = json.loads(data['other_information_dict'])
				service_availability = other_information_dict['uber']['service_availability']
				menus.append({"id":_id,"title":title,"category_ids":category_ids,"service_availability":service_availability})
				# print("menus",menus)
		# print("menus",menus)
		# categories part ============ 
		categories = []
		for data in self.menu_data:
			if self._equal_level(data,2):
				_id,title = self._uber_must_element(data)
				entities = []
				dependency = json.loads(data['dependency'])
				for dependencies in dependency:
					entities.append({"id":dependencies})
				categories.append({"id":_id,"title":title,"entities":entities})
		# items part =================
		items = []
		for data in self.menu_data:
			if self._equal_level(data,3):
				_id,title = self._uber_must_element(data)

				description = UberMenuTemplate.description.value
				description = copy.deepcopy(description)
				description['translations']['en'] = data['name']
				item = UberMenuTemplate.item.value
				item = copy.deepcopy(item)
				item['image_url'] = data.get("image_url","")
				item['price_info']['price'] = data['delivery_price'] * UberPriceTransform.Taiwan
				item['suspension_info']['suspension']['suspend_until'] = data['suspend']
				item['modifier_group_ids']['ids'] = json.loads(data['dependency'])
				item.update({"id":_id,"title":title,"description":description})
				items.append(item)
		# modifier group part =================
		modifier_groups = []
		for data in self.menu_data:
			if self._equal_level(data,4):
				_id,title = self._uber_must_element(data)
				other_information_dict = json.loads(data['other_information_dict']) 
				modifier_group = UberMenuTemplate.modifier_group.value
				modifier_group = copy.deepcopy(modifier_group)
				other_information_dict_uber = other_information_dict.get("uber",{"min_permitted":1,"max_permitted":1})
				modifier_group['quantity_info']['quantity']['min_permitted'] = other_information_dict_uber["min_permitted"]
				modifier_group['quantity_info']['quantity']['max_permitted'] = other_information_dict_uber["max_permitted"]
				
				modifier_options = []
				dependency = json.loads(data['dependency'])
				for dependencies in dependency:
					modifier_options.append({"id":dependencies,"type":"ITEM"})

				modifier_group.update({"id":_id,"title":title,"modifier_options":modifier_options})
				modifier_groups.append(modifier_group)

		_return_dict = {"menus":menus,"categories":categories,"items":items,"modifier_groups":modifier_groups,"display_options": {"disable_item_instructions": True}}
		# _return_dict = json.dumps(_return_dict)
		return _return_dict



	def Export_To_Pcube_Format(self,menu,**kwargs):
		"""
		This function transfers to the pcube format
		Concept 
		- *category
			- regions
				- CanBeHead: true
				- MandatoryModifiers: []
				- OptionalModifiers: []
				- PriceIfChosenAsAddon: 60
				- boundaries: []
				- id: 零糖豆漿豆花
				- price: 60
				- type: ItemRegion
		- *modifier_groups
			- regions
				- CanBeHead: false
				- MandatoryModifiers: []
				- OptionalModifiers: []
				- PriceIfChosenAsAddon: 0
				- boundaries: []
				- id: 去冰
				- price: 60
				- type: ItemRegion
		- Buttons(This will be the default value)
		"""
		mapping_table = self._mapping_table

		for i in self.menu_data:
			if i['name'] == menu:
				level2_dependency = json.loads(i['dependency'])
				# level2_dependency == categories ids ex. ['2313123','hsukdfhk']
		categories_dict = {}		
		for level2 in level2_dependency:
			# level2 is the id of the category ex. 精選系列
			level3_dependency = json.loads(mapping_table[level2]['dependency'])
			regions_list = []
			for level3 in level3_dependency:
				# level3 is the id of the item ex. 絕配ㄧ
				item = self._pcube_item_must_element(mapping_table[level3])
				regions_list.append(item)
			categories_dict.update({mapping_table[level2]['name']:regions_list})

		modifier_groups_dict = {}
		level4_data = self.select_item(self,level=4,level_search=True,**kwargs)
		for level4 in level4_data:
			level5_dependency = json.loads(level4['dependency'])
			# level5_dependency == addons options ex.去冰 ex. ['2313123','hsukdfhk']
			regions_list = []
			for level5 in level5_dependency:
				item = self._pcube_addons_must_element(mapping_table[level5])
				regions_list.append(item)
			modifier_groups_dict.update({level4['name']:regions_list})
		
		s = PcubeMenuTemplate.Required_button.value
		modifier_groups_dict.update({"id":"Buttons","regions":s})

		_return_dict = {}
		_return_dict.update(categories_dict)
		_return_dict.update(modifier_groups_dict)
		return _return_dict


	def doday_check_availability(self):
		"""
		Name might be conflict, maybe there will be better way to 
		return Name:Boolean way
		"""
		menu_data = self.menu_data
		_return_availability_dict = {}
		for data in menu_data:
			if data['suspend'] < int(serverTime()):
				_return_availability_dict.update({data["name"]:True})
			else:
				_return_availability_dict.update({data["name"]:False})
		return _return_availability_dict


	def generate_doday_name_mapping_table(self):
		"""
		This function makes key -> dict
		ex. [{"key":"aa","name":"bb"},{"key":"cc","name":"dd"}]
			-> {"aa":{"key":"aa","name":"bb"},"cc":{"key":"cc","name":"dd"}
		"""
		_return_dict = {}
		for item in self.menu_data:
			_return_dict.update({item["name"]:item})
		return _return_dict

	# ====================================================================
	# Helper Function
	# ====================================================================

	def _check_level(self,data_dict):
		if data_dict['level'] == MenuLevel.item.value and data_dict['connected_level'] == MenuLevel.modifier_group.value:
			pass
		elif data_dict['level'] - data_dict['connected_level'] != 1:
			raise Exception("level Error")

	def _equal_level(self,dict_data,level):
		if dict_data['level'] != level:
			return False
		else:
			return True

	def _generate_mapping_table(self):
		"""
		This function makes key -> dict
		ex. [{"key":"aa","name":"bb"},{"key":"cc","name":"dd"}]
			-> {"aa":{"key":"aa","name":"bb"},"cc":{"key":"cc","name":"dd"}
		"""
		_return_dict = {}
		for item in self.menu_data:
			_return_dict.update({item["key"]:item})
		self._mapping_table = _return_dict

	def _isinstance_list(self,a):
		if not isinstance(a, list):
			raise TypeError

	def _isinstance_dict(self,a):
		if not isinstance(a, dict):
			raise TypeError

	def _item_check(self,input_dict):
		# check whether item stick to the rule
		require_content_list = ["level","name","price","suspend","other_information_dict","delivery_price"]
		option_content_list = ["description","image_url"]
		if not all([i in input_dict for i in require_content_list]):
			raise ValueError
		if input_dict['level'] not in [MenuLevel.menu.value,MenuLevel.category.value,MenuLevel.item.value,MenuLevel.modifier_group.value]:
			raise ValueError
		if input_dict['suspend'] < 0 and input_dict['price'] < 0:
			raise ValueError
		for option in option_content_list:
			if option not in input_dict:
				input_dict[option] = ""
		self._isinstance_dict(json.loads(input_dict['other_information_dict']))

	def _list_duplicate_check(self,element):
		if len(element) != len(set(element)):
			raise ValueError

	def _level_mode_search(self,argument):
		_return_list = []
		for entry in self.menu_data:
			if entry['level'] == argument:
				_return_list.append(entry)
		return _return_list

	def _normal_mode_search(self,level,argument,multicontraint=False):
		"""
		Select information with normal_mode
		- Input
			argument string
		_ Output
			_return_list [{},{}] or [{}] 
		"""
		_return_list = []
		for entry in self.menu_data:
			if entry['name'] == argument and entry['level'] == level:
				_return_list.append(entry)
		if len(_return_list) >= 2 and multicontraint:
			raise ValueError
		return _return_list

	def item_data_test(self,item):
		"""
		check whether Exist or not
		"""
		try:
			item = item[0]
		except:
			raise Exception("Item does not Exist")
		return item

	def _renew_menu_data(self):
		self.menu_data = get_data('menu',["store_id"],[self.store_id])
		self._generate_mapping_table()

	def _specific_mode_search(self,argument):
		"""
		Select information with normal_mode
		- Input
			argument string
		_ Output
			_return_list [{},{}] or [{}] 
		"""
		_return_list = []
		for entry in self.menu_data:
			if entry['key'] == argument:
				_return_list.append(entry)
				break
		return _return_list

	def _update_item_check(self,item):
		restrict_content_list = ["store_id","brand_id","level","time","dependency"]
		if not all([i in item for i in require_content_list]):
			raise ValueError
		if "key" not in item.keys():
			raise "Require key to update the list"

	def _update_information_prepare(self,item):
		_return_dict = {}
		authorized_content_list = ["name","price","suspend","other_information_dict"]
		for i in authorized_content_list:
			try:
				_return_dict[i] = item[i]
			except:
				pass
		return _return_dict

	def _update_connect_item(self,subitem,mainitem,_update_dict):
		if mainitem["key"] in _update_dict.keys():
			# when the items are in connect list before
			if subitem["key"] not in mainitem["dependency"]:
				_update_dict[mainitem["key"]]['dependency'].append(subitem["key"])
		else:
			# when the items are not in connect list
			try:
				mainitem["dependency"] = json.loads(mainitem["dependency"])
			except:
				pass
			if subitem["key"] not in mainitem["dependency"]:
				mainitem["dependency"].append(subitem["key"])
				_update_dict.update({mainitem["key"]:{"key":mainitem["key"],"dependency":mainitem["dependency"]}})
		return _update_dict



	def _doday_addons_helper(self,addons_dependency_list):
		"""
		This function handles the addons to make code simpler
		the input will be the add_ons title
		[]
		"""
		_return_dict = {}
		mapping_table = self._mapping_table
		for addons in addons_dependency_list:
			level5_dependency = json.loads(mapping_table[addons]['dependency'])
			addons_group_name_dict = {}
			addons_name_list,addons_price_list = [],[]
			for level5 in level5_dependency:
				addons_name_list.append(mapping_table[level5]['name'])
				addons_price_list.append(mapping_table[level5]['price'])
			doday_dict = json.loads(mapping_table[addons]['other_information_dict'])
			addons_group_name_dict[mapping_table[addons]['name']]= {"choices":addons_name_list,"addonid":addons_name_list,"addprice":addons_price_list,"mode":doday_dict['doday']['mode']}
			_return_dict.update(addons_group_name_dict)

		return _return_dict


	def _uber_must_element(self,data):			
		_id = data['key']
		title = UberMenuTemplate.title.value
		title = copy.deepcopy(title)
		title['translations']['en'] = data['name']
		return _id,title

	def _pcube_item_must_element(self,data):
		# the program will default as mandatory option only if there is specific define in the other information
		# "CanBeHead":True,"MandatoryModifiers":[],"OptionalModifiers":[] these three things are somehow complicated
		mapping_table = self._mapping_table
		item = PcubeMenuTemplate.ItemRegion_element.value
		item = copy.deepcopy(item)
		item['PriceIfChosenAsAddon'] = data['price']
		item['price'] = data['price']
		item['id'] = data['name']
		if json.loads(data['dependency']) == []:
			item['CanBeHead'] = False

		for _id in json.loads(data['dependency']):
			level4 = mapping_table[_id]
			other_information_dict = json.loads(level4['other_information_dict'])
			level4_other_information_dict = other_information_dict.get("pcube",{"min_permitted":1,"max_permitted":1})
			if level4_other_information_dict["min_permitted"] == 0:		
				for i in range(0,level4_other_information_dict['max_permitted']):
					item['OptionalModifiers'].append(level4['name'])
			else:
				for i in range(0,level4_other_information_dict['max_permitted']):
					item['MandatoryModifiers'].append(level4['name'])
		return item


	def _pcube_addons_must_element(self,data):
		mapping_table = self._mapping_table
		item = PcubeMenuTemplate.ItemRegion_element.value
		item = copy.deepcopy(item)
		item['PriceIfChosenAsAddon'] = data['price']
		item['price'] = data['price']
		item['id'] = data['name']
		# other_information_dict = json.loads(level4['other_information_dict'])
		# level4_other_information_dict = other_information_dict.get("pcube",{"CanBeHead":False})
		item['CanBeHead'] = False
		item['OptionalModifiers'] = []
		item['MandatoryModifiers'] = []
		return item