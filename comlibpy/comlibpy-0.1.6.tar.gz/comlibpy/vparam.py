
from comlibpy.func import vparam

import operator

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
