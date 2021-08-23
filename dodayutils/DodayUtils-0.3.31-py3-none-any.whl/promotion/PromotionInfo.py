from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *
from DodayUtils._helpers import *
from DodayUtils.promotion.PromotionEffector import *
from gadgethiServerUtils.time_basics import *
from gadgethiServerUtils.file_basics import *

class PromotionInfo:
	"""
	This is the ADT that represents the promotion
	info for PCube / DoDay. 

	Rep:
		* store_id: DDA, DDB or "", for universal stores
		* brand_id: DODAY, MINC, or "", for universal brand
		* start_time: The start time for this promotion, epoch time, 
			If not provided, defaults 0, to no limit. 
		* end_time: The end time for this promotion, epoch time
			If not provided, defaults to -1, no limit. 
		* creation_time: epoch
		* exclusive_member: "", or the member's phone number
		* title: human readable promotion title
		* description: human readable string
		* effector: PromotionEffector object (order_info) -> PromotionEffector -> total_discount, 
			the init argument should be a string that represents the identifier of the effector
		* usage_amount: remaining usage amount for this promotion. defaults to 1
		* required_points: required member points to exchange this promotion. -1 if can't be exchanged
		* default_for_store: "", or DDA, DDB store id. 
		* added_to_member: [], this holds a list of members that
			have been added this promotion
		* one_time_per_member: True or False
	"""
	# Assigned default 0 if in the list
	NUMBER_VALUE_ENTRIES = ["start_time"]
	# These are all the direct mapping list that have the same
	# key names and default empty string
	DIRECT_MAPPING_LIST = ["store_id", "brand_id", "exclusive_member", "default_for_store", 
		"start_time", "end_time", "title", "description", "effector", "promotion_key"]

	# Key : Values = Info Attr : (Json key, defaults)
	#	'-->' means under a dictionary
	SPECIAL_INFO_JSON_MAPPING = {
		"creation_time": ("creation_time", serverTime()),
		"usage_amount": ("usage_amount", 1),
		"end_time": ("end_time", -1),
		"required_points": ("required_points", -1),
		"added_to_member": ("added_to_member", []),
		"one_time_per_member": ("one_time_per_member", False)
	}

	def __init__(self, **kwargs):
		# Assign all external variables before doing the orders operations
		handle_direct_mapping(self, self.DIRECT_MAPPING_LIST, **kwargs)
		handle_special_mapping(self, self.SPECIAL_INFO_JSON_MAPPING, **kwargs)
		self.tracked_keys = self.DIRECT_MAPPING_LIST + list(self.SPECIAL_INFO_JSON_MAPPING.keys())
		# self.effector should be a key that exists in pcube_promotions
		if not isinstance(self.effector, PromotionEffector):
			self.effector = PromotionEffector() if self.effector == "" else \
				PromotionEffector(**read_yaml_on_s3("gadgethi-css", "pcube_promotions/"+self.effector+".yaml"))

	@dutils
	def __str__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __repr__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __eq__(self, item, **kwargs):
		if item == None or type(item) != PromotionInfo:
			return False

		compare_list = ["store_id","brand_id","exclusive_member","start_time","end_time","title","description","effector","required_points"]
		equal_flag_list = []
		for key in compare_list:
			equal_flag_list.append(getattr(self, key) == getattr(item, key))

		return all(equal_flag_list)

	@dutils
	def __lt__(self, item, **kwargs):
		return str(self.start_time) < str(item.start_time)

	@classmethod
	@dutils
	def json_format_to_promotion_info(cls, json_data, **kwargs):
		"""
		Function to transform json (dict) format to promotion info
		class object. As there should only be 1 db entry, the
		json and db format is the same thing. 

		There should only be 1 giant dictionary -> representing
		an entry
		"""
		# Clone the db data
		promo_data = copy.deepcopy(json_data)

		return cls(**promo_data)

	@dutils
	def tojson(self, **kwargs):
		"""
		This is the function to transform
		promotion info into json format. do
		json dumps before sending it. 
		"""
		json_dict = {}
		for key in self.tracked_keys:
			json_dict[key] = getattr(self, key)

		return json_dict

	@dutils
	def todb(self, **kwargs):
		"""
		For database format, all dict and list
		must be dump to string before adding it. 
		"""
		db_format = self.tojson()
		for key in db_format:
			if isinstance(db_format[key], (dict, list)):
				db_format[key] = json.dumps(db_format[key], ensure_ascii=False)

		return db_format

	@dutils
	def execute_promotion(self, order_info, **kwargs):
		'''
		Use to enable the discount by reading the order_data and key which the user use.
		Input:
			- order_info
		'''
		if self.exclusive_member != "":
			assert self.exclusive_member == order_info["member_phone"], "Please Login to use this private promotion"

		assert self.usage_amount > 0, "Not enough usage amount for this promotion"

		assert (self.start_time < serverTime() and serverTime() < self.end_time) or self.end_time == -1, "Promotion Expired. "

		return self.effector.apply(order_info)

	@dutils	
	def has_expired(self, **kwargs):
		"""
		This is the observer function
		to check whether the promotion
		has expired or not. 
		"""
		return (self.start_time < serverTime() and serverTime() < self.end_time) or self.end_time == -1

