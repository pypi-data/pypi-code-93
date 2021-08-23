'''
Created on 20 mai 2020

@author: olivier
'''
import unittest
import logging
import sys, cProfile, pstats


from pypos3dtu.tuConst import ChronoMem, P7ROOT, PP2_VILLE_TEST_MOD, PP2_VILLE_TEST, PZ3_FLAT_GRID_1, PZ3_MAPPINGCUBES_CLOTHE
from langutil import C_OK, C_ERROR , C_FAIL, C_FILE_NOT_FOUND
from langutil.File import File
from pypos3d.wftk.WFBasic import Vector3d, Point3d, C_BAD_DELTAINDEX
from pypos3d.wftk.WaveGeom import readGeom
from pypos3d.pftk.PoserBasic import PoserConst
from pypos3d.pftk.PoserMeshed import ReportOption
from pypos3d.pftk.PoserFile import PoserFile

PROFILING = False


# This code was written by Krzysztof Kowalczyk (http://blog.kowalczyk.info)
# and is placed in public domain.

# -->To be used in pypos3dapp installation procedure

# Convert a Mozilla-style version string into a floating-point number
#   1.2.3.4, 1.2a5, 2.3.4b1pre, 3.0rc2, etc
def version2float(v):

  def v2fhelper(v, suff, version, weight):
    parts = v.split(suff)
    if 2 != len(parts):
        return v
    version[4] = weight
    version[5] = parts[1]
    return parts[0]
  
  version = [
      0, 0, 0, 0, # 4-part numerical revision
      4, # Alpha, beta, RC or (default) final
      0, # Alpha, beta, or RC version revision
      1  # Pre or (default) final
  ]
  parts = v.split("pre")
  if 2 == len(parts):
      version[6] = 0
      v = parts[0]

  v = v2fhelper(v, "a",  version, 1)
  v = v2fhelper(v, "b",  version, 2)
  v = v2fhelper(v, "rc", version, 3)

  parts = v.split(".")[:4]
  for (p, i) in zip(parts, range(len(parts))):
      version[i] = p
  ver = float(version[0])
  ver += float(version[1]) / 100.
  ver += float(version[2]) / 10000.
  ver += float(version[3]) / 1000000.
  ver += float(version[4]) / 100000000.
  ver += float(version[5]) / 10000000000.
  ver += float(version[6]) / 1000000000000.
  return ver


