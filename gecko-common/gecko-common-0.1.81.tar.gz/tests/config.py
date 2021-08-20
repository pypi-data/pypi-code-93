import os


class Huobi:
    API_KEY = os.environ.get("huobi_main_api_key")
    API_SECRET = os.environ.get("huobi_main_api_secret")


class Binance:
    API_KEY = os.environ.get("binance_quant_api_key")
    API_SECRET = os.environ.get("binance_quant_api_secret")


class Okex:
    API_KEY = os.environ.get("okex_simulated_api_key")
    API_SECRET = os.environ.get("okex_simulated_api_secret")
    API_PASSPHRASE = os.environ.get("okex_simulated_api_passphrase")
