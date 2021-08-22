import datetime
import json

import numpy as np
import pandas as pd
import requests


class oandacandle:
    def __init__(self, authorization, endpoint, sym, payload):
        self.authorization = authorization
        self.sym = sym
        self.endpoint = endpoint
        self.payload = payload

    def get(self):

        authorization = self.authorization
        endpoint = self.endpoint
        sym = self.sym
        payload = self.payload

        auth = {"Authorization": "Bearer " + authorization}
        url = endpoint + sym + "/candles"
        error = 0

        try:

            response = requests.get(url, params=payload, headers=auth)
            raw = response.json()
            data = json.dumps(raw, indent=2)
            dataset = pd.read_json(data)
            df = pd.json_normalize(dataset["candles"])
            del df["complete"]

            df["time"] = pd.to_datetime(df["time"]).dt.tz_localize(None)
            df.columns = ["vol", "time", "open", "high", "low", "close"]
            df1 = df[["time", "vol", "high", "low", "open", "close"]]

        except:

            error = 1
            df1 = pd.DataFrame()

        return df1, error


class oandaclose:
    def __init__(self, symbol, account, authorization, los, endpoint):

        self.symbol = symbol
        self.account = account
        self.authorization = authorization
        self.los = los
        self.endpoint = endpoint

    def closeposition(self):

        symbol = self.symbol
        account = self.account
        authorization = self.authorization
        los = self.los

        # Headers and Parameters
        url = self.endpoint + account + "/positions/" + symbol + "/close"
        auth = {
            "Authorization": "Bearer " + authorization,
            "Content-Type": "application/json",
        }

        if los == 0:
            order_details = {"shortUnits": "ALL"}
        else:
            order_details = {"longUnits": "ALL"}

        # Execute Position Close
        response = requests.put(
            url, headers=auth, data=json.dumps(order_details), timeout=5
        )

        if response.status_code == 200:
            close = 1

        else:

            # Position Not Found
            if response.status_code == 404:
                close = 1
            else:
                # WAIT
                print(
                    str(account)
                    + " - WAIT "
                    + str(los)
                    + " "
                    + symbol
                    + " : "
                    + str(response.status_code)
                )
                close = 8

        return close


class oandaorders:
    def __init__(
        self,
        account,
        authorization,
        price,
        stoploss,
        takeprofit,
        symbol,
        units,
        endpoint,
        ttl,
    ):

        self.account = account
        self.authorization = authorization
        self.price = price
        self.stoploss = stoploss
        self.takeprofit = takeprofit
        self.symbol = symbol
        self.units = units
        self.endpoint = endpoint
        self.ttl = ttl

    def postlimit(self):

        # Redundancy
        account = self.account
        authorization = self.authorization
        price = self.price
        stoploss = self.stoploss
        takeprofit = self.takeprofit
        symbol = self.symbol
        units = self.units
        endpoint = self.endpoint

        # Get TTL
        ts = datetime.datetime.now() + datetime.timedelta(seconds=int(self.ttl))
        ttl = round(ts.timestamp(), 2)

        if "JPY" in symbol:

            price = round(price, 2)
            risk_check = round(abs(stoploss), 2)
            profit_check = round(abs(takeprofit), 2)

        else:

            price = round(price, 4)
            risk_check = round(abs(stoploss), 4)
            profit_check = round(abs(takeprofit), 4)

        # Headers and Parameters
        url = endpoint + account + "/orders"
        auth = {
            "Authorization": "Bearer " + authorization,
            "Content-Type": "application/json",
        }

        order_details = {
            "order": {
                "price": str(price),
                "instrument": str(symbol),
                "units": str(units),
                "stopLossOnFill": {"timeInForce": "GTC", "distance": str(risk_check)},
                "takeProfitOnFill": {
                    "timeInForce": "GTC",
                    "distance": str(profit_check),
                },
                "timeInForce": "GTD",
                "gtdTime": str(ttl),
                "type": "LIMIT",
                "positionFill": "DEFAULT",
            }
        }

        # Execute Order
        response = requests.post(
            url, headers=auth, data=json.dumps(order_details), timeout=5
        )

        if response.status_code == 201:

            raw = response.json()
            data = json.dumps(raw, indent=2)
            dataset = json.loads(data)
            ticket = dataset["orderCreateTransaction"]["id"]
            print(
                str(account)
                + " - PLACED "
                + str(units)
                + " "
                + symbol
                + " : "
                + str(response.status_code)
            )

        else:

            print(
                str(account)
                + " - FAILED "
                + str(units)
                + " "
                + symbol
                + " : "
                + str(response.status_code)
            )
            ticket = np.nan
            raw = response.json()
            data = json.dumps(raw, indent=2)
            dataset = json.loads(data)
            reason = dataset["errorMessage"]
            print("LIMIT ORDER")
            print(str(reason))
            print(" ")

        return float(ticket)

    def postmarket(self):

        # Redundancy
        account = self.account
        authorization = self.authorization
        price = self.price
        stoploss = self.stoploss
        takeprofit = self.takeprofit
        symbol = self.symbol
        units = self.units
        endpoint = self.endpoint

        # Get TTL
        ts = datetime.datetime.now() + datetime.timedelta(seconds=int(self.ttl))
        ttl = round(ts.timestamp(), 2)

        if "JPY" in symbol:

            price = round(price, 2)
            risk_check = round(abs(stoploss), 2)
            profit_check = round(abs(takeprofit), 2)

        else:

            price = round(price, 4)
            risk_check = round(abs(stoploss), 4)
            profit_check = round(abs(takeprofit), 4)

        # Headers and Parameters
        url = endpoint + account + "/orders"
        auth = {
            "Authorization": "Bearer " + authorization,
            "Content-Type": "application/json",
        }

        order_details = {
            "order": {
                "priceBound": str(price),
                "instrument": str(symbol),
                "units": str(units),
                "stopLossOnFill": {"timeInForce": "GTC", "distance": str(risk_check)},
                "takeProfitOnFill": {
                    "timeInForce": "GTC",
                    "distance": str(profit_check),
                },
                "timeInForce": "FOK",
                "gtdTime": str(ttl),
                "type": "MARKET",
                "positionFill": "DEFAULT",
            }
        }

        # Execute Order
        response = requests.post(
            url, headers=auth, data=json.dumps(order_details), timeout=5
        )

        if response.status_code == 201:

            raw = response.json()
            data = json.dumps(raw, indent=2)
            dataset = json.loads(data)
            ticket = dataset["orderCreateTransaction"]["id"]
            print(
                str(account)
                + " - PLACED "
                + str(units)
                + " "
                + symbol
                + " : "
                + str(response.status_code)
            )

        else:

            print(
                str(account)
                + " - FAILED "
                + str(units)
                + " "
                + symbol
                + " : "
                + str(response.status_code)
            )
            ticket = np.nan
            raw = response.json()
            data = json.dumps(raw, indent=2)
            dataset = json.loads(data)
            reason = dataset["errorMessage"]
            print("MARKET ORDER")
            print(str(reason))
            print(" ")

        return float(ticket)
