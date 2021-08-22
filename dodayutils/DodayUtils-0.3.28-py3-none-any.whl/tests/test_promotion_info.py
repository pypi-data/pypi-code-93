import unittest
import datetime
from DodayUtils.order.OrderInfo import *
from DodayUtils.order.DodayItem import *
from DodayUtils.promotion.PromotionInfo import *
from DodayUtils.promotion.PromotionEffector import *
from gadgethiServerUtils.file_basics import *

class PromotionTargetTests(unittest.TestCase):
    """
    Testing Strategy:
    - constructor:
        * target list: sub item length -> 0, 1, >1
        * target list: sub item type -> split length 1, 2, 3, 4
                                     -> with wildcard and w/o wildcard
            "*"
            "極選/*"
            "極選/花生豆花/*"
            "極選/花生豆花/冰量/*"
            "極選/花生豆花/冰量/加冰"
        * target list: sub item -> number of wildcards 1, 2, 3, 4
                                -> wildcard placement

            "極選/*/冰量/*"
            "*/*/冰量/加冰"
            "*/花生豆花/*/加冰"
            "極選/*/*/加冰"
            "*/*/*/加冰"
            "*/花生豆花/*/*"
            "*/*/冰量/*"
            "*/*/*/*"
    - matches:
        order_info: match pattern -> 1, 2, 3, 4
                    fully match or wildcard match

        return: True or False
            
    """
    # target list: sub item length -> 0, 1, >1
    def test_sub_item_length(self):
        ptarget = PromotionTarget.create_target([])
        ptarget1 = PromotionTarget.create_target(["極選系列/花生豆花/*/*"])
        ptarget2 = PromotionTarget.create_target(["極選系列/*/*/*", "自選系列/*/*/*"])
        ptarget3 = PromotionTarget.create_target(["自選系列/豆花自選/加料專區/芋圓"])

        item = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 50)
        item1 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)

        self.assertFalse(ptarget.matches(item))
        self.assertFalse(ptarget.matches(item1))

        self.assertTrue(ptarget1.matches(item))
        self.assertFalse(ptarget1.matches(item1))

        self.assertTrue(ptarget2.matches(item))
        self.assertTrue(ptarget2.matches(item1))

        self.assertFalse(ptarget3.matches(item))
        self.assertTrue(ptarget3.matches(item1))

    # target list: variable split length
    def test_var_split_length(self):
        ptarget = PromotionTarget.create_target(["*"])
        ptarget1 = PromotionTarget.create_target(["極選系列/*"])
        ptarget2 = PromotionTarget.create_target(["極選系列/花生豆花/*", "極選/花生豆花/冰量/*"])
        ptarget3 = PromotionTarget.create_target(["極選系列/豆花自選/冰量/加冰"])

        item = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 50)
        item1 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)

        self.assertTrue(ptarget.matches(item))
        self.assertTrue(ptarget.matches(item1))

        self.assertTrue(ptarget1.matches(item))
        self.assertFalse(ptarget1.matches(item1))

        self.assertTrue(ptarget2.matches(item))
        self.assertFalse(ptarget2.matches(item1))

        self.assertFalse(ptarget3.matches(item))
        self.assertFalse(ptarget3.matches(item1))

    # target list: wild card placement
    def test_wildcard_placement(self):
        ptarget = PromotionTarget.create_target(["極選系列/*/冰量/*"])
        ptarget1 = PromotionTarget.create_target(["*/*/冰量/加冰"])
        ptarget2 = PromotionTarget.create_target(["*/花生豆花/*/加冰"])
        ptarget3 = PromotionTarget.create_target(["*/*/冰量/*", "*/花生豆花/*/*"])
        ptarget4 = PromotionTarget.create_target(["*/*/*/*"])

        item = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 50)
        item1 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)

        self.assertTrue(ptarget.matches(item))
        self.assertFalse(ptarget.matches(item1))

        self.assertTrue(ptarget1.matches(item))
        self.assertTrue(ptarget1.matches(item1))

        self.assertTrue(ptarget2.matches(item))
        self.assertFalse(ptarget2.matches(item1))

        self.assertTrue(ptarget3.matches(item))
        self.assertTrue(ptarget3.matches(item1))

        self.assertTrue(ptarget4.matches(item))
        self.assertTrue(ptarget4.matches(item1))
        

