class Time(object):
    def __init__(self):
        import time
        self.year=time.strftime("%Y")
        self.month=time.strftime("%m")
        self.day=time.strftime("%d")
        self.hour=time.strftime("%H")
        self.minute=time.strftime("%M")
        self.second=time.strftime("%S")
        self.week=time.strftime("%a")
        self.time=time.strftime("%X")
        self.date=time.strftime("%F")
        self.datetime=time.strftime("%Y/%m/%d %H:%M:%S %a")
class Math(object):
    def __init__(self,num):
        import math
        self.num=int(num)
    def IsPrime(self):
        if self.num>2:
            for i in range(2,self.num):
                if self.num%i==0:
                    return False
                    break
            return True
        else:
            return False
    def IsThundernumber(self):
        wei=len(str(self.num))
        for i in range(wei):
            cut=divmod(self.num,10**i)
            if (cut[0]+cut[1])**2==self.num:
                return True
                break
        return False
    def IsPalindrome(self):
        if str(self.num)==str(self.num)[::-1]:
            return True
        else:
            return False
    def IsPerfect(self):
        a = 0
        for i in range(1,self.num):
            if self.num % i == 0:
                a = a + i
        if self.num == a:
            return True
        else:
            return False
class Rand(object):
    def randint(self,min,max):
        import random
        return random.randint(min,max)
    def randfloat(self,a,b):
        import random
        return a+random.randint(10**(b-1),10**b-1)/10**b
    def randword(self):
        import random
        wordList=[chr(i) for i in range(19968,40918)]
        return random.choice(wordList)
    def randlist(self,list):
        import random
        return random.choice(list)