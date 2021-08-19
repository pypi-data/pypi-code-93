import json
import boto3
import decimal
import os
import concurrent.futures
import time

def decimal_form(number):
    return decimal.Decimal(number).quantize(decimal.Decimal("0.0000"))

def recursion_decimal_dict(dic):
    for key in dic:
        if isinstance(dic[key], dict):
            recursion_decimal_dict(dic[key])
        else:
            if isinstance(dic[key], list):
                if isinstance(dic[key][1], float):
                    dic[key] = [ decimal_form(_) for _ in dic[key] ]
                elif isinstance(dic[key][0], dict):
                    dic[key] = [ recursion_decimal_dict(_) for _ in dic[key] ]
            
            elif isinstance(dic[key], float):
                dic[key] = decimal_form(dic[key])
                
                
            else:
                pass
    return dic

def process_bk_result_item(json_name:str='bk_20100101_500.json', folder:str='./'):
    bk_id = json_name.split('.')[0].split('_')[2]
    with open(folder+'/'+json_name,'r') as f:
        result_dic = json.load(f)
    result_dic['ef_id'] = bk_id
    return result_dic

def create_ef_table(version):
    bk_table_name = 'effective_frontier_bk' + '_v' + str(version)
    dynamodb = boto3.resource('dynamodb')
    dynamodb.create_table(
        TableName=bk_table_name,
        KeySchema=[
            {
                'AttributeName': 'ef_id',
                'KeyType': 'HASH' 
            }
            ],
        AttributeDefinitions=[
            {
                'AttributeName': 'ef_id',
                'AttributeType': 'S'
            }
        ],
        BillingMode='PAY_PER_REQUEST',
    )

def save_bk_item(ef_bk_table, json_name, folder, json_list):
    bk_table = boto3.resource('dynamodb').Table(ef_bk_table)
    bk_result = process_bk_result_item(json_name, folder)
    bk_result = recursion_decimal_dict(bk_result)
    bk_table.put_item(Item=bk_result)
    if json_list.index(json_name) % 1000 == 0:
        print(json_name)

def loop_save(version, folder):
    ef_bk_table = 'effective_frontier_bk' + '_v' + str(version)
    json_list = os.listdir(folder)
    j = json_list
    h = round(len(j) / 100 * 8.7 / 60 / 60, 1)
    print(f'cost {h} hours ')
    time0 = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        future_to_bti = {executor.submit(save_bk_item, ef_bk_table, json_name, folder, json_list): json_name for json_name in j}
        for future in concurrent.futures.as_completed(future_to_bti):
            bt_i = future_to_bti[future]
            try:
                data = future.result()
            except Exception as exc:
                print(f'{bt_i} generated an exception: {exc}')
            else:
                pass   
    time1 = time.time()
    print(time1 - time0)

if __name__ == "__main__":

    # inputs
    version = 0
    folder = './frontier_result'
    #create_ef_table(version)
    #loop_save(version, folder)

