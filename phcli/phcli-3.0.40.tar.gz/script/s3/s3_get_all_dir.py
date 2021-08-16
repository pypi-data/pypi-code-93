# -*- coding: utf-8 -*-

"""
递归获取 s3 中所有的目录，保留结构
"""

import boto3
import xlwt

client = boto3.client('s3')

buckets = client.list_buckets()
buckets = [bucket['Name'] for bucket in buckets['Buckets']]


def transition_tree(tree, k, str):
    # 终止条件
    if not str or '/' not in str:
        tree[k] = {}
        return tree

    # 初始化 key
    if k not in tree.keys():
        tree[k] = {}

    sub_tree = tree[k]
    sub_k, sub_str = str.split('/', 1)
    sub_result = transition_tree(sub_tree, sub_k, sub_str)
    sub_tree.update(sub_result)

    tree[k] = sub_tree
    return tree


main_tree = {}
for bucket in buckets:
    objects = client.list_objects(
        Bucket=bucket
    )
    objects = [object['Key'] for object in objects['Contents']]

    tree = {}
    for object in objects:
        if '/' not in object:
            continue
        sub_k, sub_str = object.split('/', 1)
        transition_tree(tree, sub_k, sub_str)
    main_tree[bucket] = tree


row, col = 0, 0
def write_excel_xls_by_subtree(sheet, sub_tree):
    if not sub_tree:
        return

    global row, col
    for k, v in sub_tree.items():
        print(row, col, k)
        sheet.write(row, col, k)
        row += 1
        col += 1
        write_excel_xls_by_subtree(sheet, v)
        col -= 1


workbook = xlwt.Workbook()
sheet = workbook.add_sheet('目录情况')

for k, v in main_tree.items():
    write_excel_xls_by_subtree(sheet, {k: v})

workbook.save('s3当前目录情况.xls')
print("xls格式表格写入数据成功！")
