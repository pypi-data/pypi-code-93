from .trader import FundTrader

from ...data.struct import AssetWeight, AssetPrice, AssetPosition, AssetValue
from ...data.struct import AssetTrade, FundTrade, FundPosition, FundWeight
from ...data.struct import AssetTradeParam, FundTradeParam
from ...data.struct import AssetTradeCache, FundWeightItem
from ...data.constant import TradeTrigger
from . import Helper
from .asset_helper import FAHelper
import numpy as np
import math


class FundScoreTolTrader(FundTrader):
    '''
    判定是否需要交易

    核心是计算 index 偏移（index_max_diff）和 fund 偏移（fund_max_diff）

    最终用 diff = lambda * fund_max_diff + (1-lambda) * index_max_diff 是否超过阈值来判定

    FundTradeParam.DiffJudgeLambda
    FundTradeParam.DiffJudgeTolarance
    FundTradeParam.DiffJudgeAssetWgtRequirement

    loop 每一个待交易的资产：(index_id)
    1. 计算该资产需要调整的比例，如果大于 index_max_diff ，则更新该值
    2. 计算该资产下应该有的基金数量 （FAHelper.get_proper_fund_num）
    3. 计算按照当前的基金排名情况，应该实际持有哪些基金（new_fund_ids）
    4. 按照 new_fund_ids 等权分布，统计该资产下所有基金需要变更的比例之和（暂时只统计买入单边，不考虑该资产占总比的情况）该资产占比超过 3%（DiffJudgeAssetWgtRequirement） 且该比例大于 fund_max_diff，则更新该值
    # 此时我们获得了 index_max_diff 和 fund_max_diff

    最终交易目标：
    对于某个资产，下面应该有 proper_num 个基金

    1. 当前持仓仍排名在前 proper_num 的基金，我们统一安排 1 / proper_num 的比例
    2. 如果排名在 proper_num + 1 ~ 2 * proper_num 的基金，如果不足 1 / proper_num 的比例，则不变，如果多于 1 / proper_num，就减至 1 / proper_num。（只减少，不增加）
    3. 如果当前已安排的基金少于 proper_num，则增加排名在前 proper_num 但不在当前列表中的 proper_num - current_num 个基金到列表中，每个安排 1 / proper_num 的比例
    4. 如果当前比例还有剩余（步骤2中产生的），如果步骤1中前 proper_num 有哪个减少过，就按照排名高低revert这个减少；如果将减少的都处理完还有剩余，那么进入到特殊状态（SPECIAL）
    5. 对于SPECIAL，我们先看fund_selected_num是否已达到proper_num，如果否，从fund_score中按评分从高到低将不在当前持仓的基金每个都增加进去，最多不超过 1 / proper_num，直到fund_selected_num等于proper_num或剩余的量消耗光；如果是，或fund_selected_num等于proper_num时剩余的量仍未消耗光，我们将剩余的比例平均分配给当前持仓的基金，以此来将剩余的量消耗光（分配后有可能超过 1 / proper_num，但实际在上边第4条中也有可能导致超过 1 / proper_num）
    '''

    def get_trades(self, dt,
            index_fund_cache: AssetTradeCache, 
            tar_fund_weight: FundWeight,
            tar_asset_weight: AssetWeight,
            cur_fund_position: FundPosition,
            cur_asset_position: AssetPosition,
            cur_fund_nav: dict,
            cur_fund_score: dict,
            cur_asset_price: AssetPrice):

        fund_tot_mv, cur_fund_wgts = cur_fund_position.calc_mv_n_w(fund_navs=cur_fund_nav)

        fund_trades = []

        for c in index_fund_cache:
            funds = {}
            fund_selected_num = 0
            fund_selected_wgt = 0
            proper_fund_wgt = 1.0 / c.proper_fund_num if c.proper_fund_num > 0 else 0
            good_fund_to_sell = []
            to_cancel = set([])
            # 如果 cur_fund_ids 超过 proper_fund_num
            if len(c.cur_fund_ids) > c.proper_fund_num:
                _d = {fund_id: c.fund_ranks.get(fund_id) for fund_id in c.cur_fund_ids}
                _dd = sorted(_d.items(), key=lambda x: x[1], reverse=True)
                for fund_id, _rank in _dd[:len(c.cur_fund_ids) - c.proper_fund_num]:
                    to_cancel.add(fund_id)
                    print(f'to_cancel (fund_id){fund_id} (rank){_rank}')

            for fund_id in c.cur_fund_ids:
                _rank = c.fund_ranks.get(fund_id)
                if _rank is None:
                    print(f'got a None rank when trying to trade, (index_id){c.index_id} (fund_id){fund_id} (dt){dt} (fund_scores){c.fund_scores} (fund_ranks){c.fund_ranks}')
                    to_cancel.add(fund_id)
                _cur_wgt = c.fund_cur_wgts.get(fund_id, 0)
                _tar_wgt = 0
                if fund_id in to_cancel:
                    _tar_wgt = 0
                elif _rank <= c.proper_fund_num:
                    # 当前持仓仍排名在前 proper_num 的基金，我们统一安排 1 / proper_num 的比例
                    _tar_wgt = proper_fund_wgt
                    if _cur_wgt * c.index_cur_wgt > _tar_wgt * c.index_tar_wgt:
                        good_fund_to_sell.append((fund_id, _rank, _cur_wgt * c.index_cur_wgt - _tar_wgt * c.index_tar_wgt))
                elif _rank <= c.proper_fund_num * 2:
                    # 如果排名在 proper_num + 1 ~ 2 * proper_num 的基金，
                    # 如果不足 1 / proper_num 的比例，则不变，如果多于 1 / proper_num，就减至 1 / proper_num。（只减少，不增加）
                    _tar_wgt = min(proper_fund_wgt, _cur_wgt * c.index_cur_wgt / c.index_tar_wgt)
                else:
                    _tar_wgt = 0

                fund_selected_wgt += _tar_wgt
                fund_selected_num += 1 if _tar_wgt > 0 else 0

                _wgt = FundWeightItem(fund_id=fund_id, index_id=c.index_id, asset_wgt=c.index_tar_wgt, fund_wgt_in_asset=_tar_wgt)
                funds[fund_id] = _wgt

            assert fund_selected_wgt <= 1, f'[fund trade] tot fund wgt <= 1: {fund_selected_wgt}'

            # 如果当前比例还有剩余（步骤2中产生的）
            if fund_selected_wgt < 1 - 1e-5 and c.index_tar_wgt > 0:
                tot_wgt_left = (1 - fund_selected_wgt) * c.index_tar_wgt
                # 如果步骤1中前 proper_num 有哪个减少过，就按照排名高低revert这个减少
                if len(good_fund_to_sell) > 0:
                    good_to_sell_list = sorted(good_fund_to_sell, key=lambda x: x[1])

                    for fund_id, _rank, _sell_wgt in good_to_sell_list:
                        print(f'one in good_to_sell_list, (index_id){c.index_id} (fund_id){fund_id} (rank){_rank} (sell_wgt){_sell_wgt}')
                        revert_wgt = min(tot_wgt_left, _sell_wgt)
                        funds[fund_id].add_tot_wgt(revert_wgt)
                        tot_wgt_left -= revert_wgt
                        if tot_wgt_left < 1e-5:
                            break

                # 如果将减少的都处理完还有剩余，那么进入到特殊状态（SPECIAL）
                if tot_wgt_left > 1e-5:
                    print(f"happy in SPECIAL CASE (proper num){c.proper_fund_num}")
                    assert fund_selected_num <= c.proper_fund_num, f'fund selected num {fund_selected_num} should le than proper fund num {c.proper_fund_num}!!'
                    # 对于SPECIAL，我们先看fund_selected_num是否已达到proper_num
                    if fund_selected_num < c.proper_fund_num:
                        # 如果否，从fund_score中按评分从高到低将不在当前持仓的基金每个都增加进去，最多不超过 1 / proper_num，直到fund_selected_num等于proper_num或剩余的量消耗光
                        for fund_id, _score in c.fund_scores:
                            if fund_id not in funds:
                                _tar_wgt = min(proper_fund_wgt, tot_wgt_left / c.index_tar_wgt)
                                _wgt = FundWeightItem(fund_id=fund_id, index_id=c.index_id, asset_wgt=c.index_tar_wgt, fund_wgt_in_asset=_tar_wgt)
                                print(f'[SPECIAL] (index_id){c.index_id} (fund){fund_id} (score){_score} (rank){c.fund_ranks[fund_id]} (tar_wgt){_tar_wgt}')
                                funds[fund_id] = _wgt
                                fund_selected_num += 1
                                tot_wgt_left -= _tar_wgt * c.index_tar_wgt
                                if tot_wgt_left < 1e-5 or fund_selected_num == c.proper_fund_num:
                                    break

                    # 如果是，或fund_selected_num等于proper_num时剩余的量仍未消耗光
                    # 我们将剩余的比例平均分配给当前持仓的基金，以此来将剩余的量消耗光（分配后有可能超过 1 / proper_num，但实际在上边第4条中也有可能导致超过 1 / proper_num）
                    if tot_wgt_left > 1e-5:
                        funds_without_no_wgt = {fund_id: fund for fund_id, fund in funds.items() if fund.fund_wgt_in_asset > 0}
                        avg_wgt_left = tot_wgt_left / len(funds_without_no_wgt)
                        for fund_id, _wgt in funds_without_no_wgt.items():
                            print(f'[SPECIAL] (index_id){c.index_id} (fund){fund_id} (rank){c.fund_ranks[fund_id] if fund_id in c.fund_ranks else None} (avg_wgt_left){avg_wgt_left}')
                            _wgt.add_tot_wgt(avg_wgt_left)
                            tot_wgt_left -= avg_wgt_left
                            assert tot_wgt_left >= 0 or math.isclose(tot_wgt_left, 0, abs_tol=1e-05), f'tot_wgt_left less than zero!! {tot_wgt_left} (index_id){c.index_id}'

                assert tot_wgt_left < 1e-5, f'special even failed: {c.index_id}'

            for fund_id, _wgt in funds.items():
                target_fund_amt = _wgt.fund_wgt * fund_tot_mv
                cur_fund_amt = c.fund_cur_wgts.get(fund_id, 0) * c.index_cur_wgt * fund_tot_mv
                if abs(target_fund_amt - cur_fund_amt) > fund_tot_mv * self.fund_param.MinCountAmtDiff or (target_fund_amt == 0 and cur_fund_amt > 0):
                    p = cur_fund_nav[fund_id]
                    _trade = FundTrade(
                        fund_id=fund_id,
                        index_id=c.index_id,
                        mark_price=p,
                        amount=abs(target_fund_amt - cur_fund_amt),
                        is_buy=target_fund_amt > cur_fund_amt,
                        submit_date=dt,
                        is_to_cleanup=(target_fund_amt == 0 and cur_fund_amt > 0)
                    )
                    fund_trades.append(_trade)
                    print(f'(fund){fund_id} (index){c.index_id} (p){p} (rank){c.fund_ranks[fund_id] if fund_id in c.fund_ranks else 0} (cur_amt){cur_fund_amt} (tar_amt){target_fund_amt} (idx){c.index_id} (amt){target_fund_amt - cur_fund_amt}')

        return fund_trades