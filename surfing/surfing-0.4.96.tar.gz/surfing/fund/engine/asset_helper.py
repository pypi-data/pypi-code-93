import pandas as pd
from ...data.struct import AssetWeight, AssetPrice, AssetPosition, AssetValue
from ...data.struct import TAAParam, FAParam, FundWeightItem, FundWeight, TaaTunerParam
from . import Helper


class SAAHelper(Helper):

    def __init__(self):
        pass

    def setup(self, saa: AssetWeight):
        self.saa = saa

    def on_price(self, dt, asset_price: AssetPrice):
        cur_saa = self.saa.copy()
        for k, v in asset_price.__dict__.items():
            if asset_price.isnan(v):
                cur_saa.__dict__[k] = 0
        cur_saa.rebalance()
        return cur_saa


class TAAStatusMode:
    NORMAL = 'normal'
    IN_LOW = 'low'
    IN_HIGH = 'high'

class TAAHelper(Helper):

    # 1. let each asset use same taa param: set taa_params and taa_param_details == None
    # 2. let some asset use special taa param and others default: set taa_params and make special params in taa_param_details
    # 3. stop some asset from using taa: make taa_param_details[index_id] = None
    # 4. only asset in taa_param_details has taa: make taa_params = None
    def __init__(self, taa_params: TAAParam=None, taa_param_details: dict=None):
        self.params = taa_params or TAAParam()
        self.param_details = taa_param_details or {}
        self.tactic_status = {}
        self.tactic_history = {}

    def on_price(self, dt, asset_price: AssetPrice, cur_saa: AssetWeight, asset_pct: pd.DataFrame, select_val: dict, score_dict: dict):
        taa = cur_saa.copy()
        taa_effected = False
        mode_changed = False
        tactic_dt = {}
        for index_id, target_w in taa.__dict__.items():
            # 如果self.param_details存在， 按照里面设定index做taa, 不设定的不做taa
            # 如果self.param_details不存在，默认值是{}, 则所有index统一参数 self.params
            cur_params = self.params if not bool(self.param_details) else self.param_details.get(index_id, None)
            if target_w == 0 or cur_params is None:
                continue
            #if index_id in TaaTunerParam.POOL:
            #assert index_id in asset_pct.index, f'{index_id} pct not exsit'
            # 无估值跳过  大部分资产08年之前没有估值百分位
            if index_id not in asset_pct.index:
                continue
            assert (index_id in select_val) or (index_id in TaaTunerParam.POOL), \
                f'index_id {index_id} without definded index valuation to taa'
            val_col = select_val[index_id] if index_id in select_val.keys() else TaaTunerParam.POOL[index_id]
            val_pct = asset_pct.loc[index_id, val_col]
            cur_mode = self.tactic_status.get(index_id, TAAStatusMode.NORMAL)
            new_mode = TAAStatusMode.NORMAL
            tactic_w = target_w

            if cur_mode == TAAStatusMode.NORMAL:

                if val_pct >= cur_params.HighThreshold:
                    tactic_w = max(target_w - cur_params.HighMinus, 0)
                    new_mode = TAAStatusMode.IN_HIGH
                elif val_pct <= cur_params.LowThreshold:
                    tactic_w = min(target_w + cur_params.LowPlus, 1)
                    new_mode = TAAStatusMode.IN_LOW
                
            elif cur_mode == TAAStatusMode.IN_LOW:

                if val_pct < cur_params.LowStop:
                    tactic_w = min(target_w + cur_params.LowPlus, 1)
                    new_mode = TAAStatusMode.IN_LOW

            elif cur_mode == TAAStatusMode.IN_HIGH:

                if val_pct > cur_params.HighStop:
                    tactic_w = max(target_w - cur_params.HighMinus, 0)
                    new_mode = TAAStatusMode.IN_HIGH
            else:
                assert False, 'should not be here!'

            self.tactic_status[index_id] = new_mode
            if new_mode != TAAStatusMode.NORMAL:
                taa.__dict__[index_id] = tactic_w
                if cur_params.ToMmf:
                    taa.mmf -= (tactic_w - target_w)

            mode_changed = mode_changed or new_mode != cur_mode
            taa_effected = taa_effected or new_mode != TAAStatusMode.NORMAL
            tactic_dt[index_id] = new_mode
        self.tactic_history[dt] = tactic_dt
        if taa.mmf < 0:
            #print(f'{dt} taa mmf less than 0 mmf weight {taa.mmf} tactic_dt {tactic_dt}')
            taa.mmf = 0
        self.rebalance_taa(taa, self.params.TuneCash)
        self.asset_adjust(taa, score_dict)
        if taa_effected:
            #print(f'taa: {dt} (mode){mode_changed} (taa){taa_effected} (saa){cur_saa} (taa){taa}')
            pass
        return taa

    def rebalance_taa(self, asset_weight:AssetWeight, to_tune_cash:bool):
        asset_weight = asset_weight.__dict__
        _sum = 0.0
        for k, v in asset_weight.items():
            assert round(v,8) >= 0, f'{k} has negative value'
            _sum += v
        assert _sum > 0, 'param sum value must be positive'
        # 验证过的非现金类资产rebalance
        if not to_tune_cash:
            if asset_weight['cash'] != _sum:
                _sum = (_sum - asset_weight['cash']) / (1 - asset_weight['cash'])
            # 资产配置只有现金时，不需要rebalance
            else:
                return
        # 不调整cash
        for k, v in asset_weight.items():
            if k == 'cash' and (not to_tune_cash):
                continue
            asset_weight[k] /= _sum

    def asset_adjust(self, asset_weight:AssetWeight, score_dict:dict):
        # 如果当前资产没有候选基金，买货基
        asset_weight = asset_weight.__dict__
        for k,v in asset_weight.items():
            if k in score_dict:
                index_fund_nums = len(list(score_dict[k].keys()))
                if index_fund_nums == 0:
                    asset_weight['mmf'] += v
                    asset_weight[k] -= v
 
