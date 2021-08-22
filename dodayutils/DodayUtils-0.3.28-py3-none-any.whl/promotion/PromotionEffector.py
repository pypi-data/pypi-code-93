import enum
import copy
import json
import logging

class PromotionType(enum.IntEnum):
	fix_price = 0
	buyget = 1
	discount = 2
	offset = 3

class PromotionStrategy(enum.IntEnum):
	choose_top_price = 0
	allow_target_partially_met = 1
	overwrite_item_based_discount_rounding = 2

class PromotionTarget:
	"""
	Represents the target that
	the promotion should apply. 

	target identifier pattern:
	- *: all
	- {category}/{title}/{options}/{subitems}: Four
	level menu hierarchy. If at any level * is presented, 
	that means all items at that level.

	Rep:
		- target_list: a list of list of menu level identifiers string / or *
			length must be 4 -> number of menu levels
	"""
	def __init__(self, target_list, **kwargs):
		self.target_list = copy.deepcopy(target_list)
		self._check_rep()

	def __eq__(self, other):
		# TODO: This is used to check target overlap
		if not isinstance(other, PromotionTarget) or other == None:
			return False

		for i in range(len(self.target_list)):
			intset = set(self.target_list[i]).intersection(set(other.target_list[i]))
			if len(intset) != 0 or ("*" in self.target_list[i] and other.target_list[i] != []) or \
				("*" in other.target_list[i] and self.target_list[i] != []):
				return True

		return False

	def _check_rep(self):
		assert len(self.target_list) == 4

	@classmethod
	def create_target(cls, target_list):
		# categories, titles, options, subitems
		target_input_list = [[], [], [], []] 
		for target in target_list:
			target_item_list = target.split("/")
			for i in range(len(target_input_list)):
				if i < len(target_item_list):
					target_input_list[i].append(target_item_list[i])
				else:
					target_input_list[i].append("*")

		return cls(target_input_list)

	def matches(self, order_item, allow_partial=False):
		"""
		This is the helper function to check whether
		the target matches the order item. 
		"""
		# Deflate value list
		option_values = []
		for val in list(order_item.options.values()):
			option_values.extend(val)

		item_match_check_list = [order_item.category, order_item.title, list(order_item.options.keys()), option_values]
		track_idx_set = set([i for i in range(len(self.target_list[0]))])
		# TODO: allow partial is not implemented right now
		for cid in range(len(self.target_list)):
			wildcard_indices = set([i for i, x in enumerate(self.target_list[cid]) if x == "*"])
			# list based matching or exact matching
			if isinstance(item_match_check_list[cid], list):
				exact_match_indices = set([i for i, x in enumerate(self.target_list[cid]) if x in item_match_check_list[cid]])
			else:
				exact_match_indices = set([i for i, x in enumerate(self.target_list[cid]) if x == item_match_check_list[cid]])

			track_idx_set = track_idx_set.intersection(wildcard_indices.union(exact_match_indices))
		
		return len(track_idx_set) != 0

