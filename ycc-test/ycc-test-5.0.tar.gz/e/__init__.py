from time import sleep as dd
def exitings(wait):
	i=wait
	print('\n请自助排查错误，若为汝所欲之，请视而不见也!')
	while i<=wait and i>0:
		i-=0.01
		dd(0.01)
		print('\r\033[1;1m\033[6;26;31m退出倒计时{:.2f}秒\033[0m'.format(abs(i)),end="",flush=True)#abs
	print('\n\033[1;23;33mdone\033[0m')
#exitings(3)
def switch(wt):#waiting time
	i=wt
	print('\n请自助排查错误，若为汝所欲之，请视而不见也!')
	while i<=wt and i>0:
		i-=0.01
		dd(0.01)
		print('\r\033[1;1m\033[6;26;32m切换模式倒计时{:.2f}秒\033[0m'.format(abs(i)),end="",flush=True)#abs
	print('\n\033[1;23;34mdone\033[0m')
#switch(12)
#exitings(12)