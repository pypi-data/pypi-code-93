#!/usr/bin/env python3

import timeit
from matutil import evalmat


def test():
   print("Starting Timeit Test - matutil")
   amat = [list(range(1,11))]*10
   start = timeit.default_timer()
   evalmat(amat)
   stop = timeit.default_timer()
   print("Time = {:g} sec.".format(stop-start))

   from cmatutil import evalmat as cevalmat
   print("Starting Timeit Test -cmatutil")
   amat = [list(range(1,11))]*10
   start = timeit.default_timer()
   cevalmat(amat)
   stop = timeit.default_timer()
   print("Time = {:g} sec.".format(stop-start))
                                      
if __name__ == "__main__":
   test() 
