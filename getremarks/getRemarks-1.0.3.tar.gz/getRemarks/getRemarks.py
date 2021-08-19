class Grade:#This module will get the grades of the students according to their marks

    def __init__(self,marksSecured,marksOutOf=None):
        if marksOutOf is None:
            print("Total marks part is missing, should be after marks scored followed by comma. Say (200, 500). WARNING: Re-Run the code from Grade()!")
            
        elif marksOutOf <0 or marksSecured<0:
            print("This module works with postive values only. WARNING: Re-Run the code from Grade()!")
            
        elif marksOutOf==0:
            print("How can total marks be 0? WARNING: Re-Run the code from Grade()!")
    
        else:
            self.marksSecured=marksSecured
            self.marksOutOf=marksOutOf
            self.grade=100
            self.total=(self.marksSecured/self.marksOutOf)*100

    def getGrade(self):#this will calculate grade
        totalValString=str(self.total)
        totalValFloat= float(self.total)
        total= "{:.2f}".format(totalValFloat)
        if self.marksOutOf=='': 
            self.grade=99
            print("How can you expect any result from this module with invalid total marks value!")
        
        elif self.marksSecured>self.marksOutOf:
            self.grade=98
            print("How can you expect any result from this module when you provide more marks scored than total marks!")
        
        elif self.marksSecured<0:            
            self.grade=97
            print("Please provide positive integer values only!")
            
        elif self.total>89 and self.total<101:
            self.grade=1
            print("You got A-Grade with "+total+"% of marks")
            
        elif self.total>69 and self.total<90:
            self.grade=2     
            print("You got B-Grade with "+total+"% of marks")
           
        elif self.total>59 and self.total<70:
            self.grade=3
            print("You got C-Grade with "+total+"% of marks")
            
           
        elif self.total>44 and self.total<60:
            self.grade=4
            print("You got D-Grade with "+total+"% of marks")
            
        
        elif self.total<44 and self.total>0:
            self.grade=5
            print("You got F-Grade with "+total+"% of marks")
            
           
    def remarks(self):
        #this will ouput the result according to the grade secured
                    
        if self.grade==99:
            print("Please provide proper values to get remarks!")
            
        elif self.grade==98:
            print("How can any one get more marks than total marks?")
            
        elif self.grade==97:
            print("Sorry! This module is not designed to work with negative integers.")
        
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
