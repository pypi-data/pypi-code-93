import enum
from DodayUtils._exceptions import *
from DodayUtils._dwrappers import *
from DodayUtils._helpers import *
from DodayUtils.promotion.PromotionEffector import *
from gadgethiServerUtils.time_basics import *
from gadgethiServerUtils.file_basics import *

class MemberLevel(enum.IntEnum):
	# Higher level has higher privileges
	basic_member = 0
	silver_member = 1
	black_member = 2
	employee = 3
	manager = 4
	tenant = 5
	admin = 6
	blocked = -1
	
class MemberInfo:
	"""
	This is the ADT that represents the member
	info for PCube / DoDay. 

	Rep:
		* store_id: DDA, DDB or "", for universal stores
		* brand_id: DODAY, MINC, or "", for universal brand
		* activation_key: The key used when duo activation is needed to auth account
		* feedback: admin feedback for this member
		* username: member user name
		* user_id: member user id (line id)
		* national_id: National ID
		* user_phone: member phone number
		* user_email: member email
		* user_address: member resident address
		* password: member password
		* qr_code_id: member qr code id
		* qr_code_address: member qr code card file path
		* reward_points: member points
		* gender: male or female
		* birthday: YYYYmmdd
		* membership_level: membership type
		* payment_method: preferred payment method -> linked credit card in comments
		* favorite_items: list of favorite items
		* enablekey: whether the member is enabled
		* account_verification: verification status
		* profile_pic_url: profile pic url
	"""
	# Assigned default 0 if in the list
	NUMBER_VALUE_ENTRIES = ["reward_points"]
	# These are all the direct mapping list that have the same
	# key names and default empty string
	DIRECT_MAPPING_LIST = ["store_id", "brand_id", "activation_key", "feedback", 
		"username","user_id" ,"national_id" ,"user_phone" ,"user_email" ,"user_address" ,"password" ,"qr_code_id" ,"qr_code_address" ,
		"reward_points", "gender" ,"birthday","payment_method" ,"enablekey" ,"account_verification" , "profile_pic_url",
		"comment1", "comment2", "comment3", "comment4", "comment5", "comment6", "comment7", "comment8", "comment9"]

	# Key : Values = Info Attr : (Json key, defaults)
	#	'-->' means under a dictionary
	SPECIAL_INFO_JSON_MAPPING = {
		"activation_time": ("activation_time", serverTime()),
		"owned_promotion_keys": ("owned_promotion_keys", []),
		"time": ("time", serverTime()),
		"favorite_items": ("favorite_items", []),
		"membership_level": ("membership_level", MemberLevel.basic_member.value)
	}

	# RULES FOR REWARD POINTS ACCUMULATION
	PRICE_TO_REWARD_POINTS_RATIO = 1/50

	def __init__(self, **kwargs):
		# Assign all external variables before doing the orders operations
		handle_direct_mapping(self, self.DIRECT_MAPPING_LIST, **kwargs)
		handle_special_mapping(self, self.SPECIAL_INFO_JSON_MAPPING, **kwargs)
		self.tracked_keys = self.DIRECT_MAPPING_LIST + list(self.SPECIAL_INFO_JSON_MAPPING.keys())
		
	@dutils
	def __str__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __repr__(self, **kwargs):
		return str(self.tojson())

	@dutils
	def __eq__(self, item, **kwargs):
		if item == None or type(item) != MemberInfo:
			return False

		compare_list = ["store_id","brand_id","user_phone", "qr_code_id", "qr_code_address", 
			"reward_points", "username","user_id" ,"national_id"]
		equal_flag_list = []
		for key in compare_list:
			equal_flag_list.append(getattr(self, key) == getattr(item, key))

		return all(equal_flag_list)

	@dutils
	def __lt__(self, item, **kwargs):
		return str(self.activation_time) < str(item.activation_time)

	@classmethod
	@dutils
	def json_format_to_member_info(cls, json_data, **kwargs):
		"""
		Function to transform json (dict) format to member info
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
		member info into json format. do
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
	def add_reward_points_from_order(self, order_info, **kwargs):
		"""
		This is the helper function to add 
		reward points based on the provided
		order info. 
		"""
		self.reward_points += int(order_info.get_total_price()*self.PRICE_TO_REWARD_POINTS_RATIO)

	@dutils
	def deduct_reward_points_from_order(self, order_info, **kwargs):
		"""
		This is the helper function to deduct 
		reward points based on the provided
		order info. 
		"""
		self.reward_points -= order_info["deducted_point"]

	@dutils
	def remove_owned_promotion(self, promotion_key, **kwargs):
		"""
		This is the helper function to move
		owned promotion from the member list. 
		"""
		if promotion_key in self.owned_promotion_keys:
			self.owned_promotion_keys.remove(promotion_key)
		else:
			logging.warning("[MemberInfo]: Promotion Key %s not in member" % promotion_key)

	@dutils
	def prune_expired_promotions(self, expirary_func, **kwargs):
		"""
		This is the helper function to remove
		all the expired promotions from the list.
		- Input:
			* expirary_func: promotion_key -> expirary function -> True/False
				A function that returns whether the promotion key has expired. 
		"""
		for promokey in self.owned_promotion_keys:
			if expirary_func(promokey):
				self.owned_promotion_keys.remove(promokey)





