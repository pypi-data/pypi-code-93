
from comlibpy.func import vparam, vparam1

import operator
import math

xand = vparam( operator.and_ )
xor = vparam( operator.xor )
xxor = vparam( operator.xor )

xadd = vparam( operator.add )
xsub = vparam( operator.sub )
xmul = vparam( operator.mul )
xdiv = vparam( operator.truediv )
xfloor = vparam( operator.floordiv )
xmod = vparam( operator.mod )
xpow = vparam( operator.pow )

xmin = vparam( min )
xmax = vparam( max )

def ceil(a, b=1):
    if a % b == 0: return a
    return int( math.ceil( a / b ) * b )


def gcd(a,b):
    if a < b:
        a,b = b,a
    remainder = a % b
    if remainder == 0:
        return b
    else:
        return gcd(remainder,b)

def sumwgt(wgt,rate):
    rates = sum(map(lambda x,y: x*y, wgt, rate))
    wgts = sum(iter(wgt))
    return rates / wgts


xceil = vparam1( ceil )
xgcd = vparam( gcd )
xsumwgt = vparam( sumwgt )
