from persianBrokers import utils
import json
import logging
logger=logging.getLogger()




def get_stocks():
    url = "https://core.tadbirrlc.com//StocksHandler.ashx?%7B%22Type%22:%22ALL21%22,%22la%22:%22Fa%22%7D&jsoncallback="
    response = utils.request(method="GET", url=url)
    response = utils.convert_json(response)
    clean_data = []
    for item in response:
        data = {'symbol': item['sf'], 'company': item['cn'], 'isin': item['nc']}
        clean_data.append(data)  
    return clean_data


def buy(isin,order_count,order_price):
    url = "https://api3.mobinsb.ir/web/v1/Order/Post"

    payload = json.dumps({
        "orderCount": order_count,
        "orderPrice": order_price,
        "FinancialProviderId": 1,
        "isin": isin,
        "orderSide": 65,
        "orderValidity": 74,
        "orderValiditydate": "",
        "maxShow": 0,
        "orderId": 0
    })
    headers = {
        'Authorization': F'BasicAuthentication {utils.give_token()}',
        'Content-Type': 'application/json',
    }

    response = utils.request(method="POST", url=url, headers=headers, data=payload)
    response= utils.convert_json(response)
    logger.info(f"buy request sent successfully, {isin}, order price {order_price}, order count {order_count}: {response}")
    return response['IsSuccessfull']
    

def sell(isin,order_count,order_price):
  
    url = "https://api3.mobinsb.ir/web/v1/Order/Post"

    payload = json.dumps({
        "orderCount": order_count,
        "orderPrice": order_price,
        "FinancialProviderId": 1,
        "isin": isin,
        "orderSide": 86,
        "orderValidity": 74,
        "orderValiditydate": "",
        "maxShow": 0,
        "orderId": 0
    })
    headers = {

        'Authorization': F'BasicAuthentication {utils.give_token()}',
        'Content-Type': 'application/json',
    }

    response = utils.request(method="POST", url=url, headers=headers, data=payload)
    response= utils.convert_json(response)
    logger.info(f"sell request sent successfully, {isin}, order price {order_price}, order count {order_count}: {response}")
    return response['IsSuccessfull']

def get_detail(isin):
        
    url = F"https://core.tadbirrlc.com//StockFutureInfoHandler.ashx?%7B%22Type%22:%22getLightSymbolInfoAndQueue%22,%22la%22:%22Fa%22,%22nscCode%22:%22{isin}%22%7D&jsoncallback="
    
    response = utils.request(method="GET", url=url)
    response = utils.convert_json(response)
    data = {'symbol': response['symbolinfo']['ect'], 'company': response['symbolinfo']['est'], 'isin': response['symbolinfo']['nc'],
        'tomorrow-high': response['symbolinfo']['th'] , 'tomorrow-low': response['symbolinfo']['tl']}
            
    return data

def open_order():
    url = "https://api3.mobinsb.ir/Web/V1/Order/GetOpenOrder/OpenOrder"

    headers = {

        'Authorization': F'BasicAuthentication {utils.give_token()}',
    }
    response = utils.request(method="GET", url=url, headers=headers)
    response = utils.convert_json(response)
    clean_data = []
    for item in response['Data']:
        data = {'symbol': item['symbol'], 'company': item['cn'], 'isin': item['nsccode'], 'time':item['time'],
        'date':item['dtime'], 'order price':item['orderprice'], 'orderid':item['orderid'], 'orderside':item['orderside'],
        'qunatity':item['qunatity'],'status':item['status']}
        clean_data.append(data)  
    return clean_data
    

