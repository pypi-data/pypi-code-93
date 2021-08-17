from p.__init__ import *
pai2='π'
def part_yh():#圆环
    while True:
        r1=input('请输入外圆半径:')#输入r1（外圆半经）
        try:
            r1=eval(r1)
        except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('输入符号时注意是英文的,输入正确数字')
        except ZeroDivisionError:
            print('除数不能为0，emmm，2年级小孩都知道')
        if r1<=0.00000000:
            print('可能是你输入的数太小了\n1.内圆半径不允许大于等于外圆半径\n2.重新选择模式使用\n *注意外圆半径和内圆半径的顺序，上面是外圆半径')
            switch(2)
            break
        r2=input('请输入内圆半径:')
        try:
            r2=eval(r2)
        except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('输入符号时注意是英文的,输入正确数字')
        except ZeroDivisionError:
            print('除数不能为0，emmm，2年级小孩都知道')
        if r2<=0.000000000:
            print('可能是你输入的数太小了\n1.内圆半径不允许大于等于外圆半径\n2.重新选择模式使用\n *注意外圆半径和内圆半径的顺序，上面是外圆半径')
            switch(2)
            break
        print('【圆环】')
        aboutpi()
        xxx=input('请输入(1,2,3,4,5)中的一个数字:')
        print(' ')
        try:
            xxx=int(xxx)
        except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('请输入正确的整数')
        except ZeroDivisionError:
            print('除数不能为0，emmm，2年级小孩都知道') 
        print(' ')
        if xxx>5 or xxx<=0:
            end1=sj.now()-start
            print('即将\033[10;31m退出\033[0m,','本次使用时间:',end1,'\n程序将在5秒后关闭,谢谢使用')
            exitings(5)
            tc('谢谢使用')
        elif xxx==5:
            print('-'*40)
            switch(0.1)
            break
        elif xxx==1:
            Sr1=r1*r1*3.14 #外圆s
            Sr2=r2*r2*3.14 #内圆s
            S=Sr1-Sr2     #圆环s
            C1=6.28*r1 #外圆周长
            C2=6.28*r2 #内圆周长        
            if S>0:
                dw()
                print('=====计算结果=====')
                print('圆环面积=','{:.6f}'.format(S))
                print('外圆周长=','{:.6f}'.format(C1))
                print('内圆周长=','{:.6f}'.format(C2))
                print('外圆面积=','{:.7f}'.format(Sr1))
                print('内圆面积=','{:.7f}'.format(Sr2))
            else:
                print('可能是你输入的数太小了\n1.内圆半径不允许大于等于外圆半径\n2.重新选择模式使用\n *注意外圆半径和内圆半径的顺序，上面是外圆半径')
                switch(1)
                break
        elif xxx==2:
            Sr1=r1*r1*pai1 #外圆s #6
            Sr2=r2*r2*pai1 #内圆s #7
            S=Sr1-Sr2      #圆环s #6
            C1=2*pai1*r1 #外圆周长#6
            C2=2*pai1*r2 #内圆周长 #6 
            if S>0:
                dw()
                print('=====计算结果=====')
                print('圆环面积=','{:.6f}'.format(S))
                print('外圆周长=','{:.6f}'.format(C1))
                print('内圆周长=','{:.6f}'.format(C2))
                print('外圆面积=','{:.7f}'.format(Sr1))
                print('内圆面积=','{:.7f}'.format(Sr2))
            else: 
                print('可能是你输入的数太小了\n1.内圆半径不允许大于等于外圆半径\n2.重新选择模式使用\n *注意外圆半径和内圆半径的顺序，上面是外圆半径')
                switch(1)
                break
        elif xxx==3:
            Sr1=r1*r1 #外圆s 
            Sr2=r2*r2#内圆s
            S=Sr1-Sr2      #圆环s
            C1=2*r1 #外圆周长
            C2=2*r2#内圆周长        
            if S>0:
                dw()
                print('=====计算结果=====')
                print('圆环面积=','{:.6f}'.format(S),pai2) 
                print('外圆周长=','{:.6f}'.format(C1),pai2)
                print('内圆周长=','{:.6f}'.format(C2),pai2)
                print('外圆面积=','{:.7f}'.format(Sr1),pai2)
                print('内圆面积=','{:.7f}'.format(Sr2),pai2)
            else: 
                print('可能是你输入的数太小了\n1.内圆半径不允许大于等于外圆半径\n2.重新选择模式使用\n *注意外圆半径和内圆半径的顺序，上面是外圆半径')
                switch(1)
                break
        elif xxx==4:
            defpi=input('请输入要自定义的π(大于等于3且小于3.2)->')
            try:
                defpi=eval(defpi)
            except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
                print('请输入正确的数字')
            except ZeroDivisionError:
                print('除数不能为0，emmm，2年级小孩都知道')
            if defpi<3 or defpi >3.2:
                    switch(0.3)
                    break
            if defpi >=3 and defpi <3.2:
                print('最后结果精确到小数点后8位')
                Sr1=r1*r1*defpi    #外圆s
                Sr2=r2*r2*defpi,8 #内圆s
                S=Sr1-Sr2,8              #圆环s
                C1=2*defpi,8           #外圆周长
                C2=2*defpi*r2,8    #内圆周长
                if S>0:
                    dw()
                    print('=====计算结果=====')
                    print('圆环面积=','{:.8f}'.format(S))
                    print('外圆周长=','{:.8f}'.format(C1))
                    print('内圆周长=','{:.8f}'.format(C2))
                    print('外圆面积=','{:.8f}'.format(Sr1))
                    print('内圆面积=','{:.8f}'.format(Sr2))
                else: 
                    print('可能是你输入的数太小了\n1.内圆半径不允许大于等于外圆半径\n2.重新选择模式使用\n *注意外圆半径和内圆半径的顺序，上面是外圆半径')
                    switch(1)
                    break
        else:
            end=sj.now()-start
            print('即将\033[10;31m退出\033[0m,','本次使用时间:',end,'\n程序将在5秒后关闭,谢谢使用')
            exitings(5)
            tc('谢谢使用')
#part_yh()  
