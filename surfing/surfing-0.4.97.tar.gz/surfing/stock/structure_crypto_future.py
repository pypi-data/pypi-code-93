# 数字货币期货与股票最大不同还是在仓位的计算上
# 不论是保证金计算还是市值计算都有区别,而这些都是体现在 PositionInfo 上的
# 因此,要想让回测引擎同时支持两种标的就需要在 PositionInfo 跟 PosItem 里写大量的 if
# 这在支持标的增多的时候会成为负担而且也不是一种简洁的方式
# 因此,我认为更合理的方式应是不同标的的 Pos 就用一个子类来实现,所以现在即使用了 if 实现之后也是需要重构的
# 而目前在可预计的范围内(两三个月?)这会测系统也不需要接入股票的,即使要接入别的标的也是数字货币的现货以及期权可能性大
# 所以现在采取的方法是直接改写 PositionInfo 使其只支持数字货币的期货
# 让程序先跑通再考虑怎么重构
import os
import yaml
from ..constant import OrderStatus, ExecRole, ExchangeID, Direction, OrderType, AssetType, PosiDirection
from collections import deque
import numpy as np
# 重写 structure 三部分,TransferRequest,虽然 order_manager和 backtest_engine 都出现了 transfer 相关的东西,但好像都不需要改
# 只需要改 position 里面的 transfer 就好了.好像也不需要重写 TransferRequest,只需要把里面的 ticker 理解方式改一下就好了
# 之前的 ticker 填的是具体要转的币,现在要转的是对应这个 ticker 的保证金


class PosItem:

    def __init__(self, **kwds):
        # 抛弃昌浩记录 posItem 的方式,他的方式是保证金也好合约也好都用 PosItem 记录
        # 但是保证金和合约很多attribute 都不一样,因此都记作 PosItem 不太合适,即使以后完善了也应该是分为不同种类的 position 的
        # 因此在这改变记法,初始化的时候就把保证金看做合约position的其中一个属性,因此 transfer 部分要进行改动
        # 现在采取的是开仓均价计算保证金的方式,因此保证金就有未实现与已实现两部分,而计算总保证金的时候是把两者都加一起计算
        self.exchange = kwds.get('exchange', ExchangeID.NOT_AVAILABLE)
        self.ticker = kwds.get('ticker')
        # 用来判断手续费率的,因为相同交易所不同到期日合约名称不一样,但其实是相同性质的合约,费率也都是一样
        self.fee_rate_type = kwds.get('fee_rate_type')
        # 记录这个合约是用什么作为保证金的,其实只支持倒数合约,因为在计算 margin 变化的时候只对这一种做支持
        # 所以在这两边期货合约保证金都是BTC
        self.margin_ticker = kwds.get('margin_ticker', PositionInfo.MARGIN)
        # 记录当前仓位的开仓均价
        self.avg_cost = kwds.get('avg_cost', 0)
        self.asset_type = kwds.get('asset_type', AssetType.NOT_AVAILABLE)
        self.posi_direction = kwds.get('posi_direction', PosiDirection.NET)
        # 假设可以开到无限杠杆吧,或者说维持保证金率是 0,也就是说只要保证金大于 0 就不爆仓,所以 margin_frozen 这项应该总为 0
        self.margin_frozen = kwds.get('margin_frozen', 0)
        # 初始化的时候相当于起始保证金,初始化时候必须得有,之后只有每次平仓的时候才会改变这个值,开仓的话是不会变的
        self.realized_margin = kwds.get('realized_margin', 0)
        if self.realized_margin is None:
            raise Exception("没钱炒什么币,充值再来")
        # 相当于浮盈浮亏,计算的是开仓了的那部分浮动盈亏,但为避免交易所插针或者 1token 数据有误,这里计算用的价格是近 100 个 tick 的 last 的算术平均值
        self.unrealized_margin = kwds.get('unrealized_margin', 0)
        self.cal_unreal_len = 100
        self.clear_prices = deque(maxlen=self.cal_unreal_len)
        self.mean_price = 0
        # 如果是合约的仓位,大于 0 代表多头,小于 0 代表空头
        self.position = kwds.get('position', 0)
        # 应该叫 margin_to_transfer,但能转账的只有保证金,所以这个就不改了
        self.to_transfer = kwds.get('to_transfer', 0)
        self.leverage = 0

    @staticmethod
    def ticker_to_exchange(ticker):
        return 'BITMEX' if len(ticker) > 10 else 'OKEX'

    def get_market_value(self):
        return self.realized_margin + self.unrealized_margin

    def transfer(self, volume):
        if self.realized_margin + self.unrealized_margin - self.margin_frozen - self.to_transfer >= volume:
            self.realized_margin -= volume
            self.to_transfer += volume
            return True
        return False

    def init_clear(self, tick):
        # clear_prices 为空时对其进行初始化
        self.clear_prices[tick.ticker] = deque(maxlen=self.cal_unreal_len)
        self.clear_prices[tick.ticker].append((tick.ask_price1 + tick.bid_price1) / 2)

    def append_clear(self, tick):
        # 后面把每个 tick 的价格都append 在后面,顺便把 unrealized 都更新一下
        self.clear_prices.append((tick.ask_price1 + tick.bid_price1) / 2)
        self.mean_price = np.mean(self.clear_prices)
        if self.position != 0:
            self.unrealized_margin = self.position * PositionInfo.CONTRACT_SIZE[self.ticker_to_exchange(tick.ticker)] * (1 / self.avg_cost - 1 / self.mean_price)
            self.leverage = abs(self.position * PositionInfo.CONTRACT_SIZE[self.ticker_to_exchange(tick.ticker)] / self.mean_price) / (self.realized_margin + self.unrealized_margin)

    def __str__(self):
        return '<PosItem ex={} ticker={} at={} d={} pos={} trans={} realized={} unrealized={} avg_cost={} leverage={}>'.format(
            ExchangeID.read(self.exchange), self.ticker, AssetType.read(self.asset_type),
            PosiDirection.read(self.posi_direction), self.position, self.to_transfer, self.realized_margin, self.unrealized_margin, self.avg_cost, self.leverage
        )


