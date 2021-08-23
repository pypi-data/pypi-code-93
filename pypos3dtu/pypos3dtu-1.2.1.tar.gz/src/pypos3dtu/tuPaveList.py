'''
Created on 18 August 2020

@author: olivier
'''
import unittest
import sys, cProfile, pstats, logging

from pypos3dtu.tuConst import ChronoMem
from pypos3d.wftk.WFBasic import TexCoord2f
from pypos3d.wftk.WaveGeom import readGeom
from pypos3d.wftk.PaveList2D import PaveList2D

PROFILING = False

class Test(unittest.TestCase):

  def setUp(self):
    logging.getLogger().setLevel(logging.INFO)
    if PROFILING:
      self.pr = cProfile.Profile()
      self.pr.enable()


  def tearDown(self):
    if PROFILING:
      self.pr.disable()
      sortby = 'time'
      ps = pstats.Stats(self.pr, stream=sys.stdout).sort_stats(sortby)
      ps.print_stats()

  def test4x4(self):
    l = [ TexCoord2f(0.0,0.0), TexCoord2f(1.0,1.0), TexCoord2f(0.0,0.5), \
         TexCoord2f(0.5,0.0), TexCoord2f(0.5,0.5), TexCoord2f(0.1,0.1), \
         TexCoord2f(0.8,0.8) ]

    pl = PaveList2D(n=2,texList=l)
    
    idx = pl.search( TexCoord2f(0.0,0.0) )
    self.assertEqual(idx, 0)

    idx = pl.search( TexCoord2f(0.5,0.5) )
    self.assertEqual(idx, 4)

  def testAddSearch(self):    
    objsrc = readGeom('srcdata/TerrePoignees+Trou.obj')

    l = [ TexCoord2f(0.0,0.0), TexCoord2f(1.0,1.0), TexCoord2f(0.0,0.5), \
         TexCoord2f(0.5,0.0), TexCoord2f(0.5,0.5), TexCoord2f(0.1,0.1), \
         TexCoord2f(0.8,0.8) ]

    plterre = PaveList2D(n=2,texList=objsrc.texList)
    
    idx = plterre.search( TexCoord2f(0.0,0.0) )
    self.assertEqual(idx, -1)

    idx = plterre.search( TexCoord2f(0.5,0.5) )
    self.assertEqual(idx, 136)
  
    idx = plterre.IndexAdd(TexCoord2f(0.0,0.0))
    self.assertEqual(idx, 286)

    idx = plterre.IndexAdd(TexCoord2f(0.5,0.5))
    self.assertEqual(idx, 136)

    idx = plterre.IndexAdd(TexCoord2f(0.5+1e-8,0.5))
    self.assertEqual(idx, 136)

    print(plterre.statStr())

  def testPerf1(self):    
    objsrc = readGeom('srcdata/TerrePoignees+Trou.obj')

    l = [ TexCoord2f(0.0,0.0), TexCoord2f(1.0,1.0), TexCoord2f(0.0,0.5), \
         TexCoord2f(0.5,0.0), TexCoord2f(0.5,0.5), TexCoord2f(0.1,0.1), \
         TexCoord2f(0.8,0.8) ]

    c = ChronoMem('Add Terre in 4x4')
    plterre4 = PaveList2D(n=4,texList=objsrc.getTexList())
    c.stopPrint()
    print(plterre4.statStr())

    c = ChronoMem('Add Terre in 16x16')
    plterre16 = PaveList2D(n=16,texList=objsrc.getTexList())
    c.stopPrint()
    print(plterre16.statStr())

    c = ChronoMem('Search Terre in 4x4')
    for t in l+objsrc.texList:
      idx = plterre4.search(t)
    c.stopPrint()


  def testPerf2(self):    
    objsrc = readGeom('srcdata/ressort.obj')

    l = [ TexCoord2f(0.0,0.0), TexCoord2f(1.0,1.0), TexCoord2f(0.0,0.5), \
         TexCoord2f(0.5,0.0), TexCoord2f(0.5,0.5), TexCoord2f(0.1,0.1), \
         TexCoord2f(0.8,0.8) ]

    c = ChronoMem('Add Ressort in 16x16')
    pl16 = PaveList2D(n=16,texList=objsrc.getTexList())
    c.stopPrint()
    print(pl16.statStr())
    print('Insert Speed:{0:.1f} pt/s'.format( len(objsrc.texList)/(c.tf-c.t0)))

    c = ChronoMem('Add Ressort in 32x32')
    for i in range(0,10):
      pl32 = PaveList2D(n=32,texList=objsrc.getTexList())
    c.stopPrint()
    print(pl32.statStr())
    print('Insert Speed:{0:.1f} pt/s'.format( 10*len(objsrc.texList)/(c.tf-c.t0)))

  def testCoverage(self):    
    objsrc = readGeom('srcdata/ressort.obj')

    l = [ TexCoord2f(0.0,0.0), TexCoord2f(1.0,1.0), TexCoord2f(0.0,0.5), \
         TexCoord2f(0.5,0.0), TexCoord2f(0.5,0.5), TexCoord2f(0.1,0.1), \
         TexCoord2f(0.8,0.8) ]

    pl16 = PaveList2D(n=16,texList=objsrc.getTexList())

    self.assertEqual(pl16.length(), 5664)
    
    pl16.addList(l)
    
    self.assertEqual(pl16.length(), 5671)
    
    pl16.fill([])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
