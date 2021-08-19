from .constant import OrderStatus, ExecRole, ExchangeID, Direction, OrderType, AssetType, PosiDirection
from collections import deque
import numpy as np
import yaml
import dataclasses

class TickerInfo:

    def __init__(self):
        self.loc = 0
        self.file = ' '
        self.file_reader_time = 0
        self.df = ' '
        self.len = 0
        self.file_end_time = 0

class Sell():
    def __init__(self, ticker, volume):
        self.ticker = ticker
        self.volume = volume

class Tick:

    def __init__(self, **kwds):
        self.ticker = kwds.get('ticker')
        self.up_limit = kwds.get('up_limit')
        self.down_limit = kwds.get('down_limit')
        self.last_price = kwds.get('last_price')
        self.mkt_time = kwds.get('mkt_time') # datetime
        self.bid_price1 = kwds.get('bid_price1')
        self.ask_price1 = kwds.get('ask_price1')
        self.bid_volume1 = kwds.get('bid_volume1')
        self.ask_volume1 = kwds.get('ask_volume1')
        self.bid_price2 = kwds.get('bid_price2')
        self.ask_price2 = kwds.get('ask_price2')
        self.bid_volume2 = kwds.get('bid_volume2')
        self.ask_volume2 = kwds.get('ask_volume2')
        self.bid_price3 = kwds.get('bid_price3')
        self.ask_price3 = kwds.get('ask_price3')
        self.bid_volume3 = kwds.get('bid_volume3')
        self.ask_volume3 = kwds.get('ask_volume3')
        self.bid_price4 = kwds.get('bid_price4')
        self.ask_price4 = kwds.get('ask_price4')
        self.bid_volume4 = kwds.get('bid_volume4')
        self.ask_volume4 = kwds.get('ask_volume4')
        self.bid_price5 = kwds.get('bid_price5')
        self.ask_price5 = kwds.get('ask_price5')
        self.bid_volume5 = kwds.get('bid_volume5')
        self.ask_volume5 = kwds.get('ask_volume5')

    def __str__(self):
        return '<Tick ticker={} tm={} b1={} a1={} b1v={} a1v={} last_price={}>'.format(
            self.ticker, self.mkt_time.strftime('%Y%m%d-%H:%M:%S.%f'),
            self.bid_price1, self.ask_price1, self.bid_volume1, self.ask_volume1, self.last_price
        )

class Order:

    def __init__(self, **kwds):
        self.order_id = kwds.get('order_id')
        self.exchange = kwds.get('exchange', ExchangeID.NOT_AVAILABLE)
        self.ticker = kwds.get('ticker')
        self.asset_type = kwds.get('asset_type', AssetType.NOT_AVAILABLE)
        self.direction = kwds.get('direction', Direction.NOT_AVAILABLE)
        self.order_type = kwds.get('order_type', OrderType.NOT_AVAILABLE)
        self.price = kwds.get('price') # price is None means order_type has to be MARKET
        self.volume = kwds.get('volume')
        self.source = kwds.get('source')
        self.err_msg = kwds.get('err_msg')
        self.status = kwds.get('status', OrderStatus.NOT_AVAILABLE)

    def __str__(self):
        return '<Order id={} ticker={} direction={} ot={} at={} ex={} price={} volume={} source={} err_msg={}>'.format(
            self.order_id, self.ticker, Direction.read(self.direction), OrderType.read(self.order_type),
            AssetType.read(self.asset_type), ExchangeID.read(self.exchange), self.price, self.volume, self.source, self.err_msg
        )


class Trade:

    def __init__(self, **kwds):
        self.order_id = kwds.get('order_id')
        self.exchange = kwds.get('exchange', ExchangeID.NOT_AVAILABLE)
        self.ticker = kwds.get('ticker')
        self.asset_type = kwds.get('asset_type', AssetType.NOT_AVAILABLE)
        self.direction = kwds.get('direction', Direction.NOT_AVAILABLE)
        self.trade_price = kwds.get('trade_price')
        self.trade_volume = kwds.get('trade_volume')
        self.exec_role = kwds.get('exec_role', ExecRole.NOT_AVAILABLE)
        self.trade_id = kwds.get('trade_id')
        self.source = kwds.get('source')
        self.time = kwds.get('time','')

    def __str__(self):
        return f'<Trade id={self.trade_id} exchange={ExchangeID.read(self.exchange)} ticker={self.ticker} direction={Direction.read(self.direction)} at={AssetType.read(self.asset_type)} ' \
               f'price={self.trade_price} volume={self.trade_volume} source={self.source} role={ExecRole.read(self.exec_role)} order_id={self.order_id} time={self.time}>'

    def save_trade(self):
        return {'id'        :   self.trade_id,
                'exchange'  :   ExchangeID.read(self.exchange),
                'ticker'    :   self.ticker,
                'direction' :   self.direction,
                'asset_type':   self.asset_type,
                'price'     :   self.trade_price,
                'volume'    :   self.trade_volume,
                'time'      :   self.time}

