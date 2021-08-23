'''
Created on 12 mai 2020

UnitTests for class WaveGeom (basic methods)

Unittests of high level algorithms are in the module tuPlaneCut.py

@author: olivier
'''
import unittest
import sys, cProfile, pstats
import math
import array
from pypos3dtu.tuConst import *

from langutil import C_OK, C_ERROR, C_FAIL
from pypos3d.wftk.WFBasic import C_MISSING_MAT, C_MISSING_FACEMAT, FEPSILON, Point3d
from pypos3d.wftk.WaveGeom import readGeom, WaveGeom

PROFILING = False

class Test(unittest.TestCase):
  wg_cube_gris = None
  wg_ressort = None
  wg_ressort2800 = None

  def setUp(self):
    logging.basicConfig(format='%(asctime)s %(module)s.%(funcName)s %(message)s') # , datefmt='%H:%M:%S,uuu')
    logging.getLogger().setLevel(logging.INFO)
    Test.wg_cube_gris = readGeom(OBJ_FILE_GREY_CUBE)
    if PROFILING:
      self.pr = cProfile.Profile()
      self.pr.enable()


  def tearDown(self):
    if PROFILING:
      self.pr.disable()
      sortby = 'time'
      ps = pstats.Stats(self.pr, stream=sys.stdout).sort_stats(sortby)
      ps.print_stats()


  def testMultiAttrObj(self):
    
    objsrc = readGeom('srcdata/Caudron460-Exp.obj')
    
    
    objsrc = readGeom('srcdata/dodeca.obj')
    ret = objsrc.sanityCheck()
    self.assertEqual(ret, C_OK)

    g = objsrc.getGroups()[0]
    #print(str(g))
    #print(str(g.fAttr))
    l = [ fao.fAttr for fao in g.matIdx ]
    self.assertEqual(str(l), "[33554432, 33554432, 33554432, 33554432, 33554432, 33554432, 33554432, 33554432, 33554432, 33554432, 33554432, 50331649]")
    ret = objsrc.writeOBJ('tures/dodeca.obj')
    self.assertEqual(ret, C_OK)

  # Bug fix test (for addGroup)
  def testlBombLoading(self):
    objsrc = readGeom('srcdata/p51d-exp.obj', usemtl=True)
    objsrc.sanityCheck()
    g = objsrc.getGroup('lBomb')
    wg = WaveGeom()
    wg.addGroup(g)
    wg.optimizeGroups(cleaning=True, radius=FEPSILON)
    ret = wg.save('srcdata/results/lBomb.obj')
    self.assertEqual(ret, C_OK)
    wg.sanityCheck()
    
    # Non Reg: Untriangularize
    g = wg.getGroup('lBomb')
    
    ret = wg.unTriangularize([ g, ], math.sin(5.0/180.0*math.pi))
    
    self.assertEqual(ret, 2736)
    self.assertEqual(g.getNbFace(), 2736)

  def testBarycentre(self):
    wg = readGeom('srcdata/CubeTestBaryCentre.obj')
    b = wg.getGroups()[0].calcBarycentre()
    print(str(wg.getGroups()[0]) +' bary='+str(b))
    
    n = wg.findMinDist(Point3d(0.0,0.0,0.0), 50, 10.0)
    self.assertEqual(n, 0)

    objsrc = readGeom('srcdata/MappingCube-c1bis.obj', usemtl=True)
    wg.addGroup(objsrc.getGroups()[0])
    wg.removeGroup(wg.getGroups()[0], cleaning=True)
    
    wg.save('tures/ctb.obz') # Just for coverage aspect
    
  def testUnTriagularize(self):
    
    wg = Test.wg_cube_gris.copy()
    
    grp = wg.getGroups()[0]
    
    ret = grp.unTriangularize()
    self.assertEqual(grp.getNbFace(), 6)
    self.assertEqual(ret, C_FAIL)
    
    wg = readGeom('srcdata/UnTriang.obj')
    grp = wg.getGroup('cube1Tri')
    self.assertEqual(grp.getNbFace(), 7)
    ret = grp.unTriangularize()
    
    self.assertEqual(ret, 6)
    self.assertEqual(str(grp.vertIdx), "array('l', [43, 47, 48, 44, 44, 46, 45, 43, 45, 49, 47, 43, 46, 50, 49, 45, 47, 49, 50, 48, 48, 50, 46, 44])")
    self.assertEqual(str(grp.matIdx[0].normIdx), "array('l', [43, 47, 48, 44])") 
    self.assertEqual(str(grp.matIdx[-1].normIdx), "array('l', [48, 50, 46, 44])")

    grp = wg.getGroup('cube2Tri')
    ret = grp.unTriangularize()
    self.assertEqual(ret, 6)
    self.assertEqual(str(grp.vertIdx), "array('l', [35, 39, 40, 36, 36, 38, 37, 35, 37, 41, 39, 35, 39, 41, 42, 40, 40, 42, 38, 36, 38, 42, 41, 37])")
