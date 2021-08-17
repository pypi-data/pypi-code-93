from p.__init__ import *
pai2='π' 
def part_y():#圆
    while True:
        r=input('请输入圆的半径:')
        try:
            r=eval(r)
        except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('请输入有效数字')
        except ZeroDivisionError:
            print('除数不能为0，emmm，2年级小孩都知道')
        if r<=0:
            print('\n2个问题，要不你输入的数太小（0.0001 0.001…），python一算结果就是0\n要不然就是r＜0，你见过r小于0的吗？\n1请重新输入选择模式使用')
            switch(1)
            break
        print('【圆】')
        aboutpi()
        xxx=input('请输入(1,2,3,4,5)中的一个数字:')
        print(' ')
        try:
            xxx=int(xxx)
        except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('请输入指定范围的整数')
            switch(0.3)
            break
        except ZeroDivisionError:
            print('除数不能为0，emmm，2年级小孩都知道')
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
            if r<=0:
                print('\n2个问题，要不你输入的数太小（0.0001 0.001…），python一算结果就是0\n要不然就是r＜0，你见过r小于0的吗？\n1请重新输入选择模式使用')
                print('0.3s后切换模式')
                switch(0.3) 
                break
            d=2*r #直径
            ra=r**2
            s=3.14*ra#面积
            c=3.14*d#周长
            dw()
            print('======计算结果======')
            print('当半径=',r,'直径=',d,'时')
            print('周长=','{:.6f}'.format(c))
            print('面积=','{:.6f}'.format(s))
        elif xxx==2:#π为pai1
            if r<=0:
                print('\n2个问题，要不你输入的数太小（0.0001 0.001…），python一算结果就是0\n要不然就是r＜0，你见过r小于0的吗？\n请重新输入选择模式使用')
                switch(0.3)
                break
            d=2*r #直径
            ra=r**2
            s=pai1*ra#面积
            c=pai1*d
            dw()
            print('======计算结果======')
            print('当半径=',r,'直径=',d,'时')
            print('周长=','{:.8f}'.format(c))
            print('面积=','{:.8f}'.format(s))
        elif xxx==3:
            if r<=0:
                print('2个问题，要不你输入的数太小（0.0001 0.001…），python一算结果就是0\n要不然就是r＜0，你见过r小于0的吗？\n请重新选择模式后运行')
                switch(0.3)
                break
            d=2*r #直径
            ra=r**2
        #精确到第9位
            s=ra#面积
            c=r*2 #周长
            dw()
            print('======计算结果======')
            print('当半径=',r,'直径=',d,'时')
            print('周长=','{:.8f}'.format(c),pai2)
            print('面积=','{:.8f}'.format(s),pai2)
        elif xxx==4:
            defpi=input('(请输入你要自定义的π，但是不要小于3或大于等于3.2):')
            try:
                defpi=eval(defpi)
            except (ValueError,TypeError,IOError):
                print('请输入指定范围的数字')
            except ZeroDivisionError:
                print('除数不能为0，emmm，2年级小孩都知道')
            if defpi<3 or defpi >3.2:
                    end=sj.now()-start
                    print('本次使用时间:',end)
                    print('拜拜了您嘞，自己想想为什么,别生气哈,想明白后再用,5s后关闭')
                    exitings(5)
                    tc('谢谢使用')
            if defpi >=3 and defpi <3.2:
                if r<=0:
                    print('2个问题，要不你输入的数太小（0.0001 0.001…），python一算结果就是0\n要不然就是r＜0，你见过r小于0的吗？\n请重新选择该模式使用')
                    switch(0.3)
                    break
                d=2*r #直径
                ra=r**2
                s=defpi*ra#面积
                c=defpi*d
                dw()
                print('======计算结果======')
                print('当半径=',r,'直径=',d,'时')
                print('周长=','{:.8f}'.format(c))
                print('面积=','{:.8f}'.format(s))
        else:
            end1=sj.now()-start
            print('即将\033[10;31m退出\033[0m,','本次使用时间:',end1,'\n程序将在5s后关闭,谢谢使用')
            exitings(5)
            tc('谢谢使用')