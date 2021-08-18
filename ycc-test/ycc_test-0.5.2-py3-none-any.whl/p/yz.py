from p.__init__ import *
pai2='π'
def part_yz():#圆柱
    while True:
        r=input('请输入半径:')#半径输入
        try:
            r=eval(r)
        except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('')
        except ZeroDivisionError:
            print('除数不能为0，emmm，2年级小孩都知道')
            print('请使用正确符号或正确数字')
        H=input('请输入高:')#高输入 
        try:
            H=eval(H)
        except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('请使用正确符号或正确数字')
        except ZeroDivisionError:
            print('除数不能为0，emmm，2年级小孩都知道')
        print('【圆柱】')
        aboutpi()
        xxx=input('请输入(1,2,3,4,5)中的一个数字:')
        print(' ')
        try:
            xxx=int(xxx)
        except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
            print('请输入有效数字')
        except ZeroDivisionError:
            print('除数不能为0，emmm，2年级小孩都知道')
        if r<=0 or H<=0:
            print('虽然输入成功，但是为什么弹出选择模式，自己想想为什么')
            switch(0.1)
            break
        print(' ')
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
                print('请重新输入半径和高，因为其中一个小于0或者数太小了，就像0.0001这样的，所以停止运行了')
                print('请选择模式，再次尝试运行')
                switch(0.5)
                break
            elif r>0 and H>0:
                dw()
                print('======计算结果======')
                print('当半径=',r,'直径=',d,'高=',H,'时')
                print('\n一个圆的周长=','{:.7f}'.format(C))
                print('一个圆的面积=','{:.7f}'.format(sU))
                print('两个圆的面积=','{:.7f}'.format(sD))
                print('圆柱的侧面积=','{:.7f}'.format(Sc))
                print('圆柱的体积=','{:.7f}'.format(V))
                print('圆柱的表面积=','{:.7f}'.format(S))
            else:
                print('重新输入半径和高，无需关闭')
                print('如果下面没有弹出请输入半径和请输入高，请关闭后重新打开')
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
                print('请重新选择圆柱，再次尝试运行')
                switch(0.5)
                break
            elif r>0 and H>0:
                dw()
                print('=====计算结果=====')
                print('当半径=',r,'直径=',d,'高=',H,'时')
                print('\n一个圆的周长=','{:.7f}'.format(C))
                print('一个圆的面积=','{:.7f}'.format(sU))
                print('两个圆的面积=','{:.7f}'.format(sD))
                print('圆柱的侧面积=','{:.7f}'.format(Sc))
                print('圆柱的体积=','{:.7f}'.format(V))
                print('圆柱的表面积=','{:.7f}'.format(S))
            else:
                print('重新输入半径和高，无需关闭')
                print('如果下面没有弹出请输入半径和请输入高,请重新打开')
        elif xxx==3:
            sU=r*r#上圆s 
            sD=sU*2#双圆s 
            d=2*r  #直径
            C=d #周长
            Sc=C*H #侧s 
            S=sD+Sc #表s 
            V=sU*H
            if r<=0 and H<=0 or (S or C or Sc or sD or sU or d)<=0 : #if重点检查区域
                print('请重新输入半径和高，因为其中一个小于0或者数太小了，就像0.0001这样的，所以停止运行了')
                print('请重新选择圆柱，再次尝试运行')
                switch(0.5)
                break
            elif r>0 and H>0:
                dw()
                print('=====计算结果=====')
                print('当半径=',r,'直径=',d,'高=',H,'时')
                print('\n一个圆的周长=','{:.7f}'.format(C),pai2)
                print('一个圆的面积=','{:.7f}'.format(sU),pai2)
                print('两个圆的面积=','{:.7f}'.format(sD),pai2)
                print('圆柱的侧面积=','{:.7f}'.format(Sc),pai2)
                print('圆柱的体积=','{:.7f}'.format(V),pai2)
                print('圆柱的表面积=','{:.7f}'.format(S),pai2)
            else:
                print('重新输入半径和高')
        elif xxx==4:
            defpi=input('(请输入你要自定义的π，但是不要小于3或大于等于3.2):')
            try:
                defpi=eval(defpi)
            except (IOError,ValueError,TypeError,SyntaxError,EOFError,NameError):
                print('请输入指定范围的数字')
            except ZeroDivisionError:
                print('除数不能为0，emmm，2年级小孩都知道')       
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
                    print('请重新输入半径和高，因为其中一个小于0或者数太小了，就像0.0001这样的，所以停止运行了')
                    print('请重新打开，再次尝试运行')
                    switch(0.5)
                    break
                elif r>0 and H>0:
                    dw()
                    print('=====计算结果=====')
                    print('当半径=',r,'直径=',d,'高=',H,'时')
                    print('\n一个圆的周长=','{:.8f}'.format(C))
                    print('一个圆的面积=','{:.8f}'.format(sU))
                    print('两个圆的面积=','{:.8f}'.format(sD))
                    print('圆柱的侧面积=','{:.8f}'.format(Sc))
                    print('圆柱的体积=','{:.8f}'.format(V))
                    print('圆柱的表面积=','{:.8f}'.format(S))
                else:
                    print('重新输入半径和高，无需关闭')
                    print('如果下面没有弹出请输入半径和请输入高,请重新打开(运行)')
        else:
            end1=sj.now()-start
            print('即将\033[10;31m退出\033[0m,','本次使用时间:',end1,'\n程序将在5秒后关闭,谢谢使用')
            exitings(5)
            tc('谢谢使用')