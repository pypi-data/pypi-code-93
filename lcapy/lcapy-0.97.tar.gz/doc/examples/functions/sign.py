from matplotlib.pyplot import savefig, style
from lcapy import *

style.use('function.mplstyle')
sign(t).plot((-2, 2), title='sign(t)')
savefig(__file__.replace('.py', '.png'))

