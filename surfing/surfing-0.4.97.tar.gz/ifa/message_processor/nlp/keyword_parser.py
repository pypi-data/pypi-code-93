import re

class KeywordParser(object):

    def parse(self, word_tuples, text, result):
        words = [x[0] for x in word_tuples]

        if '我的持仓' in text:
            result['type'] = 'cczx'
            result['data']['target'] = 'all'
        elif '我的净值' in text:
            result['type'] = 'cczx'
            result['data']['target'] = 'nav'
        elif '交易记录' in text:
            result['type'] = 'cczx'
            result['data']['target'] = 'trades'
        # # 处理通用咨询 (tyzx)
        # if '投资' in text and ('策略' in text or ('建立' in text and '组合' in text)):
        #     result['type'] = 'tyzx'
        #     result['data'] = {
        #         'target': '投资策略'
        #     }
        # elif '收益' in text and '风险' in text and '预估' in text:
        #     result['type'] = 'tyzx'
        #     result['target'] = '投资策略'
        # elif '持有' in text and ('多久' in text or '时间' in text):
        #     result['type'] = 'tyzx'
        #     result['target'] = '持有时间'
        # elif '赎回' in text:
        #     result['type'] = 'tyzx'
        #     result['target'] = '持有时间'
        # elif '费用' in text or '收费' in text or '交易费' in text:
        #     result['type'] = 'tyzx'
        #     result['target'] = '收费方式'
        # elif '交易' in text:
        #     if '记录' in text:
        #         result['type'] = 'cczx'
        #         result['target'] = 'trading_history'
        #     elif '如何' in text:
        #         result['type'] = 'tyzx'
        #         result['target'] = '收费方式'
        # elif '年化' in text and '收益' in text:
        #     arr = re.findall(r"\d+\.?\d*", text)
        #     if len(arr) > 0:
        #         ret = float(arr[0])
        #         if ret > 1:
        #             ret = ret / 100
        #         result['type'] = 'zhtj'
        #         result['target'] = 'ret'
        #         result['ret'] = ret
        # elif '高' in text and '收益' in text:
        #     result['type'] = 'zhtj'
        #     result['target'] = 'ret'
        #     result['ret'] = 'high'
        # elif '回撤' in text:
        #     arr = re.findall(r"\d+\.?\d*", text)
        #     if len(arr) > 0:
        #         mdd = float(arr[0])
        #         if mdd > 1:
        #             mdd = mdd / 100
        #         result['type'] = 'zhtj'
        #         result['target'] = 'mdd'
        #         result['mdd'] = mdd
        # elif '低' in text and '风险' in text:
        #     result['type'] = 'zhtj'
        #     result['target'] = 'mdd'
        #     result['mdd'] = 'low'
        # elif '股票' in text:
        #     if '为何' in text or '为什么' in text:
        #         if '收益' in text and ('不明显' in text or '下降' in text):
        #             result['type'] = 'yjfx'
        #             result['baseline'] = 'stock'
        #         else:
        #             result['type'] = 'chfx'
        #             result['target'] = 'asset'
        #             result['asset'] = 'stock'
        #     else:
        #         result['type'] = 'hqzx'
        #         result['target'] = 'asset'
        #         result['asset'] = 'stock'
        # elif '信用债' in text:
        #     if '为何' in text or '为什么' in text:
        #         result['type'] = 'chfx'
        #         result['target'] = 'asset'
        #         result['asset'] = 'credit_debt'
        #     else:
        #         result['type'] = 'hqzx'
        #         result['target'] = 'asset'
        #         result['asset'] = 'credit_debt'
        # elif 'target' in result.keys() and result['target'] == 'fund':
        #     if '为何' in text or '为什么' in text:
        #         result['type'] = 'chfx'
        #     else:
        #         result['type'] = 'hqzx'
        # elif '组合' and '收益' in text:
        #     result['type'] = 'cczx'
        #     result['target'] = 'nav'
        # elif '组合' in text and '板' in text:
        #     result['type'] = 'cczx'
        #     result['target'] = 'industry'
        # elif '大类' in text and ('配比' in text or '表现' in text):
        #     if '为何' in text or '为什么' in text:
        #         result['type'] = 'chfx'
        #         result['target'] = 'asset'
        #         result['asset'] = 'all'
        #     else:
        #         result['type'] = 'cczx'
        #         result['target'] = 'asset'
        # elif '持仓' in text:
        #     result['type'] = 'cczx'
        #     result['target'] = 'fund'
        # elif '基金' in text:
        #     if '怎么' in text or '为什么' in text or '为何' in text:
        #         result['type'] = 'chfx'
        #         result['target'] = 'fund'
        #         result['fund'] = 'all'
        #     else:
        #         result['type'] = 'cczx'
        #         result['target'] = 'fund'
        # elif '业绩' in text:
        #     result['type'] = 'cczx'
        #     result['target'] = 'backtest'
        # elif '国债' in text:
        #     result['type'] = 'chfx'
        #     result['target'] = 'asset'
        #     result['asset'] = 'national_debt'
        # elif '净值' in text and '下降' in text:
        #     result['type'] = 'yjfx'
        # elif '组合' in text and '亏损' in text:
        #     result['type'] = 'yjfx'

        return result

        
    
    
    
        