class BacktestKey:

    def __init__(self, **kwds):
        self.str_name   = kwds.get('strategy_name')
        self.factor     = kwds.get('factor')
        self.pool       = kwds.get('pool')
        self.longshort  = kwds.get('longshort')
        self.top        = kwds.get('top')
        self.period     = kwds.get('period')
        self.buy_price  = kwds.get('buy_price')
        self.sell_price = kwds.get('sell_price')
        self.fee        = kwds.get('fee')
        self.start      = kwds.get('start')
        self.end        = kwds.get('end')
        self.vwap_limit = kwds.get('vwap_limit')

    def key(self):
        return f'{self.str_name} {self.factor} {self.pool} {self.longshort} {self.top} {self.period} {self.buy_price} ' \
               f'{self.sell_price} {self.fee} {self.start} {self.end} {self.vwap_limit}'





class TransferRequest:

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
        return f'<Transfer id={self.transfer_id} from_ticker={self.from_ticker}  to_ticker={self.to_ticker} at={AssetType.read(self.asset_type)} from={self.from_exchange} ' \
               f'to={self.to_exchange} volume={self.volume} source={self.source}>'


class PosItem:

    def __init__(self, **kwds):
        self.exchange = kwds.get('exchange', ExchangeID.NOT_AVAILABLE)
        self.ticker = kwds.get('ticker')
        self.asset_type = kwds.get('asset_type', AssetType.NOT_AVAILABLE)
        self.posi_direction = kwds.get('posi_direction', PosiDirection.NET)
        self.frozen = kwds.get('frozen', 0)
        self.position = kwds.get('position', 0)
        self.yd_position = kwds.get('yd_position', 0)
        self.to_transfer = kwds.get('to_transfer', 0)
        self.fee_rate_type = kwds.get('fee_rate_type')
        self.avg_cost = kwds.get('avg_cost', 0)
        # 以下两项只有当asset_type是FUTURE_MARGIN时候才有
        self.realized_margin = kwds.get('realized_margin', 0)
        self.unrealized_margin = kwds.get('unrealized_margin', 0)
        self.time = kwds.get('time','')
        # 如果这是期货合约的话,还需要标注不同保证金,因为即使同样是BTC.USD合约,用BTC结算和USDT结算都应该算作不同的合约
        # 如果这posItem是保证金的话,为了计算它的Unrealized_margin,需要把最近一段时间的价格都存进来算平均(防止插针爆仓)
        # 储存这个价格序列好像也就只有在这作为这个合约posItem的attribute比较合适了
        self.margin = kwds.get('margin')
        self.cal_unrealized_len = 0
        self.clear_prices = None
        self.mean_price = 0
        self.leverage = 0

    def get_price_ticker(self):
        # todo: based on different asset type,
        #   we should use different price
        return self.ticker

    def get_market_value(self, last_price=None):
        if self.asset_type == AssetType.CRYPTO_CONTRACT_MARGIN:
            return self.realized_margin + self.unrealized_margin
        else:
            return self.position * last_price * (-1 if self.posi_direction is PosiDirection.SHORT else 1)

    def transfer(self, volume):
        if self.asset_type == AssetType.CRYPTO_CONTRACT_MARGIN:
            if self.realized_margin + self.unrealized_margin - self.frozen - self.to_transfer >= volume:
                self.realized_margin -= volume
                self.to_transfer += volume
                return True
        if self.position - self.frozen - self.to_transfer >= volume:
            self.position -= volume
            self.to_transfer += volume
            return True
        else:
            return False

    def switch_day(self):
        self.yd_position = self.position

    def init_margin(self, pi):
        # 如果当前item是个contract,在此设定这个contract对应的margin
        self.margin = pi
        self.cal_unrealized_len = 100
        self.clear_prices = deque(maxlen=self.cal_unrealized_len)
        self.mean_price = 0

    def append_clear(self, tick):
        self.clear_prices.append((tick.ask_price1 + tick.bid_price1) / 2)
        self.mean_price = np.mean(self.clear_prices)
        if self.position != 0:
            self.margin.unrealized_margin = self.position * PositionInfo.CONTRACT_SIZES[ExchangeID.read(self.exchange)] * (1 / self.avg_cost - 1 / self.mean_price)
            self.leverage = abs(self.position * PositionInfo.CONTRACT_SIZES[ExchangeID.read(self.exchange)] / self.mean_price) / (self.margin.realized_margin + self.margin.unrealized_margin)

    def __str__(self):
        return '<PosItem ex={} ticker={} at={} d={} pos={} yd={} trans={} margin={} time={}>'.format(
            ExchangeID.read(self.exchange), self.ticker, AssetType.read(self.asset_type),
            PosiDirection.read(self.posi_direction), self.position, self.yd_position, self.to_transfer, self.margin, self.time
        )

