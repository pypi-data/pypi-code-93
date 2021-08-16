from ...data.struct import AssetWeight, AssetPrice, AssetPosition, AssetValue
from ...data.struct import AssetTrade, FundTrade, FundPosition, FundWeight
from ...data.struct import AssetTradeParam, FundTradeParam
from ...data.struct import AssetTradeCache, FundWeightItem
from ...data.constant import TradeTrigger, _DEFAULT_CASH_VALUE
from . import Helper
from .asset_helper import FAHelper
import numpy as np
import math
import datetime

class AssetTrader(Helper):

    TRADE_DAY_INTERVAL = 20
    DEFAULT_CASH_VALUE = _DEFAULT_CASH_VALUE

    def __init__(self, asset_param: AssetTradeParam=None):
        self.asset_param = asset_param or AssetTradeParam()
        self.last_trade_date = None

    def trade_interval_allow(self, dt):
        if self.last_trade_date is None or self.last_trade_date + datetime.timedelta(days=self.TRADE_DAY_INTERVAL) < dt:
            return True
        else:
            return False

    def calc_asset_trade(self, dt,
                               cur_position: AssetPosition,
                               cur_price: AssetPrice,
                               target_allocation: AssetWeight):
        cur_mv = AssetValue(prices=cur_price, positions=cur_position)
        tot_mv = cur_mv.sum()

        trades = []
        launch_trade = False
        for index_id, target_weight in target_allocation.__dict__.items():
            if index_id != 'cash':
                target_amt = tot_mv * target_weight
                p = cur_price.__dict__[index_id]
                cur_amt = cur_mv.__dict__[index_id]
                if abs(target_amt - cur_amt) > tot_mv * self.asset_param.MinCountAmtDiff:
                    amount = abs(target_amt - cur_amt)
                    is_buy = target_amt > cur_amt
                    if is_buy:
                        trades.append(AssetTrade(
                            index_id=index_id,
                            mark_price=p,
                            amount=amount,
                            is_buy=is_buy,
                            submit_date=dt
                        ))
                    else:
                        trades.append(AssetTrade(
                            index_id=index_id,
                            mark_price=p,
                            volume=amount/p,
                            is_buy=is_buy,
                            submit_date=dt
                        ))
                launch_trade = launch_trade or abs(target_amt - cur_amt) > tot_mv * self.asset_param.MinActionAmtDiff

        if not launch_trade:
            return cur_position, None
        else:
            # #如果在极端参数下 设置MinCountAmtDiff比较大，导致小单被过滤掉，如果造成trade里只有 买单或者卖单， 放弃下单（会导致cash失控）
            sell_trades_amt = sum([i.mark_price * i.volume for i in trades if i.is_buy is False])
            buy_trades_amt = sum([i.amount for i in trades if i.is_buy is True])
            if cur_position.cash != self.DEFAULT_CASH_VALUE and (sell_trades_amt == 0 or buy_trades_amt == 0):
                return cur_position, None
            trades.sort(key=lambda x: x.is_buy)
            new_position = cur_position.copy()
            for trd in trades:
                new_position.update(trd)
            #如果一个交易单过小，不达到交易下限，会被忽略，导致买单和卖单交易额相加不相等
            buy_adjusted = sell_trades_amt / buy_trades_amt if (sell_trades_amt > 0 and buy_trades_amt > 0) else 1
            for trd in trades:
                if trd.is_buy == True:
                    trd.amount *= buy_adjusted
            # buy_trades_amt = sum([i.amount for i in trades if i.is_buy is True])
            # sell_trades_amt = sum([i.mark_price * i.volume for i in trades if i.is_buy is False]) 
            # print(f' compare trades amt buy {buy_trades_amt} and sell {sell_trades_amt} diff {buy_trades_amt-sell_trades_amt }')
            return new_position, trades

    def finalize_trade(self, dt, trades: list,
                            t1_price: AssetPrice,
                            bt_position: AssetPosition):
        pendings = []
        traded_list = []
        if trades is None or len(trades) == 0:
            return pendings, traded_list
        for trd in trades:
            trd.trade_price = t1_price.__dict__[trd.index_id]
            trd.volume = trd.volume if trd.volume else (trd.amount / trd.trade_price)
            trd.trade_date = dt
            if not trd.is_buy:
                if not(bt_position.__dict__[trd.index_id] - trd.volume > -1e-8):
                    #print(f'trade volume exceeds, adjusted to pos (index_id){trd.index_id} (vol){trd.volume} (is_buy){trd.is_buy} (pos){bt_position.__dict__[trd.index_id]}')
                    trd.volume = bt_position.__dict__[trd.index_id]
            trd.amount = trd.volume * trd.trade_price    
            if self.asset_param.EnableCommission:
                if not trd.is_buy:
                    trd.commission = trd.amount * self.asset_param.RedeemDiscount * self.asset_param.AssetRedeemRate[trd.index_id]
                    trd.amount -= trd.commission

        _trade_list_buy = [i  for i in trades if i.is_buy is True]
        _trade_list_sel = [i  for i in trades if i.is_buy is False]
        # 买单按照amount下单， 不会出现计划资金和实际资金不符合情况
        # 卖单按照volume下单， 会出现计算资金和实际资金不符合情况
        # 保证卖单和买单实际成交的金额一致，就不会出现现金比例波动的情况，现金就可以设置为0，去掉现金资产比例 
        plan_sel_amount = 0 if len(_trade_list_sel) < 1 else sum([i.amount for i in _trade_list_sel])
        plan_buy_amount = 0 if len(_trade_list_buy) < 1 else sum([i.amount for i in _trade_list_buy])
        if plan_sel_amount == 0 or plan_buy_amount == 0: 
            buy_amount_adjusted_rate = 1
        else:
            buy_amount_adjusted_rate = plan_sel_amount / plan_buy_amount
        for trd in trades:
            if trd.is_buy:
                trd.amount *= buy_amount_adjusted_rate
            if self.asset_param.EnableCommission:
                if trd.is_buy:
                    trd.volume = trd.amount / trd.trade_price / (1 + self.asset_param.PurchaseDiscount * self.asset_param.AssetPurchaseRate[trd.index_id])
                    trd.commission = trd.volume * trd.trade_price * self.asset_param.PurchaseDiscount * self.asset_param.AssetPurchaseRate[trd.index_id]
            else:
                trd.commission = 0
            bt_position.update(trd)
            traded_list.append(trd)
        
        self.last_trade_date = dt
        return pendings, traded_list

