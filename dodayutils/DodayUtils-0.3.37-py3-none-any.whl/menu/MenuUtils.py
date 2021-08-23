from enum import Enum,IntEnum

class MenuLevel(IntEnum):
	menu = 1
	category = 2
	item = 3
	modifier_group = 4

class UberMenuTemplate(Enum):
	title = {"translations": {"en": ""}}
	description = {"translations": {"en": ""}}
	item = {"external_data": "",
			"image_url": "",
			"price_info": {"price":"int","overrides": []},
			"quantity_info": {"quantity": {}, "overrides": []},
			"suspension_info": {"suspension": {"suspend_until":"int"},"overrides": []},
			"modifier_group_ids": {"ids": [],"overrides": []},
			"tax_info": {},
			"nutritional_info": {},
			"dish_info": {},
			"tax_label_info": { "default_value": {"labels": [],"source": 1}},
			"product_info": {}}

	modifier_group = {"external_data": "",
			"quantity_info": {"quantity": {"min_permitted":"int","max_permitted":"int"},
			"overrides": []}}

class UberPriceTransform(IntEnum):
	Taiwan = 100


class PcubeMenuTemplate(Enum):
	ItemRegion_element = {"CanBeHead":True,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":"int",\
					"boundaries":[],"id":"str","price":"int","type":"ItemRegion"}			
	Required_button = [{"CanBeHead":False,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":0,\
					"boundaries":[],"id":"加一碗","price":0,"type":"AddItemRegion"},{"CanBeHead":False,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":0,
					"boundaries":[],"id":"減一碗","price":0,"type":"MinusItemRegion"},{"CanBeHead":False,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":0,
					"boundaries":[],"id":"上一步","price":0,"type":"ModifyCartRegion"},{"CanBeHead":True,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":0,
					"boundaries":[],"id":"放棄訂單","price":0,"type":"GiveUpCartRegion"},{"CanBeHead":True,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":0,
					"boundaries":[],"id":"送出訂單","price":0,"type":"SubmitRegion"},{"CanBeHead":False,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":0,
					"boundaries":[],"id":"加入購物車","price":0,"type":"AddToShoppingCartRegion"},{"CanBeHead":True,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":0,
					"boundaries":[],"id":"現金付款","price":0,"type":"CashPaymentRegion"},{"CanBeHead":False,"MandatoryModifiers":[],"OptionalModifiers":[],"PriceIfChosenAsAddon":0,
					"boundaries":[],"id":"電子錢包付款","price":0,"type":"LinePaymentRegion"}]			

