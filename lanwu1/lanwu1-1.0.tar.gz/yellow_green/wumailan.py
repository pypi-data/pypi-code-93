employee=['小王','小白','小陈','吴签']            #工资对应的人
average=0
list=[]
i=0
while i<len(employee):
    s=input('请输入该员工的工资（按q或Q结束录入）：')

    if not s.isdigit():                         #确保输入为纯数字
        print('该员工输入的工资有误')
        continue
    elif  float(s)<=0 :                         #确保大于0
        print('该员工输入的工资有误')
        continue

    elif s.upper()=='Q':
        print('录入结束')
        break

    i+=1
    list.append(s)
    average+=float(s)

else:
    print('该组成员全部录入完成')
for m in range(len(employee)):
    print('工资情况:',employee[m],list[m])
print('平均工资：',average/len(list))


