<<<<<<< HEAD
def help(helpmsg=''):
	if not helpmsg:
		print(openhelptxt('快速入门'))
	else:
		print(openhelptxt(help_txt))
		

def openhelptxt(name):
	try:
		with open('help_txt/'+name+'.txt',encoding='utf-8')as fp:
			return fp.read()
	except Exception as e:
		return e
help()
=======
def help():
    print('''三角函数相关
sin
功能：返回一个数的角度值正弦
可能返回的错误：
无
示例
>>>from mathprolib.simple import *
>>>sin(90)
1
>>>sin(30)
0.5
sinr
功能：返回一个数的弧度制正弦
可能返回的错误：
无
示例
>>>from mathprolib.simple import *
>>> sinr(π)
0
cos
功能：返回一个数的角度值余弦
可能返回的错误：
无
示例
>>>from mathprolib.simple import *
>>>cos(180)
-1
cosr
功能：返回一个数的弧度制余弦
可能返回的错误：
无
示例
>>>from mathprolib.simple import *
>>> cosr(π)
-1''')
>>>>>>> 2d6890282b46d56417a51d3bcb1ce455dc62012a