class PositionInfo:

    # path1 = '../python/config'
    # path2 = './config'
    # try:
    #     with open(f'{path1}/fee_rate.yml', 'r') as f:
    #         FEE_RATE = yaml.safe_load(f)
    #     with open(f'{path1}/contract_sizes.yml', 'r') as f:
    #         CONTRACT_SIZES = yaml.safe_load(f)
    # except:
    #     with open(f'{path2}/fee_rate.yml', 'r') as f:
    #         FEE_RATE = yaml.safe_load(f)
    #     with open(f'{path2}/contract_sizes.yml', 'r') as f:
    #         CONTRACT_SIZES = yaml.safe_load(f)


    def __init__(self, **kwds):
        # 不同交易所不同同币种手续费率都不一样,因此在这更合适的方法是将手续费率用config形式读入,需要新的交易币种交易方式在此添加即可

        self.cash = kwds.get('cash', PosItem())
        _holdings = kwds.get('holdings', [])
        self.holdings = []
        self._tick_idx = {}
        self.stock_buy_fee  =  self.FEE_RATE['STOCK']['BUYFEE']
        self.stock_sell_fee =  self.FEE_RATE['STOCK']['SELLFEE']
        for pi in _holdings:
            self.create_holding(pi)
        # 把合约与对应保证金的关系在这里明确好
        for pi in _holdings:
            if pi.asset_type == AssetType.CRYPTO_COIN_MARGIN_CONTRACT:
                pi.init_margin(self.get_holding(ticker=pi.margin, exchange=pi.exchange))

    def get_holding(self, ticker, exchange=ExchangeID.NOT_AVAILABLE):
        idx = self._tick_idx.get((ticker, exchange))
        return None if idx is None else self.holdings[idx]

    def create_holding(self, pos_item):
        self.holdings.append(pos_item)
        self._tick_idx[(pos_item.ticker, pos_item.exchange)] = len(self.holdings) - 1

    @staticmethod
    def get_commission(trade, pos):
        rate = PositionInfo.FEE_RATE[ExchangeID.read(trade.exchange)][AssetType.read(trade.asset_type)][pos.fee_rate_type][-1][ExecRole.read(trade.exec_role)]
        commission = rate * trade.trade_volume * PositionInfo.CONTRACT_SIZES[ExchangeID.read(trade.exchange)] / trade.trade_price
        return commission

    def process_trade(self, trade):

        if trade.asset_type >= AssetType.CRYPTO_ASSET:
            # 只处理倒数合约情况
            pos = self.get_holding(ticker=trade.ticker, exchange=trade.exchange)
            margin_pos = pos.margin
            if pos is None:
                pos = PosItem(exchange=trade.exchange, ticker=trade.ticker, asset_type=trade.asset_type)
                self.create_holding(pos)
            if pos.position < 0:
                if trade.direction == Direction.SELL:
                    new_position = pos.position - trade.trade_volume
                    pos.avg_cost = new_position / (pos.position / pos.avg_cost - trade.trade_volume / trade.trade_price)
                    pos.position = new_position
                    margin_pos.realized_margin -= self.get_commission(trade, pos)
                elif trade.direction == Direction.BUY:
                    if trade.trade_volume + pos.position > 0:
                        margin_pos.realized_margin -= self.get_commission(trade, pos)
                        margin_pos.realized_margin += pos.position * PositionInfo.CONTRACT_SIZES[ExchangeID.read(trade.exchange)] * ((1 / pos.avg_cost) - (1 / trade.trade_price))
                        pos.position += trade.trade_volume
                        pos.avg_cost = trade.trade_price
                    else:
                        pos.position += trade.trade_volume
                        margin_pos.realized_margin += trade.trade_volume * PositionInfo.CONTRACT_SIZES[ExchangeID.read(trade.exchange)] * ((1 / trade.trade_price) - (1 / pos.avg_cost)) \
                            - self.get_commission(trade, pos)
            elif pos.position > 0:
                if trade.direction == Direction.BUY:
                    new_position = pos.position + trade.trade_volume
                    pos.avg_cost = new_position / (pos.position / pos.avg_cost + trade.trade_volume / trade.trade_price)
                    pos.position = new_position
                    margin_pos.realized_margin -= self.get_commission(trade, pos)
                elif trade.direction == Direction.SELL:
                    if pos.position - trade.trade_volume < 0:
                        margin_pos.realized_margin -= self.get_commission(trade, pos)
                        margin_pos.realized_margin += pos.position * PositionInfo.CONTRACT_SIZES[ExchangeID.read(trade.exchange)] * ((1 / pos.avg_cost) - (1 / trade.trade_price))
                        pos.position -= trade.trade_volume
                        pos.avg_cost = trade.trade_price
                    else:
                        pos.position -= trade.trade_volume
                        margin_pos.realized_margin += trade.trade_volume * PositionInfo.CONTRACT_SIZES[ExchangeID.read(trade.exchange)] * ((1 / pos.avg_cost) - (1 / trade.trade_price)) - \
                            self.get_commission(trade, pos)
            else:
                margin_pos.realized_margin -= self.get_commission(trade, pos)
                pos.avg_cost = trade.trade_price
                if trade.direction == Direction.BUY:
                    pos.position = trade.trade_volume
                elif trade.direction == Direction.SELL:
                    pos.position = -trade.trade_volume
            return
        else:
            pos = self.get_holding(ticker=trade.ticker, exchange=trade.exchange)
            if pos is None:
                pos = PosItem(exchange=trade.exchange, ticker=trade.ticker,
                            asset_type=trade.asset_type)
                self.create_holding(pos)
            pos.position += trade.trade_volume if trade.direction == Direction.BUY else - trade.trade_volume
            if pos.asset_type in [AssetType.STOCK]:
                trade_amount = trade.trade_volume * trade.trade_price
                if trade.direction == Direction.BUY:
                    trade_amount = -trade_amount * ( 1 + self.stock_buy_fee)
                else:
                    trade_amount = trade_amount * (1 - self.stock_sell_fee)
                self.cash.position += trade_amount
            # todo: as contract or futures, we should make cash into margin or frozen
            # some logic needs to be confirmed

    def init_transfer(self, transfer):
        from_pos = self.get_holding(ticker=transfer.from_ticker, exchange=transfer.from_exchange)  # 就不担心出现position 比要转的 volume 低的情况吗?下面的 from_pos.transfer检查了
        return False if from_pos is None else from_pos.transfer(transfer.volume)

    def confirm_transfer(self, transfer):
        from_pos = self.get_holding(ticker=transfer.from_ticker, exchange=transfer.from_exchange)
        from_pos.to_transfer -= transfer.volume
        to_pos = self.get_holding(ticker=transfer.to_ticker, exchange=transfer.to_exchange)
        if to_pos is None:
            to_pos = PosItem(exchange=transfer.to_exchange, ticker=transfer.to_ticker, asset_type=transfer.asset_type)
            self.create_holding(to_pos)
        to_pos.realized_margin += transfer.volume

    def process_tick(self, tick):
        # 如果有仓位需要在每个tick之后进行处理的都在此处理
        # 例如对于期货合约,每个tick之后要计算即时保证金的变化,就放在这
        for pi in self.holdings:
            if pi.ticker == tick.ticker:
                if pi.asset_type == AssetType.CRYPTO_COIN_MARGIN_CONTRACT:
                    # 对于期货,需要每个tick结束后计算它的unrealized_margin
                    pi.append_clear(tick)

    def get_total_market_value(self):
        total_market_value = 0
        for pi in self.holdings:
            total_market_value += pi.get_market_value()
        return total_market_value

    def __str__(self):
        msg = '<PositionInfo cash={} \n'.format(self.cash)
        for pi in self.holdings:
            msg += ' {}\n'.format(pi)
        msg += '>'
        return msg
