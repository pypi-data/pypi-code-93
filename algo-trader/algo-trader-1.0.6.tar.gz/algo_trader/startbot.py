import argparse
import pickle
import sys
import os

settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "settings")


def run():
    # entrypoint
    pass


class BrokerSettings:
    token = ''
    api_key = ''
    api_secret = ''
    symbols = []


class Symbol():
    def __init__(self, name, position_size=1, last_order_id=''):
        self.name = name
        self.position_size = position_size
        self.last_order_id = last_order_id


def bot_settings(symbols=['XBTUSD'], strategy='lotus', broker='bitmex'):
    settings_name = '{}_{}_settings.pickle'.format(broker, strategy)
    setting_path = os.path.join(settings_path, settings_name)
    if os.path.exists(setting_path):
        symbol_exists = []
        settings = pickle.load(open(setting_path, 'rb'))
        for symbol, i in enumerate(symbols):
            symbol_exists.append(False)
            for _symbol in settings.symbols:
                if _symbol.name == symbol:
                    symbol_exists[i] = True
        if all(symbol_exists):
            return settings
    print('Bot settings are not available. Please start the Bot in terminal first to set settings.', flush=True)
    sys.exit()


def file_create_input(check_exist=True, symbols=['XBTUSD'], broker='bitmex', strategy='lotus'):
    setting_name = '{}_{}_settings.pickle'.format(broker, strategy)
    setting_path = os.path.join(settings_path, setting_name)
    if check_exist and os.path.exists(setting_path):
        settings = pickle.load(open(setting_path, 'rb'))
        return check_settings(settings)
    else:
        token = input(
            "Submit your Strategytoken (found in your member area): ")
        api_key = input("Submit your " + broker + " API Key (ID): ")
        api_secret = input("Submit your " + broker + " API Secret: ")
        symbol_settings = []
        for symbol in symbols:
            pos_size = input(
                "Choose your Position Size for {} per trade in %: ".format(symbol))
            pos_size = check_pos_size(pos_size)
            symbol_settings.append(Symbol(name=symbol, position_size=pos_size))
        return make_pickle_file(settings_path, settings_name, token, api_key, api_secret, symbol_settings)


def position_symbol_sizes(symbols):
    output = ''
    for symbol in symbols:
        output += '\n\t{} Position Size: {} %\n\n'.format(
            symbol['name'], symbol['position_size'])
    return output


def check_settings(settings, broker):
    while True:
        qr = input("Start Algo Trader Bot with"
                   "\n\tBroker: " + broker +
                   "\n\tToken: {}..."
                   "\n\tAPI ID: {}"
                   "\n\tAPI Secret: ...{}"
                   "{}"
                   "Do you want to continue? ['y' for yes, 'n' for no, 'c' for"
                   " change settings] "
                   .format(settings.token[:4], settings.api_key, settings.api_secret[-4:], position_symbol_sizes(settings.symbols)))
        if qr == '' or qr[0].lower() not in ['y', 'n', 'c']:
            print("'y' for yes, 'n' for no or 'c' for "
                  "change settings (you don't have to write '').")
        elif qr[0].lower() == 'c':
            return file_create_input(check_exist=False)
        else:
            answer = qr[0].lower()
            if answer == 'y':
                return settings
            else:
                print("Shutting down...")
                sys.exit()


def check_pos_size(pos_size, max_position_size=10):
    try:
        float(pos_size)
    except ValueError:
        new_size = input("Position Size is not a number,"
                         " please type it in again: ")
        return check_pos_size(new_size, max_position_size=max_position_size)
    if float(pos_size) > max_position_size:
        new_size = input("Position Size is over " + str(max_position_size) +
                         " %, please type in a lower size: ")
        return check_pos_size(new_size, max_position_size=max_position_size)
    return pos_size


def make_pickle_file(filepath, filename, token, api_key, api_secret, symbol_settings):
    settings = BrokerSettings
    settings.token = token
    settings.api_key = api_key
    settings.api_secret = api_secret
    for setting in symbol_settings:
        settings.symbols.append(setting)
    pickle.dump(settings, file=open(os.path.join(filepath, filename), 'wb'))
    return settings


parser = argparse.ArgumentParser()
parser.add_argument(
    'run', help='You have to say algotrader to \'run\' on symbol(s) and a broker to trade on.')
parser.add_argument(
    'symbol', help='Define on which Symbol to trade. E.g.: BTCUSD for Bitcoin vs Dollar. Multiple Symbols f.e. btc,eth with comma seperation.'
)
parser.add_argument(
    'broker', help='Define on which broker to run the strategy')
parser.add_argument('-strategy', nargs='?', default='lotus')
parser.add_argument('start', nargs='?', default='')

args = parser.parse_args()

if args.run in ['run', 'Run', 'RUN']:
    testnet = True
    broker = ''
    if args.broker in ['bitmex_testnet', 'bitmextestnet', 'Bitmextestnet', 'Bitmex-Testnet', 'bitmex-testnet']:
        broker = 'bitmex_testnet'
    elif args.broker in ['bitmex', 'bitmex_live', 'Bitmex', 'Bitmex-Live', 'bitmex-live']:
        testnet = False
        broker = 'bitmex'
    else:
        print('This broker is not supported.')
        sys.exit()

    symbols = []
    for symbol in args.symbol.split(','):
        if args.symbol in ['BTCUSD', 'Bitcoin', 'bitcoin', 'XBTUSD', 'BTC', 'btc', 'btcusd']:
            symbols.append('XBTUSD')
        if args.symbol in ['ETHUSD', 'Ethereum', 'ethereum', 'ETH', 'eth', 'ethusd']:
            symbols.append('ETHUSD')
    if not symbols:
        print("No recognizable Symbol found. Supported are 'ETHUSD' and 'BTCUSD'.")
        sys.exit()

    if args.start == 'start':  # start without input prompt
        start_settings = bot_settings(symbols=symbols, broker=broker, strategy=args.strategy)
    else:
        start_settings = file_create_input(
            symbols=symbols, broker=broker, strategy=args.strategy)

    setting_file_name = '{}_{}_settings.pickle'.format(broker, args.strategy)

    if args.strategy == 'lotus' and broker in ['bitmext_testnet', 'bitmex']:
        from algo_trader.strategies import Lotus
        from algo_trader.clients import BitmexClient

        client = BitmexClient(api_key=start_settings.api_key, api_secret=start_settings.api_secret, test=testnet)
        lotus = Lotus(client, symbols, token=start_settings.token, pos_size=start_settings.position_size, testnet=testnet, settings_file_name=setting_file_name)
        lotus.run()
    
    """
    any custom made strategy has to be run with the -strategy <strategy name> argument.
    You have to create a new strategy class in /strategies folder to run it.
    """
else:
    print("Sorry, your entries were not matched with a valid symbol and broker. You need to input e.g. 'algotrader run btcusd bitmex_testnet' to run the Algo Trader Bot.")
