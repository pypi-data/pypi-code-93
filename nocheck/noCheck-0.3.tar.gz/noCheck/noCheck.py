import  sys
class Number:

    def __init__(self,firstNum=None,secondNum=None):
        if firstNum is None or secondNum is None :
            sys.exit("Please provide both the numbers")
        else:
            self.firstNum=firstNum
            self.secondNum=secondNum
            self.check=100
            self.diff=''

    def checkNum(self):#this will calculate grade
        numFirst= str(self.firstNum)
        numSecond=str(self.secondNum)
    
    
        if self.firstNum==0 and self.secondNum==0:
            self.check=0
            return "Both the numbers are same!"   
        
        
        elif self.firstNum>self.secondNum:
            self.check=1
            return 'Number '+numFirst+' is greater than other number '+numSecond

        elif self.firstNum<self.secondNum:
            self.check=2
            return 'Number '+numSecond+' is greater than other number '+numFirst
           
    def conc(self):
        numFirst= str(self.firstNum)
        numSecond=str(self.secondNum)
        diffH =str(self.firstNum-self.secondNum)
        diffL =str(self.secondNum-self.firstNum)
                    
        if self.check==0:
            print('Number '+numFirst+' is equal to number '+numSecond)
        
        elif self.check==1:
            print('Number '+numFirst+' is greater than '+numSecond+' by '+diffH)
           
        elif self.check==2:
            print('Number '+numSecond+' is greater than '+numFirst+' by '+diffL)
           