class FundTrader(AssetTrader):

    SMALL_POS_FLOAT = 1e-6
    BIG_INT = 1e10

    def __init__(self, asset_param: AssetTradeParam=None, fund_param: FundTradeParam=None):
        AssetTrader.__init__(self, asset_param=asset_param)
        self.fund_param = fund_param or FundTradeParam()
        self.pos_manager_list = []

    def set_helper(self, fa_helper: FAHelper):
        self.fa_helper = fa_helper
        self.last_trade_date = None

    def has_expired_fund(self, cur_fund_position:FundPosition, _prep_fund_score:dict):
         # 如果持仓基金 没有分数， 返回True
        pos_fund_set = {fund_id for fund_id, fund_pos_i in cur_fund_position.funds.items() if fund_pos_i.volume > 0}
        score_set = set()
        for index_id, pos_i in _prep_fund_score.items():
            score_set.update(pos_i.keys())
        return bool(pos_fund_set.difference(score_set))

    # to be deprecated
    def calc_fund_trade(self, dt, fund_weight: FundWeight, cur_fund_position: FundPosition,
                            cur_fund_nav: dict,
                            fund_purchase_fees: dict,
                            fund_redeem_fees: dict) -> list:
        new_fund_position = cur_fund_position.copy()
        fund_trades = []
        # return trade list
        fund_tot_mv, cur_fund_wgts = cur_fund_position.calc_mv_n_w(fund_navs=cur_fund_nav)
        all_funds = {}
        # prepare fund candidates and its index_id
        for fund_id, fund_wgt_item in fund_weight.funds.items():
            all_funds[fund_id] = fund_wgt_item.index_id
        for fund_id, fund_pos_item in cur_fund_position.funds.items():
            all_funds[fund_id] = fund_pos_item.index_id
        # calc trade
        for fund_id, index_id in all_funds.items():
            target_fund_amt = fund_weight.get_wgt(fund_id) * fund_tot_mv
            cur_fund_volume = cur_fund_position.get_volume(fund_id) or 0
            p = cur_fund_nav[fund_id]
            cur_fund_amt = cur_fund_volume * p

            if abs(target_fund_amt - cur_fund_amt) > fund_tot_mv * self.fund_param.MinCountAmtDiff or (target_fund_amt == 0 and cur_fund_amt > 0):
                # TODO: commision and 如果是清某一只基金的逻辑，清空可以执行
                is_buy = target_fund_amt > cur_fund_amt
                if is_buy:
                    _trade = FundTrade(
                        fund_id=fund_id,
                        index_id=index_id,
                        mark_price=p,
                        amount=abs(target_fund_amt - cur_fund_amt),
                        is_buy=is_buy,
                        submit_date=dt
                    )
                else:
                    _trade = FundTrade(
                        fund_id=fund_id,
                        index_id=index_id,
                        mark_price=p,
                        volume=abs(target_fund_amt - cur_fund_amt)/p,
                        is_buy=is_buy,
                        submit_date=dt
                    )
                fund_trades.append(_trade)
                #print(f'(fund){fund_id} (p){p} (amt0){cur_fund_amt} (amt1){target_fund_amt} (idx){index_id} (amt){abs(target_fund_amt - cur_fund_amt)} (direc) {target_fund_amt > cur_fund_amt} ')

        fund_trades.sort(key=lambda x: x.is_buy)
        for _trade in fund_trades:
            new_fund_position.update(_trade)
        return new_fund_position, fund_trades

    def finalize_trade(self, dt, trades: list,
                            t1_price: AssetPrice,
                            bt_position: AssetPosition,
                            cur_fund_position: FundPosition,
                            cur_fund_nav: dict,
                            cur_fund_unit_nav: dict,
                            fund_purchase_fees: dict,
                            fund_redeem_fees: dict,
                            disproved_set: set,
                            tar_fund_weight: FundWeight):

        if trades is None or len(trades) == 0:
            return [], []
        self.pos_manager_list = tar_fund_weight.get_funds('active')
        pendings = []
        traded_list = []
        # TODO: if some trades needs more time
        # 先成交卖单， 再根据卖单成交金额 等额成交买单
        for trd in trades:
            trd.trade_price = cur_fund_nav[trd.fund_id]
            trd.fund_unit_nav = cur_fund_unit_nav[trd.fund_id]
            trd.volume = trd.volume if trd.volume else (trd.amount / trd.trade_price)
            trd.amount = trd.amount if trd.amount else (trd.volume * trd.trade_price)
            trd.fund_unit_volume = trd.amount / trd.fund_unit_nav
            trd.trade_date = dt
            if not trd.is_buy:
                cur_vol = cur_fund_position.get_volume(trd.fund_id)
                if not((cur_vol or 0) - trd.volume > -1e-8):
                    #print(f'trade volume exceeds, adjusted to pos (fund_id){trd.fund_id} (vol){trd.volume} (is_buy){trd.is_buy} (pos){cur_vol}')
                    assert cur_vol is not None, 'sell fund with no current position!'
                    trd.volume = cur_vol
                    trd.amount = trd.volume * trd.trade_price
            
            if self.fund_param.EnableCommission:
                if not trd.is_buy:
                    redeem_fee = fund_redeem_fees[trd.fund_id] * self.fund_param.RedeemDiscount
                    if np.isnan(redeem_fee):
                        #print(f'fund_id {trd.fund_id} redeem fee data not avaiable')
                        redeem_fee = 0
                    trd.commission = trd.amount * redeem_fee
                    trd.amount -= trd.commission
            else:
                trd.commission = 0
            if not trd.is_buy:
                trade_status = cur_fund_position.update(trd)
                if trade_status:
                    traded_list.append(trd)
        _trade_list_buy = [i  for i in trades if i.is_buy is True]
        _trade_list_sel = [i  for i in traded_list if i.is_buy is False]
        plan_sel_amount = 0 if len(_trade_list_sel) < 1 else sum([i.amount for i in _trade_list_sel])
        plan_buy_amount = 0 if len(_trade_list_buy) < 1 else sum([i.amount for i in _trade_list_buy])
        if plan_sel_amount == 0 or plan_buy_amount == 0: 
            buy_amount_adjusted_rate = 1
        else:
            buy_amount_adjusted_rate = plan_sel_amount / plan_buy_amount
        
        for trd in trades:
            if not trd.is_buy:
                continue
            trd.amount *= buy_amount_adjusted_rate
            if self.fund_param.EnableCommission:
                purchase_fee = fund_purchase_fees[trd.fund_id] * self.fund_param.PurchaseDiscount 
                if np.isnan(purchase_fee):
                    #print(f'fund_id {trd.fund_id} purchase fee data not avaiable')
                    purchase_fee = 0
                trd.volume = trd.amount / trd.trade_price / (1 + purchase_fee)
                trd.commission = trd.volume * trd.trade_price * purchase_fee
                trd.fund_unit_volume = trd.amount / trd.fund_unit_nav
            else:
                trd.commission = 0            
                #print(f'trade is not permitted : {trd}')
            trade_status = cur_fund_position.update(trd)
            if trade_status:
                traded_list.append(trd)
                if trd.fund_id in disproved_set:
                    print(f' trade bannded fund dt {dt} fund_id {trd.fund_id} index_id {trd.index_id}')
            else:
                pass
                #print(f'trade failed alert : {trd}')
        _trade_list_buy = [i  for i in traded_list if i.is_buy is True]
        _trade_list_sel = [i  for i in traded_list if i.is_buy is False]
        # plan_sel_amount = 0 if len(_trade_list_sel) < 1 else sum([i.amount for i in _trade_list_sel])
        # plan_buy_amount = 0 if len(_trade_list_buy) < 1 else sum([i.amount for i in _trade_list_buy])
        # print(f'trade date {dt} sell amount {plan_sel_amount} buy amount {plan_buy_amount} diff {plan_buy_amount-plan_sel_amount}')

        # get cur asset weight from fund weight
        cur_mv, cur_fund_weight = cur_fund_position.calc_mv_n_w(cur_fund_nav)
        fund_index_dic = {}
        for fund_id, fund_pos_item in cur_fund_position.funds.items():
            fund_index_dic[fund_id] = fund_pos_item.index_id
        asset_wgt = { _ : 0 for _ in set(fund_index_dic.values())}
        for fund_id, wgt_i in cur_fund_weight.items():
            index_id = fund_index_dic[fund_id]
            asset_wgt[index_id] += wgt_i
        # set index position:
        for index_id in asset_wgt:
            asset_p = t1_price.__dict__[index_id]
            amount = cur_mv * asset_wgt[index_id]
            bt_position.__dict__[index_id] = amount / asset_p
        
        self.last_trade_date = dt
        # fund cash -> asset cash
        bt_position.cash = cur_fund_position.cash
        return pendings, traded_list

    def judge_trade(self, dt, 
            index_fund_cache: list, # to change
            tar_fund_weight: FundWeight,
            tar_asset_weight: AssetWeight,
            cur_fund_position: FundPosition,
            cur_asset_position: AssetPosition,
            cur_fund_nav: dict,
            cur_fund_score: dict,
            cur_asset_price: AssetPrice,
            score_select: dict,
            fund_end_date_dict: dict) -> bool:

        index_rebalance_max_diff = 0
        fund_selection_min_score = 1
        fund_rebalance_min_score = 1
        fund_end = 0
        _index_rebalance_max_diff_name = ''
        _fund_selection_min_name = ''
        _fund_rebalance_min_name = ''
        fund_rank_list = []
        cur_asset_mv = AssetValue(prices=cur_asset_price, positions=cur_asset_position)
        #cur_asset_weight = cur_asset_mv.get_weight()
        cur_asset_weight = cur_fund_position.calc_index_weight_by_fund_pos(fund_navs=cur_fund_nav).__dict__
        for index_id, index_tar_wgt in tar_asset_weight.__dict__.items():
            if index_id == 'cash':
                continue
            c = AssetTradeCache(index_id=index_id)
            c.index_tar_wgt = index_tar_wgt
            c.index_cur_wgt = cur_asset_weight[index_id]
            c.index_diff = c.index_tar_wgt - c.index_cur_wgt
            if abs(c.index_diff) > index_rebalance_max_diff:
                index_rebalance_max_diff = abs(c.index_diff)
                _index_rebalance_max_diff_name = index_id

            c.fund_cur_wgts = cur_fund_position.calc_mv_n_w(cur_fund_nav, index_id)[1]
            c.cur_fund_ids = set(c.fund_cur_wgts.keys())
            type_i = score_select[index_id]
            
            c.fund_scores = sorted(cur_fund_score.get(index_id, {}).get(type_i, {}).items(), key=lambda item: item[1], reverse=True)
            
            c.fund_ranks = {info[0]: rank + 1 for rank, info in enumerate(c.fund_scores)}
            c.proper_fund_num = min(self.fa_helper.get_max_fund_num(index_id), len(c.fund_scores)) if index_tar_wgt > self.SMALL_POS_FLOAT else 0
            # 维度1：现有基金的选取优化情况：（评估整体现有基金池的好坏）
            c.fund_judge_ranking_score = 0
            wgt_func = lambda _rank: 1.0 / math.pow(_rank, 1/3)
            _rank_list = []
            _fund_list = self.pos_manager_list if index_id == 'active' else c.cur_fund_ids     
            for f in _fund_list:
                rank_i = c.fund_ranks.get(f, self.BIG_INT)
                _end_date = fund_end_date_dict.get(f)
                if _end_date <= dt or rank_i == self.BIG_INT:
                    fund_end = 1
                _rank_list.append((f, rank_i))
                c.fund_judge_ranking_score += wgt_func(rank_i)

            c.fund_judge_ranking_best = 0
            for i in range(0, c.proper_fund_num):
                c.fund_judge_ranking_best += wgt_func(i + 1)
            c.fund_judge_ranking = (c.fund_judge_ranking_score + self.SMALL_POS_FLOAT) / (c.fund_judge_ranking_best + self.SMALL_POS_FLOAT)
            
            # 维度2：现有基金的比例平均化情况：（评估现有基金比例的合理性）
            if len(c.cur_fund_ids) != c.proper_fund_num:
                c.fund_judge_diverse = 0
            else:
                c.fund_judge_diverse = 1
                for fund_id in c.cur_fund_ids:
                    old_wgt = c.fund_cur_wgts.get(fund_id, 0)
                    c.fund_judge_diverse *= old_wgt * c.proper_fund_num

            # to start or others, cur_fund_ids is few
            if len(c.cur_fund_ids) < c.proper_fund_num:
                for fund_id, _score in c.fund_scores:
                    if fund_id not in c.cur_fund_ids:
                        c.cur_fund_ids.add(fund_id)
                        if len(c.cur_fund_ids) == c.proper_fund_num:
                            break
            assert len(c.cur_fund_ids) >= c.proper_fund_num, 'cur fund id candidate should be no less than proper_fund_num'
            
            if index_tar_wgt > self.fund_param.DiffJudgeAssetWgtRequirement:
                if index_id != 'mmf':
                    if fund_selection_min_score >= c.fund_judge_ranking:
                        fund_selection_min_score = c.fund_judge_ranking
                        _fund_selection_min_name = index_id
                        fund_rank_list = _rank_list

                if fund_rebalance_min_score > c.fund_judge_diverse:
                    fund_rebalance_min_score = c.fund_judge_diverse
                    _fund_rebalance_min_name = index_id
                #print(f'{dt} dt c.cur_fund_ids {c.cur_fund_ids} index_id {index_id} fund_rank_list {fund_rank_list} _rank_list {_rank_list} index_tar_wgt {index_tar_wgt} DiffJudgeAssetWgtRequirement {self.fund_param.DiffJudgeAssetWgtRequirement} con {index_tar_wgt > self.fund_param.DiffJudgeAssetWgtRequirement} fund_selection_min_score {fund_selection_min_score} c.fund_judge_ranking {c.fund_judge_ranking}')
            index_fund_cache.append(c)
        # self.fund_param.DiffJudgeLambda = 0
        trigger = 0
        trigger += TradeTrigger.IndexRebalance if index_rebalance_max_diff > self.fund_param.JudgeIndexDiff else 0
        trigger += TradeTrigger.FundSelection if fund_selection_min_score < self.fund_param.JudgeFundSelection else 0
        trigger += TradeTrigger.FundRebalance if fund_rebalance_min_score < self.fund_param.JudgeFundRebalance else 0
        trigger += TradeTrigger.FundEnd if fund_end == 1 else 0

        trigger_reason = TradeTrigger.trigger_log(trigger,
                                                  index_rebalance_max_diff,
                                                  _index_rebalance_max_diff_name,
                                                  self.fund_param.JudgeIndexDiff,
                                                  fund_selection_min_score,
                                                  _fund_selection_min_name,
                                                  self.fund_param.JudgeFundSelection,
                                                  fund_rank_list,
                                                  fund_rebalance_min_score,
                                                  _fund_rebalance_min_name,
                                                  self.fund_param.JudgeFundRebalance)

        trigger_detail = TradeTrigger.trigger_detail(trigger,
                                                  index_rebalance_max_diff,
                                                  _index_rebalance_max_diff_name,
                                                  self.fund_param.JudgeIndexDiff,
                                                  fund_selection_min_score,
                                                  _fund_selection_min_name,
                                                  self.fund_param.JudgeFundSelection,
                                                  fund_rank_list,
                                                  fund_rebalance_min_score,
                                                  _fund_rebalance_min_name,
                                                  self.fund_param.JudgeFundRebalance)
        
        #print(f'trigger_detail {trigger_detail}')
        if trigger > 0:
            if self.trade_interval_allow(dt):
                #print(f'judge allow {dt} (trigger){TradeTrigger.parse(trigger)} (Fs){fund_selection_min_score}[{_fund_selection_min_name}]#{self.fund_param.JudgeFundSelection} (Fr){fund_rebalance_min_score}/[{_fund_rebalance_min_name}]#{self.fund_param.JudgeFundRebalance} (Ir){index_rebalance_max_diff}/[{_index_rebalance_max_diff_name}]#{self.fund_param.JudgeIndexDiff}')
                pass
            elif (not self.trade_interval_allow(dt)) and TradeTrigger.is_end(trigger):
                #print(f'{dt}  fund end trigger rebalance when not allow trigger {trigger} trigger_reason {trigger_reason}')
                pass
            else:
                trigger = 0
                #print(f'judge dismiss {dt} (trigger){TradeTrigger.parse(trigger)} (Fs){fund_selection_min_score}[{_fund_selection_min_name}]#{self.fund_param.JudgeFundSelection} (Fr){fund_rebalance_min_score}/[{_fund_rebalance_min_name}]#{self.fund_param.JudgeFundRebalance} (Ir){index_rebalance_max_diff}/[{_index_rebalance_max_diff_name}]#{self.fund_param.JudgeIndexDiff}')
        return trigger, trigger_reason, trigger_detail

    def calc_trade(self, dt,
            tar_fund_weight: FundWeight,
            tar_asset_weight: AssetWeight,
            cur_fund_position: FundPosition,
            cur_asset_position: AssetPosition,
            cur_fund_nav: dict,
            cur_fund_score: dict,
            cur_asset_price: AssetPrice,
            cur_fund_unit_nav: dict,
            is_real_trade: bool,
            cur_manager_funds: dict,
            score_select: dict,
            fund_end_date_dict: dict) -> list:
        '''
        v_asset_position, asset_trade_list = self.calc_asset_trade(dt, cur_asset_position, cur_asset_price, tar_asset_weight)
        if not asset_trade_list:
            return v_asset_position, asset_trade_list
        else:
            return self.calc_fund_trade(dt, tar_fund_weight, cur_fund_position, cur_fund_nav, fund_purchase_fees, fund_redeem_fees)
        '''
        index_fund_cache = []

        if is_real_trade:
            for fund_id, pos_info in cur_fund_position.funds.items():
                pos_info.volume = pos_info.unit_volume
            trigger, trigger_reason, trigger_detail = self.judge_trade(dt, index_fund_cache, 
                                        tar_fund_weight, tar_asset_weight,
                                        cur_fund_position, cur_asset_position, cur_fund_unit_nav, 
                                        cur_fund_score, cur_asset_price, score_select, fund_end_date_dict)
        else:
            trigger, trigger_reason, trigger_detail = self.judge_trade(dt, index_fund_cache, 
                                        tar_fund_weight, tar_asset_weight,
                                        cur_fund_position, cur_asset_position, cur_fund_nav, 
                                        cur_fund_score, cur_asset_price, score_select, fund_end_date_dict)
        
        # 如果是真实交易 且cash 不为零，按照当日cash，返回买单
        if (is_real_trade is False and trigger == 0) or (is_real_trade is True and cur_fund_position.cash == 0 and trigger == 0):
            return cur_fund_position, [], {}, trigger_detail

        fund_trades = self.get_trades(dt, index_fund_cache, 
                                    tar_fund_weight, tar_asset_weight,
                                    cur_fund_position, cur_asset_position, cur_fund_nav, 
                                    cur_fund_score, cur_asset_price, cur_fund_unit_nav, is_real_trade, cur_manager_funds)
        fund_trades.sort(key=lambda x: x.is_buy)
        new_fund_position = cur_fund_position.copy()

        for _trade in fund_trades:
            _trade.trigger = trigger
            new_fund_position.update(_trade)
        return new_fund_position, fund_trades, trigger_reason, trigger_detail

    def get_trades(self, dt,
            index_fund_cache, 
            tar_fund_weight: FundWeight,
            tar_asset_weight: AssetWeight,
            cur_fund_position: FundPosition,
            cur_asset_position: AssetPosition,
            cur_fund_nav: dict,
            cur_fund_score: dict,
            cur_asset_price: AssetPrice,
            cur_fund_unit_nav: dict,
            is_real_trade: bool,
            cur_manager_funds: dict):

        # 只对不含重复头名基金的基金经理做映射
        _tar_mng_list = tar_fund_weight.get_funds('active')
        cur_funds_manager = {f:m for m,f in cur_manager_funds.items() if m in _tar_mng_list}
        # 如果是真实交易， 把单位份额赋值给复权份额， 价格不用后复权，用真实单位净值
        if is_real_trade:
            fund_tot_mv, cur_fund_wgts = cur_fund_position.calc_mv_n_w(fund_navs=cur_fund_unit_nav)
        else:
            fund_tot_mv, cur_fund_wgts = cur_fund_position.calc_mv_n_w(fund_navs=cur_fund_nav)
        fund_trades = []
        for c in index_fund_cache:
            index_id = c.index_id
            # 主动型基金， tar_fund_list 实际是基金经理 列表 需要转换为基金序列
            tar_fund_list = tar_fund_weight.get_funds(index_id)
            if index_id == 'active':
                tar_fund_list = [cur_manager_funds[i] for i in tar_fund_list]
            cur_fund_list = cur_fund_position.get_funds(index_id)
            for fund_id in set(tar_fund_list).union(cur_fund_list):
                _id = cur_funds_manager[fund_id] if (index_id == 'active') and (fund_id in cur_funds_manager) else fund_id
                
                target_fund_amt = tar_fund_weight.get_wgt(_id) * fund_tot_mv
                cur_fund_volume = cur_fund_position.get_volume(fund_id) or 0
                p = cur_fund_unit_nav[fund_id] if is_real_trade else cur_fund_nav[fund_id]
                cur_fund_amt = cur_fund_volume * p
                if abs(target_fund_amt - cur_fund_amt) > fund_tot_mv * self.fund_param.MinCountAmtDiff \
                    or (target_fund_amt == 0 and cur_fund_amt > 0):
                    # 如果是清某一只基金的逻辑，清空可以执行
                    # commision 放到 finalize_trade 部分执行
                    is_buy = target_fund_amt > cur_fund_amt
                    _amt = abs(target_fund_amt - cur_fund_amt)
                    if is_buy:
                        _trade = FundTrade(
                            fund_id=fund_id,
                            index_id=index_id,
                            mark_price=p,
                            amount=_amt,
                            is_buy=is_buy,
                            submit_date=dt,
                            fund_unit_nav=cur_fund_unit_nav[fund_id],
                            fund_unit_volume=_amt/cur_fund_unit_nav[fund_id]
                        )
                    else:
                        is_to_clean_up = target_fund_amt == 0 and cur_fund_amt > 0
                        _trade = FundTrade(
                            fund_id=fund_id,
                            index_id=index_id,
                            mark_price=p,
                            # 如果清仓 在 calc_trade时就把volume 改成全部仓位， 防止小量仓位残留
                            volume= cur_fund_volume if is_to_clean_up else abs(target_fund_amt - cur_fund_amt)/p,
                            is_buy=is_buy,
                            submit_date=dt,
                            is_to_cleanup=is_to_clean_up,
                            fund_unit_nav=cur_fund_unit_nav[fund_id],
                            fund_unit_volume=_amt/cur_fund_unit_nav[fund_id],
                        )
                    # 如果一个基金属于多个资产类别导致重复下单，只下一次
                    _is_duplicate_fund = False
                    for _t in fund_trades:
                        if fund_id == _t.fund_id:
                            _is_duplicate_fund = True
                    if _is_duplicate_fund:
                        continue
                    fund_trades.append(_trade)
                    # print(f'(fund){fund_id} (d){"buy" if is_buy else "sell"} (r){c.fund_ranks.get(fund_id, -1)} (p){p} (amt){target_fund_amt - cur_fund_amt} (tar){target_fund_amt} (ind){index_id}')

        if is_real_trade and cur_fund_position.cash > 0 :
            #如果是真实交易，现金不为0， 按照cash值调整买单交易量，只返回买单
            buy_trades_amt = sum([i.amount for i in fund_trades if i.is_buy is True])
            sell_trades_amt = cur_fund_position.cash
            buy_adjusted = sell_trades_amt / buy_trades_amt if (sell_trades_amt > 0 and buy_trades_amt > 0) else 1
            _fund_trades = []
            for trd in fund_trades:
                if trd.is_buy == True:
                    trd.amount *= buy_adjusted
                    trd.fund_unit_volume = trd.amount/trd.fund_unit_nav
                    _fund_trades.append(trd)
            fund_trades = _fund_trades
        else:
            #如果一个交易单过小，不达到交易下限，会被忽略，导致买单和卖单交易额相加不相等
            buy_trades_amt = sum([i.amount for i in fund_trades if i.is_buy is True])
            sell_trades_amt = sum([i.mark_price * i.volume for i in fund_trades if i.is_buy is False]) 
            buy_adjusted = sell_trades_amt / buy_trades_amt if (sell_trades_amt > 0 and buy_trades_amt > 0) else 1
            for trd in fund_trades:
                if trd.is_buy == True:
                    trd.amount *= buy_adjusted
                    trd.fund_unit_volume = trd.amount/trd.fund_unit_nav
        ## 检查买卖量是否一致
        # buy_trades_amt = sum([i.amount for i in fund_trades if i.is_buy is True])
        # sell_trades_amt = sum([i.mark_price * i.volume for i in fund_trades if i.is_buy is False]) 
        # print(f'  compare trades dt {dt} amt buy {buy_trades_amt} and sell {sell_trades_amt} diff {buy_trades_amt-sell_trades_amt }')
        return fund_trades

