#####
# Used to load local lumibot folder into a venv
import os
import sys

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "/../")
#####

import logging
from datetime import datetime, timedelta
from time import time

import pandas as pd
from strategies.nic_strategy import NicBot
from twilio.rest import Client

from credentials import AlpacaConfig, InteractiveBrokersConfig, TwilioConfig
from lumibot.backtesting import (
    AlpacaBacktesting,
    AlphaVantageBacktesting,
    BacktestingBroker,
    PandasDataBacktesting,
    YahooDataBacktesting,
)
from lumibot.brokers import Alpaca, InteractiveBrokers
from lumibot.data_sources import PandasData
from lumibot.strategies.examples import (
    BuyAndHold,
    DebtTrading,
    Diversification,
    DiversifiedLeverage,
    FastTrading,
    IntradayMomentum,
    Momentum,
    Simple,
    Strangle,
)
from lumibot.tools import indicators
from lumibot.traders import Trader

# Choose your budget and log file locations
budget = 50000
logfile = "logs/test.log"
benchmark_asset = None

# Initialize all our classes
trader = Trader(logfile=logfile)

# Development: Minute Data
asset = "SPY"
df = pd.read_csv(f"data/{asset}_Minute_2021.csv")
df = df.set_index("time")
df.index = pd.to_datetime(df.index)
my_data = dict()
my_data[asset] = df
backtesting_start = datetime(2021, 8, 8)
backtesting_end = datetime(2021, 8, 14)

####
# Select our strategy
####

pandas = PandasData(my_data)
broker = BacktestingBroker(pandas)

strategy_name = "NicBot"

####
# Backtest
####

datestring = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
stats_file = f"logs/{strategy_name}_{datestring}.csv"
plot_file = f"logs/{strategy_name}_{datestring}.jpg"
trades_file = f"logs/{strategy_name}_trades_{datestring}.csv"

NicBot.backtest(
    strategy_name,
    budget,
    PandasDataBacktesting,
    backtesting_start,
    backtesting_end,
    stats_file=stats_file,
    trades_file=trades_file,
    plot_file=plot_file,
    config=AlpacaConfig,
    pandas_data=my_data,
    symbol=asset,
)

####
# Run the strategy
####

broker = Alpaca(AlpacaConfig)
strategy = NicBot(
    name=strategy_name,
    budget=budget,
    broker=broker,
)
trader.add_strategy(strategy)
trader.run_all()
