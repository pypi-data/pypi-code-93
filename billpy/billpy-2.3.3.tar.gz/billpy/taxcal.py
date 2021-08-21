from maths import *
class billpy:
    def findtax(percent,netamount):
        taxamount=mul(netamount,div(percent,100))
        return taxamount