import argparse
import pickle
import sys
import os

settings_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "settings")

settings_file_name = ''
broker_name = ''


def run():
    # entrypoint
    pass


class Settings:
    token = ''
    api_key = ''
    api_secret = ''
    position_size = 0
    last_order_id = ''

start_settings = Settings()

def file_create_input(check_exist=True, start=False):
    setting_path = os.path.join(settings_path, settings_file_name)
    if check_exist and os.path.exists(setting_path):
        settings = pickle.load(open(setting_path, 'rb'))
        check_settings(settings.token, settings.api_key,
                       settings.api_secret, settings.position_size, start=start)
    else:
        token = input(
            "Submit your Strategytoken (found in your member area): ")
        api_key = input("Submit your " + broker_name + " API Key (ID): ")
        api_secret = input("Submit your " + broker_name + " API Secret: ")
        pos_size = input("Choose your Position Size per trade in %: ")
        pos_size = check_pos_size(pos_size)
        make_pickle_file(settings_path, settings_file_name,
                         token, api_key, api_secret, pos_size)
        check_settings(token, api_key, api_secret, pos_size, start=start)


def check_settings(token, api_key, api_secret, position_size, start=False):
    if start:
        start_settings.token = token
        start_settings.api_key = api_key
        start_settings.api_secret = api_secret
        start_settings.position_size = position_size
    else:
        while True:
            qr = input("Start Algo Trader Bot with"
                    "\n\tBroker: " + broker_name +
                    "\n\tToken: {}..."
                    "\n\tAPI ID: {}"
                    "\n\tAPI Secret: ...{}"
                    "\n\tPosition Size: {} %\n\n"
                    "Do you want to continue? ['y' for yes, 'n' for no, 'c' for"
                    " change settings] "
                    .format(token[:4], api_key, api_secret[-4:], position_size))
            if qr == '' or qr[0].lower() not in ['y', 'n', 'c']:
                print("Please answer with 'y' for yes, 'n' for no or 'c' for "
                    "change settings (you don't have to write '').")
            elif qr[0].lower() == 'c':
                return file_create_input(check_exist=False)
            else:
                answer = qr[0].lower()
                if answer == 'y':
                    start_settings.token = token
                    start_settings.api_key = api_key
                    start_settings.api_secret = api_secret
                    start_settings.position_size = position_size
                    return
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


def make_pickle_file(filepath, filename, token, api_key, api_secret, position_size):
    settings = Settings()
    settings.token = token
    settings.api_key = api_key
    settings.api_secret = api_secret
    settings.position_size = position_size
    pickle.dump(settings, file=open(os.path.join(filepath, filename), 'wb'))


parser = argparse.ArgumentParser()
parser.add_argument(
    'run', help='You have to say algotrader to \'run\' + symbol to trade and broker to trade on.')
parser.add_argument(
    'symbol', help='Define on which Symbol to trade. E.g.: BTCUSD for Bitcoin vs Dollar'
)
parser.add_argument(
    'broker', help='Define on which broker to run the strategy')
parser.add_argument('start', nargs='?', default='')

args = parser.parse_args()

if args.run in ['run', 'Run', 'RUN']:
    symbol = ''
    if args.symbol in ['BTCUSD', 'Bitcoin', 'bitcoin', 'XBTUSD', 'BTC', 'btc']:
        symbol = 'XBTUSD'
    elif args.symbol in ['ETHUSD', 'Ehtereum', 'ETH', 'eth']:
        symbol = 'ETHUSD'
    else:
        print('This symbol can\'t be traded with the the Algo Trader Bot.')
        sys.exit()

    testnet = True
    broker = ''
    if args.broker in ['bitmex_testnet', 'bitmextestnet', 'Bitmextestnet', 'Bitmex-Testnet', 'bitmex-testnet']:
        broker = 'bitmex_testnet'
        broker_name = 'Bitmex Testnet'
    elif args.broker in ['bitmex', 'bitmex_live', 'Bitmex', 'Bitmex-Live', 'bitmex-live']:
        testnet = False
        broker = 'bitmex'
        broker_name = 'Bitmex Live'
    else:
        print('This broker is not supported.')
        sys.exit()

    settings_file_name = '{}_lotus_{}_settings.pickle'.format(broker, symbol)

    if args.start == 'start':
        file_create_input(start=True)
    else:
        file_create_input()

    from algo_trader.strategies import Lotus
    from algo_trader.clients import BitmexClient

    client = BitmexClient(symbol=symbol, api_key=start_settings.api_key,
                          api_secret=start_settings.api_secret, test=testnet)
    lotus = Lotus(client, token=start_settings.token, pos_size=start_settings.position_size,
                  testnet=testnet, settings_file_name=settings_file_name)
    lotus.run()
else:
    print("Sorry, your entries were not matched with a valid symbol and broker. You need to input e.g. 'algotrader run btcusd bitmex_testnet' to run the Algo Trader Bot.")
