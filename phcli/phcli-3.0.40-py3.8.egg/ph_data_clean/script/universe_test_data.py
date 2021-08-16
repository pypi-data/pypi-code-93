# -*- coding: utf-8 -*-

import xlrd
import yaml

test_file = r'../../../file/ph_data_clean/s3_test_data/product-product-test.yaml'
# test_file = r'../../file/ph_data_clean/s3_test_data/universe-universe-test.yaml'
readbook = xlrd.open_workbook(r'../../../file/ph_data_clean/s3_primitive_data/Product_origin_file.xlsx')
# readbook = xlrd.open_workbook(r'..\..\file\ph_data_clean\s3_primitive_data\Universe_origin_file.xlsx')
sheet = readbook.sheet_by_index(0)
nrows = sheet.nrows
ncols = sheet.ncols
print(ncols)
test_data_key = sheet.row_values(0)


def get_universe_test_data():

    test_data_lst = []

    for i in range(50, 150):
        value = sheet.row_values(i)
        test_data = {'data': {},
                     'metadata': {'fileName': 'Book1',
                                  # 'providers': ['universe', 'universe'],
                                  'providers': ['product', 'product'],
                                  'sheetName': 'sheet1'}}
        for j in range(0, ncols-1):
            real_key = str(j) + '#' + str(test_data_key[j])
            test_data['data'][real_key] = value[j]

        # 加上tag
        test_data['data']['_Tag'] = 'yes'

        test_data_str = str(test_data['data'])
        test_data['data'] = test_data_str

        meta_data_str = str(test_data['metadata'])
        test_data['metadata'] = meta_data_str

        test_data_lst.append(test_data)
    return test_data_lst


if __name__ == '__main__':
    with open(test_file, 'a', encoding='UTF-8') as file:
        yaml.dump(get_universe_test_data(), file, default_flow_style=False, encoding='utf-8', allow_unicode=True)
