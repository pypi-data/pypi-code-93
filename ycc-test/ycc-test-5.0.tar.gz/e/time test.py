#test-time old
#for exit waiting time
#5s,3s,0,3s,2s,0.1s

#int
'''
def t5():
	for i in range(5, 0, -1):
		print("\r倒计时{}秒！".format(i), end="", flush=True)
		dd(1)
	print('\nEnd')
def t3():
	i=3.00
	while i<=3.00 and i>0.00:
		i-=0.01
		dd(0.01)
		print('\r倒计时{:.2f}秒'.format(abs(i)),end="",flush=True)#abs
	print('\n\033[1;23;34mfinished\033[0m')
def t2(x):
	i=x
	while i<=x and i>0.00:
		i-=0.01
		dd(0.01)
		print('\r倒计时{:.2f}秒'.format(abs(i)),end="",flush=True)#abs
	print('\n\033[1;23;34mfinished\033[0m')
t2(0.2)
def t1():
	for i in range(2, 0, -1):
		print("\r倒计时{}秒！".format(1), end="", flush=True)
		dd(0.5)
	print('\nEnd')
#float
def p3():
	i=0.30
	while i<=0.3 and i>0:
		i-=0.01
		dd(0.01)
		print('\r倒计时{:.2f}秒'.format(abs(i)),end="",flush=True)#abs
	print('\n\033[1;23;34mfinished\033[0m')
def p1():
	i=0.10
	while i<=0.1 and i>0:
		i-=0.01
		dd(0.01)
		print('\r倒计时{:.2f}秒'.format(abs(i)), end="", flush=True)
	print('\n\033[1;23;34mfinished\033[0m')
已废弃，发现了新方法'''