class FAHelper(Helper):
    
    def __init__(self, fa_params: FAParam=None):
        self.params = fa_params or FAParam()
        self.proper_fund_numbers = {}

    def setup(self, saa: AssetWeight):
        self.saa = saa
        ## set proper fund num for each 
        self.fund_nums = {}
        for index_id, asset_wgt in self.saa.__dict__.items():
            if index_id == 'active':
                self.fund_nums[index_id] = 10
                continue
            max_fund_num = int(round(asset_wgt / 0.05, 0))
            if asset_wgt > 0 and max_fund_num <= 0:
                max_fund_num = 1
            max_fund_num = min(max_fund_num, self.params.MaxFundNumUnderAsset)
            if max_fund_num > 0:
                self.fund_nums[index_id] = max_fund_num
            
    def get_max_fund_num(self, index_id):
        return int(self.fund_nums.get(index_id, 1))        

    def on_price(self, dt, cur_asset_allocation: AssetWeight, cur_fund_score: dict, cur_manager_score_cleaned : dict, score_select_dict : dict):
        
        # if no fund in index_id, rebalance again
        for index_id, w in cur_asset_allocation.__dict__.items():
            if w == 0 or index_id == 'cash':
                continue
            _score_dic = cur_fund_score.get(index_id,None)
            if not _score_dic:
                cur_asset_allocation.__dict__[index_id] = 0
            else:
                _score_dic = _score_dic[score_select_dict[index_id]]
                if not _score_dic:
                    cur_asset_allocation.__dict__[index_id] = 0
        cur_asset_allocation.rebalance()

        res = FundWeight()
        for index_id in cur_asset_allocation.__dict__.keys():
            if index_id == 'cash':
                continue
            score_type = score_select_dict[index_id]
            asset_wgt = cur_asset_allocation.__dict__[index_id]
            if asset_wgt > 0:
                # 保证主动基金不买到相同基金 的基金经理
                if index_id == 'active':
                    # print(f'cur_manager_score_cleaned {cur_manager_score_cleaned}')
                    # print(f'score_type {score_type}')
                    _scores = sorted(cur_manager_score_cleaned[score_type].items(), key=lambda item: item[1], reverse=True)
                else:     
                    _scores = sorted(cur_fund_score.get(index_id, {}).get(score_type, {}).items(), key=lambda item: item[1], reverse=True)
                proper_fund_num = self.get_max_fund_num(index_id) # for a single asset, for each 5% wgt it gots, they should take 1 extra fund

                if proper_fund_num > len(_scores):
                    #print(f'lack fund candidates: (dt){dt} (index_id){index_id} (proper_num){proper_fund_num} (fund_num){len(_scores)}')
                    proper_fund_num = len(_scores)
                for i in range(0, proper_fund_num):
                    fund_id, _score = _scores[i]
                    fund_weight_item = FundWeightItem(fund_id=fund_id, index_id=index_id, asset_wgt=asset_wgt, fund_wgt_in_asset=1.0 / proper_fund_num)
                    res.add(fund_weight_item)

                #assert proper_fund_num > 0, f'no fund is selected in {index_id}'                    
        return res