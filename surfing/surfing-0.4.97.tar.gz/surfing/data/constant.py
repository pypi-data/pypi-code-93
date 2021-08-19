import datetime

_DEFAULT_CASH_VALUE = 1e8

class TradeTrigger:

    IndexRebalance = 1
    FundSelection = 10
    FundRebalance = 100
    FundEnd = 1000

    @staticmethod
    def _is(trigger, num):
        return trigger % (num * 10) / num == 1

    @staticmethod
    def is_end(trigger):
        return trigger / TradeTrigger.FundEnd >= 1

    @staticmethod
    def parse(trigger):
        _s = ''
        _s += 'Fe' if TradeTrigger.is_end(trigger) else '' # Fund End
        _s += 'Ir' if TradeTrigger._is(trigger, TradeTrigger.IndexRebalance) else '' # Index Rebalance  
        _s += 'Fs' if TradeTrigger._is(trigger, TradeTrigger.FundSelection) else '' # Fund Selection
        _s += 'Fr' if TradeTrigger._is(trigger, TradeTrigger.FundRebalance) else '' # Fund Rebalance
        if len(_s) == 0:
            _s = 'None'
        return _s

    @staticmethod
    def trigger_log(trigger:int, 
                    # Ir params
                    index_rebalance_max_diff:float,
                    _index_rebalance_max_diff_name:float,
                    JudgeIndexDiff:float,
                    #Fs params
                    fund_selection_min_score:float,
                    _fund_selection_min_name:str,
                    JudgeFundSelection:float,
                    fund_rank_list:list,
                    #Fr params
                    fund_rebalance_min_score:float,
                    _fund_rebalance_min_name:str,
                    JudgeFundRebalance:float,
              ):
        trigger_result = []
        if TradeTrigger.is_end(trigger):
            dic = {
                'rebalanace_reason': 'Fe',
                'index_id': _fund_rebalance_min_name,
                'rebalance_details': f'fund_rebalance_min_score: {round(fund_rebalance_min_score,3)} threshold: {JudgeFundRebalance} fund rank :{fund_rank_list}'
            }
            trigger_result.append(dic)
            return trigger_result

        if TradeTrigger._is(trigger, TradeTrigger.IndexRebalance):
            dic = {
                'rebalanace_reason': 'Ir',
                'index_id': _index_rebalance_max_diff_name,
                'rebalance_details': f'index_rebalance_max_diff: {round(index_rebalance_max_diff,3)} threshold: {JudgeIndexDiff}'
            }
            trigger_result.append(dic)
        
        if TradeTrigger._is(trigger, TradeTrigger.FundSelection):
            dic = {
                'rebalanace_reason': 'Fs',
                'index_id': _fund_selection_min_name,
                'rebalance_details': f'fund_selection_min_score: {round(fund_selection_min_score,3)} threshold: {JudgeFundSelection} fund rank :{fund_rank_list}'
            }
            trigger_result.append(dic)

        if TradeTrigger._is(trigger, TradeTrigger.FundRebalance):
            dic = {
                'rebalanace_reason': 'Fr',
                'index_id': _fund_rebalance_min_name,
                'rebalance_details': f'fund_rebalance_min_score: {round(fund_rebalance_min_score,3)} threshold: {JudgeFundRebalance}'
            }
            trigger_result.append(dic)
        
        return trigger_result

    @staticmethod
    def trigger_detail(trigger:int, 
                    # Ir params
                    index_rebalance_max_diff:float,
                    _index_rebalance_max_diff_name:float,
                    JudgeIndexDiff:float,
                    #Fs params
                    fund_selection_min_score:float,
                    _fund_selection_min_name:str,
                    JudgeFundSelection:float,
                    fund_rank_list:list,
                    #Fr params
                    fund_rebalance_min_score:float,
                    _fund_rebalance_min_name:str,
                    JudgeFundRebalance:float,
              ):
        result = {
            'index_rebalance_detail':   f'index_id {_index_rebalance_max_diff_name} index_rebalance_max_diff: {round(index_rebalance_max_diff,3)} threshold: {JudgeIndexDiff}',
            'fund_selection':           f'index_id {_fund_selection_min_name} fund_selection_min_score: {round(fund_selection_min_score,3)} threshold: {JudgeFundSelection} fund rank :{fund_rank_list}',
            'fund_rebalance':           f'index_id {_fund_rebalance_min_name} fund_rebalance_min_score {round(fund_rebalance_min_score,5)} threshold: {JudgeFundRebalance}'

        }
        return result