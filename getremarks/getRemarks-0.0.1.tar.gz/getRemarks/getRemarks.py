import  sys
class Grade:#This module will get the grades of the students according to their marks

    def __init__(self,marksSecured,marksOutOf=None):
        if marksOutOf is None:
            sys.exit("Total marks part is missing, should be after marks scored followed by comma. Say (200, 500)")
        elif marksOutOf <1 or marksSecured<0:
            sys.exit("Did you made any mistake? This module works with postive values only!")
        else:
            self.marksSecured=marksSecured
            self.marksOutOf=marksOutOf
            self.grade=100
            self.total=(self.marksSecured/self.marksOutOf)*100

    def getGrade(self):#this will calculate grade
        total=str(self.total)
        if self.marksOutOf==''  or self.marksSecured > self.marksOutOf or self.marksSecured<0:
            self.grade=0
            return "Can't find grades with this data!"   
            
        elif self.total>89 and self.total<101:
            self.grade=1
            return "You got A-Grade with "+total+"% of marks"
            
        elif self.total>69 and self.total<90:
            self.grade=2     
            return "You got B-Grade with "+total+"% of marks"
           
        elif self.total>59 and self.total<70:
            self.grade=3
            return "You got C-Grade with "+total+"% of marks"
            
           
        elif self.total>44 and self.total<60:
            self.grade=4
            return "You got D-Grade with "+total+"% of marks"
            
        
        elif self.total<44 and self.total>0:
            self.grade=5
            return "You got F-Grade with "+total+"% of marks"
            
           
    def remarks(self):
        #this will ouput the result according to the grade secured
                    
        if self.grade==0:
            print("Please provide proper values!")
        
        elif self.grade==1:
            print('It is great saying that hard work pays-off! You did it, congratulations!')
           
        elif self.grade==2:
            print('You performed well in your exams.')
           
        elif self.grade==3:
            print("A good grade but not satsfactory!")
        
        elif self.grade==4:
            print("You need to work hard, you passed with a small margin!")
            
        elif self.grade==5:
            print("alas! you didn't made it. You failed!")
