'''
Created on 13 avr. 2020

@author: olivier
'''

import math

import unittest
import sys, cProfile, pstats, logging

from langutil import  C_ERROR
from pypos3d.wftk import WFBasic
from pypos3d.wftk.WFBasic import Point3d, Vector3d, Edge, CreateLoop, FaceCut,\
  CoordSyst
from pypos3d.wftk.WaveGeom import readGeom, PlaneCut, PlaneSlice, PlaneSplit, RadialScaleRemesh
from pypos3dtu.tuConst import ChronoMem

# ===================================================================================================
# Unit Tests Part
# ===================================================================================================
def ToEdges(vxtab):
  return [ (vxtab[i], vxtab[i+1]) for i in range(0, len(vxtab)-1) ] + [ (vxtab[-1], vxtab[0]), ]

def EdgeToIdxStr(coordList, EdgeLst):
  #return str( [ "(" + str(coordList.index(e[0])) + "," + str(coordList.index(e[1])) + ")" for e in EdgeLst ] )
  return str( [ ( coordList.index(e[0]), coordList.index(e[1]) ) for e in EdgeLst ] )


WFBasic.PYPOS3D_TRACE=False
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

  def coordListAssert(self, nwg, lpt):
    for i,pres in enumerate(lpt):
      self.assertAlmostEqual(nwg.coordList[i].x, pres.x, msg='coordList['+str(i)+'].x', delta=1e-6)
      self.assertAlmostEqual(nwg.coordList[i].y, pres.y, msg='coordList['+str(i)+'].y', delta=1e-6)
      self.assertAlmostEqual(nwg.coordList[i].z, pres.z, msg='coordList['+str(i)+'].z', delta=1e-6)


  def testSegmentIntersect(self):
    p0 = Point3d(-1.0, -1.0,  0.0)
    p1 = Point3d( 1.0, -1.0,  0.0)
    p2 = Point3d( 1.0,  1.0,  0.0)
    p3 = Point3d(-1.0,  1.0,  0.0)
    
    e0 = Edge(p0, p0)
    e1 = Edge(p1, p3)
    code,t = e0.intersect(e1)
    self.assertEqual(code, C_ERROR)
    
    e0 = Edge(p1, p2)
    e1 = Edge(p0, p3)
    code,t = e0.intersect(e1)
    self.assertEqual(code, WFBasic.C_COLINEAR)
    self.assertAlmostEqual(t, sys.float_info.max, delta=1e-6)

    e0 = Edge(p0, p2)
    e1 = Edge(p1, p3)    
    code,t = e0.intersect(e1)
    self.assertEqual(code, WFBasic.C_INTERSECT)
    self.assertAlmostEqual(t, 0.5, delta=1e-6)

    e0 = Edge(p0.add([0.0,0.0,1.0]), p2)
    e1 = Edge(p1, p3)
    code,t = e0.intersect(e1)
    self.assertEqual(code, WFBasic.C_NOT_COPLANAR)
    self.assertAlmostEqual(t, sys.float_info.max, delta=1e-6)

    e0 = Edge(p0, p2.add([0.0,0.0,1.0]))
    e1 = Edge(p1.add([0.0,0.0,1.0]), p3.add([0.0,0.0,1.0]))
    code,t = e0.intersect(e1)
    self.assertEqual(code, WFBasic.C_INTERSECT)
    self.assertAlmostEqual(t, 0.5, delta=1e-6)

    p0 = Point3d( 1.0, 1.0,  1.0)
    p1 = Point3d( 5.0, 5.0,  5.0)
    u  = Vector3d(p1.x-p0.x, p1.y-p0.y, p1.z-p0.z)

    ud = Vector3d(u).scale(2.0)
    p2 = Point3d(p0).add(ud)
    p3 = Point3d(p1).add(ud)
    e0 = Edge(p0, p1)
    e1 = Edge(p2, p3)
    code,t = e0.intersect(e1)
    self.assertEqual(code, WFBasic.C_COLINEAR)
    self.assertAlmostEqual(t, 2.0, delta=1e-6)

    ud = Vector3d(u).scale(0.1)
    p2 = Point3d(p0).add(ud)
    p3 = Point3d(p1).add(ud)
    e0 = Edge(p0, p1)
    e1 = Edge(p2, p3)
    code,t = e0.intersect(e1)
    self.assertEqual(code, WFBasic.C_COLINEAR_CROSS)
    self.assertAlmostEqual(t, 0.1, delta=1e-6)

    e0 = Edge(p0, p2)
    e1 = Edge(p2, p3)
    code,t = e0.intersect(e1)
    self.assertEqual(code, WFBasic.C_COLINEAR_CROSS)
    self.assertAlmostEqual(t, 1.0, delta=1e-6)

    code,t = e1.intersect(e0)
    self.assertEqual(code, WFBasic.C_COLINEAR_CROSS)
    self.assertAlmostEqual(t, -0.1, delta=1e-6) # The second of point of e0 crosses


  def testCreateLoopBench(self):
    for n in range(1,4):
      lstEdge = []
      
      for i in range(0, n):
        for j in range(0,2):
          p0 = Point3d(float(i), float(j), 0.0)
          p1 = Point3d(p0).add([1.0, 0.0, 0.0])
          p2 = Point3d(p0).add([1.0, 1.0, 0.0])
          p3 = Point3d(p0).add([0.0, 1.0, 0.0])
          lstEdge += ToEdges([p0,p1,p2,p3])
          
      c = ChronoMem.start('CreateLoopNEW:'+str(n))
      loop, lst, s = CreateLoop(lstEdge) 
      c.stopPrint()
      
      

  def testCreateLoop(self):
    triangle = ToEdges([ Point3d(-1.0, 0.0, -1.0), Point3d(-1.0, 0.0, 1.0), Point3d(1.0, 0.0, -1.0) ])
    carre = ToEdges([ Point3d(-1.0, 0.0, -1.0), Point3d(-1.0, 0.0, 1.0), Point3d(1.0, 0.0, 1.0), Point3d(1.0,0.0, -1.0)])

    loop, lst, s = CreateLoop(triangle) 
    self.assertEqual(len(loop), 1)
    self.assertEqual(EdgeToIdxStr(lst, loop[0]), '[(0, 1), (1, 2), (2, 0)]')


    loop, lst, s = CreateLoop(carre)
    self.assertEqual(len(loop), 1)
    self.assertEqual(EdgeToIdxStr(lst, loop[0]), '[(0, 1), (1, 2), (2, 3), (3, 0)]')
    
    
    pentagone = ToEdges([ Point3d(-1.0, 0.0, -1.0), Point3d(-1.0, 0.0, 1.0), Point3d(1.0, 0.0, 1.0), Point3d(1.0,0.0, -1.0), Point3d(1.0, 2.0, -1.0) ])
    loop, lst, s = CreateLoop(pentagone)
    self.assertEqual(len(loop), 1)
    self.assertEqual(EdgeToIdxStr(lst, loop[0]), '[(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]')
    
    # Change edge order
    e = pentagone[0]
    pentagone[0] = pentagone[3]
    pentagone[3] = e
    loop, lst, s = CreateLoop(pentagone)
    self.assertEqual(len(loop), 1)
    self.assertEqual(EdgeToIdxStr(lst, loop[0]), '[(0, 1), (1, 4), (4, 2), (2, 3), (3, 0)]')
    
    
    p0 = Point3d(-1.0, -1.0,  0.0)
    p1 = Point3d( 1.0, -1.0,  0.0)
    p2 = Point3d( 1.0,  1.0,  0.0)
    p3 = Point3d(-1.0,  1.0,  0.0)

    p4 = Point3d( 3.0, -1.0,  0.0)
    p5 = Point3d( 3.0,  1.0,  0.0)
    p6 = Point3d( 3.0,  2.0,  0.0)
    p7 = Point3d( 1.0,  2.0,  0.0)
    p8 = Point3d( 4.0, -1.0,  0.0)


    grandL = ToEdges([ p0,p1,p4,p5,p6,p7,p2,p3])
    loop, lst, s = CreateLoop(grandL)    
    self.assertEqual(len(loop), 1)
    self.assertEqual(EdgeToIdxStr(lst, loop[0]), '[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0)]')

    loop, lst, s = CreateLoop(carre + ToEdges([p0,p4,p5,p2]))
    self.assertEqual(len(loop), 2)
    for f in loop: print(EdgeToIdxStr(lst, f))
    self.assertEqual(EdgeToIdxStr(lst, loop[0]), '[(0, 1), (1, 2), (2, 3), (3, 0)]')
    self.assertEqual(EdgeToIdxStr(lst, loop[1]), '[(4, 5), (5, 6), (6, 7), (7, 4)]')
    
    loop, lst, s = CreateLoop(grandL+ToEdges([p4,p5,p8]) + [ (p3,p7), ])
    self.assertEqual(len(loop), 2)
    self.assertEqual(s, 11)
    for f in loop: print(EdgeToIdxStr(lst, f))
    self.assertEqual(EdgeToIdxStr(lst, loop[0]), '[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0)]')
    self.assertEqual(EdgeToIdxStr(lst, loop[1]), '[(2, 3), (3, 8), (8, 2)]')
    
    loop, lst, s = CreateLoop(grandL+ToEdges([p2,p1,p4,p8,p7]))    
    self.assertEqual(len(loop), 2)
    #Plot(loop[0],loop[1])
    self.assertEqual(s, 13)
    for f in loop: print(EdgeToIdxStr(lst, f))
    self.assertEqual(EdgeToIdxStr(lst, loop[0]), '[(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 0)]')
    self.assertEqual(EdgeToIdxStr(lst, loop[1]), '[(1, 6), (6, 5), (5, 8), (8, 2), (2, 1)]')
    

  def testFindEdges(self):
    objsrc = readGeom('srcdata/CutterT4-Manchon.obj')
    
    part = objsrc.getGroup("Cube3")
 
    topLoop = part.findEdges()
    for e in topLoop:
      print("{0:d} : {1:s} - {2:s} - {3:d}- {4:d}".format(e.hashCode(), str(e.p0), str(e.p1), e.idx0, e.idx1))
    
    part = objsrc.getGroup("ManchonVert")
    topLoop = part.findEdges()      
    self.assertEqual(32, len(topLoop))

    topLoop = part.findEdges(geomcond = lambda p: (p.y < 0.1) )
    self.assertEqual(16, len(topLoop))

  
  def testPlaneSlice(self):

    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)

    objsrc = readGeom('srcdata/CutterT4-Manchon.obj')
    part = objsrc.getGroup("ManchonCourt")
    nLoop = PlaneSlice(part, center05, Oz, Ox)     
    for e in nLoop: print(str(e))
    self.assertEqual(16, len(nLoop))

    part = objsrc.getGroup("ManchonVert")
    nLoop2 = PlaneSlice(part, center05, Oz, Ox)     
    for i,e in enumerate(nLoop2): 
      print(str(e) + '-' + 'OK' if e==nLoop[i] else '==> KO')
      
    self.assertEqual(16, len(nLoop))

    part = objsrc.getGroup("Manchon")
    nLoop = PlaneSlice(part, Point3d(0.5, 2, 0.0), Oy, Oz)     
    for e in nLoop: print(str(e))
    self.assertEqual(16, len(nLoop))

    # Test with textured object
    part = objsrc.getGroup("Cube3")
    nLoop = PlaneSlice(part, center05, Oz, Ox)     
    for e in nLoop: print(str(e))
    self.assertEqual(4, len(nLoop))
    self.assertAlmostEqual(nLoop[0].p0.texture.x, 0.75, delta=1e-6)
    self.assertAlmostEqual(nLoop[0].p0.texture.y, 0.1875, delta=1e-6)
 
    self.assertAlmostEqual(nLoop[3].p0.texture.x, 1.0, delta=1e-6)
    self.assertAlmostEqual(nLoop[3].p0.texture.y, 0.1875, delta=1e-6)
    self.assertAlmostEqual(nLoop[3].p1.texture.x, 0.75, delta=1e-6)
    self.assertAlmostEqual(nLoop[3].p1.texture.y, 0.1875, delta=1e-6)


  def testPlaneSliceScale(self):
    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)

    objsrc = readGeom('srcdata/CutterT4-Manchon.obj')
    # Test with textured object
    part = objsrc.getGroup("Cube3")
    nLoop = PlaneSlice(part, center05, Oz, Ox, radialScale=0.5)     
    for e in nLoop:
      print(str(e))
    self.assertEqual(str(nLoop[0]), 'Edge(-1, -1, V(-0.5,0.5,0.5), V(-0.5,0.5,-0.5))')
    self.assertEqual(str(nLoop[1]), 'Edge(-1, -1, V(-0.5,0.5,-0.5), V(0.5,0.5,-0.5))')
    self.assertEqual(str(nLoop[2]), 'Edge(-1, -1, V(0.5,0.5,-0.5), V(0.5,0.5,0.5))')
    self.assertEqual(str(nLoop[3]), 'Edge(-1, -1, V(0.5,0.5,0.5), V(-0.5,0.5,0.5))')
      
    self.assertEqual(4, len(nLoop))
    self.assertAlmostEqual(nLoop[0].p0.texture.x, 0.75, delta=1e-6)
    self.assertAlmostEqual(nLoop[0].p0.texture.y, 0.1875, delta=1e-6)
 
    self.assertAlmostEqual(nLoop[3].p0.texture.x, 1.0, delta=1e-6)
    self.assertAlmostEqual(nLoop[3].p0.texture.y, 0.1875, delta=1e-6)
    self.assertAlmostEqual(nLoop[3].p1.texture.x, 0.75, delta=1e-6)
    self.assertAlmostEqual(nLoop[3].p1.texture.y, 0.1875, delta=1e-6)




  def testRadialScaleMeshP51D(self):
    # Warning: Cutting planes were not correctly exported by Wing3d
    # p51d-lBomb.obj hacked to remove the bad first faces of those planes
    objsrc = readGeom('srcdata/p51d-lBomb.obj')
    part = objsrc.getGroup("lBomb")
    topP = objsrc.getGroup("lBomb_CutTop")
    botP = objsrc.getGroup("lBomb_CutBot")
     
    grpAnn = part.extractFaces( materialName='AnneauBomb') # , inGeom=True)
     
    nwg,cd = RadialScaleRemesh(part, botP, nbSlice=10, repOrtopPlane=topP, reMesh=True, cutBottom=False, cutTop=False, \
                              fillHole=False, filledHoleMat=None)
    nwg.writeOBJ('tures/lBomb-remeshed.obj')
     
    # Put back the extrated faces
    nwg.getGroups()[0].fusion(grpAnn) 
    nwg.writeOBJ('tures/lBomb-finished.obj')


  #
  # Remeshing and rescale
  # 
  def testRadialScaleMeshPlan(self):
        
    objsrc = readGeom('srcdata/RadialScaleMesh.obj')
    part = objsrc.getGroup("Cylinder1")
    topP = objsrc.getGroup("topP")
    botP = objsrc.getGroup("botP")
    #center, eu, ev = botP.calcCoordSyst()
    
    nwg,cd = RadialScaleRemesh(part, botP, dh=0.025, ds=0.01, nbSlice=2, repOrtopPlane=topP, \
                               reScale=True, tabScale = [ 0.70*0.85*0.95, 0.85*0.95, 0.95 ], \
                               reMesh=True, cutBottom=True, fillHole=False, filledHoleMat='filledBottomMat')

    nwg.writeOBJ("tures/Remeshed-Cylinder-Plans.obj")


  def testRadialMesh(self):
    
    #WFBasic.PYPOS3D_TRACE = True
    c = ChronoMem.start("PlaneCut.RadiaMesh All")
      
    center01 = Point3d(0.0,0.1,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
        
    objsrc = readGeom('srcdata/CutterT4-Manchon.obj')
    part = objsrc.getGroup("Cube3")
    nwg,cd = RadialScaleRemesh(part, center01, Oz, Ox, 0.6, nbSlice=4, reMesh=True, cutTop=False, cutBottom=True, fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-Cube3.obj")

    nwg,cd = RadialScaleRemesh(part, center01, Oz, Ox, 0.6, nbSlice=4, reMesh=True, cutTop=True, cutBottom=True, fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-Cube3+Cut.obj")
    
    center05 = Point3d(0.0,0.5,0.0)
    theta = 15.0*math.pi/180.0
    MRotZ = [ \
      [ math.cos(theta), - math.sin(theta), 0.0], \
      [ math.sin(theta),   math.cos(theta), 0.0 ], \
      [             0.0,               0.0, 1.0 ], \
      ]
    ev = Ox.Lin33(MRotZ)

    wgmanchon = readGeom('srcdata/CutterT4-ManchonVert.obj')
    part = wgmanchon.getGroup("ManchonVert")
    nwg,cd = RadialScaleRemesh(part, center05, Oz, ev, 1.0, nbSlice=5, reMesh=True, cutBottom=True)
    nwg.writeOBJ("tures/Remeshed-ManchonVertRotZ.obj")

    part = wgmanchon.getGroup("ManchonVert")
    nwg,cd = RadialScaleRemesh(part, center05, Oz, ev, 1.0, nbSlice=5, reMesh=True, cutTop=True, cutBottom=True, fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-ManchonVertRotZ+Cut.obj")

    objsrc = readGeom('srcdata/CutterCylindre0.obj')
    part = objsrc.getGroup("Cylinder1")
    center0125 = Point3d(0.0, 0.1875, 0.0)
   
    nwg,cd = RadialScaleRemesh(part, center0125, Oz, Ox, 1.5, nbSlice=5, cutTop=True, cutBottom=True) # , fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-Cylinder0+Cut.obj")

    nwg,cd = RadialScaleRemesh(part, center0125, Oz, Ox, 1.5, nbSlice=5, cutTop=False, cutBottom=True, fillHole=True, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-Cylinder0+Cut+Filled.obj")

    objsrc = readGeom('srcdata/CutterT4-Manchon.obj')
    part = objsrc.getGroup("ManchonVert")
    part.sanityCheck()
    nwg,cd = RadialScaleRemesh(part, center01, Oz, Ox, 1.0, nbSlice=5, cutTop=True, cutBottom=True) # , fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-ManchonVert.obj")


    objsrc = readGeom('srcdata/CutterT4-Manchon.obj')
    part = objsrc.getGroup("ManchonVert")
    part.sanityCheck()
    nwg,cd = RadialScaleRemesh(part, center01, Oz, Ox, 1.0, nbSlice=5, tabScale=[0.2, 0.2, 0.3, 0.3, 0.5, 0.8], reScale=True, reMesh=True, cutTop=True, cutBottom=True) # , fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-ManchonVert+Scale.obj")
    
    center08 = Point3d(0.0,-0.8,0.0)
    part = readGeom('srcdata/CutterT4-Sablier.obj').getGroup("Sablier")
    nwg,cd = RadialScaleRemesh(part, center08, Oz, Ox, 1.2, nbSlice=17, reMesh=True, cutTop=True, cutBottom=True) # , fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-Sablier-17.obj")

    nwg,cd = RadialScaleRemesh(part, center08, Oz, Ox, 1.2, nbSlice=20, reMesh=True, cutTop=True, cutBottom=True) # , fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-Sablier-20.obj")

    nwg,cd = RadialScaleRemesh(part, center08, Oz, Ox, 1.2, nbSlice=3, reMesh=True, cutTop=True, cutBottom=True) # , fillHole=False, filledHoleMat='Hole')
    nwg.writeOBJ("tures/Remeshed-Sablier-03.obj")

    c.stopRecord("tuPlaneCut.txt")
     

  # ---------------------------------------------------------------------------
  # Cut Cube along standard axis
  #
  def testRadialScaleRemesh(self):
    center = Point3d(0.0,0.1875,0.0)
    
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oz = Vector3d(0.0, 0.0, -1.0)
    
    objsrc = readGeom('srcdata/CutterCylindre0.obj')
    part = objsrc.getGroup("Cylinder1")
    nwg,cd = RadialScaleRemesh(part, center, Ox, Oz, 1.0, reScale=True)
    nwg.writeOBJ("tures/CutterCylindre0-cutOy.obj")


    nwg,cd = RadialScaleRemesh(part, center, Ox, Oz, 1.0, minLength=0.01, repOrtopPlane=objsrc.getGroup('topP'), reScale=True, reMesh=True) #, fillHole=False)
    nwg.writeOBJ("tures/CutterCylindre0-cutOy+Plane.obj")


  # ---------------------------------------------------------------------------
  # Cut Cube along standard axis
  #
  def testRadialScale(self):
    center = Point3d(0.0,0.1875,0.0)
    
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oz = Vector3d(0.0, 0.0, -1.0)
    
    objsrc = readGeom('srcdata/CutterCylindre0.obj')
    part = objsrc.getGroup("Cylinder1")
    part.RadialScale(center, Ox, Oz, 0.1, 0.2, 1.0)
    objsrc.writeOBJ("tures/RSCutterCylindre0-cutOy.obj")

    # FIXME: This option does not work!!
    # part.RadialScale(center, Ox, Oz, 0.1, 0.2, 1.0, topPlaneGrp=objsrc.getGroup('topP'))

    part.FaceRadialScale(center, Ox, Oz, 0.85, lstFaceNo=(1,2,3))

    part.FaceRadialScale(center, Ox, Oz, 0.85, materialName='Skin')

    #nwg,cd = RadialScaleRemesh(part, center, Ox, Oz, 1.0, minLength=0.01, repOrtopPlane=objsrc.getGroup('topP'), reScale=True, reMesh=True) #, fillHole=False)
    #nwg.writeOBJ("tures/CutterCylindre0-cutOy+Plane.obj")


 

  # ---------------------------------------------------------------------------
  # Cut Cube along standard axis
  #
  def testFaceRemove(self):
    
    objsrc = readGeom('srcdata/CutterCubey0_25Tex.obj')
    cube = objsrc.getGroup("Cubey0_25")
    cube.removeFaces([0])
    objsrc.writeOBJ("tures/Cubey0_25Tex-Rem0.obj")

    objsrc = readGeom('srcdata/CutterCubeTriy0_25.obj')
    cubeTriY0_25 = objsrc.getGroup("Cubey0_25Tri")
    cubeTriY0_25.removeFaces([1,8,7])
    objsrc.writeOBJ("tures/Cubey0_25Tex-Rem2.obj")
    

  def testFaceCut(self):
    vnorm = Vector3d(0.0,0.0,1.0)
    triangle = [ Point3d(-1.0, 0.0, -1.0), Point3d(-1.0, 0.0, 1.0), Point3d(1.0, 0.0, -1.0) ]
    carre = [ Point3d(-1.0, 0.0, -1.0), Point3d(-1.0, 0.0, 1.0), Point3d(1.0, 0.0, 1.0), Point3d(1.0,0.0, -1.0)]

    lstFace, lstEdges, multi = FaceCut( ToEdges(triangle), vnorm, False, False, 0.0)
    self.assertEqual(3, len(lstFace))
    self.assertEqual(Point3d(-1.0,0.0,0.0), lstEdges[0][0])
    self.assertEqual(Point3d(0.0,0.0,0.0), lstEdges[0][1])

    lstFace, lstEdges, multi = FaceCut( ToEdges(carre), vnorm, False, False, 0.0)
    self.assertEqual(4, len(lstFace))
    self.assertEqual(Point3d(-1.0,0.0,0.0), lstEdges[0][0])
    self.assertEqual(Point3d(1.0,0.0,0.0), lstEdges[0][1])
    
    pentagone = carre[0:2] + [ Point3d(0.0, 0.0, 2.0), ] + carre[2:]
    lstFace, lstEdges, multi = FaceCut( ToEdges(pentagone), vnorm, False, False, 0.0)

    self.assertTrue(multi)
    self.assertEqual(2, len(lstFace))
    self.assertEqual(4, len(lstFace[0]))
    self.assertEqual(4, len(lstFace[1]))
    self.assertEqual(Point3d(-1.0,0.0,0.0), lstEdges[0][0])
    self.assertEqual(Point3d(1.0,0.0,0.0), lstEdges[1][1])

    hexagone = pentagone[0:5] + [ Point3d(0.0, 0.0, -2.0), ] 
    lstFace, lstEdges, multi = FaceCut( ToEdges(hexagone), vnorm, False, False, 0.0)

    self.assertTrue(multi)
    self.assertEqual(2, len(lstFace))
    self.assertEqual(5, len(lstFace[0]))
    self.assertEqual(3, len(lstFace[1]))
    self.assertEqual(Point3d(-1.0,0.0,0.0), lstEdges[0][0])
    self.assertEqual(Point3d(1.0,0.0,0.0), lstEdges[1][1])
    
    heptagone = [ hexagone[0], Point3d(-2.0, 0.0, 0.0) ] + hexagone[1:] 
    lstFace, lstEdges, multi = FaceCut( ToEdges(heptagone), vnorm, False, False, 0.0)

    self.assertTrue(multi)
    self.assertEqual(3, len(lstFace))
    self.assertEqual(4, len(lstFace[0]))
    self.assertEqual(4, len(lstFace[1]))
    self.assertEqual(3, len(lstFace[2]))
    self.assertEqual(Point3d(-2.0,0.0,0.0), lstEdges[0][0])
    self.assertEqual(Point3d(0.0,0.0,0.0), lstEdges[1][1])
    self.assertEqual(Point3d(1.0,0.0,0.0), lstEdges[2][1])

    # The other heptagone    
    octogone = heptagone[:5] + [ Point3d(2.5, 0.0, 0.0), ] + heptagone[5:] 
    lstFace, lstEdges, multi = FaceCut( ToEdges(octogone), vnorm, False, False, 0.0)

    self.assertTrue(multi)
    self.assertEqual(3, len(lstFace))
    self.assertEqual(3, len(lstFace[0]))
    self.assertEqual(5, len(lstFace[1]))
    self.assertEqual(3, len(lstFace[2]))
    self.assertEqual(Point3d(-2.0,0.0,0.0), lstEdges[0][0])
    self.assertEqual(Point3d(0.0,0.0,0.0), lstEdges[1][1])
    self.assertEqual(Point3d(2.5,0.0,0.0), lstEdges[2][1])
    
    # Change the Start Point to enhance coverage
    heptagone = hexagone[1:] + [ hexagone[0], ]  
    lstFace, lstEdges, multi = FaceCut( ToEdges(heptagone), vnorm, False, False, 0.0)
    self.assertTrue(multi)
    self.assertEqual(2, len(lstFace))
    self.assertEqual(5, len(lstFace[0]))
    self.assertEqual(3, len(lstFace[1]))

    heptagone = hexagone[1:] + [ hexagone[0], ]  
    lstFace, lstEdges, multi = FaceCut( ToEdges(heptagone), vnorm, False, False, 0.0)
    self.assertTrue(multi)
    self.assertEqual(2, len(lstFace))
    self.assertEqual(5, len(lstFace[0]))
    self.assertEqual(3, len(lstFace[1]))
    



  # ---------------------------------------------------------------------------
  # Cut Cube along standard axis
  #
  def testCutCubeAxes(self):
    origin = Point3d(0.0,0.0,0.0)
    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    objsrc = readGeom('srcdata/CutterCubey0_25.obj')
    cube = objsrc.getGroup("Cubey0_25")

    # Cut at the bottom on the cube
    center25 = Point3d(0.0,-0.25,0.0)
    nwg,cd = PlaneCut(cube, center25, Ox, Vector3d(Oz).neg() )
    nwg.writeOBJ("tures/Cubey0_25-cutOy-RAZ.obj")
    
    nwg,cd = PlaneCut(cube, origin, Ox, Oy )
    self.coordListAssert(nwg, [ Point3d(-0.5,-0.25,-0.5), \
                 Point3d(-0.5,-0.25,0.5), \
                 Point3d(-0.5,0.75,-0.5), \
                 Point3d(-0.5,0.75,0.5), \
                 Point3d(0.5,-0.25,-0.5), \
                 Point3d(0.5,-0.25,0.5), \
                 Point3d(0.5,0.75,-0.5), \
                 Point3d(0.5,0.75,0.5), \
                 Point3d(0.5,-0.25,0), \
                 Point3d(-0.5,-0.25,0), \
                 Point3d(-0.5,0.75,0), \
                 Point3d(0.5,0.75,0) ])
      
    nwg.writeOBJ("tures/Cubey0_25-cutOz.obj") # Ok 4-juin-2020 a 6h20

    objsrc = readGeom('srcdata/CutterCubey0_25.obj')
    cube = objsrc.getGroup("Cubey0_25")
    nwg,cd = PlaneCut(cube, origin, Oy, Oz )
    self.coordListAssert(nwg, [ Point3d(-0.5,-0.25,-0.5), \
                 Point3d(-0.5,-0.25,0.5), \
                 Point3d(-0.5,0.75,-0.5), \
                 Point3d(-0.5,0.75,0.5), \
                 Point3d(0.5,-0.25,-0.5), \
                 Point3d(0.5,-0.25,0.5), \
                 Point3d(0.5,0.75,-0.5), \
                 Point3d(0.5,0.75,0.5), \
                 Point3d(0.0,-0.25,-0.5), \
                 Point3d(0.0,-0.25,0.5), \
                 Point3d(0.0,0.75,0.5), \
                 Point3d(0.0,0.75,-0.5) ])
    nwg.writeOBJ("tures/Cubey0_25-cutOx.obj")

    objsrc = readGeom('srcdata/CutterCubey0_25.obj')
    cube = objsrc.getGroup("Cubey0_25")
    nwg,cd = PlaneCut(cube, origin, Oz, Ox )
    self.coordListAssert(nwg, [ Point3d(-0.5,-0.25,-0.5), \
                 Point3d(-0.5,-0.25,0.5), \
                 Point3d(-0.5,0.75,-0.5), \
                 Point3d(-0.5,0.75,0.5), \
                 Point3d(0.5,-0.25,-0.5), \
                 Point3d(0.5,-0.25,0.5), \
                 Point3d(0.5,0.75,-0.5), \
                 Point3d(0.5,0.75,0.5), \
                 Point3d(-0.5,0.0,0.5), \
                 Point3d(-0.5,0.0,-0.5), \
                 Point3d(0.5,0.0,0.5), \
                 Point3d(0.5,0.0,-0.5) ])
    nwg.writeOBJ("tures/Cubey0_25-cutOy.obj")
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24])")

    center025 = Point3d(0.0,0.25,0.0)

    for center025 in [Point3d(-0.5,0.75,-0.5), Point3d(-0.5,-0.25,-0.5), Point3d(-0.5,0.75,0.5), Point3d(-0.5,-0.25,0.5)]:
      for theta in [math.pi/6.0, math.pi/4.0, -math.pi/4.0, -math.pi/6.0]:
        MRotX = [ \
         [ 1.0, 0.0, 0.0], \
         [ 0.0, math.cos(theta), - math.sin(theta) ], \
         [ 0.0, math.sin(theta),   math.cos(theta) ], \
         ]
    
        ur = Ox.Lin33(MRotX)
        vr = Oy.Lin33(MRotX)
        
        nwg,cd = PlaneCut(cube, center025, ur, vr)

        for iy in range(-15, 15):
          center025.y = 0.25 + float(iy)*0.05
          nwg,cd = PlaneCut(cube, center025, ur, vr)


  # ---------------------------------------------------------------------------
  # Cut Cube along standard axis
  #
  def testCutCubeDiag(self):
    origin = Point3d(0.0,0.0,0.0)
    center025 = Point3d(0.0,0.25,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    objsrc = readGeom('srcdata/CutterCubey0_25.obj')
    cube = objsrc.getGroup("Cubey0_25")

    theta = math.pi/6.0
    MRotZ = [ \
      [ math.cos(theta), - math.sin(theta), 0.0], \
      [ math.sin(theta),   math.cos(theta), 0.0 ], \
      [             0.0,               0.0, 1.0 ], \
      ]
  
    ur = Ox.Lin33(MRotZ)
    vr = Oy.Lin33(MRotZ)

    nwg,cd = PlaneCut(cube, origin, ur, vr )
    nwg.writeOBJ("tures/Cubey0_25-cutOzRot30Oz.obj") # Ok - Rotation sans effet - 5-juin-2020 à 7h41

    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)
    nwg,cd = PlaneCut(cube, origin, ur, vr )
    nwg.writeOBJ("tures/Cubey0_25-cutOzRot30Ox.obj")

    theta = math.pi/4.0
    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)

    nwg,cd = PlaneCut(cube, center025, ur, vr)
    nwg.writeOBJ("tures/Cubey0_25-cutOzRot45Ox.obj")
    # self.assertEqual(str(nwg.groups[0].stripCount), "[0, 4, 8, 12, 16, 20, 24]")

    for theta in [math.pi/6.0, math.pi/4.0, -math.pi/4.0, -math.pi/6.0]:
      MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
      ur = Ox.Lin33(MRotX)
      vr = Oy.Lin33(MRotX)
      for iy in range(-15, 15):
        center025.y = 0.25 + float(iy)*0.05
        nwg,cd = PlaneCut(cube, center025, ur, vr)



    # Add a Oy Rotation
    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
  
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    nwg,cd = PlaneCut(cube, center025, ur, vr)
    nwg.writeOBJ("tures/Cubey0_25-cutOzRot45OxOy.obj")

    center025 = Point3d(0.0,0.25,0.0)

    theta = math.pi/4.0
    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)

    theta = math.pi/2.0
    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    
    nwg,cd = PlaneCut(cube, center025, ur, vr)
    nwg.writeOBJ("tures/Cubey0_25-cutOzRot45Oy.obj")

    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    
    nwg,cd = PlaneCut(cube, center025, ur, vr)


  # ---------------------------------------------------------------------------
  # Cut Cube along standard axis
  #
  def testCutCubeTexDiag(self):
    origin = Point3d(0.0,0.0,0.0)
    center025 = Point3d(0.0,0.25,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    objsrc = readGeom('srcdata/CutterCubey0_25Tex.obj')
    cube = objsrc.getGroup("Cubey0_25")

    theta = math.pi/6.0
    MRotZ = [ \
      [ math.cos(theta), - math.sin(theta), 0.0], \
      [ math.sin(theta),   math.cos(theta), 0.0 ], \
      [             0.0,               0.0, 1.0 ], \
      ]
  
    ur = Ox.Lin33(MRotZ)
    vr = Oy.Lin33(MRotZ)

    nwg,cd = PlaneCut(cube, origin, ur, vr )
    nwg.writeOBJ("tures/Cubey0_25Tex-cutOzRot30Oz.obj") # Ok - Rotation sans effet - 5-juin-2020 à 7h41

    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)
    nwg,cd = PlaneCut(cube, origin, ur, vr )
    nwg.writeOBJ("tures/Cubey0_25Tex-cutOzRot30Ox.obj")

    theta = math.pi/4.0
    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)

    nwg,cd = PlaneCut(cube, center025, ur, vr)
    nwg.writeOBJ("tures/Cubey0_25Tex-cutOzRot45Ox.obj")




  # ---------------------------------------------------------------------------
  # Cut Tetrahedre along standard axis
  #
  def testCutTetrahedreAxes(self):
    objsrc = readGeom('srcdata/CutterTetraHedre.obj')

    th = objsrc.getGroup("tetrahedron5")
    
    origin = Point3d(0.0,0.0,0.0)
    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    nwg,cd = PlaneCut(th, origin, Ox, Oy )
    nwg.writeOBJ("tures/tetrahedre-cutOz.obj")
    
    self.coordListAssert(nwg, [   \
                              Point3d(0.0,1.08866211,0.0), \
                              Point3d(0.0,-0.544331,1.1547), \
                              Point3d(-1.0,-0.544331,-0.57735), \
                              Point3d(1.0,-0.544331,-0.57735), \
                              Point3d(-0.666667,-0.544331,0.0), \
                              Point3d(0.666667,-0.544331,0.0) \
                 ])
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [4, 1, 0, 5, 1, 4, 5, 0, 1, 4, 0, 5])")
 
    nwg,cd = PlaneCut(th, origin, Oy, Oz )
    nwg.writeOBJ("tures/tetrahedre-cutOx.obj")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [0, 3, 4, 4, 3, 1, 3, 0, 1, 0, 4, 1])")
    
    # No Closing face
    nwg,cd = PlaneCut(th, origin, Oz, Ox, materialName=None )
    nwg.writeOBJ("tures/tetrahedre-cutOy.obj")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [0, 4, 5, 6, 0, 5, 4, 0, 6])")

    nwg,cd = PlaneCut(th, origin, Ox, Oy, slicing=True)
    nwg.writeOBJ("tures/tetrahedre-sliceOz.obj")
    nwg,cd = PlaneCut(th, origin, Oy, Oz, slicing=True)
    nwg.writeOBJ("tures/tetrahedre-sliceOx.obj")
    nwg,cd = PlaneCut(th, origin, Oz, Ox, materialName=None, slicing=True )
    nwg.writeOBJ("tures/tetrahedre-sliceOy.obj")






    
  # ---------------------------------------------------------------------------
  # Cut a Cube with triangles and quadrilatères along standard axis
  #
  def testCutCubeTriAxes(self):
    objsrc = readGeom('srcdata/CutterCubeTriy0_25.obj')

    cubeTriY0_25 = objsrc.getGroup("Cubey0_25Tri")
    
    origin = Point3d(0.0,0.0,0.0)
    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    nwg,cd = PlaneCut(cubeTriY0_25, origin, Ox, Oy )
    nwg.writeOBJ("tures/CutterCubeTriy0_25-cutOz.obj")
    #print(str(nwg.groups[0].stripCount))
    #print(str(nwg.groups[0].vertIdx))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 3, 7, 11, 15, 19, 22, 25, 28, 32])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [1, 8, 10, 1, 10, 7, 3, 3, 12, 8, 1, 3, 7, 13, 12, 5, 11, 13, 7, 7, 10, 5, 8, 11, 10, 10, 11, 5, 8, 12, 13, 11])")
 
    nwg,cd = PlaneCut(cubeTriY0_25, origin, Oy, Oz )
    nwg.writeOBJ("tures/CutterCubeTriy0_25-cutOx.obj")
    #print(str(nwg.groups[0].stripCount))
    #print(str(nwg.groups[0].vertIdx))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 3, 7, 10, 14, 18, 21, 24, 27, 30, 34])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [10, 7, 12, 12, 7, 6, 13, 4, 6, 11, 5, 11, 6, 7, 6, 4, 9, 13, 7, 10, 5, 9, 11, 10, 10, 11, 5, 11, 9, 4, 10, 12, 13, 9])")
 
    nwg,cd = PlaneCut(cubeTriY0_25, origin, Oz, Ox )
    nwg.writeOBJ("tures/CutterCubeTriy0_25-cutOy.obj")
    #print(str(nwg.groups[0].stripCount))
    #print(str(nwg.groups[0].vertIdx))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 7, 11, 15, 18, 22, 26, 29, 32, 40])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [12, 7, 3, 13, 2, 14, 15, 3, 2, 16, 13, 3, 7, 6, 2, 17, 6, 18, 18, 6, 7, 19, 6, 17, 14, 2, 7, 12, 19, 16, 2, 15, 12, 13, 16, 15, 14, 17, 18, 19])")
    
    
  # ---------------------------------------------------------------------------
  # Cut a Cube with triangles and quadrilatères along standard axis
  #
  def testCutRadialLimit(self):
    objsrc = readGeom('srcdata/Plug.obj')

    plug = objsrc.getGroup("Plug")
    
    origin = Point3d(0.0,0.0,0.0)
    center = Point3d(-1.25, 0.0, 1.5)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    nwg,cd = PlaneCut(plug, center, Ox.neg(), Oy, radialLimit=1.40)
    nwg.writeOBJ("tures/CutterPlug.obj")
    #print(str(nwg.groups[0].stripCount))
    #print(str(nwg.groups[0].vertIdx))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 151, 155, 159, 162, 166, 169, 173, 176, 179, 183, 186, 189, 193, 196, 199, 203, 206, 209, 213, 216, 219, 223, 226, 229, 233, 236, 239, 243, 247, 251, 255, 259, 263, 267, 283])")
    #self.assertEqual(str(nwg.groups[0].vertIdx), "[1, 8, 10, 1, 10, 7, 3, 3, 12, 8, 1, 3, 7, 13, 12, 5, 11, 13, 7, 7, 10, 5, 8, 11, 10, 10, 11, 5, 8, 12, 13, 11]")
 
    nwg,cd = PlaneCut(plug, center, Ox.neg(), Oy, slicing=True, radialLimit=1.40)
    nwg.writeOBJ("tures/CutterPlugSlice.obj")

    
    objsrc = readGeom('srcdata/PlugExt.obj')
    plug = objsrc.getGroup("PlugExt")    
    origin = Point3d(0.0,0.0,0.0)
    center = Point3d(-1.25, 0.0, 1.5)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    nwg,cd = PlaneCut(plug, center, Ox.neg(), Oy, radialLimit=1.40)
    nwg.writeOBJ("tures/CutterPlugExt.obj")
    #print(str(nwg.groups[0].stripCount))
    #print(str(nwg.groups[0].vertIdx))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 151, 155, 159, 163, 167, 171, 175, 179, 183, 187, 191, 195, 199, 203, 207, 211, 215, 219, 223, 227, 231, 235, 239, 243, 247, 251, 255, 259, 263, 267, 271, 275, 279, 283, 287, 291, 295, 299, 303, 307, 311, 315, 319, 323, 327, 331, 335, 339, 343, 347, 351, 354, 358, 362, 366, 369, 373, 377, 381, 385, 389, 393, 397, 401, 405, 409, 413, 417, 421, 425, 429, 433, 437, 441, 445, 449, 453, 457, 461, 465, 469, 473, 477, 481, 485, 489, 493, 497, 501, 505, 509, 513, 517, 521, 525, 529, 533, 537, 541, 545, 549, 553, 557, 561, 565, 569, 585])")
    
  # ---------------------------------------------------------------------------
  # Cut a Cube with triangles and quadrilatères along standard axis
  #
  def testSliceCubeTriAxes(self):
    objsrc = readGeom('srcdata/CutterCubeTriy0_25.obj')

    cubeTriY0_25 = objsrc.getGroup("Cubey0_25Tri")
    
    origin = Point3d(0.0,0.0,0.0)
    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    nwg,cd = PlaneCut(cubeTriY0_25, origin, Ox, Oy, slicing=True )
    nwg.writeOBJ("tures/SlicerCubeTriy0_25-cutOz.obj")
    self.assertEqual(nwg.groups[0].getNbFace(), 19)
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 3, 6, 10, 13, 17, 20, 24, 28, 31, 35, 38, 42, 45, 48, 51, 54, 57, 60, 64])")
 
    nwg,cd = PlaneCut(cubeTriY0_25, origin, Oy, Oz, slicing=True  )
    nwg.writeOBJ("tures/SlicerCubeTriy0_25-cutOx.obj")
    self.assertEqual(nwg.groups[0].getNbFace(), 19)
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 3, 6, 9, 13, 16, 20, 24, 28, 31, 35, 39, 42, 45, 48, 51, 54, 57, 60, 64])")
 
    nwg,cd = PlaneCut(cubeTriY0_25, origin, Oz, Ox, materialName=None, slicing=True  )
    nwg.writeOBJ("tures/SlicerCubeTriy0_25-cutOy.obj")
    self.assertEqual(nwg.groups[0].getNbFace(), 22)
    #print(str(nwg.groups[0].stripCount))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 3, 6, 10, 14, 17, 21, 25, 29, 33, 36, 40, 44, 48, 52, 56, 59, 63, 66, 70, 74, 77, 80])")

  # ---------------------------------------------------------------------------
  # Cut Cube along standard axis
  #
  def testSliceCubeDiag(self):
    origin = Point3d(0.0,0.0,0.0)
    center025 = Point3d(0.0,0.25,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    objsrc = readGeom('srcdata/CutterCubey0_25.obj')
    cube = objsrc.getGroup("Cubey0_25")

    theta = math.pi/6.0
    MRotZ = [ \
      [ math.cos(theta), - math.sin(theta), 0.0], \
      [ math.sin(theta),   math.cos(theta), 0.0 ], \
      [             0.0,               0.0, 1.0 ], \
      ]
  
    ur = Ox.Lin33(MRotZ)
    vr = Oy.Lin33(MRotZ)

    nwg,cd = PlaneCut(cube, origin, ur, vr, slicing=True)
    nwg.writeOBJ("tures/Cubey0_25-sliceOzRot30Oz.obj") # Ok - Rotation sans effet - 5-juin-2020 à 7h41

    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)
    nwg,cd = PlaneCut(cube, origin, ur, vr, slicing=True )
    nwg.writeOBJ("tures/Cubey0_25-sliceOzRot30Ox.obj")

    theta = math.pi/4.0
    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)

    nwg,cd = PlaneCut(cube, center025, ur, vr, slicing=True)
    nwg.writeOBJ("tures/Cubey0_25-sliceOzRot45Ox.obj")
    # self.assertEqual(str(nwg.groups[0].stripCount), "[0, 4, 8, 12, 16, 20, 24]")

    for theta in [math.pi/6.0, math.pi/4.0, -math.pi/4.0, -math.pi/6.0]:
      MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
      ur = Ox.Lin33(MRotX)
      vr = Oy.Lin33(MRotX)
      for iy in range(-15, 15):
        center025.y = 0.25 + float(iy)*0.05
        nwg,cd = PlaneCut(cube, center025, ur, vr, slicing=True)



    # Add a Oy Rotation
    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
  
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    nwg,cd = PlaneCut(cube, center025, ur, vr, slicing=True)
    nwg.writeOBJ("tures/Cubey0_25-sliceOzRot45OxOy.obj")

    center025 = Point3d(0.0,0.25,0.0)

    theta = math.pi/4.0
    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)

    theta = math.pi/2.0
    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    
    nwg,cd = PlaneCut(cube, center025, ur, vr, slicing=True)
    nwg.writeOBJ("tures/Cubey0_25-sliceOzRot45Oy.obj")

    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    
    nwg,cd = PlaneCut(cube, center025, ur, vr, slicing=True)

    
    
  # ---------------------------------------------------------------------------
  # Cut a Cube with triangles and quadrilatères along standard axis
  #
  def testCutTerre(self):
    center = Point3d(0.0,0.40,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    objsrc = readGeom('srcdata/TerrePoignees+Trou.obj')
    sphere = objsrc.getGroup("Terre")

    for theta in [math.pi/6.0, math.pi/4.0, 1.1*math.pi, -math.pi/4.0, -math.pi/6.0]:
      MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
      ur = Ox.Lin33(MRotX)
      vr = Oy.Lin33(MRotX)

      nwg,cd = PlaneCut(sphere, center, ur, vr)
    nwg.writeOBJ("tures/Terre-cutOzRot"+str(theta)+"Ox.obj")

    nwg,cd = PlaneCut(sphere, center, ur, vr, slicing=True)
    nwg.writeOBJ("tures/Terre-Slice"+str(theta)+"Ox.obj")

    nwg,cd = PlaneCut(sphere, Point3d(0.0,0.36,0.0), Ox, Oz, radialScale=0.9)
    nwg.writeOBJ("tures/Terre+Scale+OxOz.obj")


  # ---------------------------------------------------------------------------
  # Split Cube along standard axis
  #
  def testSplitCubeAxes(self):
    origin = Point3d(0.0,0.0,0.0)
    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    objsrc = readGeom('srcdata/CutterCubey0_25.obj')
    cube = objsrc.getGroup("Cubey0_25")

    # Cut at the bottom on the cube
    center25 = Point3d(0.0,-0.25,0.0)
    nwg,cd = PlaneSplit(cube, center25, Ox, Vector3d(Oz).neg() )
    nwg.writeOBJ("tures/Cubey0_25-splitOy-RAZ.obj")
    
    nwg,cd = PlaneSplit(cube, origin, Ox, Oy )
    self.coordListAssert(nwg, [ Point3d(-0.5,-0.25,-0.5), \
                 Point3d(-0.5,-0.25,0.5), \
                 Point3d(-0.5,0.75,-0.5), \
                 Point3d(-0.5,0.75,0.5), \
                 Point3d(0.5,-0.25,-0.5), \
                 Point3d(0.5,-0.25,0.5), \
                 Point3d(0.5,0.75,-0.5), \
                 Point3d(0.5,0.75,0.5), \
                 Point3d(0.5,-0.25,0), \
                 Point3d(-0.5,-0.25,0), \
                 Point3d(-0.5,0.75,0), \
                 Point3d(0.5,0.75,0) ])
      
    nwg.writeOBJ("tures/Cubey0_25-splitOz.obj") # Ok 4-aout-2020 a 5h50
#     print(str(nwg.groups[0].stripCount))
#     print(str(nwg.groups[0].vertIdx))
#     print(str(nwg.groups[1].stripCount))
#     print(str(nwg.groups[1].vertIdx))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [8, 5, 1, 9, 1, 3, 10, 9, 1, 5, 7, 3, 3, 7, 11, 10, 11, 7, 5, 8, 8, 9, 10, 11])")
    self.assertEqual(str(nwg.groups[1].stripCount), "array('l', [0, 4, 8, 12, 16, 20])")
    self.assertEqual(str(nwg.groups[1].vertIdx), "array('l', [0, 4, 8, 9, 10, 2, 0, 9, 2, 6, 4, 0, 11, 6, 2, 10, 4, 6, 11, 8])")


  # ---------------------------------------------------------------------------
  # Cut a Cube with triangles and quadrilatères along standard axis
  #
  def testSplitCubeTriAxes(self):
    objsrc = readGeom('srcdata/CutterCubeTriy0_25.obj')

    cubeTriY0_25 = objsrc.getGroup("Cubey0_25Tri")
    
    origin = Point3d(0.0,0.0,0.0)
    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)


    nwg,cd = PlaneSplit(cubeTriY0_25, origin, Oz, Ox )
    nwg.writeOBJ("tures/CutterCubeTriy0_25-splitOy.obj")
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 7, 11, 15, 18, 22, 26, 29, 32, 40])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [12, 7, 3, 13, 2, 14, 15, 3, 2, 16, 13, 3, 7, 6, 2, 17, 6, 18, 18, 6, 7, 19, 6, 17, 14, 2, 7, 12, 19, 16, 2, 15, 12, 13, 16, 15, 14, 17, 18, 19])")
    self.assertEqual(str(nwg.groups[1].stripCount), "array('l', [0, 3, 6, 10, 14, 18, 22, 26, 30, 34, 38, 42, 45, 48])")
    self.assertEqual(str(nwg.groups[1].vertIdx), "array('l', [0, 9, 8, 1, 8, 10, 1, 10, 12, 13, 14, 9, 0, 15, 16, 8, 1, 13, 4, 17, 18, 11, 5, 11, 18, 19, 17, 4, 9, 14, 12, 10, 5, 19, 8, 16, 15, 0, 8, 9, 11, 10, 10, 11, 5, 11, 9, 4])")


    nwg,cd = PlaneSplit(cubeTriY0_25, origin, Oy, Oz )
    nwg.writeOBJ("tures/CutterCubeTriy0_25-splitOx.obj")
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 3, 7, 10, 14, 18, 21, 24, 27, 30, 34])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [10, 7, 12, 12, 7, 6, 13, 4, 6, 11, 5, 11, 6, 7, 6, 4, 9, 13, 7, 10, 5, 9, 11, 10, 10, 11, 5, 11, 9, 4, 10, 12, 13, 9])")
    self.assertEqual(str(nwg.groups[1].stripCount), "array('l', [0, 3, 6, 10, 13, 17, 21, 24, 27, 30])")
    self.assertEqual(str(nwg.groups[1].vertIdx), "array('l', [0, 9, 8, 1, 8, 10, 1, 10, 12, 3, 2, 9, 0, 3, 2, 8, 1, 3, 12, 13, 2, 9, 2, 13, 8, 2, 0, 8, 9, 10])")

    
    nwg,cd = PlaneSplit(cubeTriY0_25, origin, Ox, Oy )
    nwg.writeOBJ("tures/CutterCubeTriy0_25-splitOz.obj")
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 3, 7, 11, 15, 19, 22, 25, 28, 32])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [1, 8, 10, 1, 10, 7, 3, 3, 12, 8, 1, 3, 7, 13, 12, 5, 11, 13, 7, 7, 10, 5, 8, 11, 10, 10, 11, 5, 8, 12, 13, 11])")
    self.assertEqual(str(nwg.groups[1].stripCount), "array('l', [0, 3, 6, 9, 13, 16, 19, 23, 26, 29, 32])")
    self.assertEqual(str(nwg.groups[1].vertIdx), "array('l', [0, 9, 8, 2, 9, 0, 12, 2, 8, 13, 6, 2, 12, 4, 6, 11, 11, 6, 13, 6, 4, 9, 2, 8, 2, 0, 8, 9, 11, 11, 9, 4])")
 
 
  # ---------------------------------------------------------------------------
  # Split Cube along standard axis and rotations
  #
  def testSplitCubeDiag(self):
    origin = Point3d(0.0,0.0,0.0)
    center025 = Point3d(0.0,0.25,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    objsrc = readGeom('srcdata/CutterCubey0_25.obj')
    cube = objsrc.getGroup("Cubey0_25")

    theta = math.pi/6.0
    MRotZ = [ \
      [ math.cos(theta), - math.sin(theta), 0.0], \
      [ math.sin(theta),   math.cos(theta), 0.0 ], \
      [             0.0,               0.0, 1.0 ], \
      ]
  
    ur = Ox.Lin33(MRotZ)
    vr = Oy.Lin33(MRotZ)

    nwg,cd = PlaneSplit(cube, origin, ur, vr )
    nwg.writeOBJ("tures/Cubey0_25-splitOzRot30Oz.obj") 
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [8, 5, 1, 9, 1, 3, 10, 9, 1, 5, 7, 3, 3, 7, 11, 10, 11, 7, 5, 8, 8, 9, 10, 11])")
    self.assertEqual(str(nwg.groups[1].stripCount), "array('l', [0, 4, 8, 12, 16, 20])")
    self.assertEqual(str(nwg.groups[1].vertIdx), "array('l', [0, 4, 8, 9, 10, 2, 0, 9, 2, 6, 4, 0, 11, 6, 2, 10, 4, 6, 11, 8])")


    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)
    nwg,cd = PlaneSplit(cube, origin, ur, vr )
    nwg.writeOBJ("tures/Cubey0_25-splitOzRot30Ox.obj")
    print(str(nwg.groups[0].stripCount))
    print(str(nwg.groups[0].vertIdx))
    print(str(nwg.groups[1].stripCount))
    print(str(nwg.groups[1].vertIdx))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24])")
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [8, 5, 1, 9, 1, 3, 10, 9, 1, 5, 7, 3, 3, 7, 11, 10, 11, 7, 5, 8, 8, 9, 10, 11])")
    self.assertEqual(str(nwg.groups[1].stripCount), "array('l', [0, 4, 8, 12, 16, 20])")
    self.assertEqual(str(nwg.groups[1].vertIdx), "array('l', [0, 4, 8, 9, 10, 2, 0, 9, 2, 6, 4, 0, 11, 6, 2, 10, 4, 6, 11, 8])")
    
    
    
    theta = math.pi/4.0
    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)

    nwg,cd = PlaneSplit(cube, center025, ur, vr)
    nwg.writeOBJ("tures/Cubey0_25-splitOzRot45Ox.obj")
    # self.assertEqual(str(nwg.groups[0].stripCount), "[0, 4, 8, 12, 16, 20, 24]")

    for theta in [math.pi/6.0, math.pi/4.0, -math.pi/4.0, -math.pi/6.0]:
      MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
      ur = Ox.Lin33(MRotX)
      vr = Oy.Lin33(MRotX)
      for iy in range(-15, 15):
        center025.y = 0.25 + float(iy)*0.05
        nwg,cd = PlaneSplit(cube, center025, ur, vr)



    # Add a Oy Rotation
    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
  
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    nwg,cd = PlaneSplit(cube, center025, ur, vr)
    nwg.writeOBJ("tures/Cubey0_25-splitOzRot45OxOy.obj")

    center025 = Point3d(0.0,0.25,0.0)

    theta = math.pi/4.0
    MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
    ur = Ox.Lin33(MRotX)
    vr = Oy.Lin33(MRotX)

    theta = math.pi/2.0
    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    
    nwg,cd = PlaneSplit(cube, center025, ur, vr)
    nwg.writeOBJ("tures/Cubey0_25-splitOzRot45Oy.obj")

    MRotY = [ \
       [ math.cos(theta), 0.0, - math.sin(theta) ], \
       [             0.0, 1.0,              0.0  ], \
       [ math.sin(theta), 0.0,   math.cos(theta) ], \
       ]
    ur = ur.Lin33(MRotY)
    vr = vr.Lin33(MRotY)
    
    nwg,cd = PlaneSplit(cube, center025, ur, vr)

 
    
  # ---------------------------------------------------------------------------
  # Cut Tetrahedre along standard axis
  #
  def testSplitTetrahedreAxes(self):
    objsrc = readGeom('srcdata/CutterTetraHedre.obj')

    th = objsrc.getGroup("tetrahedron5")
    
    origin = Point3d(0.0,0.0,0.0)
    center05 = Point3d(0.0,0.5,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    nwg,cd = PlaneSplit(th, origin, Ox, Oy )
    nwg.writeOBJ("tures/tetrahedre-splitOz.obj")
    
    self.coordListAssert(nwg, [   \
                              Point3d(0.0,1.08866211,0.0), \
                              Point3d(0.0,-0.544331,1.1547), \
                              Point3d(-1.0,-0.544331,-0.57735), \
                              Point3d(1.0,-0.544331,-0.57735), \
                              Point3d(-0.666667,-0.544331,0.0), \
                              Point3d(0.666667,-0.544331,0.0) \
                 ])
    self.assertEqual(str(nwg.groups[0].vertIdx), "array('l', [4, 1, 0, 5, 1, 4, 5, 0, 1, 4, 0, 5])")


  # ---------------------------------------------------------------------------
  # Split a Cube with triangles and quadrilatères along standard axis
  #
  def testSplitTerre(self):
    center = Point3d(0.0,0.40,0.0)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    objsrc = readGeom('srcdata/TerrePoignees+Trou.obj')
    sphere = objsrc.getGroup("Terre")

    for theta in [math.pi/6.0, math.pi/4.0, 1.1*math.pi, -math.pi/4.0, -math.pi/6.0]:
      MRotX = [ \
       [ 1.0, 0.0, 0.0], \
       [ 0.0, math.cos(theta), - math.sin(theta) ], \
       [ 0.0, math.sin(theta),   math.cos(theta) ], \
       ]
  
      ur = Ox.Lin33(MRotX)
      vr = Oy.Lin33(MRotX)

      nwg,cd = PlaneSplit(sphere, center, ur, vr)

    nwg.writeOBJ("tures/Terre-splitOzRot"+str(theta)+"Ox.obj")

  # ---------------------------------------------------------------------------
  # Split a Complex form with triangles and quadrilatères along standard axis
  # with radial limit
  #
  def testSplitRadialLimit(self):
    objsrc = readGeom('srcdata/Plug.obj')

    plug = objsrc.getGroup("Plug")
    
    origin = Point3d(0.0,0.0,0.0)
    center = Point3d(-1.25, 0.0, 1.5)
    Ox = Vector3d(1.0, 0.0, 0.0)
    Oy = Vector3d(0.0, 1.0, 0.0)
    Oz = Vector3d(0.0, 0.0, 1.0)
    
    nwg,cd = PlaneSplit(plug, center, Ox.neg(), Oy, radialLimit=1.40)
    nwg.writeOBJ("tures/SplitterPlug.obj")
    #print(str(nwg.groups[0].stripCount))
    #print(str(nwg.groups[0].vertIdx))
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 151, 155, 159, 162, 166, 169, 173, 176, 179, 183, 186, 189, 193, 196, 199, 203, 206, 209, 213, 216, 219, 223, 226, 229, 233, 236, 239, 243, 247, 251, 255, 259, 263, 267, 283])")
    #print(str(nwg.groups[1].stripCount))
    #print(str(nwg.groups[1].vertIdx))
    self.assertEqual(str(nwg.groups[1].stripCount), "array('l', [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48])")
     
    objsrc = readGeom('srcdata/PlugExt.obj')
    plug = objsrc.getGroup("PlugExt")
    Repere = CoordSyst(Point3d(-1.25, 0.0, 1.5), Vector3d(-1.0, 0.0, 0.0), Vector3d(0.0, 1.0, 0.0))
    
    nwg,cd = PlaneSplit(plug, Repere, radialLimit=1.40)
    nwg.writeOBJ("tures/SplitterPlugExt.obj")
    self.assertEqual(str(nwg.groups[0].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 136, 140, 144, 148, 151, 155, 159, 163, 167, 171, 175, 179, 183, 187, 191, 195, 199, 203, 207, 211, 215, 219, 223, 227, 231, 235, 239, 243, 247, 251, 255, 259, 263, 267, 271, 275, 279, 283, 287, 291, 295, 299, 303, 307, 311, 315, 319, 323, 327, 331, 335, 339, 343, 347, 351, 354, 358, 362, 366, 369, 373, 377, 381, 385, 389, 393, 397, 401, 405, 409, 413, 417, 421, 425, 429, 433, 437, 441, 445, 449, 453, 457, 461, 465, 469, 473, 477, 481, 485, 489, 493, 497, 501, 505, 509, 513, 517, 521, 525, 529, 533, 537, 541, 545, 549, 553, 557, 561, 565, 569, 585])")
    #print(str(nwg.groups[1].stripCount))
    #print(str(nwg.groups[1].vertIdx))
    self.assertEqual(str(nwg.groups[1].stripCount), "array('l', [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60, 64, 68, 72, 76, 80, 84, 88, 92, 96, 100, 104, 108, 112, 116, 120, 124, 128, 132, 135, 139, 143, 147, 150, 154, 158, 162, 166, 170, 174, 178, 182, 186, 190, 194, 198, 202, 206, 210, 214, 218, 222, 226, 230, 234, 238, 242, 246, 250, 254, 258, 262, 266, 270, 274, 278, 282, 286, 290, 294, 298, 302, 306, 310, 314, 318, 322, 326, 330, 334, 338, 342, 346, 350])")

  # ---------------------------------------------------------------------------
  # Cut a Cube with triangles and quadrilatères along standard axis
  #
  def testSplitAll(self):
    self.testSplitCubeAxes()
    self.testSplitCubeTriAxes()
    self.testSplitTetrahedreAxes()
    self.testSplitTerre()
    self.testSplitRadialLimit()
    self.testSplitCubeDiag()
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