#     self.assertEqual(str(grp.tvertIdx), "array('l', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])")
#     self.assertEqual(str(grp.normIdx), "array('l', [35, 39, 40, 36, 36, 38, 37, 35, 37, 41, 39, 35, 39, 41, 42, 40, 40, 42, 38, 36, 38, 42, 41, 37])")
    self.assertEqual(str(grp.matIdx[0].normIdx), "array('l', [35, 39, 40, 36])") 
    self.assertEqual(str(grp.matIdx[-1].normIdx), "array('l', [38, 42, 41, 37])")

    grp = wg.getGroup('cubeNTri2Mat')
    ret = grp.unTriangularize()
    self.assertEqual(ret, 15)
    self.assertEqual(str(grp.vertIdx), "array('l', [18, 22, 29, 27, 19, 19, 26, 21, 20, 18, 20, 24, 30, 22, 18, 21, 32, 24, 20, 23, 33, 27, 34, 32, 25, 31, 34, 29, 22, 30, 32, 34, 30, 24, 31, 28, 33, 23, 31, 23, 29, 34, 28, 25, 32, 21, 28, 31, 25, 27, 29, 23, 26, 33, 28, 21, 26, 19, 27, 33])")
#     self.assertEqual(str(grp.tvertIdx), "array('l', [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1])")
#     self.assertEqual(str(grp.normIdx), "array('l', [18, 22, 29, 27, 19, 19, 26, 21, 20, 18, 20, 24, 30, 22, 18, 21, 32, 24, 20, 23, 33, 27, 34, 32, 25, 31, 34, 29, 22, 30, 32, 34, 30, 24, 31, 28, 33, 23, 31, 23, 29, 34, 28, 25, 32, 21, 28, 31, 25, 27, 29, 23, 26, 33, 28, 21, 26, 19, 27, 33])")
    self.assertEqual(str(grp.matIdx[0].normIdx), "array('l', [18, 22, 29, 27, 19])") 
    self.assertEqual(str(grp.matIdx[-1].normIdx), "array('l', [26, 19, 27, 33])")

    grp = wg.getGroup('cubeNTri2MatFold')
    ret = grp.unTriangularize()
    self.assertEqual(ret, 17)
    self.assertEqual(str(grp.vertIdx), "array('l', [0, 4, 11, 9, 1, 1, 8, 17, 0, 2, 17, 8, 3, 3, 14, 6, 2, 6, 12, 17, 2, 17, 12, 4, 0, 5, 15, 9, 16, 14, 7, 13, 16, 11, 4, 12, 14, 16, 12, 6, 13, 15, 5, 13, 5, 11, 16, 13, 7, 10, 15, 10, 7, 14, 3, 9, 11, 5, 8, 15, 10, 3, 8, 1, 9, 15])")
