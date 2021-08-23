# Helpers for Info Objects.
# ----------------------------
def handle_direct_mapping(instance, direct_mapping_list, **kwargs):
	"""
	This is the helper function to handle the direct mapping 
	list and set attributes to the order info class. 

	For direct mapping, key in order info and json will be the
	same. If it is number valued, then the default will be 0
	"""
	for key in direct_mapping_list:
		if key in instance.NUMBER_VALUE_ENTRIES:
			setattr(instance, key, kwargs.get(key, 0))
		else:
			setattr(instance, key, kwargs.get(key, ""))

def handle_special_mapping(instance, special_mapping_dict, **kwargs):
	"""
	This is the helper function to handle the special mapping 
	dict and set attributes to the order info class. 

	For special mapping, Key : Values = OrderInfo Attr : 
	(Json key, defaults) '-->' means under a dictionary
	"""
	for key in special_mapping_dict:
		if isinstance(special_mapping_dict[key], dict):
			# Handle the sub dictionary assignments
			subdict = {}
			for subkey in special_mapping_dict[key]:
				value_tuple = special_mapping_dict[key][subkey]
				# Simple Case
				if "-->" not in value_tuple[0]:
					subdict[subkey] = kwargs.get(value_tuple[0], value_tuple[1])
					continue

				# Need to evaluate subdict from json
				key_tree = value_tuple[0].split("-->")
				current_level_value = kwargs.get(key_tree[0], {})
				for tr in key_tree[1:-1]: 
					current_level_value = current_level_value.get(tr, {})
				subdict[subkey] = current_level_value.get(key_tree[-1], value_tuple[1])
			# Set info dictionary
			setattr(instance, key, subdict)
		else:
			# Default should be tuple
			value_tuple = special_mapping_dict[key]
			setattr(instance, key, kwargs.get(value_tuple[0], value_tuple[1]))