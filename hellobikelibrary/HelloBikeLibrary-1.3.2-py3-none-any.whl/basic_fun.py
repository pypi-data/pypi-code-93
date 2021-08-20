# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-12-02 21:30:32
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2020-12-02 21:47:35

"""
基础功能
"""
class BasicFun(object):
	def __init__(self):
		pass


	def getListNextValue(self,listValue,name):
		"""
		得到指定列表元素的下一个值的内容
		listValue  列表值
		name  以这个元素为参考，返回他的后面的值
		"""
		try:
			temp = listValue.index(name)
		except:
			raise Exception("你传的这个元素不在列表中")
		return listValue[temp+1]
	

if __name__ == '__main__':
	pass