#     self.assertEqual(str(grp.tvertIdx), "array('l', [17, 6, 5, 11, 16, 31, 32, 8, 2, 12, 8, 32, 41, 18, 35, 36, 19, 7, 1, 15, 20, 15, 1, 0, 14, 37, 28, 27, 24, 13, 4, 10, 24, 25, 40, 33, 13, 24, 33, 30, 38, 28, 37, 10, 9, 25, 24, 38, 39, 29, 28, 26, 34, 35, 18, 11, 5, 3, 22, 28, 29, 23, 22, 21, 27, 28])")
    self.assertEqual(str(grp.matIdx[0].tvertIdx), "array('l', [17, 6, 5, 11, 16])") 
    self.assertEqual(str(grp.matIdx[-1].tvertIdx), "array('l', [22, 21, 27, 28])")
    
#     self.assertEqual(str(grp.normIdx), "array('l', [0, 4, 11, 9, 1, 1, 8, 17, 0, 2, 17, 8, 3, 3, 14, 6, 2, 6, 12, 17, 2, 17, 12, 4, 0, 5, 15, 9, 16, 14, 7, 13, 16, 11, 4, 12, 14, 16, 12, 6, 13, 15, 5, 13, 5, 11, 16, 13, 7, 10, 15, 10, 7, 14, 3, 9, 11, 5, 8, 15, 10, 3, 8, 1, 9, 15])")
    self.assertEqual(str(grp.matIdx[0].normIdx), "array('l', [0, 4, 11, 9, 1])") 
    self.assertEqual(str(grp.matIdx[-1].normIdx), "array('l', [8, 1, 9, 15])")

    wg.save('tures/UnTriang.obj')

    wg = readGeom('srcdata/p51d-lWheel.obj')
    grp = wg.getGroup('lWheel')
    ret = grp.unTriangularize(maxsin=0.025)
    self.assertEqual(ret, 1917)
    wg.save('tures/p51d-lWheel.obj')

    wg = readGeom('srcdata/p51d-lGearLeg.obj')
    grp = wg.getGroup('lGearLeg')
    ret = grp.unTriangularize()
    self.assertEqual(ret, 417)
    wg.save('tures/p51d-lGearLeg.obj')

  def testUnTriagularizeWG(self):
    wg = readGeom(OBZ_FILE_PHF_LOWRES_SRC)
    ret = wg.unTriangularize(lstGrp=['hip', wg.getGroup('lForeArm'), 10, 'Not a group'])
    self.assertEqual(ret, C_ERROR)
    
    ret = wg.unTriangularize(maxsin=0.025)
    self.assertEqual(ret, 16088) # Because of some group have not been 'cleaned'

    c = ChronoMem.start("writeOB?-PHF Untri")
    wg.save('tures/phf-untri.obj')
    c.stopRecord("WaveFrontPerf.txt")
    

  def testsMtlLoading(self):
    objsrc = readGeom('srcdata/MappingCube-c1bis.obj', usemtl=True)
    self.assertEqual(len(objsrc.libMat), 0)
    
    objsrc = readGeom('srcdata/CutterCubey0_25Tex.obj', usemtl=True)
    self.assertEqual(len(objsrc.libMat), 1)
    mat  = objsrc.libMat['Cubey0_25_auv']
    self.assertEqual(mat.d, 1.0)
    self.assertEqual(mat.map_kd, 'auvBG.png')
    
    grp = objsrc.getGroups()[0]
    f = grp.getFaceVertexBy('Unknown', raiseExcept=False)

    try:
      f = grp.getFaceVertexBy('Not better', raiseExcept=True)
    except ValueError:
      print('ok')
    

  def testWaveFrontRead(self):
    self.assertTrue(self.wg_cube_gris != None)
    self.assertTrue(self.wg_cube_gris.getName() == OBJ_FILE_GREY_CUBE)
    self.assertEqual(8, len(self.wg_cube_gris.getCoordList()))
    self.assertEqual(1, len(self.wg_cube_gris.getGroups()))
    
    

    # For coverage purpose
    readGeom("srcdata/cube_gris.obz")
    
    wg = readGeom("/file not found.obz")
    self.assertTrue(not wg)
    
    # Read a obj file with lines
    light = readGeom(OBJ_FILE_LIGHT)
    self.assertEqual(98, len(light.getCoordList()))
    self.assertEqual(1, len(light.getGroups()))
    self.assertEqual(17, len(light.getGroups()[0].lineStripCount))
    self.assertEqual(16, light.getGroups()[0].getNbLine())
    
    # Read with 1 error on Vertex
    wg = readGeom('srcdata/ERR_CutterT1.obj')
    part = wg.getGroup('Cutter')
    self.assertTrue(part!=None)
    n = part.getFaceNormIdx(0)
    self.assertTrue(n!=None)
    le = part.getFaceLoop(0, True)
    print(str(le))
    # FIXME : Does not work --- But not used
    #fno = part.findTVertIdx(2)
    #self.assertEqual(fno, 0)
    
    
    # Read with 1 error on Normal
    try:
      wg = readGeom('srcdata/ERR_CutterT2.obj')
    except Exception:
      print('ok')
      
    # Read with 1 error on Texture
    try:
      wg = readGeom('srcdata/ERR_CutterT3.obj')
    except Exception:
      print('ok')
    
    
    
  # ---------------------------------------------------------------------------
  # Textured Cube to verify Identity 
  #
  def testCutCubeTexDiag(self):
    objsrc = readGeom('srcdata/CutterCubey0_25Tex.obj')
    cube = objsrc.getGroup("Cubey0_25")
    objsrc.writeOBJ("tures/CutterCubey0_25TexId.obj")
    

  def testCreateGeomGroup(self):
    gg1 = self.wg_cube_gris.createGeomGroup("grp3")
    self.assertTrue(gg1 != None)

    gg2 = self.wg_cube_gris.createGeomGroup(None)
    self.assertTrue(gg2 != None)
    

  def testGetMaterialList(self):
    lm = self.wg_cube_gris.getMaterialList()
    self.assertEqual(lm[0], "cube1_auv")
    self.assertEqual(lm[1], "matRouge")

    grp = self.wg_cube_gris.getGroups()[0]
    nTvertIdx = self.wg_cube_gris.calcGroupTVertIndex(grp)
    self.assertEqual(str(nTvertIdx), "[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]")
