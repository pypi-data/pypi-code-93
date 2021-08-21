from billpy.maths import maths 
class billpy:
    def findtax(percent,netamount):
        taxamount=maths.mul(netamount,maths.div(percent,100))
        return taxamount