# Return True if ver1 > ver2 using semantics of comparing version
# numbers
def ProgramVersionGreater(ver1, ver2):
  v1f = version2float(ver1)
  v2f = version2float(ver2)
  return v1f > v2f



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

  def testCreateDeltasMLS(self):
    sc1 = PoserFile(PP2_VILLE_TEST_MOD)
    lprp = sc1.getLstProp()
    p1 = lprp[0]

    sc2 = PoserFile(PP2_VILLE_TEST)
    lprp2 = sc2.getLstProp()
    pRef = lprp2[0]

    # === Test : Colline/MLS enhancement/No Bounding =========================================
    hs = { "Ville_morphColline" }

    c = ChronoMem.start("PoserMeshedObject.createDeltas Ville MLS")
    ropt = ReportOption( Vector3d(), 0.005, PoserConst.C_MLS_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6)
    
    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEqual(res, C_OK)

    gt = p1.getTargetGeom("Ville_morphColline")
    t = sorted(gt.getDeltas().deltaSet.values(), key=lambda p:p.noPt)
    self.assertEqual(1773, len(t))

    self.assertEqual(5481, t[0].noPt)
    self.assertAlmostEqual(Vector3d(4.268659260775465E-4, -0.0019890811223694654, 8.042339065665316E-4), t[0].toV3d(), delta=1e-6)
    self.assertEqual(5582, t[25].noPt)
    self.assertAlmostEqual(Vector3d(-0.003635393340107651, 0.009744775219383495, -0.007931459514205597), t[25].toV3d(), delta=1e-6)
    self.assertEqual(5584, t[27].noPt)
    self.assertAlmostEqual(0.03664886, t[27].y, delta=1e-6)

    gt.setName("Ville_morphColline_NoBounding")

    # Save result for Poser Visual verification    
    sc1.writeFile("tures/Ville_Test_MLS_Reported.pp2")

  def testCreateDeltasSimple(self):
    sc1 = PoserFile(PP2_VILLE_TEST_MOD)
    lprp = sc1.getLstProp()
    p1 = lprp[0]
    # TODO: + checkChannelDelta
    sc2 = PoserFile(PP2_VILLE_TEST)
    lprp2 = sc2.getLstProp()
    pRef = lprp2[0]

    ropt = ReportOption(Vector3d(), 0.0, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, False, 0.0)
    
    # === Degrated directory test =============================================================
    res = p1.createDeltas("badrep", pRef, None, ropt)
    self.assertEqual(res, C_ERROR)

    sc1 = PoserFile(PP2_VILLE_TEST_MOD)
    lprp = sc1.getLstProp()
    p1 = lprp[0]

    sc2 = PoserFile(PP2_VILLE_TEST)
    lprp2 = sc2.getLstProp()
    pRef = lprp2[0]

    # === Test : Antenne/NO enhancement/No Bounding ===============================================
    hs = { "Ville_morphAntenne" }
    ropt = ReportOption(Vector3d(), 0.005, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, False, 0.0)

    c = ChronoMem.start("PoserMeshedObject.createDeltas Ville NO NO")
    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    c.stopRecord("FigurePerf.txt")

    self.assertEqual(res, C_OK)
    gt = p1.getTargetGeom("Ville_morphAntenne")
    dlt = gt.getDeltas()
    t = sorted(dlt.deltaSet.values(), key=lambda p:p.noPt)
    self.assertEqual(2, len(t))
    self.assertEqual(10059, t[0].noPt)
    self.assertAlmostEqual(Vector3d(0.0, 0.1885228, 0.0), t[0], delta=1e-6)
    self.assertEqual(10062, t[1].noPt)
    self.assertAlmostEqual(Vector3d(0.0, 0.1885228, 0.0), t[1], delta=1e-6)

    # Save result for Poser Visual verification    
    sc1.writeFile("tures/Ville_Test_Simple_Reported.pp2")

  def testCreateDeltasSimple2(self):
    sc1 = PoserFile(PZ3_FLAT_GRID_1)
    lprp = sc1.getLstProp()
    pRef = lprp[0]
    p1 = lprp[1]

    # === Test : Antenne/NO enhancement/No Bounding ===============================================
    hs = { "Bosse 1" }

    ropt = ReportOption(Vector3d(), 0.2, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, False, 0.0)
    c = ChronoMem.start("PoserMeshedObject.createDeltas NO NO")
    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEqual(res, C_OK)
    t = p1.getTargetGeom("Bosse 1").getDeltas().deltaSet
    self.assertEqual(365, len(t)) # Result was 365 with the Java exact algorithm

    
    ropt = ReportOption(Vector3d(), 0.2, PoserConst.C_AVG_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6)
    c = ChronoMem.start("PoserMeshedObject.createDeltas AVG NO")
    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEqual(res, C_OK)
    t = p1.getTargetGeom("Bosse 1").getDeltas().deltaSet
    self.assertEqual(461, len(t)) 
    sc1.writeFile("tures/Flat_Grid_Report_AVG_NO.pz3")

    # Save result for Poser Visual verification    
    sc1.writeFile("tures/Flat_Grid_Report_NO_NO.pz3")

    ropt = ReportOption(Vector3d(), 0.2, PoserConst.C_MLS_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6)
    c = ChronoMem.start("PoserMeshedObject.createDeltas MLS NO")
    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEqual(res, C_OK)
    t = p1.getTargetGeom("Bosse 1").getDeltas().deltaSet
    self.assertEqual(414, len(t))
    sc1.writeFile("tures/Flat_Grid_Report_MLS_NO.pz3")
   

  # Test with a centrale deformation 
  def testCreateDeltasSimple3(self):
    sc1 = PoserFile(PZ3_FLAT_GRID_1)
    lprp = sc1.getLstProp()
    pRef = lprp[0]
    p1 = lprp[1]

    hs = { "Bosse Centrale" }

    ropt = ReportOption(Vector3d(), 0.2, PoserConst.C_AVG_ENHANCEMENT, PoserConst.C_NO_BOUNDING, False, 0.0)

    # File not found error case
    res = p1.createDeltas('/tmp', pRef, hs, ropt)
    self.assertEqual(res, C_FILE_NOT_FOUND)

    sc1 = PoserFile(PZ3_FLAT_GRID_1)
    lprp = sc1.getLstProp()
    pRef = lprp[0]
    p1 = lprp[1]

    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    self.assertEqual(res, C_OK)
    sc1.writeFile("tures/Flat_Grid_M2_Report_AVG_NO.pz3")

    ropt = ReportOption(Vector3d(), 0.2, PoserConst.C_AVG_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6)
    c = ChronoMem.start("PoserMeshedObject.createDeltas MLS NO 3")
    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEqual(res, C_OK)
    t = p1.getTargetGeom("Bosse Centrale").getDeltas().deltaSet
    self.assertEqual(1053, len(t))
    sc1.writeFile("tures/Flat_Grid_M2_Report_MLS_NO.pz3")


  def testCreateDeltasAVG(self):
    sc1 = PoserFile(PP2_VILLE_TEST_MOD)
    lprp = sc1.getLstProp()
    p1 = lprp[0]

    sc2 = PoserFile(PP2_VILLE_TEST)
    lprp2 = sc2.getLstProp()
    pRef = lprp2[0]

    # === Test : Toit/Average enhancement/Box Bounding =========================================
    hs = { "Ville_morphToit" }
    
    ropt = ReportOption(Vector3d(), 0.005, PoserConst.C_AVG_ENHANCEMENT, PoserConst.C_BOX_BOUNDING, True, 0.0)
    c = ChronoMem.start("PoserMeshedObject.createDeltas")
    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    
    gt = p1.getTargetGeom("Ville_morphToit")
    dlt = gt.getDeltas()
    t = sorted(dlt.deltaSet.values(), key=lambda p:p.noPt)
    self.assertEqual(16, len(t))

    self.assertEqual(10074, t[0].noPt)
    self.assertEqual(Vector3d(0.0, 0.04999995, 0.0), t[0])
    self.assertEqual(10076, t[2].noPt)
    self.assertEqual(Vector3d(0.0, 0.15, 0.0), t[2])

    gt.setName("Ville_morphToit_Boxed")
    self.assertEqual(res, C_OK)

    # === Test : Toit/Average enhancement/Sphere Bounding =========================================
    c = ChronoMem.start("PoserMeshedObject.createDeltas")
    ropt = ReportOption(Vector3d(), 0.005, PoserConst.C_AVG_ENHANCEMENT, PoserConst.C_SPHERE_BOUNDING, True, 0.0)
    res = p1.createDeltas(P7ROOT, pRef, hs, ropt)
    c.stopRecord("FigurePerf.txt")

    gt = p1.getTargetGeom("Ville_morphToit")
    dlt = gt.getDeltas()
    t = sorted(dlt.deltaSet.values(), key=lambda p:p.noPt)
    self.assertEqual(28, len(t))
    self.assertEqual(10073, t[9].noPt)
    self.assertAlmostEqual(0.0, t[9].x, delta=1e-6)
    self.assertAlmostEqual(0.07499995500000001, t[9].y, delta=1e-6)
    self.assertAlmostEqual(0.0, t[9].z, delta=1e-6)
    
    self.assertEqual(10074, t[10].noPt)
    #self.assertEqual(Vector3d(0.0, 0.04999995, 0.0), t[1])
    self.assertAlmostEqual(0.0, t[10].x, delta=1e-6)
    self.assertAlmostEqual(0.04999995, t[10].y, delta=1e-6)
    self.assertAlmostEqual(0.0, t[10].z, delta=1e-6)
    
    self.assertEqual(10076, t[12].noPt)
    self.assertAlmostEqual(Vector3d(0.0, 0.15, 0.0), t[12], delta=1e-6)
    #self.assertAlmostEqual(0.0, t[14].x, delta=1e-6)
    #self.assertAlmostEqual(0.15, t[14].y, delta=1e-6)
    #self.assertAlmostEqual(0.0, t[14].z, delta=1e-6)   
    
    gt.setName("Ville_morphToit_Sphere")
    self.assertEqual(res, C_OK)

    # Save result for Poser Visual verification    
    sc1.writeFile("tures/Ville_Test_AVG_Reported.pp2")

  def testCreateMorph(self):
    sc1 = PoserFile(PZ3_MAPPINGCUBES_CLOTHE)
    fig = sc1.getLstFigure()[0]
    body = fig.getActors()[0]
    c0Act = fig.findActor('c0:1')
    c1Act = fig.findActor('c1:1')
    #top = sc1.getLstProp()[0]

    wg = readGeom('srcdata/MappingCube-c0-Morphed.obj')
    wg1 = readGeom('srcdata/MappingCube-c1bis-Morphed.obj')

    #ret = act.createMorph(poserRootDir, morphGeomGroup, targetMorphName, masterMorphName=None, altGeomNo=0, minVectLen=0.0)
    ret = body.createMorph('Bad dir', wg.getGroup('c0'), 'Edge_Morph') # , masterMorphName=None, altGeomNo=0, minVectLen=0.0)
    self.assertEqual(ret, C_FILE_NOT_FOUND)

    #ret = act.createMorph(poserRootDir, morphGeomGroup, targetMorphName, masterMorphName=None, altGeomNo=0, minVectLen=0.0)
    ret = c0Act.createMorph('Bad dir', wg.getGroup('c0'), 'Edge_Morph', altGeomNo=0) # , masterMorphName=None, altGeomNo=0, minVectLen=0.0)
    self.assertEqual(ret, C_FILE_NOT_FOUND)

    ret = c1Act.createMorph('', wg1.getGroup('c1bis'), 'Edge_Morph', altGeomNo=1, masterMorphName='Edge_Top_Morph', minVectLen=0.0)
    self.assertEqual(ret, C_FILE_NOT_FOUND)
    
    ret = c0Act.createMorph(P7ROOT, wg.getGroup('c0'), 'Edge_Morph', altGeomNo=2) # , masterMorphName=None, altGeomNo=0, minVectLen=0.0)
    self.assertEqual(ret, C_FAIL)

    ret = c1Act.createMorph(P7ROOT, wg.getGroup('c0'), 'Edge_Morph', altGeomNo=1) # , masterMorphName=None, altGeomNo=0, minVectLen=0.0)
    self.assertEqual(ret, C_BAD_DELTAINDEX)

    ret = c0Act.createMorph(P7ROOT, wg.getGroup('c0'), 'Edge_Morph' , masterMorphName='Edge_Top_Morph', altGeomNo=0, minVectLen=0.0)
    self.assertEqual(ret, C_OK)

    ret = c1Act.createMorph(P7ROOT, wg1.getGroup('c1bis'), 'Edge_Morph', altGeomNo=1, masterMorphName='Edge_Top_Morph', minVectLen=0.0)
    self.assertEqual(ret, C_OK)


    sc1.save('tures/MappingCube-Morphed.pz3')


  def testSetters(self):
    sc1 = PoserFile(PZ3_MAPPINGCUBES_CLOTHE)
    fig = sc1.getLstFigure()[0]
    act = fig.getActors()[0]
    top = sc1.getLstProp()[0]

    act.setPrintName(None)
    act.setName("Neu")

    s = act.getDisplayName()

    act.isVisible()
    act.setVisible(True)

    act.isHidden()
    act.setHidden(False)

    act.isBend()

    act.setBend(False)
    act.isAddToMenu()
    act.setAddToMenu(True)

    act.isDisplayOrigin()
    act.setDisplayOrigin(False)

    act.getDisplayMode()

    act.getCreaseAngle()
    act.setCreaseAngle(80.0)

    act.getEndPoint()
    act.setEndPoint( Point3d())

    act.getParent()
    act.setParent('Parent String')

    act.getConformingTarget()
    act.setConformingTarget("hand")

    act.getCustomMaterial()
    act.setCustomMaterial(0)

    act.isLocked()

    act.getOrigin()
    act.setOrigin(Vector3d())
  
    act.getOrientation()
    act.setOrientation(Vector3d())

    
    geom = top.getBaseMesh(P7ROOT)
    self.assertTrue(geom)
    
    s = act.printBaseGeomCustom()
    self.assertEqual(s, 'None')
    s = top.printBaseGeomCustom()
    self.assertEqual(s, 'File[:Runtime:Geometries:Pojamas:MappingCubes-c1Clothe.obj]')

    c1 = fig.findActor('c1:1')
    lstAl = c1.getAltGeomList()
    self.assertEqual(len(lstAl), 1)
    
    
    fi = File('srcdata/PoserRoot/Runtime/Geometries/Pojamas/MappingCube-c1bis.obj')
    ret = c1.addAltGeom(altGeomFile=fi, poserRootDir=P7ROOT)
    self.assertEqual(ret, C_OK)    
    lstAl = c1.getAltGeomList()
    self.assertEqual(len(lstAl), 2)
    ag = lstAl[1]
    print(str(lstAl))

    ret = c1.removeAltGeom(None)
    self.assertEqual(ret, C_FAIL)
    
    ret = c1.moveAltGeom(ag)
    self.assertEqual(ret, C_OK)
    lstAl = c1.getAltGeomList()
    print(str(lstAl))
    
    ret = c1.removeAltGeom(ag)
    self.assertEqual(ret, C_OK)
    
    
    # Complement to CustomData
    self.assertFalse( c1.hasCustomData() )
    d = c1.getCustomData()
    self.assertTrue( d==None )
    
    c1.setCustomData('cle', 'donnees=1')
    
    # Coverage Compl
    ret = c1.deleteChannel('no name')
    self.assertEqual(ret, C_FAIL)
    
    ret = c1.deleteChannel('taper')
    self.assertEqual(ret, C_OK)
    
    dlt = c1.findDelta('Enlarge', 4)
    self.assertEqual(str(dlt), 'd 4  0.00000000 -0.20000000  0.20000000')
    dlt = c1.findDelta('Enlarge', 50)
    self.assertTrue(dlt==None)
    
    ret = c1.checkChannelDelta(c1.getChannel('enlarge'), P7ROOT)
    self.assertEqual(ret, C_OK)
# 
#     


  def testProgramVersion(self):
    assert ProgramVersionGreater("0.1", "0.1.0rc0")
    assert ProgramVersionGreater("1", "0.9")
    assert ProgramVersionGreater("0.0.0.2", "0.0.0.1")
    assert ProgramVersionGreater("1.0", "0.9")
    assert ProgramVersionGreater("2.0.1", "2.0.0")
    assert ProgramVersionGreater("2.0.1", "2.0")
    assert ProgramVersionGreater("2.0.1", "2")
    assert ProgramVersionGreater("0.9.1", "0.9.0")
    assert ProgramVersionGreater("0.9.2", "0.9.1")
    assert ProgramVersionGreater("0.9.11", "0.9.2")
    assert ProgramVersionGreater("0.9.12", "0.9.11")
    assert ProgramVersionGreater("0.10", "0.9")
    assert ProgramVersionGreater("2.0", "2.0b35")
    assert ProgramVersionGreater("1.10.3", "1.10.3b3")
    assert ProgramVersionGreater("88", "88a12")
    assert ProgramVersionGreater("0.0.33", "0.0.33rc23")
    print("All tests passed")

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
    