#     
#     
    nomIdx = self.wg_cube_gris.calcGroupNormIndex(grp)
    self.assertEqual(str(nomIdx), "[0, 1, 2, 3, 4, 5, 6, 7]")

  def testScale(self):
    self.wg_cube_gris.scale(2.0, 3.0, -4.0)
    
    lstpt = self.wg_cube_gris.getCoordList()

    self.assertEqual(lstpt[0].x, -2.0)
    self.assertEqual(self.wg_cube_gris.getCoordList()[0].y, -3.0)
    self.assertEqual(self.wg_cube_gris.getCoordList()[0].z, -4.0)

  def testWriteOBJ(self):
    res = self.wg_cube_gris.writeOBJ(OBJ_FILE_GREY_CUBE_RES)
    self.assertTrue(res == C_OK)

    res = self.wg_cube_gris.writeOBJ("badrep/toto.obj")
    self.assertTrue(res == C_ERROR)

    # Write in a non authorized directory
    res = self.wg_cube_gris.writeOBJ('/error.obj')
    self.assertTrue(res == C_ERROR)

    # self.wg_cube_gris.removeGroupLoc()
    res = self.wg_cube_gris.writeOBJ(OBJ_FILE_GREY_CUBE_RES)
    self.assertTrue(res == C_OK)
    
    wg = readGeom('srcdata/LL-403.obj')
    c = ChronoMem.start("writeOBJ.LL403 50MB")
    wg.writeOBJ('tures/ll403.obj')
    c.stopRecord("WaveFrontPerf.txt")
  



  def testWriteOBZ(self):
    res = self.wg_cube_gris.writeOBZ(OBZ_FILE_GREY_CUBE_RES)
    self.assertTrue(res == C_OK)#

    res = self.wg_cube_gris.writeOBZ("badrep/toto.obz")
    self.assertTrue(res == C_ERROR)

    # Write in a non authorized directory
    res = self.wg_cube_gris.writeOBZ('/error.obz')
    self.assertTrue(res == C_ERROR)

    wg = readGeom(OBZ_FILE_PHF_LOWRES)

    c = ChronoMem.start("writeOBZ-PHFemaleLowRes.obz")
    wg.writeOBZ(OBZ_FILE_PHF_LOWRES_RES)
    c.stopRecord("WaveFrontPerf.txt")

  def testFusion(self):
    wg = readGeom(OBJ_FILE_RED_CUBE)
    wg_ressort = readGeom(OBJ_FILE_GREEN_TRON)
    li = [ wg_ressort ]
    outMapLst = [ ]
    wg.fusion(li, outMapLst)
    wg.writeOBJ("tures/fusioned_cubes.obj")


  def testCopy(self):
    wgnew = Test.wg_cube_gris.copy()
    self.assertTrue(wgnew != None)
    
    ret = wgnew.selectMaterial('Unfound')
    self.assertEqual(ret, -1)
    ret = wgnew.selectMaterial('matRouge')
    self.assertEqual(ret, 1)
    
    wgnew.scale(1.0,1.0,1.0)
    
    wgnew.translate(.0,.0,.0)

    grp = wgnew.getGroups()[0]
    r = grp.getFaceVertex(0, restab=[None, None, None, None])

    d = grp.calcXYRadius(grp.getFaceVertIdx(1))
    self.assertEqual(d, math.sqrt(2.0))
    
    r = grp.findFace(10)
    self.assertEqual(r, -1)
    
    grp.invertFaceOrder()
    self.assertEqual(grp.getFaceVertIdx(0), array.array('l', [1,2,3,0]))
    
    ret = grp.extractFaces(materialName='Bad Material')
    self.assertEqual(ret, None)

    # Bed dest name
    print(str(wgnew.lstMat))
    ret = grp.extractFaces(destName='Not a mat', materialName='matRouge')
    self.assertEqual(ret, None)

    wgnew.applySymZY()
    
    ret = wgnew.removeGroup('Not a Group', cleaning=True)
    self.assertEqual(ret, C_FAIL)

    ret = wgnew.removeGroup('cube1', cleaning=True)
    self.assertEqual(ret, C_OK)

    

  def testReadPerf(self):
    for i in range(0, 5):      
      c = ChronoMem.start("AbsWaveGeom.readGeom-2800f")
      wg_ressort = readGeom(OBJ_FILE_RESSORT)
      self.assertTrue(wg_ressort != None)
      c.stopRecord("WaveFrontPerf.txt")

 
  def testFillHoleSpider(self):
    #ChronoMem c
    wg = readGeom(OBJ_FILE_SPHERE_HOLE)

    r = wg.fillHole("sphere1", "Notfound", "unused", "Color", True, 2, 0.0625)
    self.assertEqual(r, C_MISSING_MAT)

    wg.lstMat.append('Alone')
    r = wg.fillHole("sphere1", "Alone", "unused", "Color", True, 2, 0.0625)
    self.assertEqual(r, C_MISSING_FACEMAT)

    c = ChronoMem.start("fillHoleSpider-Sphere1")
    r = wg.fillHole("sphere1", "TROU", "unused", "Color", True, 2, 0.0625)
    c.stopRecord("WaveFrontPerf.txt")

    self.assertEqual(r, C_OK)
    wg.writeOBJ("tures/sphere_filled3.obj")

    wg = readGeom(OBJ_FILE_SPHERE_HOLE)

    c = ChronoMem.start("fillHoleSpider-Sphere2")
    r = wg.fillHole(None, "TROU", "unused", "Color", False, 2, 0.1)
    c.stopRecord("WaveFrontPerf.txt")

    self.assertEqual(r, C_OK)
    wg.writeOBJ("tures/sphere_filled4.obj")

    wg = readGeom(OBJ_FILE_EARTH_HOLE)
    r = wg.fillHole("Terre", "TROU", "newGrp", "Color", True, 2, 0.0625) #, createCenter=False)
    
    wg.writeOBJ("tures/TerrePoignees+Trou_filled.obj")

    self.assertEqual(r, C_OK)
    self.assertEqual(814, len(wg.coordList))
    self.assertAlmostEqual(0.08213272, wg.coordList[801].x, delta=1e-6)
    self.assertAlmostEqual(0.35574902, wg.coordList[801].y, delta=1e-6)
    self.assertAlmostEqual(0.03402049, wg.coordList[801].z, delta=1e-6)

    self.assertAlmostEqual(0.0765935, wg.coordList[813].x, delta=1e-6)
    self.assertAlmostEqual(0.363881, wg.coordList[813].y, delta=1e-6)
    self.assertAlmostEqual(0.0218888, wg.coordList[813].z, delta=1e-6)

    self.assertEqual(299, len(wg.texList))
    self.assertAlmostEqual(0.330287, wg.texList[286].x, delta=1e-6)
    self.assertAlmostEqual(0.206048, wg.texList[286].y, delta=1e-6)
    self.assertAlmostEqual(0.379576, wg.texList[298].x, delta=1e-6)
    self.assertAlmostEqual(0.220285, wg.texList[298].y, delta=1e-6)


    wg = readGeom(OBJ_FILE_TOP_HOLE)
    c = ChronoMem.start("fillHoleSpider-Sphere2-01Top")
    r = wg.fillHole("lCollar", "TROU", "newGrp", "Color", True, 2, 0.0625)
    self.assertEqual(r, C_OK)
    self.assertEqual(7571, len(wg.coordList))
    self.assertEqual(7619, len(wg.texList))
    c.stopRecord("WaveFrontPerf.txt")

  def testExtract(self):
    c = ChronoMem.start("WaveGeom.readGeom-PHFemaleLowRes.obz")
    wg = readGeom(OBZ_FILE_PHF_LOWRES)
    c.stopRecord("WaveFrontPerf.txt")

    wgr = wg.extractSortGeom("badname")
    self.assertTrue(wgr == None)

    wgr = wg.extractSortGeom("hip:1")
    self.assertTrue(wgr != None)
    wgr.writeOBJ("tures/hip_extracted.obj")

    t = wg.extractSortJonction("lForeArm:1", "daube:1")
    self.assertTrue(t == None)

    t = wg.extractSortJonction("daube:1", "lShldr:1")
    self.assertTrue(t == None)

    c = ChronoMem.start("extractSortJonction-PHFemaleLowRes.obz")
    wg = readGeom(OBJ_FILE_ICOSAHEDRON)
    t = wg.extractSortJonction("icosahedron", "Prisme")
    c.stopRecord("WaveFrontPerf.txt")

    self.assertTrue(t != None)
    #self.assertEqual(3, len(t))
    self.assertEqual(str(t), '[12, 13, 14]')

