import boto3
import json
import decimal
from pprint import pprint

TABLE_NAME = 'backtest_report'
backtest_Table = boto3.resource('dynamodb').Table(TABLE_NAME)

def decimal_form(number):
    return decimal.Decimal(number).quantize(decimal.Decimal("0.0000"))

def float_form(number):
    return float(number)

def recursion_decimal_dict(dic):
    for key in dic:
        if isinstance(dic[key], dict):
            recursion_decimal_dict(dic[key])
        else:
            if isinstance(dic[key], list):
                if isinstance(dic[key][1], float):
                    dic[key] = [ decimal_form(_) for _ in dic[key] ]
            elif isinstance(dic[key], float):
                dic[key] = decimal_form(dic[key])
            else:
                pass
    return dic

def backtest_result_to_dynamodb(data):
    data = recursion_decimal_dict(data)
    backtest_Table.put_item(Item=data, ReturnConsumedCapacity='TOTAL')