class PromotionEffector:
	"""
	Represent a transfer function from order info 
	to total discount. 
	(order_info) -> PromotionEffector -> total_discount

	Rep:
		* promoproperties: effector yaml for effector definition. e.g.
			promotion:
				- 
				promotype: PromotionType enum identifier (str)
				promostrategy: a list of PromotionStrategy enum identifier (str)
				promopricing: ident to indicate the amount of promotion pricing (str)
				target: PromotionTarget identifier list (list of str)
				max_save_price: max price that is able to discount (int)
				max_apply_items: If there are multiple occurences, 
					defines the maximum apply items.  (int)
	
	Rep invariant:
		* if there are multiple promotion properties, they must be mutually exclusive. 
		i.e., the target should be different set. 
	"""
	def __init__(self, **promoproperties):
		self.properties = promoproperties["promotion"]
		self._check_rep()

	def __str__(self):
		return json.dumps(self.properties)

	def __repr__(self):
		return json.dumps(self.properties)

	def __eq__(self, other):
		if not isinstance(other, PromotionEffector) or other == None:
			return False

		return self.properties == other.properties

	def _check_rep(self):
		# target_list = []
		# for promo_properties in self.properties:
		# 	target_list.append(PromotionTarget.create_target(promo_properties["target"]))

		# # Make sure mutually exclusive
		# for x in range(len(target_list)):
		# 	for y in range(len(target_list)):
		# 		if x == y:
		# 			continue
		# 		assert target_list[x] != target_list[y] and isinstance(target_list[x], PromotionTarget) \
		# 			and isinstance(target_list[y], PromotionTarget), "Promotion Includes Overlapping Targets"
		for prop in self.properties:
			# Buy get not allowed
			assert prop["promotype"] != "buyget" or "overwrite_item_based_discount_rounding" not in prop["promostrategy"],\
				"Promostrategy not allowed"

			assert "overwrite_item_based_discount_rounding" not in prop["promostrategy"] or ("*" in prop["target"] or "*/*/*/*" in prop["target"]),\
				"The strategy needs global target"

	def apply(self, order_info):
		"""
		This is the main mutator function that
		executes the promotion effector. 
		- Input:
			* order_info: Order that should
			apply promotion on. 
		"""
		total_discount = 0
		for promo_properties in self.properties:
			# Call effector function and apply min max guard
			total_discount += min(getattr(self, promo_properties["promotype"]+"_eff")(order_info, **promo_properties), promo_properties["max_save_price"])

		logging.info("exc promotion promo properties "+str(self.properties))
		logging.info("exc promotion return order_info = "+str(order_info))
		logging.info("exc promotion return total discount = "+str(total_discount))

		return total_discount

	# Effectors for different promotion types
	# ------------------------------------------
	def fix_price_eff(self, order_info, **properties):
		"""
		Effector for fix price item promotion. 
		- Input:
			* order_info: original order info data

		promopricing: (str) fix price. 
		promostrategy: if overwritten is on, the fix price
			will be the global fix. 
		"""
		fix_price = int(properties["promopricing"])

		def item_mutator(item):
			item['discount'] = int(item['price'])
			item['final_price'] = fix_price
			return fix_price

		overwritten_discounted_price = int(order_info['plastic_bag']) + fix_price
		return self._promotion_universal_eff(order_info, item_mutator, 
										overwritten_discounted_price, **properties)

	def buyget_eff(self, order_info, **properties):
		"""
		Effector for buy get free item promotion. 
		Must be exactly same item, allow for partially
		matches
		- Input:
			* order_info: original order info data

		promopricing: (str) 1/1 -> buy one get one free
			2/1 -> buy two get one free
		"""
		buy, get = properties["promopricing"].split("/")
		buybowl, getbowl = int(buy), int(get)
		checked_index_set = set()

		def item_mutator(item):
			temp_list = [item]
			total_bowl_counter = 1
			for inner_item in order_info:
				if id(item) == id(inner_item):
					# Exactly identical
					continue

				# TODO: In the future, if partial matches is required, need
				# to provide this function in DodayItem
				if item == inner_item and id(item) not in checked_index_set \
					and id(inner_item) not in checked_index_set:
					# Add total identical bowl count if not counted yet and identical
					total_bowl_counter += 1
					temp_list.append(inner_item)

					# Not met the buy get req yet. 
					if total_bowl_counter < buybowl + getbowl:
						continue

					# Assign free items
					for free_item in temp_list[:getbowl]:
						free_item['discount'] = int(free_item['price'])
						free_item['final_price'] = 0

					for added_item in temp_list:
						checked_index_set.add(id(added_item))

			return item['final_price'] if id(item) in checked_index_set else item["price"]

		return self._promotion_universal_eff(order_info, item_mutator, **properties)

	def discount_eff(self, order_info, **properties):
		"""
		Effector for selected item discount promotion. 
		- Input:
			* order_info: original order info data

		promopricing: (str -> to int) e.g. 80, 79, (% discount)
		"""
		# global total price
		discount_rate = int(properties["promopricing"]) / 100.0

		def item_mutator(item):
			final_price = round(int(item['price']) * discount_rate)	
			item['discount'] = int(item['price']) - final_price
			item['final_price'] = final_price
			return final_price

		overwritten_discounted_price = round((int(order_info.get_total_price())-int(order_info['plastic_bag'])) * discount_rate)+int(order_info['plastic_bag'])

		return self._promotion_universal_eff(order_info, item_mutator, 
										overwritten_discounted_price, **properties)

	def offset_eff(self, order_info, **properties):
		"""
		Effector for selected item offset promotion. 
		- Input:
			* order_info: original order info data

		promopricing: (str -> to int) e.g. 5, -5, etc.
		"""
		# global total price
		offset_price = int(properties["promopricing"])

		def item_mutator(item):
			final_price = int(item['price']) + offset_price
			item['discount'] = int(item['price']) - final_price
			item['final_price'] = final_price
			return final_price

		overwritten_discounted_price = int(order_info.get_total_price()) + offset_price

		return self._promotion_universal_eff(order_info, item_mutator, 
										overwritten_discounted_price, **properties)

	# Effectors helper function
	def _promotion_universal_eff(self, order_info, item_info_mutator, 
			overwritten_discounted_price=0, **properties):
		"""
		This is the universal effector for promotion execution
		- Input:
			* order_info: info for the order input
			* item_info_mutator: mutator function to modify the item
				info. Need to return discounted price
			* overwritten_discounted_price: what would the discount be if 
				this applies to the whole order and the effector target
				apply to all. This is necessary because the rounding might
				be different if you apply discount separately as compared
				to applying as a whole. 
		"""
		effector_target = PromotionTarget.create_target(properties["target"])

		# Get promotion strategy
		promo_strategy_str_list = properties.get("promostrategy", [])
		promo_strategy = []
		for strategy_str in promo_strategy_str_list:
			promo_strategy.append(getattr(PromotionStrategy, strategy_str))

		# flags
		order_based_discount_calc = PromotionStrategy.overwrite_item_based_discount_rounding in promo_strategy

		sorted_order_info = sorted(order_info, key=lambda k: int(k['price']), \
			reverse=PromotionStrategy.choose_top_price in promo_strategy)

		total_discount = 0
		apply_items = 0
		# loop through the order_info and put the data in
		for item in sorted_order_info:
			# Check whether the target matches item. 
			if not effector_target.matches(item, allow_partial=PromotionStrategy.allow_target_partially_met in promo_strategy):
				continue

			# Check apply items
			apply_items += 1
			if apply_items > properties["max_apply_items"]:
				break

			# Update final price for each item
			after_discount_price = item_info_mutator(item)
			total_discount += int(item['price']) - after_discount_price

		if order_based_discount_calc:
			# When order based discount round option is on, overwrite
			# The item based discount calculation by the global discount calculation
			total_discount = order_info.get_total_price() - overwritten_discounted_price

		order_info['total_discount'] = total_discount
		
		return total_discount
		


