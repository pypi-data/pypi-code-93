'''
Created on 24 nov. 2020

@author: olivier
'''
import unittest
import sys, cProfile, pstats, logging
import random

from pypos3dtu.tuConst import OBJ_FILE_RESSORT, ChronoMem

from pypos3d.wftk.WaveGeom import readGeom

from pypos3d.propslim.MxBasic import MxHeap
from pypos3d.propslim.PropSlim import decimate, edge_info

PROFILING = False

class Test(unittest.TestCase):

  def setUp(self):
    logging.basicConfig(format='%(asctime)s %(module)s.%(funcName)s %(message)s') # , datefmt='%H:%M:%S,uuu')
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


  def testHeap(self):
    h = MxHeap(64)

    e1 = edge_info(1)
    e1.heap_key(-1.0)
    h.insert(e1)

    e2 = edge_info(1)
    e2.heap_key(1.0)
    h.insert(e2)
    print(str(h))

    e3 = edge_info(1)
    e3.heap_key(2.0)
    h.insert(e3)
    print(str(h))

    e4 = edge_info(1)
    e4.heap_key(-.5)
    h.insert(e4)
    print(str(h))
    
    e2.heap_key(75.0)
    h.update(e2)
    print(str(h))
 
    e5 = edge_info(1)
    e5.heap_key(-5.0)
    h.insert(e5)
    print(str(h))
 
    for e in [e1,e2,e3,e4,e5]:
      ex = h.extract()
      h.remove(ex)
      print("e:"+str(ex))
    print(str(h))
 
  def testHeapPerf(self):
    h = MxHeap(64)
    nbtour = 100000
    
    c = ChronoMem.start("HeapPerf-100000")
    for i in range(nbtour):
      e = edge_info(1)
      e.heap_key(float(i)*random.random())
      h.insert(e)
    c.stopRecord("HeapPerf.txt")
      
    # Modif 100%
    for i in range(nbtour):
      e = h.get(random.randint(0,nbtour-1))
      e.heap_key(float(i)*random.random())
      h.update(e)
    
    # Extract 100%
    for i in range(nbtour):
      h.extract()

  def testDecimate(self):
    wg_ressort = readGeom(OBJ_FILE_RESSORT)
    c = ChronoMem.start("decimateMemory11000faces")
    resg = decimate(2800, wg_ressort)
    c.stopRecord("QSlimPerf.txt")

    resg.writeOBJ('tures/ress-dec.obj')

  def testDecimatePHF10k(self):
    wg_phf = readGeom("srcdata/PoserRoot/Runtime/Geometries/ProjectHuman/PHFemaleLowRes.obj")
    
    c = ChronoMem.start("decimate-phf10k")
    resg = decimate(10000, wg_phf)
    c.stopRecord("QSlimPerf.txt")
    resg.writeOBJ('tures/ress-phf10k.obj')


  def testDecimatePHF4k(self):
    wg_phf = readGeom("srcdata/PoserRoot/Runtime/Geometries/ProjectHuman/PHFemaleLowRes.obj")
    
    c = ChronoMem.start("decimate-phf4k")
    resg = decimate(4000, wg_phf)
    c.stopRecord("QSlimPerf.txt")
    resg.writeOBJ('tures/res-phf4k.obj')
    
    # The same with group preservation
    c = ChronoMem.start("decimate-phf4k+Restorations")
    geom = decimate(4000, wg_phf, restoreQuad=True, restoreGrp=True)
    c.stopRecord("QSlimPerf.txt")
    geom.writeOBJ('tures/res-phf4k+Preserv.obj')

    
  def testDecimateTorus(self):
    wg = readGeom("srcdata/LumpyTorusCut.obj")
    
    c = ChronoMem.start("decimate-Torus5k")
    resg = decimate(1765, wg)
    c.stopRecord("QSlimPerf.txt")
    resg.writeOBJ('tures/res-torus1_7k.obj')

  def testCmpJava(self):
    wg = readGeom("srcdata/sphere_cut.obj")
    
    c = ChronoMem.start("decimate-SphereCut225")
    resg = decimate(120, wg)
    c.stopRecord("QSlimPerf.txt")
    resg.writeOBJ('tures/decimate-sphere120.obj')


  def testFrozenFace(self):
    srcGeom = readGeom("srcdata/sphere_cut.obj")

    c = ChronoMem.start("decimate-SphereCut225+FrozenFace")
    geom = decimate(120, srcGeom, lstProtFaces= { 0 })
    c.stopRecord("QSlimPerf.txt")
    geom.writeOBJ('tures/decimate-sphere120.obj')

    c = ChronoMem.start("decimate-SphereCut225+FrozenFace")
    geom = decimate(130, srcGeom, protMat="FrozenMat")
    c.stopRecord("QSlimPerf.txt")
    geom.writeOBJ('tures/decimate-sphere130.obj')


  def testFrozenFaceQuad(self):
    srcGeom = readGeom("srcdata/sphere_cut.obj")

    c = ChronoMem.start("decimate-SphereCut225+FrozenFace")
    geom = decimate(120, srcGeom, lstProtFaces= { 0 }, restoreQuad=True)
    self.assertEqual(geom.getNbFace(), 78)
    c.stopRecord("QSlimPerf.txt")
    geom.writeOBJ('tures/decimate-sphere120+Quad.obj')


  def testFrozenEdge(self):
    srcGeom = readGeom("srcdata/LumpyTorusCut.obj")
    c = ChronoMem.start("decimate-Torus+FrozenEgdeMat")
    geom = decimate(1700, srcGeom, protEdges=True, protMat="FrozenMat")
    c.stopRecord("QSlimPerf.txt")
    geom.writeOBJ('tures/res-torus1_7k-protected.obj')

  # Non reachable target
  def testFrozenMatDeg(self):
    srcGeom = readGeom("srcdata/LumpyTorusCut.obj")
    geom = decimate(1700, srcGeom, protEdges=True, protMat="Mat1")
    self.assertGreater(geom.getNbFace(), 1700)
    
  # Non reachable target
  def testPyPos3dOOO(self):
    srcGeom = readGeom("srcdata/p51d-lBomb.obj")
    geom = decimate(1000, srcGeom) # , protEdges=True, protMat="Mat1")
    self.assertGreater(geom.getNbFace(), 998)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()