class PromotionEffectorTests(unittest.TestCase):
    """
    promotion:
    - 
    promotype: PromotionType enum identifier (str)
    promostrategy: a list of PromotionStrategy enum identifier (str)
    promopricing: ident to indicate the amount of promotion pricing (str)
    target: PromotionTarget identifier list (list of str)
    max_save_price: max price that is able to discount (int)
    max_apply_items: If there are multiple occurences, 
        defines the maximum apply items.  (int)

    Testing Strategy:

    constructor, apply
    - promotion entries length: 0, 1, >1
    - promotype: fix_price, buyget, discount
    - promostrategy: overwrite, choose_top_price, # future -> allow_target_partially_met, 
        list 0, 1, 2
    - promopricing: 
        fix_price: 0, 1, 100 (with overwrite strategy on/off)
        buyget: 1/1, 2/1, 5/1
        discount: 0,40,50,90,100 (with overwrite strategy on/off)
    - target: length 0, 1, >1
    - max_save_price: 0, 1, >1
    - max_apply_items: 0, 1, >1

    - max_save_price: total_discount exceed max_save_price, not exceed
    - max_apply_items: occurences < max_apply_items, occurences = max_apply_items, 
        occurences > max_apply_items 
    
    apply:
    - No discount, with discount
    """
    # empty and no effect promotion, fix price
    def test_empty_promo_effector(self):
        promoeff1 = {
            "promotion": []
        }
        promoeff2 = {
            "promotion": [{
                "promotype": "fix_price",
                "promostrategy": ["choose_top_price", "overwrite_item_based_discount_rounding"],
                "promopricing": "10",
                "target": ["*/*/*/*", "*/花生豆花/*/*"],
                "max_save_price": 300,
                "max_apply_items": 1
            }]
        }
        promoeff3 = {
            "promotion": [{
                "promotype": "fix_price",
                "promostrategy": ["choose_top_price"],
                "promopricing": "0",
                "target": [],
                "max_save_price": 0,
                "max_apply_items": 0
            }, {
                "promotype": "fix_price",
                "promostrategy": ["choose_top_price"],
                "promopricing": "1",
                "target": ["*"],
                "max_save_price": 5,
                "max_apply_items": 2
            }]
        }
        eff1 = PromotionEffector(**promoeff1)
        eff2 = PromotionEffector(**promoeff2)
        eff3 = PromotionEffector(**promoeff3)

        item = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 50)
        item1 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item2 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 50)
        item3 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item4 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 50)
        item5 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item_list = [item, item1, item2, item3, item4, item5]
        order_info = OrderInfo(item_list)

        self.assertEqual(eff1.apply(order_info), 0)
        self.assertEqual(eff2.apply(order_info), 290)
        self.assertEqual(eff3.apply(order_info), 5)

    # test buy get type
    def test_buy_get_effector(self):
        promoeff1 = {
            "promotion": [{
                "promotype": "buyget",
                "promostrategy": ["choose_top_price"],
                "promopricing": "1/1",
                "target": ["*/*/冰量/*", "*/花生豆花/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }]
        }
        promoeff2 = {
            "promotion": [{
                "promotype": "fix_price",
                "promostrategy": ["choose_top_price"],
                "promopricing": "10",
                "target": ["*/*/加料專區/紅豆"],
                "max_save_price": 300,
                "max_apply_items": 1
            },
            {
                "promotype": "buyget",
                "promostrategy": [],
                "promopricing": "1/1",
                "target": ["*/花生豆花/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 1
            }]
        }
        promoeff3 = {
            "promotion": [{
                "promotype": "buyget",
                "promostrategy": [],
                "promopricing": "2/1",
                "target": ["*/*/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }, {
                "promotype": "buyget",
                "promostrategy": [],
                "promopricing": "4/1",
                "target": ["*/*/*/紅豆"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }]
        }
        eff1 = PromotionEffector(**promoeff1)
        eff2 = PromotionEffector(**promoeff2)
        eff3 = PromotionEffector(**promoeff3)

        item = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item1 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item2 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item3 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item4 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item5 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["紅豆", "芋圓", "粉圓"]}, 50)
        item_list = [item, item1, item2, item3, item4, item5]
        order_info = OrderInfo(item_list)

        self.assertEqual(eff1.apply(order_info), 110)
        self.assertEqual(eff2.apply(order_info), 100)
        self.assertEqual(eff3.apply(order_info), 60)

    # test discount type
    def test_discount_effector(self):
        promoeff1 = {
            "promotion": [{
                "promotype": "discount",
                "promostrategy": ["choose_top_price"],
                "promopricing": "79",
                "target": ["*/*/冰量/*", "*/花生豆花/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }]
        }
        promoeff2 = {
            "promotion": [{
                "promotype": "fix_price",
                "promostrategy": ["choose_top_price"],
                "promopricing": "10",
                "target": ["*/*/加料專區/紅豆"],
                "max_save_price": 300,
                "max_apply_items": 1
            },
            {
                "promotype": "discount",
                "promostrategy": ["overwrite_item_based_discount_rounding"],
                "promopricing": "79",
                "target": ["*/*/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 1
            }]
        }
        promoeff3 = {
            "promotion": [{
                "promotype": "discount",
                "promostrategy": [],
                "promopricing": "0",
                "target": ["極選系列/*/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }, {
                "promotype": "discount",
                "promostrategy": [],
                "promopricing": "100",
                "target": ["*/*/*/紅豆"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }]
        }
        eff1 = PromotionEffector(**promoeff1)
        eff2 = PromotionEffector(**promoeff2)
        eff3 = PromotionEffector(**promoeff3)

        item = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item1 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item2 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item3 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item4 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item5 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["紅豆", "芋圓", "粉圓"]}, 50)
        item_list = [item, item1, item2, item3, item4, item5]
        order_info = OrderInfo(item_list)

        self.assertEqual(eff1.apply(order_info), 69)
        self.assertEqual(eff2.apply(order_info), 109)
        self.assertEqual(eff3.apply(order_info), 180)

    # test offset type
    def test_offset_effector(self):
        promoeff1 = {
            "promotion": [{
                "promotype": "offset",
                "promostrategy": ["choose_top_price"],
                "promopricing": "5",
                "target": ["*/*/冰量/*", "*/花生豆花/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }]
        }
        promoeff2 = {
            "promotion": [{
                "promotype": "offset",
                "promostrategy": ["choose_top_price"],
                "promopricing": "-5",
                "target": ["*/*/加料專區/紅豆"],
                "max_save_price": 300,
                "max_apply_items": 1
            },
            {
                "promotype": "offset",
                "promostrategy": [],
                "promopricing": "7",
                "target": ["*/花生豆花/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 1
            }]
        }
        promoeff3 = {
            "promotion": [{
                "promotype": "offset",
                "promostrategy": ["overwrite_item_based_discount_rounding"],
                "promopricing": "-110",
                "target": ["*/*/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }]
        }
        eff1 = PromotionEffector(**promoeff1)
        eff2 = PromotionEffector(**promoeff2)
        eff3 = PromotionEffector(**promoeff3)

        item = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item1 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item2 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item3 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item4 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item5 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["紅豆", "芋圓", "粉圓"]}, 50)
        item_list = [item, item1, item2, item3, item4, item5]
        order_info = OrderInfo(item_list)

        self.assertEqual(eff1.apply(order_info), -30)
        self.assertEqual(eff2.apply(order_info), -2)
        self.assertEqual(eff3.apply(order_info), 110)


class PromotionInfoTests(unittest.TestCase):
    """
    Testing Strategy:
    - constructor: empty, full_info
    - equal: equal, not equal
    - lt: lt, equal, gt
    - tojson
    - fromjson
    - execute_promotion: with promotion, without promotion.
        assertion
    """
    # covers simple promotion info
    def test_simple_promotion_info(self):
        promoeff1 = {
            "promotion": [{
                "promotype": "buyget",
                "promostrategy": ["choose_top_price"],
                "promopricing": "1/1",
                "target": ["*/*/冰量/*", "*/花生豆花/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }]
        }

        promo_info1 = PromotionInfo(effector=PromotionEffector(**promoeff1))
        promo_info2 = PromotionInfo(effector=PromotionEffector(**promoeff1))

        self.assertTrue(promo_info1 == promo_info2)

        item = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item1 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item2 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item3 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["芋頭", "芋圓", "粉圓"]}, 50)
        item4 = DodayItem("極選系列", "花生豆花", {"冰量": ["加冰"]}, 60)
        item5 = DodayItem("自選系列", "豆花自選", {"冰量": ["加冰"], "加料專區": ["紅豆", "芋圓", "粉圓"]}, 50)
        item_list = [item, item1, item2, item3, item4, item5]
        order_info = OrderInfo(item_list)

        self.assertTrue(promo_info1.execute_promotion(order_info)["indicator"])
        self.assertEqual(promo_info1.execute_promotion(order_info)["message"], 110)

        self.assertTrue(promo_info2.execute_promotion(order_info)["indicator"])
        self.assertEqual(promo_info2.execute_promotion(order_info)["message"], 110)

    # covers promotion info json conversion
    def test_json_promotion_info(self):
        promoeff1 = {
            "promotion": [{
                "promotype": "buyget",
                "promostrategy": ["choose_top_price"],
                "promopricing": "1/1",
                "target": ["*/*/冰量/*", "*/花生豆花/*/*"],
                "max_save_price": 1000,
                "max_apply_items": 6
            }]
        }

        promo_info1 = PromotionInfo(effector=PromotionEffector(**promoeff1))

        self.assertEqual(promo_info1.tojson(), promo_info1.tojson())
        self.assertEqual(PromotionInfo.json_format_to_promotion_info(promo_info1.tojson()), promo_info1)

        