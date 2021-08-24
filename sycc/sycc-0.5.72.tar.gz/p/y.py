from p.__init__ import * #检测8-12是否需要备份
pai2='π'
from sys import path
path.append('..')
from e.__init__ import *
import platform
os=platform.system()
def part_y():#圆
    while True:
        r=input('请输入圆的半径:')
        try:
            r=eval(r)
            if r<=0:
            	print('请输入有效数字')
            	print('0.5s后切换模式')
            	switch(0.5)
            	break
        except ZeroDivisionError:
            print('除数不能为0')
        except (Exception,IOError,ValueError,TypeError,SyntaxError,EOFError,NameError,KeyboardInterrupt):
            print('请输入有效数字')
            print('出现\033[6;31mError\033[0m\n')
            print('请选择\033[6;36m圆\033[0m\033[1;1m模式重试')
            switch(2)
            break
        print('【圆】')
        aboutpi()
        if os=='Linux':
            xxx=input('请输入(\033[1;32m1,2,3,4,5\033[0m\033[1;1m)中的一个数字:')
        elif os=='Windows':
            xxx=input('请输入1~5中的数字')
        print('')
        try:
            xxx=int(xxx)
        except ZeroDivisionError:
            print('除数不能为0')
        except (Exception,IOError,ValueError,TypeError,SyntaxError,EOFError,NameError,KeyboardInterrupt):
            print('请输入指定范围的整数,不可以使用运算符')
            switch(0.3)
            break
        try:
        	if xxx>5 or xxx<=0:
        		end1=sj.now()-start
        		print('即将\033[10;31m退出\033[0m,','本次使用时间:',end1,'\n程序将在3s后关闭,谢谢使用')
        		exitings(3)
        		tc('谢谢使用')
        	elif xxx==5:
        		print('-'*40)
        		switch(0.3)
        		break
        	elif xxx==1:
        		d=2*r #直径
        		ra=r**2
        		s=3.14*ra#面积
        		c=3.14*d#周长
        		dw()
        		print('======计算结果======')
        		print('当半径=',r,'直径=',d,'时')
        		print('周长=','{:.3f}'.format(c))
        		print('面积=','{:.3f}'.format(s))
        	elif xxx==2:
        	    d=2*r #直径
        	    ra=r**2
        	    s=pai1*ra#面积
        	    c=pai1*d
        	    dw()
        	    print('======计算结果======')
        	    print('当半径=',r,'直径=',d,'时')
        	    print('周长=','{:.3f}'.format(c))
        	    print('面积=','{:.3f}'.format(s))
        	elif xxx==3:
        	    d=2*r #直径
        	    ra=r**2
        	    s=ra#面积
        	    c=r*2 #周长
        	    dw()
        	    print('======计算结果======')
        	    print('当半径=',r,'直径=',d,'时')
        	    print('周长=','{:.5f}'.format(c),pai2)
        	    print('面积=','{:.5f}'.format(s),pai2)
        	elif xxx==4:
        	    defpi=input('请输入要自定义的π(大于等于3且小于3.2)->')
        	    try:
        	        defpi=eval(defpi)
        	    except ZeroDivisionError:
        	        print('除数不能为0')
        	    except (Exception,ValueError,TypeError,IOError,KeyboardInterrupt):
        	        print('请输入指定范围的数字')
        	    if defpi<3 or defpi >3.2:
        	        end=sj.now()-start
        	        print('本次使用时间:',end)
        	        print('^大于3小于3.2^|||5s后关闭')
        	        exitings(5)
        	        tc('谢谢使用')
        	    elif (defpi >=3 and defpi <3.2):
        	        d=2*r 
        	        ra=r**2
        	        s=defpi*ra
        	        c=defpi*d
        	        dw()
        	        print('======计算结果======')
        	        print('当半径=',r,'直径=',d,'π=',defpi,'时')
        	        print('周长=','{:.6f}'.format(c))
        	        print('面积=','{:.6f}'.format(s))
        	else:
        	    end1=sj.now()-start
        	    print('即将\033[10;31m退出\033[0m,','本次使用时间:',end1,'\n程序将在5s后关闭,谢谢使用')
        	    exitings(5)
        	    tc('谢谢使用')
        except Exception:
            print('圆beta报告:在本模式中您的操作出现\033[1;1m\033[6;31mError\033[0m\n','\b已为您自动跳转选择模式,请选择圆模式')
            switch(1)
            break