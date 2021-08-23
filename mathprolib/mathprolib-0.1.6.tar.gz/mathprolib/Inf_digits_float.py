from functools import total_ordering


class CalculateError(Exception):
    pass


@total_ordering
class InfDigitsFloat:
    def __init__(self,float_string):
        self.integer = float_string.split(".")[0]
        self.decmincal_part = float_string.split(".")[1].rstrip('0')
    
    def __str__(self):
        return f"{self.integer}.{self.decmincal_part}"
        
    def __eq__(self,other):
        return str(self) == str(other) if isinstance(other,InfDigitsFloat) else eval(str(self)) == other

    def __lt__(self,other):
        if isinstance(other,InfDigitsFloat):
            return self.integer < other.integer or (self.decmincal_part < other.decmincal_part)
        elif isinstance(other,(int,float)):
            return eval(str(self)) < other
        raise CalculateError
        

    def __add__(self,other):
        if isinstance(other,InfDigitsFloat):
            #1.进行计算小数位数
            k = max(len(self.decmincal_part),len(other.decmincal_part))
            #2.进行加法
            m = eval(self.decmincal_part) + eval(other.decmincal_part)
            m = str(m)
            n = eval(self.integer) + eval(other.integer)
            #3.点上小数点
            decmincal_part = m[:-k]+"."+m[-k:]
            #4.进位处理
            integer = int(eval(decmincal_part))+n
            decmincal_part = decmincal_part.split(".")[1]
            return InfDigitsFloat(f"{integer}.{decmincal_part}")
        elif isinstance(other,int):
            return self+InfDigitsFloat(f"{other}.0")
        elif isinstance(other,float):
            return self+InfDigitsFloat(str(other))
        raise CalculateError

    
if __name__ == "__main__":
    print(InfDigitsFloat("1.2345")+InfDigitsFloat("1.2345"))