#   def testCleanDupVert(self):
#     wg_cube_gris = readGeom(OBJ_FILE_GREY_CUBE)
#     r = wg_cube_gris.cleanDupVert(0.0)
#     self.assertEqual(C_FAIL, r)
# 
#     wg = readGeom(OBJ_FILE_DUPVERT_01)
#     r = wg.cleanDupVert(1.e-7)
#     self.assertEqual(C_OK, r)
#     self.assertEqual(20, len(wg.coordList))
#     wg.writeOBJ("tures/t1.obj")
# 
#     wg = readGeom(OBJ_FILE_DUPVERT_02)
#     r = wg.cleanDupVert(1.e-7)
#     self.assertEqual(C_OK, r)
#     self.assertEqual(32, len(wg.coordList))
#     wg.writeOBJ("tures/t2.obj")
# 
#     wg = readGeom(OBZ_FILE_PHF_LOWRES_SRC)
#     self.assertEqual(17184, len(wg.coordList))
#     r = wg.cleanDupVert(1e-7)
#     self.assertEqual(15981, len(wg.coordList))
#     self.assertEqual(C_OK, r)
#     wg.writeOBJ("tures/PHFemaleLowRes.obj")


  def testCleanDupVertKD(self):
    wg_cube_gris = readGeom(OBJ_FILE_GREY_CUBE)
    r = wg_cube_gris.cleanDupVert(0.0)
    self.assertEqual(C_FAIL, r)

    wg = readGeom(OBJ_FILE_DUPVERT_01)
    r = wg.cleanDupVert(1.e-6)
    self.assertEqual(C_OK, r)
    self.assertEqual(20, len(wg.coordList))
    wg.writeOBJ("tures/kdt1.obj")

    wg = readGeom(OBJ_FILE_DUPVERT_02)
    r = wg.cleanDupVert(1.e-7)
    self.assertEqual(C_OK, r)
    self.assertEqual(32, len(wg.coordList))
    wg.writeOBJ("tures/kdt2.obj")

    wg = readGeom(OBZ_FILE_PHF_LOWRES_SRC)
    self.assertEqual(17184, len(wg.coordList))
    r = wg.cleanDupVert(1e-7)
    self.assertEqual(15981, len(wg.coordList))
    self.assertEqual(C_OK, r)
    wg.writeOBJ("tures/kdPHFemaleLowRes.obj")
    # diff of files done with previous O(n2) done : No diff

  def testOptimizeGroups(self):
    wg_cube_gris = readGeom(OBJ_FILE_GREY_CUBE)
    r = wg_cube_gris.optimizeGroups(False, radius=0.0)
    self.assertEqual(C_FAIL, r)

    wg = readGeom(OBJ_FILE_DUPVERT_01)
    r = wg.optimizeGroups(True, radius=1.e-6)
    self.assertEqual(C_OK, r)
    self.assertEqual(20, len(wg.coordList))
    wg.writeOBJ("tures/optkdt1.obj")

    wg = readGeom(OBJ_FILE_DUPVERT_02)
    r = wg.optimizeGroups(True, radius=1.e-7)
    self.assertEqual(C_OK, r)
    self.assertEqual(32, len(wg.coordList))
    wg.writeOBJ("tures/optkdt2.obj")

    wg = readGeom(OBZ_FILE_PHF_LOWRES_SRC)
    self.assertEqual(17184, len(wg.coordList))
    r = wg.optimizeGroups(True, radius=1e-7)
    self.assertEqual(15981, len(wg.coordList))
    self.assertEqual(C_OK, r)
    wg.writeOBJ("tures/optkdPHFemaleLowRes.obj")
    # diff of files done with previous O(n2) done : No diff

    wg = readGeom('srcdata/CutterCubey0_252Optim.obj')
    #self.assertEqual(17184, len(wg.coordList))
    r = wg.optimizeGroups()
    self.assertEqual(8, len(wg.coordList))
    self.assertEqual(12, len(wg.texList))
    self.assertEqual(8, len(wg.normList))
    self.assertEqual(C_OK, r)


  def testRemoveFace(self):
    wg_cube_gris = readGeom(OBJ_FILE_GREY_CUBE)
    cube = wg_cube_gris.groups[0]
    
    ret = cube.createStrip([], [], None, None, False)
    self.assertEqual(ret, C_ERROR)
    
    ret = cube.removeFace()
    self.assertEqual(ret, C_ERROR)
    
    cube.removeFace(0)
    cube.removeFace(2)
    cube.removeFace(cube.getNbFace()-1)
    cube.sanityCheck()
    wg_cube_gris.writeOBJ('tures/Cube-removeFace.obj')

    wg = readGeom(OBJ_FILE_EARTH_HOLE)
    terre = wg.getGroup('Terre')
    terre.sanityCheck()

    ret = terre.removeFace(materialName='not a mat')
    self.assertEqual(ret, C_FAIL)


    terre.removeFace(0)
    terre.sanityCheck()
    terre.removeFace(50)
    terre.sanityCheck()
    terre.removeFace(terre.getNbFace()-1)
    terre.sanityCheck()
    wg.sanityCheck()
    wg.writeOBJ('tures/Terre-removeFace.obj')
    
    # Data Coruption
    del wg.coordList[10:15]
    del wg.texList[1:1]
    wg.sanityCheck()

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
