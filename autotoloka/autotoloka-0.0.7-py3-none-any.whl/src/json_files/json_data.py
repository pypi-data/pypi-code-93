import os
import json

json_data = {}
for item in os.listdir('../autotoloka_test/json_files'):
    if item[-5:] == '.json':
        key = item
        with open(f'../autotoloka_test/json_files/{item}', 'r', encoding='utf-8') as file:
            value = json.load(file)
        json_data[key] = value
