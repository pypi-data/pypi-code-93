from statistics import mean, mode

from shameni import Gaze
from namari import Namari
from arkivist import Arkivist
from sometime import Sometime

class Wimby:
    def __init__(self, coins, aliased=False, debug=False):
        self.debug = False
        if isinstance(debug, bool):
            self.debug = debug
        if isinstance(aliased, bool):
            self.aliased = aliased
        self.aliases = []
        if aliased:
            self.aliases = _get_aliases(Gaze().supported())
        self.coins = _supported(coins, self.aliases, self.aliased, self.debug)
        self.momentum = Arkivist()
        self.movers = Arkivist()
    
    def analyze(self):
        self.momentum = _historical_averages(self.coins, self.debug)
        self.movers = _movements(self.momentum, self.debug)
    
    def add(self, coin):
        temp = self.coins.extend(coin)
        self.coins = _supported(temp, self.aliases, self.aliased, self.debug)
        
    
    def change(self, coins):
        self.coins = _supported(coins, self.aliases, self.aliased, self.debug)

    def reload(self):
        print("Wimby: Deprecated method, use analyze() instead.")
        self.analyze()
    
    def dump(self, yesterday=None):
        pass

def format_price(price):
    if price < 1:
        return f"{price:.8f}"
    if price < 10:
        return f"{price:,.6f}"
    return f"{price:,.2f}"

def _supported(coins, aliases, aliased, debug):
    supported = []
    if isinstance(coins, list):
        if aliased:
            if debug:
                print("Getting token aliases...")
            for coin in coins:
                alias = aliases.get(coin)
                if alias is not None:
                    supported.append(alias)
        else:
            return coins
    return list(set(supported))

def _movements(momentum, debug):
    if debug:
        print("Analyzing movements...")
    movers = Arkivist()
    for token, trends in momentum.items():
        price = trends.get("0", 0)
        wavg = trends.get("3", 0)
        if min(price, wavg) > 0:
            change = (price - wavg) / wavg
            tokens = movers.get(change, [])
            tokens.append(token)
            tokens = list(sorted(tokens))
            movers.set(str(change), tokens)
    return movers

def _historical_averages(coins, debug):
    if debug:
        print("Collecting periodic median prices...")
    momentum = Arkivist()
    prevailing = _prevailing(",".join(coins))
    periods = (90, 60, 30, 15, 7, 3, 1)
    for token in coins:
        trends = momentum.get(token, {})
        price = prevailing.get(token, {}).get("usd", 0)
        if price > 0:
            prices = {}
            pattern = []
            trends.update({"0": price})
            for days in periods:
                if len(prices) == 0:
                    prices = _prices(token, days=days)
                    low, high = min(prices), max(prices)
                    trends.update({"price_vs_min": (price - low)})
                    trends.update({"price_vs_max": (price - high)})
                    trends.update({"high": high})
                    trends.update({"low": low})
                wavg = trends.get(str(days), 0)
                if wavg <= 0:
                    wavg = _median_price(prices, days)
                if wavg > 0:
                    trends.update({str(days): wavg})
                    if price > wavg:
                        pattern.append("+")
                    else:
                        pattern.append("-")
                else:
                    pattern.append(" ")
            
            buy_score, sell_score = _scoring(pattern)
            trends.update({"trend": "".join(pattern)})
            trends.update({"buy": buy_score})
            trends.update({"sell": sell_score})
            momentum.set(token, trends)
    return momentum

def _scoring(pattern):
    buy_points = 0
    sell_points = 0
    for x in range(0, 7):
        index = 7 - (x+1)
        score = index+1
        if pattern[index] == "+":
            sell_points += score
        else:
            buy_points += score
    buy_score = buy_points / 28
    sell_score = sell_points / 28
    return (buy_score, sell_score)

def _prevailing(token):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={token}&vs_currencies=usd"
    return Arkivist().fetch(url)

def _prices(token, days=1):
    prices = {}
    root = Arkivist().fetch(f"https://api.coingecko.com/api/v3/coins/{token}/market_chart?vs_currency=usd&days={days}&interval=daily").show()
    for price in root.get("prices", []):
        prices.update({int((price[0] / 1000)): float(price[1])})
    return prices

def _median_price(dataset, days):
    dates = []
    prices = []
    limit = Sometime().add(days=-(days+1)).timestamp()
    for timestamp, price in dataset.items():
        date = Sometime(timestamp=int(timestamp)).custom("%Y-%m-%d")
        if date not in dates:
            if timestamp >= limit:
                prices.append(price)
                dates.append(date)
    
    if len(prices) > 0:
        if len(prices) > 2:
            prices = list(sorted(prices))
            median = 0
            count = len(prices)
            if ((count % 2) == 0):
                print(count, int((count/2)), int(((count/2)+1)))
                return ((prices[int((count/2))] + prices[int(((count/2)+1))]) / 2)
            print(count, (((count-1)/2)+1))
            return prices[int((((count-1)/2)+1))]
        else:
            return (sum(prices) / len(prices))
    return -1

def _get_aliases(supported):
    aliases = Namari()
    assets = Arkivist()
    for token in supported:
        asset = {}
        url = f"https://api.coingecko.com/api/v3/coins/{token}" \
            "?localization=false&tickers=false&market_data=false&community_data=false&developer_data=false&sparkline=false"
        data = Arkivist().fetch(url).show()
        if isinstance(data, list):
            if len(data) > 0:
                asset = data[0]
        
        aliases.set(token, token)
        aliases.attach(token, token.lower())
        aliases.attach(token, token.upper())
        aliases.attach(token, token.title())
        aliases.attach(token, token.capitalize())
        
        if len(asset) > 0:
            symbol = asset.get("symbol", token)
            aliases.attach(token, symbol)
            aliases.attach(token, symbol.lower())
            aliases.attach(token, symbol.upper())
            aliases.attach(token, symbol.title())
            aliases.attach(token, symbol.capitalize())
            
            name = asset.get("name", token)
            aliases.attach(token, name)
            aliases.attach(token, name.lower())
            aliases.attach(token, name.upper())
            aliases.attach(token, name.title())
            aliases.attach(token, name.capitalize())
    return aliases