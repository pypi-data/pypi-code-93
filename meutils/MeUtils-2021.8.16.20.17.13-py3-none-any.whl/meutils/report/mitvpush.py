#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : mitvpush
# @Time         : 2021/2/20 3:29 下午
# @Author       : yuanjie
# @WeChat       : 313303303
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

file = Path('/Users/yuanjie/Desktop/').glob("Push用户数_*") | xlist | xsort | xgetitem
logger.info(f"DAU数据：{file.name}")

df = pd.read_csv(file).sort_values('行为时间')[-15:-1]
print(df.tail())
logger.info(f"数据EDA：{df['行为时间'].min()} ~ {df['行为时间'].max()}")

a = df['启动事件的用户数'][:7].mean()
b = df['启动事件的用户数'][7:14].mean()

print(a, b)

# 本次/上次 - 1
print(f"小米视频PUSH {df['行为时间'].max()[:10]} DAU {int(b)}", f"环比 {b / a - 1:.2%}")