class BasicFundTrader(Helper):

    MIN_AMT_DIFF = 1.0
    ENABLE_COMMISSION = True
    PURCHASE_DISCOUNT = 0.15
    REDEEM_DISCOUNT = 1.0

    def __init__(self):
        self.last_trade_date = None

    # Used in basic strategy (manually prepared fund weights)
    def calc_fund_trade(self, dt, fund_weight: FundWeight, cur_fund_position: FundPosition,
                        cur_fund_nav: dict,
                        fund_purchase_fees: dict,
                        fund_redeem_fees: dict):
        new_fund_position = cur_fund_position.copy()
        fund_trades = []
        # return trade list
        fund_tot_mv, cur_fund_wgts = cur_fund_position.calc_mv_n_w(fund_navs=cur_fund_nav)
        all_funds = {}
        # prepare fund candidates and its index_id
        for fund_id, fund_wgt_item in fund_weight.funds.items():
            all_funds[fund_id] = fund_wgt_item.index_id
        for fund_id, fund_pos_item in cur_fund_position.funds.items():
            all_funds[fund_id] = fund_pos_item.index_id
        # calc trade
        for fund_id, index_id in all_funds.items():
            target_fund_amt = fund_weight.get_wgt(fund_id) * fund_tot_mv
            cur_fund_volume = cur_fund_position.get_volume(fund_id) or 0
            p = cur_fund_nav[fund_id]
            cur_fund_amt = cur_fund_volume * p

            if abs(target_fund_amt - cur_fund_amt) > self.MIN_AMT_DIFF or (target_fund_amt == 0 and cur_fund_amt > 0):
                is_buy = target_fund_amt > cur_fund_amt
                if is_buy:
                    _trade = FundTrade(
                        fund_id=fund_id,
                        index_id=index_id,
                        mark_price=p,
                        amount=abs(target_fund_amt - cur_fund_amt),
                        is_buy=is_buy,
                        submit_date=dt
                    )
                else:
                    is_to_clean_up = target_fund_amt == 0 and cur_fund_amt > 0
                    _trade = FundTrade(
                        fund_id=fund_id,
                        index_id=index_id,
                        mark_price=p,
                        volume=abs(target_fund_amt - cur_fund_amt)/p,
                        is_buy=is_buy,
                        submit_date=dt,
                        is_to_cleanup=is_to_clean_up
                    )
                fund_trades.append(_trade)
                #print(f'(fund){fund_id} (p){p} (amt0){cur_fund_amt} (amt1){target_fund_amt} (idx){index_id} (amt){abs(target_fund_amt - cur_fund_amt)} (direc) {target_fund_amt > cur_fund_amt} ')

        fund_trades.sort(key=lambda x: x.is_buy)
        for _trade in fund_trades:
            new_fund_position.update(_trade)
        return new_fund_position, fund_trades

    def finalize_trade(self, dt, trades: list,
                        t1_price: AssetPrice,
                        bt_position: AssetPosition,
                        cur_fund_position: FundPosition,
                        cur_fund_nav: dict,
                        cur_fund_unit_nav: dict,
                        fund_purchase_fees: dict,
                        fund_redeem_fees: dict,
                        disproved_set: set):

        if trades is None or len(trades) == 0:
            return [], []

        pendings = []
        traded_list = []
        # TODO: if some trades needs more time
        # 先成交卖单， 再根据卖单成交金额 等额成交买单
        for trd in trades:
            trd.trade_price = cur_fund_nav[trd.fund_id]
            trd.fund_unit_nav = cur_fund_unit_nav[trd.fund_id]
            trd.volume = trd.volume if trd.volume else (trd.amount / trd.trade_price)
            trd.amount = trd.amount if trd.amount else (trd.volume * trd.trade_price)
            trd.fund_unit_volume = trd.amount / trd.fund_unit_nav
            trd.trade_date = dt
            if not trd.is_buy:
                cur_vol = cur_fund_position.get_volume(trd.fund_id)
                if not((cur_vol or 0) - trd.volume > -1e-8):
                    #print(f'trade volume exceeds, adjusted to pos (fund_id){trd.fund_id} (vol){trd.volume} (is_buy){trd.is_buy} (pos){cur_vol}')
                    assert cur_vol is not None, 'sell fund with no current position!'
                    trd.volume = cur_vol
                    trd.amount = trd.volume * trd.trade_price
            
            if self.ENABLE_COMMISSION:
                if not trd.is_buy:
                    redeem_fee = fund_redeem_fees[trd.fund_id] * self.REDEEM_DISCOUNT
                    if np.isnan(redeem_fee):
                        redeem_fee = 0
                    trd.commission = trd.amount * redeem_fee
                    trd.amount -= trd.commission
            else:
                trd.commission = 0
            if not trd.is_buy:
                trade_status = cur_fund_position.update(trd)
                if trade_status:
                    traded_list.append(trd)
        _trade_list_buy = [i  for i in trades if i.is_buy is True]
        _trade_list_sel = [i  for i in traded_list if i.is_buy is False]
        # plan_sel_amount = 0 if len(_trade_list_sel) < 1 else sum([i.amount for i in _trade_list_sel])
        # plan_buy_amount = 0 if len(_trade_list_buy) < 1 else sum([i.amount for i in _trade_list_buy])
        # if plan_sel_amount == 0 or plan_buy_amount == 0:
        #     buy_amount_adjusted_rate = 1
        # else:
        #     buy_amount_adjusted_rate = plan_sel_amount / plan_buy_amount
        
        for trd in trades:
            if not trd.is_buy:
                continue
            # trd.amount *= buy_amount_adjusted_rate
            if self.ENABLE_COMMISSION:
                purchase_fee = fund_purchase_fees[trd.fund_id] * self.PURCHASE_DISCOUNT 
                if np.isnan(purchase_fee):
                    #print(f'fund_id {trd.fund_id} purchase fee data not avaiable')
                    purchase_fee = 0
                trd.volume = trd.amount / trd.trade_price / (1 + purchase_fee)
                trd.commission = trd.volume * trd.trade_price * purchase_fee
                trd.fund_unit_volume = trd.amount / trd.fund_unit_nav
            else:
                trd.commission = 0            
                #print(f'trade is not permitted : {trd}')
            trade_status = cur_fund_position.update(trd)
            if trade_status:
                traded_list.append(trd)
            else:
                pass
                #print(f'trade failed alert : {trd}')
        _trade_list_buy = [i  for i in traded_list if i.is_buy is True]
        _trade_list_sel = [i  for i in traded_list if i.is_buy is False]
        # plan_sel_amount = 0 if len(_trade_list_sel) < 1 else sum([i.amount for i in _trade_list_sel])
        # plan_buy_amount = 0 if len(_trade_list_buy) < 1 else sum([i.amount for i in _trade_list_buy])
        # print(f'trade date {dt} sell amount {plan_sel_amount} buy amount {plan_buy_amount} diff {plan_buy_amount-plan_sel_amount}')

        # get cur asset weight from fund weight
        cur_mv, cur_fund_weight = cur_fund_position.calc_mv_n_w(cur_fund_nav)
        fund_index_dic = {}
        for fund_id, fund_pos_item in cur_fund_position.funds.items():
            fund_index_dic[fund_id] = fund_pos_item.index_id
        asset_wgt = { _ : 0 for _ in set(fund_index_dic.values())}
        for fund_id, wgt_i in cur_fund_weight.items():
            index_id = fund_index_dic[fund_id]
            asset_wgt[index_id] += wgt_i
        # set index position:
        for index_id in asset_wgt:
            if index_id in t1_price.__dict__:
                asset_p = t1_price.__dict__[index_id]
            else:
                asset_p = 1.0
            amount = cur_mv * asset_wgt[index_id]
            bt_position.__dict__[index_id] = amount / asset_p
        
        self.last_trade_date = dt
        # fund cash -> asset cash
        bt_position.cash = cur_fund_position.cash
        return pendings, traded_list