class PositionInfo:
    
    MARGIN = 'btc'
    CONTRACT_SIZE = {'BITMEX': 1,
                        'OKEX': 100}
    os.path.abspath('../config/fee_rate.yml')
    with open('../config/fee_rate.yml', 'r') as f:
        FEE_RATE = yaml.safe_load(f)
                
    def __init__(self, **kwds):
    
        
        _holdings = kwds.get('holdings', [])
        self.holdings = []
        self._tick_idx = {}
        for pi in _holdings:
            self.create_holding(pi)

    def create_holding(self, pos_item):
        self.holdings.append(pos_item)
        # 以 ticker 和 exchange 来标识这个仓位,ticker在这相当于合约的品种
        self._tick_idx[(pos_item.ticker, pos_item.exchange)] = len(self.holdings) - 1  # 以 ticker 和 exchange 来标识这个仓位

    def get_holding(self, ticker, exchange=ExchangeID.NOT_AVAILABLE):
        idx = self._tick_idx.get((ticker, exchange))
        return None if idx is None else self.holdings[idx]

    def init_transfer(self, transfer):
        from_pos = self.get_holding(ticker=transfer.from_ticker, exchange=transfer.from_exchange)
        return False if from_pos is None else from_pos.transfer(transfer.volume)

    def confirm_transfer(self, transfer):
        from_pos = self.get_holding(ticker=transfer.from_ticker, exchange=transfer.from_exchange)
        from_pos.to_transfer -= transfer.volume
        to_pos = self.get_holding(ticker=transfer.to_ticker, exchange=transfer.to_exchange)
        if to_pos is None:
            to_pos = PosItem(exchange=transfer.to_exchange, ticker=transfer.to_ticker, asset_type=transfer.asset_type)
            self.create_holding(to_pos)
        to_pos.realized_margin += transfer.volume

    @staticmethod
    def get_commission(trade, pos):
        # 根据 trade 计算手续费多少
        rate = PositionInfo.FEE_RATE[ExchangeID.read(trade.exchange)][AssetType.read(trade.asset_type)][pos.fee_rate_type][-1][ExecRole.read(trade.exec_role)]
        commission = rate * trade.trade_volume * PositionInfo.CONTRACT_SIZE[ExchangeID.read(trade.exchange)] / trade.trade_price
        return commission

    def process_trade(self, trade):
        # print(f'来到了 structure 的 process_trade,你的交易是{trade}')
        # 只处理数字货币的期货交易
        pos = self.get_holding(ticker=trade.ticker, exchange=trade.exchange)
        if pos is None:
            pos = PosItem(exchange=trade.exchange, ticker=trade.ticker, asset_type=trade.asset_type)
            self.create_holding(pos)
        # print(f'你要进行处理的仓位是{pos}')
        if pos.position < 0:
            # 原本空头,现在如果是 sell 则重新计算 avg_cost
            if trade.direction == Direction.SELL:
                new_position = pos.position - trade.trade_volume
                pos.avg_cost = new_position / (pos.position / pos.avg_cost - trade.trade_volume / trade.trade_price)
                pos.position = new_position
                # 手续费从已实现保证金改变
                pos.realized_margin -= self.get_commission(trade, pos)
            elif trade.direction == Direction.BUY:
                # 如果是平仓, 平均成本不变,但改变已实现盈亏
                if trade.trade_volume + pos.position > 0:
                    # 这时候仓位得反向了
                    pos.realized_margin -= self.get_commission(trade, pos)
                    pos.realized_margin += pos.position * PositionInfo.CONTRACT_SIZE[ExchangeID.read(trade.exchange)] * ((1 / pos.avg_cost) - (1 / trade.trade_price))
                    pos.position += trade.trade_volume
                    pos.avg_cost = trade.trade_price
                else:
                    pos.position += trade.trade_volume
                    pos.realized_margin += trade.trade_volume * PositionInfo.CONTRACT_SIZE[ExchangeID.read(trade.exchange)] * ((1 / trade.trade_price) - (1 / pos.avg_cost)) - self.get_commission(
                        trade, pos)
        elif pos.position > 0:
            if trade.direction == Direction.BUY:
                new_position = pos.position + trade.trade_volume
                pos.avg_cost = new_position / (pos.position / pos.avg_cost + trade.trade_volume / trade.trade_price)
                pos.position = new_position
                pos.realized_margin -= self.get_commission(trade, pos)
            elif trade.direction == Direction.SELL:
                if pos.position - trade.trade_volume < 0:
                    pos.realized_margin -= self.get_commission(trade, pos)
                    pos.realized_margin += pos.position * PositionInfo.CONTRACT_SIZE[ExchangeID.read(trade.exchange)] * ((1 / pos.avg_cost) - (1 / trade.trade_price))
                    pos.position -= trade.trade_volume
                    pos.avg_cost = trade.trade_price
                else:
                    pos.position -= trade.trade_volume
                    pos.realized_margin += trade.trade_volume * PositionInfo.CONTRACT_SIZE[ExchangeID.read(trade.exchange)] * ((1 / pos.avg_cost) - (1 / trade.trade_price)) - self.get_commission(
                        trade, pos)
        else:
            # 此时仓位是 0,第一次开仓状态
            pos.realized_margin -= self.get_commission(trade, pos)
            pos.avg_cost = trade.trade_price
            if trade.direction == Direction.BUY:
                pos.position = trade.trade_volume
            elif trade.direction == Direction.SELL:
                pos.position = -trade.trade_volume
            else:
                raise Exception(f'下单方向有问题{trade.direction}')
        # print(f'处理完后的仓位是-{pos}')

    def cal_unrealized(self, tick):
        for pi in self.holdings:
            if pi.ticker == tick.ticker:
                # 没办法,因为获取不了 tick 的 exchange 信息,所以无法直接用 get_holding
                pi.append_clear(tick)

    def get_total_market_value(self):
        total_market_value = 0
        for pi in self.holdings:
            total_market_value += pi.get_market_value()
        return total_market_value

    def __str__(self):
        msg = '<'
        for pi in self.holdings:
            msg += ' {}\n'.format(pi)
        msg += '>'
        return msg

class TransferRequest:
    # transfer 也需要改写一下,因为之前是直接转账一个 PosItem,但现在转的是 PosItem 中的margin(直接默认这两个 margin 相同吧)
    # 所以参数的 ticker 需要改为 from_ticker 和 to_ticker
    def __init__(self, **kwds):
        self.transfer_id = kwds.get('transfer_id')
        self.from_ticker = kwds.get('from_ticker')
        self.to_ticker = kwds.get('to_ticker')
        self.asset_type = kwds.get('asset_type', AssetType.NOT_AVAILABLE)
        self.from_exchange = kwds.get('from_exchange')
        self.to_exchange = kwds.get('to_exchange')
        self.volume = kwds.get('volume')
        self.source = kwds.get('source')
        self.err_msg = kwds.get('err_msg')

    def __str__(self):
        return f'<Transfer id={self.transfer_id} from_ticker={self.from_ticker} to_ticker={self.to_ticker} at={AssetType.read(self.asset_type)} from_exchange={self.from_exchange} to_exchange' \
               f'={self.to_exchange} volume={self.volume} source={self.source}>'




if __name__ == '__main__':
    print(PositionInfo.FEE_RATE)