def evens_between(n1,n2):
    li=[]
    for i in range(n1,n2+1):
        if(i%2==0):
            li.append(i)
    return li