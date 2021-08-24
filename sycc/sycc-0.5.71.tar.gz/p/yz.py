from p.__init__ import *
from sys import path
path.append('..')
from e.__init__ import *
import platform
os=platform.system()
pai2='π'
def part_yz():#圆柱
    while True:
        r=input('请输入半径:')#半径输入
        try:
            r=eval(r)
            if r<=0:
                print('请输入有效数字')
                switch(1)
                break
        except ZeroDivisionError:
            print('除数不能为0')
        except (Exception,KeyboardInterrupt,IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('请输入有效数字')
        H=input('请输入高:')#高输入 
        try:
            H=eval(H)
            if H<0:
                print('请输入有效数字')
        except ZeroDivisionError:
            print('除数不能为0')
        except (Exception,IOError,ValueError,TypeError,SyntaxError,EOFError,NameError,KeyboardInterrupt):
            print('请输入有效数字')
        try:
            if H<=0 and r<=0:#请勿删除，仿照yh.py
                print('①.半径和高>0\n②.2s后重新选择圆柱模式使用\n\033[7;35mtips\033[0m\033[1;1m')
                switch(3)
                break
        except Exception:
            print('出现\033[6;31mError\033[0m\n')
            print('请选择\033[6;36m圆柱\033[0m\033[1;1m模式重试')
            switch(2)
            break
        print('【圆柱】')
        aboutpi()
        if os=='Linux':
            xxx=input('请输入(\033[1;32m1,2,3,4,5\033[0m\033[1;1m)中的一个数字:')
        elif os=='Windows':
            xxx=input('请输入1~5中的数字')
        try:
            xxx=int(xxx)
        except ZeroDivisionError:
            print('除数不能为0')
        except (Exception,IOError,ValueError,TypeError,SyntaxError,EOFError,NameError,KeyboardInterrupt):
            print('请输入有效数字')
        try:
            if xxx>5 or xxx<=0:
                end1=sj.now()-start
                print('即将\033[10;31m退出\033[0m,','本次使用时间:',end1,'\n程序将在5秒后关闭,谢谢使用')
                exitings(5)
                tc('谢谢使用')
            elif xxx==5:
                print('-'*40)
                print('切换模式')
                switch(0.1)
                break
            elif xxx==1:
                dw()
                sU=r*r*3.14#上圆s
                sD=sU*2#双圆s
                d=2*r  #直径
                C=d*3.14 #周长
                Sc=C*H #侧s
                S=sD+Sc #表s
                V=sU*H
                if r<=0 and H<=0 or (S or C or Sc or sD or sU or d)<=0 : #if重点检查区域
                    print('请重新输入半径和高')
                    print('请圆柱模式，再次尝试运行')
                    switch(0.5)
                    break
                elif r>0 and H>0:
                    dw()
                    print('======计算结果======')
                    print('当半径=',r,'直径=',d,'高=',H,'时')
                    print('\n一个圆的周长=','{:.5f}'.format(C))
                    print('一个圆的面积=','{:.5f}'.format(sU))
                    print('两个圆的面积=','{:.5f}'.format(sD))
                    print('圆柱的侧面积=','{:.5f}'.format(Sc))
                    print('圆柱的体积=','{:.5f}'.format(V))
                    print('圆柱的表面积=','{:.5f}'.format(S))
                else:
                    print('请重新输入半径和高')
                    print('请圆柱模式，再次尝试运行')
            elif xxx==2:
                sU=r*r*pai1#上圆s
                sD=sU*2#双圆s
                d=2*r  #直径
                C=d*pai1 #周长
                Sc=C*H #侧s
                S=sD+Sc #表s
                V=sU*H
                if r<=0 and H<=0 or (S or C or Sc or sD or sU or d)<=0 : #if重点检查区域
                    print('请重新输入半径和高，因为其中一个小于0或者数太小了，就像0.0001这样的，所以停止运行了')
                    print('请重新选择圆柱模式，再次尝试运行')
                    switch(0.5)
                    break
                elif r>0 and H>0:
                    dw()
                    print('=====计算结果=====')
                    print('当半径=',r,'直径=',d,'高=',H,'时')
                    print('\n一个圆的周长=','{:.5f}'.format(C))
                    print('一个圆的面积=','{:.5f}'.format(sU))
                    print('两个圆的面积=','{:.5f}'.format(sD))
                    print('圆柱的侧面积=','{:.5f}'.format(Sc))
                    print('圆柱的体积=','{:.5f}'.format(V))
                    print('圆柱的表面积=','{:.5f}'.format(S))
                else:
                    print('重新输入半径和高')
            elif xxx==3:
                sU=r*r#上圆s 
                sD=sU*2#双圆s 
                d=2*r  #直径
                C=d #周长
                Sc=C*H #侧s 
                S=sD+Sc #表s 
                V=sU*H
                if r<=0 and H<=0 or (S or C or Sc or sD or sU or d)<=0 : #if重点检查区域
                    print('请重新输入半径和高')
                    print('请圆柱模式，再次尝试运行')
                    switch(0.5)
                    break
                elif r>0 and H>0:
                    dw()
                    print('=====计算结果=====')
                    print('当半径=',r,'直径=',d,'高=',H,'时')
                    print('\n一个圆的周长=','{:.5f}'.format(C),pai2)
                    print('一个圆的面积=','{:.5f}'.format(sU),pai2)
                    print('两个圆的面积=','{:.5f}'.format(sD),pai2)
                    print('圆柱的侧面积=','{:.5f}'.format(Sc),pai2)
                    print('圆柱的体积=','{:.6f}'.format(V),pai2)
                    print('圆柱的表面积=','{:.5f}'.format(S),pai2)
                else:
                    print('重新输入半径和高')
            elif xxx==4:
                defpi=input('请输入要自定义的π(大于等于3且小于3.2)->')
                try:
                    defpi=eval(defpi)
                except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError,KeyboardInterrupt):
                    print('请输入指定范围的数字')
                except ZeroDivisionError:
           	     print('除数不能为0')
           	     print('请使用正确符号或正确数字')
                if defpi<3 or defpi >3.2:
                        switch(0.3)
                        break
                if defpi >=3 and defpi <3.2:
                    sU=r*r*defpi#上圆s
                    sD=sU*2#双圆s
                    d=2*r  #直径
                    C=d*defpi #周长
                    Sc=C*H #侧s
                    S=sD+Sc #表s
                    V=sU*H#体积
                    if r<=0 and H<=0 or (S or C or Sc or sD or sU or d)<=0 : #if重点检查区域
                        print('请重新输入半径和高')
                        switch(0.5)
                        break
                    elif r>0 and H>0:
                        dw()
                        print('=====计算结果=====')
                        print('当半径=',r,'直径=',d,'高=',H,'π=',defpi,'时')
                        print('\n一个圆的周长=','{:.6f}'.format(C))
                        print('一个圆的面积=','{:.6f}'.format(sU))
                        print('两个圆的面积=','{:.6f}'.format(sD))
                        print('圆柱的侧面积=','{:.6f}'.format(Sc))
                        print('圆柱的体积=','{:.6f}'.format(V))
                        print('圆柱的表面积=','{:.6f}'.format(S))
                    else:
                        print('重新输入半径和高')
            else:
                end1=sj.now()-start
                print('即将\033[10;31m退出\033[0m,','本次使用时间:',end1,'\n程序将在5秒后关闭,谢谢使用')
                exitings(5)
                tc('谢谢使用')
        except Exception:
            print('\n圆柱beta报告:在本模式中您的操作出现\033[1;1m\033[6;31mError\033[0m\n','\b已为您自动跳转选择模式,请选择圆柱模式')
            switch(1)
            break

