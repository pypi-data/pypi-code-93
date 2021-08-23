# %%
import pandas as pd
import json
import os
from datetime import datetime
from DataLoader import consus, reports
from abc import ABC, abstractmethod
from . import daily, status, reports
from .config import provider_config, defualt_start_date, defualt_end_date
from .calendarpd import Tdcal
from .registor import regist_TDP


# %%
class BaseProvider(ABC):

    @abstractmethod
    def daily(self, instruments, fields, start_date=defualt_start_date, end_date=defualt_end_date):
        """ daily info provider"""
        raise NotImplementedError


class LocalPorvider(BaseProvider):

    def calendar(self, start_date=defualt_start_date, end_date=defualt_end_date, freq='Tdays'):
        return Tdcal.calendar(start_date, end_date, freq)

    def list_instrument(self, univ, start_date, end_date):
        """

        :param univ:
        :param start_date:
        :param end_date:
        :return:
        """
        return InstSP.list_instrument(univ, start_date, end_date)

    def col_oriented_index(self, univ="all", start_date=defualt_start_date, end_date=defualt_end_date):
        """
            get Multiindex for col oriented data
        """
        if end_date is None:
            end_date = int(datetime.now().strftime("%Y%m%d"))
        timeindex = self.calendar(start_date, end_date)
        stklist = self.list_instrument(univ, start_date, end_date).index.values
        index = pd.MultiIndex.from_product([stklist, timeindex])
        return index

    def daily(self, instruments: list, fields: list, start_date: str = defualt_start_date,
              end_date: str = defualt_end_date):
        """ 
            table_name: 'AShareEODPrices'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fileds: 'preclose', 'open', 'high', 'low', 'close', 'change', 'pctchange',
                    'volume', 'amount', 'adjpreclose', 'adjopen', 'adjhigh', 'adjlow',
                    'adjclose', 'adjfactor', 'avgprice', 'tradestatus'
        """
        return TDP.get_daily_share_data(instruments, fields, start_date, end_date)

    def daily_blocktrade(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                         end_date: str = defualt_end_date):
        """ 
            table_name: 'AShareBlockTrade'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: block_price	block_volume block_amount block_frequency
        """
        return TDP.get_daily_blocktrade(instruments, fields, start_date, end_date)

    def daily_derivative_indi(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                              end_date: str = defualt_end_date):
        """ 
            table_name: 'AShareEODDerivativeIndicator'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: 's_val_mv', 's_dq_mv', 's_pq_high_52w_', 's_pq_low_52w_', 's_val_pe',
                    's_val_pb_new', 's_val_pe_ttm', 's_val_pcf_ocf', 's_val_pcf_ocfttm',
                    's_val_pcf_ncf', 's_val_pcf_ncfttm', 's_val_ps', 's_val_ps_ttm',
                    's_dq_turn', 's_dq_freeturnover', 'tot_shr_today', 'float_a_shr_today',
                    's_dq_close_today', 's_price_div_dps', 's_pq_adjhigh_52w',
                    's_pq_adjlow_52w', 'free_shares_today', 'net_profit_parent_comp_ttm',
                    'net_profit_parent_comp_lyr', 'net_assets_today',
                    'net_cash_flows_oper_act_ttm', 'net_cash_flows_oper_act_lyr',
                    'oper_rev_ttm', 'oper_rev_lyr', 'net_incr_cash_cash_equ_ttm',
                    'net_incr_cash_cash_equ_lyr', 'up_down_limit_status',
                    'lowest_highest_status'
        """
        return TDP.get_daily_share_deridi(instruments, fields, start_date, end_date)

    def daily_dividend_rec(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                           end_date: str = defualt_end_date):
        """ 
            table_name: 'AShareEXRightDividendRecord'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: 'cash_dividend_ratio', 'bonus_share_ratio', 'rightsissue_ratio',
                    'rightsissue_price', 'conversed_ratio', 'seo_price', 'seo_ratio',
                    'consolidate_split_ratio'
        """
        return TDP.get_daily_share_divdrec(instruments, fields, start_date, end_date)

    def daily_l2indicator(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                          end_date: str = defualt_end_date):
        """
            table_name: 'AShareL2Indicators'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: 's_li_initiativebuyrate', 's_li_initiativebuymoney',
                    's_li_initiativebuyamount', 's_li_initiativesellrate',
                    's_li_initiativesellmoney', 's_li_initiativesellamount',
                    's_li_largebuyrate', 's_li_largebuymoney', 's_li_largebuyamount',
                    's_li_largesellrate', 's_li_largesellmoney', 's_li_largesellamount',
                    's_li_entrustrate', 's_li_entrudifferamount', 's_li_entrudifferamoney',
                    's_li_entrustbuymoney', 's_li_entrustsellmoney',
                    's_li_entrustbuyamount', 's_li_entrustsellamount'
        """
        return TDP.get_daily_share_l2idi(instruments, fields, start_date, end_date)

    def daily_margintrade(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                          end_date: str = defualt_end_date):
        """
            table_name: 'AShareMarginTrade'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: 's_margin_tradingbalance', 's_margin_purchwithborrowmoney',
                    's_margin_repaymenttobroker', 's_margin_seclendingbalance',
                    's_margin_seclendingbalancevol', 's_margin_salesofborrowedsec',
                    's_margin_repaymentofborrowsec', 's_margin_margintradebalance',
                    's_refin_sl_vol_3d', 's_refin_sl_vol_7d', 's_refin_sl_vol_14d',
                    's_refin_sl_vol_28d', 's_refin_sl_vol_182d', 's_refin_sb_vol_3d',
                    's_refin_sb_vol_7d', 's_refin_sb_vol_14d', 's_sb_vol_28d',
                    's_sb_vol_182d', 's_refin_sl_eod_vol', 's_refin_sb_eod_vol',
                    's_refin_sl_eop_vol', 's_refin_sl_eop_bal', 's_refin_repay_vol'
        """
        return TDP.get_daily_margintrade(instruments, fields, start_date, end_date)

    def daily_moneyflow(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                        end_date: str = defualt_end_date):
        """
            table_name: 'AShareMoneyFlow'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: 'buy_value_exlarge_order', 'sell_value_exlarge_order',
                    'buy_value_large_order', 'sell_value_large_order',
                    'buy_value_med_order', 'sell_value_med_order', 'buy_value_small_order',
                    'sell_value_small_order', 'buy_volume_exlarge_order',
                    'sell_volume_exlarge_order', 'buy_volume_large_order',
                    'sell_volume_large_order', 'buy_volume_med_order',
                    'sell_volume_med_order', 'buy_volume_small_order',
                    'sell_volume_small_order', 'trades_count', 'buy_trades_exlarge_order',
                    'sell_trades_exlarge_order', 'buy_trades_large_order',
                    'sell_trades_large_order', 'buy_trades_med_order',
                    'sell_trades_med_order', 'buy_trades_small_order',
                    'sell_trades_small_order', 'volume_diff_small_trader',
                    'volume_diff_small_trader_act', 'volume_diff_med_trader',
                    'volume_diff_med_trader_act', 'volume_diff_large_trader',
                    'volume_diff_large_trader_act', 'volume_diff_institute',
                    'volume_diff_institute_act', 'value_diff_small_trader',
                    'value_diff_small_trader_act', 'value_diff_med_trader',
                    'value_diff_med_trader_act', 'value_diff_large_trader',
                    'value_diff_large_trader_act', 'value_diff_institute',
                    'value_diff_institute_act', 's_mfd_inflowvolume',
                    'net_inflow_rate_volume', 's_mfd_inflow_openvolume',
                    'open_net_inflow_rate_volume', 's_mfd_inflow_closevolume',
                    'close_net_inflow_rate_volume', 's_mfd_inflow', 'net_inflow_rate_value',
                    's_mfd_inflow_open', 'open_net_inflow_rate_value', 's_mfd_inflow_close',
                    'close_net_inflow_rate_value', 'tot_volume_bid', 'tot_volume_ask',
                    'moneyflow_pct_volume', 'open_moneyflow_pct_volume',
                    'close_moneyflow_pct_volume', 'moneyflow_pct_value',
                    'open_moneyflow_pct_value', 'close_moneyflow_pct_value',
                    's_mfd_inflowvolume_large_order', 'net_inflow_rate_volume_l',
                    's_mfd_inflow_large_order', 'net_inflow_rate_value_l',
                    'moneyflow_pct_volume_l', 'moneyflow_pct_value_l',
                    's_mfd_inflow_openvolume_l', 'open_net_inflow_rate_volume_l',
                    's_mfd_inflow_open_large_order', 'open_net_inflow_rate_value_l',
                    'open_moneyflow_pct_volume_l', 'open_moneyflow_pct_value_l',
                    's_mfd_inflow_close_large_order', 'close_net_inflow_rate_valu_l',
                    'close_moneyflow_pct_volume_l', 'close_moneyflow_pct_value_l',
                    'buy_value_exlarge_order_act', 'sell_value_exlarge_order_act',
                    'buy_value_large_order_act', 'sell_value_large_order_act',
                    'buy_value_med_order_act', 'sell_value_med_order_act',
                    'buy_value_small_order_act', 'sell_value_small_order_act',
                    'buy_volume_exlarge_order_act', 'sell_volume_exlarge_order_act',
                    'buy_volume_large_order_act', 'sell_volume_large_order_act',
                    'buy_volume_med_order_act', 'sell_volume_med_order_act',
                    'buy_volume_small_order_act', 'sell_volume_small_order_act'
        """
        return TDP.get_daily_moneyflow(instruments, fields, start_date, end_date)

    def daily_tech_indicator(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                             end_date: str = defualt_end_date):
        """
            table_name: 'AShareTechIndicators'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: 'volume_ratio_5d', 'vam_1m', 'vam_5m', 'vam_22m', 'vam_60m', 'ama_1w',
                    'ama_1m', 'ama_1q', 'vmacd', 'vmacd_dea', 'vmacd_macd', 'vosc',
                    'tapi_16d', 'tapi_6d', 'vstd_10d', 'vmacd_ema12d', 'vmacd_ema26d',
                    'vrsi_6d', 'vroc_12d', 'sobv', 'vr_26d'
        """
        return TDP.get_daily_techindi(instruments, fields, start_date, end_date)

    def daily_yield(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                    end_date: str = defualt_end_date):
        """
            table_name: 'ASWSIndexEOD'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: 'pct_change_d', 'pct_change_w', 'pct_change_m', 'volume_w', 'volume_m',
                    'amount_w', 'amount_m', 'turnover_d', 'turnover_d_float', 'turnover_w',
                    'turnover_w_float', 'turnover_w_ave', 'turnover_w_ave_float',
                    'turnover_m', 'turnover_m_float', 'turnover_m_ave',
                    'turnover_m_ave_float', 'pct_change_ave_100w', 'std_deviation_100w',
                    'variance_100w', 'pct_change_ave_24m', 'std_deviation_24m',
                    'variance_24m', 'pct_change_ave_60m', 'std_deviation_60m',
                    'variance_60m', 'beta_day_1y', 'beta_day_2y', 'alpha_day_1y',
                    'alpha_day_2y', 'beta_100w', 'alpha_100w', 'beta_24m', 'beta_60m',
                    'alpha_24m', 'alpha_60m'
        """
        return TDP.get_daily_yield(instruments, fields, start_date, end_date)

    def daily_index(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                    end_date: str = defualt_end_date):
        """ 
            table_name: 'AIndexEODPrices'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: 'preclose', 'open', 'high', 'low', 'close', 'change', 'pctchange',
                    'volume', 'amount' 
        """
        return TDP.get_daily_index_data(instruments, fields, start_date, end_date)

    def daily_index_industries_eod(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                                   end_date: str = defualt_end_date):
        """ 
            table_name: AIndexIndustriesEODCITICS 
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: preclose open high low close change pctchange volume amount
        """
        return TDP.get_daily_index_industries(instruments, fields, start_date, end_date)

    def daily_aswsindex_eod(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                            end_date: str = defualt_end_date):
        """ 
            table_name: 'ASWSIndexEOD'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: preclose open high low close change pctchange volume amount
        """
        return TDP.get_daily_aswsindexeod(instruments, fields, start_date, end_date)

    def daily_cmfidxeod(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                        end_date: str = defualt_end_date):
        """ 
            table_name: 'CMFIndexEOD'
            input:instruments:list,fields:list,start_date:str,end_date:str
            output: DataFrame
            fields: preclose open high low close change pctchange volume amount
        """
        return TDP.get_daily_cmfidxeod(instruments, fields, start_date, end_date)

    def daily_barra_dly_specret(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                                end_date: str = defualt_end_date):
        """
            table_name: "CNE5S_100_Asset_DlySpecRet"
            input: instruments,start_date,end_date
            output: DataFrame
            fields: barra_factors
        """
        return TDP.get_daily_dly_specret(instruments, fields, start_date, end_date)

    def daily_barra_dly_prices(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                               end_date: str = defualt_end_date):
        """
            table_name: 'CNE5_Daily_Asset_Price'
            input: instruments,start_date,end_date
            output: DataFrame
            fields: barra_factors
        """
        return TDP.get_daily_dly_prices(instruments, fields, start_date, end_date)

    def daily_barra_dly_data(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                             end_date: str = defualt_end_date):
        """
            table_name: 'CNE5S_100_Asset_Data'
            input: instruments,start_date,end_date
            output: DataFrame
            fields: barra_factors
        """
        return TDP.get_barra_dly_data(instruments, fields, start_date, end_date)

    def daily_barra_rates(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                          end_date: str = defualt_end_date):
        """
            table_name: 'CNE5S_Rates'
            input: instruments,start_date,end_date
            output: DataFrame
            fields: barra_factors
        """
        return TDP.get_daily_rates(instruments, fields, start_date, end_date)

    def daily_barra_ashare_exposure(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                                    end_date: str = defualt_end_date):
        """
            table_name: 'CNE5S_100_Asset_Exposure'
            input: instruments,start_date,end_date
            output: DataFrame
            fields: barra_factors
        """
        return TDP.get_daily_ashare_exposure(instruments, fields, start_date, end_date)

    def daily_barra_fact_cov(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                             end_date: str = defualt_end_date):
        """
            table_name: 'CNE5S_100_Covariance'
            input: instruments,start_date,end_date
            output: DataFrame
            fields: barra_factors
        """
        return TDP.get_daily_ashare_faccov(instruments, fields, start_date, end_date)

    def daily_barra_fact_ret(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                             end_date: str = defualt_end_date):
        """
            table_name: 'CNE5S_100_DlyFacRet'
            input: instruments,start_date,end_date
            output: DataFrame
            fields: return
        """
        return TDP.get_daily_factorRet(instruments, fields, start_date, end_date)

    def daily_shsz_stkholding(self, instruments: list, fields: list, start_date: str = defualt_start_date,
                              end_date: str = defualt_end_date):
        """
            table_name: 'CNE5S_100_DlyFacRet'
            input: instruments,start_date,end_date
            output: DataFrame
            fields: return
        """
        return TDP.get_daily_shsz_stkholding(instruments, fields, start_date, end_date)

    def daily_indexweight(self, instruments, **kws):
        """
            table_name: 'AIndexFreeWeight'
            input: instruments,start_date,end_date
            output: DataFrame
            fields: stockcode, weight
        """
        return TDP.get_daily_indexweight(instruments, **kws)

    def index_member(self, indexcode: str, start_date: str = None, end_date: str = None):
        """
            table_name: 'AIndexMembers'
            input:indexcode:str,start_date:str =None,end_date:str = None
            output: DataFrame
            fields : stockcode,indate,outdate
        """
        return IdxSP.index_member(indexcode, start_date, end_date)

    def index_member_citics(self, indexcode: str, start_date: str = None, end_date: str = None):
        """
            table_name: 'AIndexMembersCITICS'
            input:indexcode:str,start_date:str =None,end_date:str = None
            output: DataFrame
            fields : stockcode,indate,outdate
        """
        return IdxSP.index_member_citics(indexcode, start_date, end_date)

    def index_member_alternative(self, indexcode: str, start_date: str = None, end_date: str = None):
        """
            table_name: 'AIndexAlternativeMembers'
            input:indexcode:str,start_date:str =None,end_date:str = None
            output: DataFrame
            fields : stockcode,indate,outdate
        """
        return IdxSP.index_member_alternative(indexcode, start_date, end_date)

    def ashare_ipodate(self, stkcode=None, fields=None):
        """  
            table_name: 'AShareDescription'
            input:instruments:List(str),fields:List(str)
                  optional: stkcode = None,fields =None
            output: DataFrame
            fields : listdate, delistdate, list_boardname
        """
        return InstSP.ashare_ipodate(stkcode, fields)

    def ashare_st(self, stkcode=None, fields=None):
        """
            table_name: 'AShareST'
            input:instruments:List(str),fields:List(str)
                  optional:stkcode = None,fields =None
            output: DataFrame
            fields : suspend_date:str,resump_date:str
        """
        return InstSP.ashare_st(stkcode, fields)

    def ashare_suspension(self, stkcode=None, fields=None):
        """ 
            table_name: 'AShareTradingSuspension'
            input:instruments:List(str),fields:List(str)
                  optional: stkcode = None,fields =None
            output: DataFrame
            fields : suspend_date,resump_date           
        """
        return InstSP.ashare_suspension(stkcode, fields)

    def suntime_typedict(self, organid=None, fields=None):
        """ 
            table_name: 'RPT_RATING_COMPARE'
            input:instruments:List(str),fields:List(str)
                  optional: stkcode = None,fields =None
            output: DataFrame
            fields : suspend_date,resump_date           
        """
        return InstSP.suntime_typedict(organid, fields)

    def Industrycompo_citics(self, stockcode=None, level=None):
        """  
            table_name: "AShareIndustriesClass_CITICS"
            input:instruments:List(str),fields:List(str)
                  optional: entry_date:str,remove_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : entry_date:str,remove_date        
        """
        return InduSP.Industrycompo_citics(stockcode, level)

    def Industrycompo_cs(self, stockcode=None, level=None):
        """  
            table_name: "AShareIndustriesClass_CS"
            input:instruments:List(str),fields:List(str)
                  optional: entry_date:str,remove_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : entry_date:str,remove_date        
        """
        return InduSP.Industrycompo_cs(stockcode, level)

    def Industrycompo_gics(self, stockcode=None, level=None):
        """  
            table_name: "AShareIndustriesClass_GICS"
            input:instruments:List(str),fields:List(str)
                  optional: entry_date:str,remove_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : entry_date:str,remove_date        
        """
        return InduSP.Industrycompo_gics(stockcode, level)

    def Industrycompo_sw(self, stockcode=None, level=None):
        """ 
            table_name: 'AShareIndustriesClass_SW'
            input:instruments:List(str),fields:List(str)
                  optional: entry_date:str,remove_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : entry_date:str,remove_date       
        """
        return InduSP.Industrycompo_sw(stockcode, level)

    def Industrycompo_wind(self, stockcode=None, level=None):
        """ 
            table_name: 'AShareIndustriesClass_WIND'
            input:instruments:List(str),fields:List(str)
                  optional: entry_date:str,remove_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : entry_date:str,remove_date       
        """
        return InduSP.Industrycompo_wind(stockcode, level)
    
    def Industrycodes(self):
        """
            Industry info, includes codes, levelnum, definition
        """
        return InduSP.Industrycodes()

    def repo_cashflow(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareCashFlow'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_cashflow(instruments, fields, **kws)

    def repo_cashflow_q(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareCashFlow_quaterly'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_cashflow_q(instruments, fields, **kws)

    def repo_income(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareIncome'
            input: instruments:List(str),fields:List(str)
                   optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_income(instruments, fields, **kws)

    def repo_income_q(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareIncome_quarterly'
            input: instruments:List(str),fields:List(str)
                   optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_income_q(instruments, fields, **kws)

    def repo_balancesheet(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareBalanceSheet'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_balancesheet(instruments, fields, **kws)

    def repo_profit_expr(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareProfitExpress'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_profit_expr(instruments, fields, **kws)

    def repo_profit_noti(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareProfitNotice'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_profit_noti(instruments, fields, **kws)

    def repo_ttmhis(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareTTMHis'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_ttmhis(instruments, fields, **kws)

    def repo_holder_number(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareHolderNumber'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_holder_number(instruments, fields, **kws)

    def repo_inside_holder(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareInsideHolder'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_inside_holder(instruments, fields, **kws)

    def repo_holder_data(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareinstHolderDerData'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_holder_data(instruments, fields, **kws)

    def repo_manage_rewr(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareManagementHoldReward'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_manage_rewr(instruments, fields, **kws)

    def repo_issuedate_pre(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareIssuingDatePredict'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_issuedate_pre(instruments, fields, **kws)

    def repo_fanc_indicator(self, instruments, fields=None, **kws):
        """
            table_name: 'AShareFinancialIndicator'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_fanc_indicator(instruments, fields, **kws)
    
    def repo_ashare_dividend(self,instruments,fields,**kws):
        """
            table_name: 'AShareDividend'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FRP.repo_ashare_dividend(instruments, fields, **kws)

    def frepo_qdii_secuportfolio(self, instruments, fields=None, **kws):
        """
            table_name: 'QDIISecuritiesPortfolio'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FuRP.frepo_qdii_secuportfolio(instruments, fields, **kws)

    def frepo_mufund_stkportfolio(self, instruments, fields=None, **kws):
        """
            table_name: 'ChinaMutualFundStockPortfolio'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return FuRP.frepo_mufund_stkportfolio(instruments, fields, **kws)

    def consus(self, instruments, fields=None, foreward_type='fy1', window_days='30d', **kws):
        """
            table_name: 'AShareConsensusData'
            input:instruments:List(str),fields:List(str)
                  foreward_type: fy0, fy1, fy2, fy3
                  window_days: 30d,90d,180d,180l
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return CDP.consus(instruments, fields, foreward_type, window_days, **kws)

    def consus_rolling(self, instruments, fields=None, foreward_type='fy1', **kws):
        """
            table_name: 'AShareConsensusRollingData'
            input:instruments:List(str),fields:List(str)
                  foreward_type: cagr, fy0, fy1, fy2, fy3 , yoy , yoy2
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return CDP.consus_rolling(instruments, fields, foreward_type, **kws)

    def stk_rating(self, instruments, fields=None, window_days='30d', **kws):
        """
            table_name: 'AShareStockRatingConsus'
            input:instruments:List(str),fields:List(str)
                  window_days: 30d,90d,180d
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return CDP.stk_rating(instruments, fields, window_days, **kws)

    def suntime_confc_stk(self, instruments, fields=None, **kws):
        """
            table_name: 'CON_FORECAST_STK'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return CDP.suntime_confc_stk(instruments, fields, **kws)

    def suntime_confc_roll_stk(self, instruments, fields=None, **kws):
        """
            table_name: 'CON_FORECAST_STK_ROLL'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return CDP.suntime_confc_roll_stk(instruments, fields, **kws)

    def suntime_repofc_stk(self, instruments, fields=None, **kws):
        """
            table_name: 'RPT_FORECAST_STK'
            input:instruments:List(str),fields:List(str)
                  optional: start_date:str,end_date:str,by [ann_date,reports_period]
            output: DataFrame
            fields : ...
        """
        return CDP.suntime_repofc_stk(instruments, fields, **kws)

    def suntime_repofc_stk_tc(self, instruments=None, fields=None, start_date=None, end_date=None):
        """
            table_name: 'RPT_FORECAST_STK_TC'
        """
        return CDP.suntime_repofc_stk_tc(instruments, fields, start_date, end_date)

    def suntime_earning_adj(self, instruments=None, fields=None, start_date=None, end_date=None):
        """
            table_name: 'RPT_EARNINGS_ADJUST'
        """
        return CDP.suntime_earning_adj(instruments, fields, start_date, end_date)

    def suntime_rating_adj(self, instruments=None, fields=None, start_date=None, end_date=None):
        """
            table_name: 'RPT_RATING_ADJUST'
        """
        return CDP.suntime_rating_adj(instruments, fields, start_date, end_date)

    def suntime_tgtprice_adj(self, instruments=None, fields=None, start_date=None, end_date=None):
        """
            table_name: 'RPT_TARGET_PRICE_ADJUST'
        """
        return CDP.suntime_tgtprice_adj(instruments, fields, start_date, end_date)


def TDP_pro(instruments, fields, start_date=defualt_start_date, end_date=defualt_end_date):
    path = os.path.join(
        os.path.split(__file__)[0], "TDP.config"
    )
    if isinstance(fields, str):
        fields = [fields]
    if not os.path.exists(path):
        regist_TDP(BP)
    with open(path, "r") as f:
        config = json.load(f)
    tasks = {}
    for field in fields:
        try:
            func = config[field]
        except KeyError:
            print(field, " not found")
            continue
        if func in tasks:
            tasks[func].append(field)
        else:
            tasks[func] = [field, ]
    dfs = []
    for func, func_field in tasks.items():
        df = getattr(BP, func)(instruments, func_field, start_date, end_date)
        if "ann_date" in df.columns:
            print("Warning: {func} return a df whose timeindex may contain weekends")
            df = df.rename(columns={"ann_date": "trade_dt"})
        df = df.set_index(["trade_dt", "code"])
        dfs.append(df)
    return pd.concat(dfs, axis=1)


TDP = getattr(daily, provider_config["TDP"])()
IdxSP = getattr(status, provider_config["IdxSP"])()
InstSP = getattr(status, provider_config["InstSP"])()
InduSP = getattr(status, provider_config["InduSP"])()
FRP = getattr(reports, provider_config["FRP"])()
FuRP = getattr(reports, provider_config["FuRP"])()
CDP = getattr(consus, provider_config["CDP"])()
BP = eval(provider_config["BP"])()
