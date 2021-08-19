import logging
import sys, os
import time
import json
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *

class InventoryItem:
	def __init__(self, **inv_properties):
		self.invid = inv_properties["invid"]
		self.subitems_count = inv_properties["subitems_count"]
		self.upstream_name = inv_properties["upstream_name"]
		self.upstream_phone = inv_properties["upstream_phone"]

class Food(InventoryItem):
	# This is for general food
	def __init__(self, **food_properties):
		super().__init__(**food_properties)
		self.name = food_properties["name"]
		self.made_date = food_properties["made_date"]
		self.expirary_date = food_properties["expirary_date"]

class CentralKitchenRawMaterials(Food):
	# This is for central kitchen raw material
	pass

class ThirdPartyOrderedFood(Food):
	# This is for third party ordered food
	pass

class BucketFood(Food):
	# This is for bucket based food
	pass

class DodayInventory:
	"""
	This is the class for DoDay inventory
	management. One instance for a store or a kitchen. 
	"""
	@dutils 
	def __init__(self, inventory_mode="store", **configs):
		# mode can be 'store' or 'kitchen'
		if inventory_mode == 'store':
			pass
		elif inventory_mode == 'kitchen':
			pass
		else:
			raise DodayUtilError("Unsupported mode for doday websocket")

