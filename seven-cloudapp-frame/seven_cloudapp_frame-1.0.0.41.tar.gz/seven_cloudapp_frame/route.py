# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-04-16 14:38:22
@LastEditTime: 2021-08-17 14:32:04
@LastEditors: HuangJianYi
:Description: 基础路由
"""
# 框架引用
from seven_framework.web_tornado.monitor import MonitorHandler
from seven_cloudapp_frame.handlers.core import *
from seven_cloudapp_frame.handlers.server import *
from seven_cloudapp_frame.handlers.client import *

def seven_cloudapp_frame_route():
    return [
        (r"/monitor", MonitorHandler),
        (r"/", IndexHandler),
        #客户端
        (r"/client/address_list", address.AddressInfoListHandler),  #收货地址列表
        (r"/client/login", user.LoginHandler),  #小程序登录
        (r"/client/update_user_info", user.UpdateUserInfoHandler),  #更新用户信息如昵称、头像等
        (r"/client/apply_black_unbind", user.ApplyBlackUnbindHandler),  #申请黑名单解封
        (r"/client/user_asset_list", user.UserAssetListHandler),  #用户资产列表
        (r"/client/asset_log_list", user.AssetLogListHandler),  #用户资产流水列表
        (r"/client/prize_roster_list", user.PrizeRosterListHandler),  #中奖记录列表
        (r"/client/get_join_member_url", user.GetJoinMemberUrlHandler),  #加入会员地址
        (r"/client/get_coupon_prize", user.GetCouponPrizeHandler),  #领取淘宝优惠券
        (r"/client/theme_info", theme.ThemeInfoHandler),  #主题信息
        (r"/client/save_theme", theme.SaveThemeHandler),  #保存主题信息，由前端通过工具进行保存
        (r"/client/save_skin", theme.SaveSkinHandler),  #保存皮肤信息，由前端通过工具进行保存
        (r"/client/theme_info_list", theme.ThemeInfoListHandler),  #主题列表
        (r"/client/skin_info_list", theme.SkinInfoListHandler),  #皮肤列表
        (r"/client/ip_info_list", ip.IpInfoListHandler),  #ip信息列表
        (r"/client/act_info", act.ActInfoHandler),  #活动信息
        (r"/client/act_prize_list", act.ActPrizeListHandler),  #活动奖品列表
        (r"/client/app_expire", app.AppExpireHandler),  #小程序过期时间
        (r"/client/submit_sku", goods.SubmitSkuHandler),  #中奖记录选择sku
        (r"/client/sku_info", goods.SkuInfoHandler),  #sku信息
        (r"/client/goods_list", goods.GoodsListHandler),  #商品列表
        (r"/client/prize_order_list", order.PrizeOrderListHandler),  #用户订单列表
        (r"/client/create_prize_order", order.SelectPrizeOrderHandler),  #选择中奖记录进行下单
        (r"/client/task_info_list", task.TaskInfoListHandler),  #任务列表
        (r"/client/receive_reward", task.ReceiveRewardHandler),  #统一领取任务奖励
        (r"/client/free_gift", task.FreeGiftHandler),  #免费领取、新人有礼等任务
        (r"/client/one_sign", task.OneSignHandler),  #单次签到任务
        (r"/client/weekly_sign", task.WeeklySignHandler),  #每周签到任务
        (r"/client/invite_new_user", task.InviteNewUserHandler),  #邀请新用户任务
        (r"/client/invite_join_member", task.InviteJoinMemberHandler),  #邀请加入会员任务
        (r"/client/share_report", task.ShareReportHandler),  #分享统计上报
        (r"/client/collect_goods", task.CollectGoodsHandler),  #收藏商品任务
        (r"/client/browse_goods", task.BrowseGoodsHandler),  #浏览商品任务
        (r"/client/favor_store", task.FavorStoreHandler),  #关注店铺任务
        (r"/client/join_member", task.JoinMemberHandler),  #加入会员任务

        #千牛端
        (r"/server/saas_custom", base_s.SaasCustomHandler),
        (r"/server/login", user_s.LoginHandler),
        (r"/server/base_info", base_s.BaseInfoHandler),
        (r"/server/send_sms", base_s.SendSmsHandler),
        (r"/server/app_info", app_s.AppInfoHandler),
        (r"/server/get_app_id", app_s.GetAppIDHandler),
        (r"/server/instantiate", app_s.InstantiateAppHandler),
        (r"/server/version_upgrade", app_s.VersionUpgradeHandler),
        (r"/server/update_telephone", app_s.UpdateTelephoneHandler),
        (r"/server/act_type_list", act_s.ActTypeListHandler),
        (r"/server/next_progress", act_s.NextProgressHandler),
        (r"/server/add_act_info", act_s.AddActInfoHandler),
        (r"/server/update_act_info", act_s.UpdateActInfoHandler),
        (r"/server/act_info_list", act_s.ActInfoListHandler),
        (r"/server/act_info", act_s.ActInfoHandler),
        (r"/server/delete_act_info", act_s.DeleteActInfoHandler),
        (r"/server/review_act_info", act_s.ReviewActInfoHandler),
        (r"/server/release_act_info", act_s.ReleaseActInfoHandler),
        (r"/server/create_act_qrcode", act_s.CreateActQrCodeHandler),
        (r"/server/save_act_module", module_s.SaveActModuleHandler),
        (r"/server/act_module_list", module_s.ActModuleListHandler),
        (r"/server/delete_act_module", module_s.DeleteActModuleHandler),
        (r"/server/review_act_module", module_s.ReviewActModuleHandler),
        (r"/server/release_act_module", module_s.ReleaseActModuleHandler),
        (r"/server/save_act_prize", prize_s.SaveActPrizeHandler),
        (r"/server/act_prize_list", prize_s.ActPrizeListHandler),
        (r"/server/delete_act_prize", prize_s.DeleteActPrizeHandler),
        (r"/server/review_act_prize", prize_s.ReviewActPrizeHandler),
        (r"/server/release_act_prize", prize_s.ReleaseActPrizeHandler),
        (r"/server/pay_order_list", order_s.PayOrderListHandler),
        (r"/server/prize_order_list", order_s.PrizeOrderListHandler),
        (r"/server/update_prize_order_status", order_s.UpdatePrizeOrderStatusHandler),
        (r"/server/update_prize_order_seller_remark", order_s.UpdatePrizeOrderSellerRemarkHandler),
        (r"/server/import_prize_order", order_s.ImportPrizeOrderHandler),
        (r"/server/stat_report_list", report_s.StatReportListHandler),
        (r"/server/trend_report_list", report_s.TrendReportListHandler),
        (r"/server/update_user_status", user_s.UpdateUserStatusHandler),
        (r"/server/update_user_status_by_black", user_s.UpdateUserStatusByBlackHandler),
        (r"/server/audit_user_black", user_s.AuditUserBlackHandler),
        (r"/server/user_black_list", user_s.UserBlackListHandler),
        (r"/server/update_user_asset", user_s.UpdateUserAssetHandler),
        (r"/server/batch_update_user_asset", user_s.BatchUpdateUserAssetHandler),
        (r"/server/asset_log_list", user_s.AssetLogListHandler),
        (r"/server/init_launch_goods", launch_s.InitLaunchGoodsHandler),
        (r"/server/async_launch_goods", launch_s.AsyncLaunchGoodsHandler),
        (r"/server/launch_goods_list", launch_s.LaunchGoodsListHandler),
        (r"/server/update_launch_goods_status", launch_s.UpdateLaunchGoodsStatusHandler),
        (r"/server/init_launch_goods_callback", launch_s.InitLaunchGoodsCallBackHandler),
        (r"/server/update_theme", theme_s.UpdateThemeHandler),
        (r"/server/theme_info_list", theme_s.ThemeInfoListHandler),
        (r"/server/skin_info_list", theme_s.SkinInfoListHandler),
        (r"/server/save_ip_info", ip_s.SaveIpInfoHandler),
        (r"/server/delete_ip_info", ip_s.DeleteIpInfoHandler),
        (r"/server/ip_info_list", ip_s.IpInfoListHandler),
        (r"/server/release_ip_info", ip_s.ReleaseIpInfoHandler),
        (r"/server/save_price_gear", price_s.SavePriceGearHandler),
        (r"/server/price_gear_list", price_s.PriceGearListHandler),
        (r"/server/delete_price_gear", price_s.DeletePriceGearHandler),
        (r"/server/review_price_gear", price_s.ReviewPriceGearHandler),
        (r"/server/check_price_gear", price_s.CheckPriceGearHandler),
        (r"/server/goods_list", goods_s.GoodsListHandler),
        (r"/server/goods_list_by_goodsids", goods_s.GoodsListByGoodsIDHandler),
        (r"/server/goods_info", goods_s.GoodsInfoHandler),
        (r"/server/benefit_detail", goods_s.BenefitDetailHandler),
        (r"/server/task_info_list", task_s.TaskInfoListHandler),
        (r"/server/save_task_info", task_s.SaveTaskInfoHandler),
    ]