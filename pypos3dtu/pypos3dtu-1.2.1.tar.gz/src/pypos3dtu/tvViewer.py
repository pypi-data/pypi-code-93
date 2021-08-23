'''
Created on 2 janv. 2021

Unit tests for wavegeom vizualisation
'''
import unittest
import sys, cProfile, pstats
import time
import logging
import threading

from pypos3dtu.tuConst import ChronoMem, OBJ_FILE_GREY_CUBE, OBJ_FILE_RESSORT, OBJ_FILE_SPHERE_HOLE, OBZ_FILE_PHF_LOWRES, OBJ_FILE_ICOSAHEDRON
  
from pypos3d.wftk.WaveGeom import readGeom, WFMat

from pypos3dv.Drawable import RendWaveGeom, AxisGrid
from pypos3dv.Window import View3dWindow, View3dProcess


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

  # Bug fix test
  def testF4ULoading(self):
    objsrc = readGeom('srcdata/PoserRoot/Runtime/Geometries/Caparros_Aircrafts/F4U_Corsair.obj', usemtl=True)
    #objsrc.scale(10.0,10.0,10.0)
    objsrc.sanityCheck()

    View3dWindow(name='test F4U4', imgdirpath='srcdata/PoserRoot/Runtime/Textures/:.').addMesh(RendWaveGeom(objsrc))
    print('Hit : q to end the test or wait 30s')
    View3dWindow.MainLoop(exitWhenEmpty=True, maxDuration=30.0)




  def testMtlLoading(self):
    objsrc = readGeom('srcdata/CutterCubey0_25Tex.obj', usemtl=True, imgdirpath='.:/does/not/exists/:srcdata:/home')
    self.assertEqual(len(objsrc.libMat), 1)
    mat  = objsrc.libMat['Cubey0_25_auv']
    self.assertEqual(mat.d, 1.0)
    self.assertEqual(mat.map_kd, 'auvBG.png')

    win3d = View3dWindow(name='testDirectWindow', imgdirpath='srcdata/PoserRoot/Runtime/Textures/:.')
    win3d.addMesh(RendWaveGeom(objsrc))
    
    objsrc = readGeom('srcdata/PoserRoot/Runtime/Geometries/Pojamas/Globe.obj', usemtl=True, \
                      imgdirpath='srcdata/PoserRoot/Runtime/Geometries/Pojamas/')

    win3d.addMesh(RendWaveGeom(objsrc, location=(0.0,1.0,1.0)))
    
    dmat = WFMat.readMtl('srcdata/Default-Brouette.mtl')
    
    win3d.add('srcdata/PoserRoot/Runtime/Geometries/Pojamas/Wheeled_Barrel3.obz', matDict=dmat,\
              location=(1.0,0.0,1.0))
    
    print('Hit : q to end the test or wait 30s')
    View3dWindow.MainLoop(exitWhenEmpty=True, maxDuration=30.0)


  def testWProc1(self):
    winproc = View3dProcess(name="No Grid", axisGrid=-1)
    
    time.sleep(1)
    
    wg_cube_gris = readGeom(OBJ_FILE_GREY_CUBE)
    
    winproc.add(wg_cube_gris)
    
    winproc.add(OBJ_FILE_RESSORT, location=(1.0,1.0,1.0))

    wg = readGeom(OBJ_FILE_SPHERE_HOLE)
    for i in range(10):      
      winproc.add(wg, { 'TROU':WFMat('', kd=(1.0,0.0,0.0)), 'default':WFMat('', kd=(0.0,0.1*i,0.0)) }, location=(-1.0,0.0,-float(i)))
        
    time.sleep(5)
    winproc.end()
    
    
  def testDirectWindow(self):
    c = ChronoMem.start("test Direct Window")
    
    win3d = View3dWindow(name='testDirectWindow', axisGrid=AxisGrid(nbStep=5, space=0.1, gridColor=(0.8,0.8,0.8,1.0), withAxis=False))
    wg = readGeom(OBJ_FILE_RESSORT)
    win3d.addMesh(RendWaveGeom(wg, location=(1.0,1.0,1.0)))
    wg = readGeom(OBJ_FILE_SPHERE_HOLE)
    win3d.addMesh(RendWaveGeom(wg, { 'TROU':WFMat('TROU', kd=(1.0,0.0,0.0, 0.5)), 'default':WFMat('default', kd=(0.0,1.0,0.0, 0.1)) }, location=(-1.0,0.0,0.0)))
    c.stopRecord("FigurePerf.txt")
    
    print('Hit : q to end the test')
    View3dWindow.MainLoop(maxDuration=30.0)


  def testBleding(self):
    win3d = View3dWindow(name='testBlending')
    fntex = 'srcdata/PoserRoot/Runtime/Textures/Wheeled_Barrel_Tex.jpg'

    c = ChronoMem.start("test Blending 1")
    wg = readGeom("srcdata/PoserRoot/Runtime/Geometries/Pojamas/Wheeled_Barrel3.obz")
    c.stopRecord("FigurePerf.txt")

    c = ChronoMem.start("test Blending 2")
    win3d.addMesh(RendWaveGeom(wg, {'Wood':WFMat('Wood', kd=(0.0,0.0,0.0,1.0), map_kd=fntex), 
                                    'Wood1':WFMat('Wood1', kd=(0.0,0.0,0.0,0.5), map_kd=fntex), 
                                    'Wood2':WFMat('Wood2', kd=(0.0,0.0,0.0,1.0), map_kd=fntex), 
                                    'Wood3':WFMat('Wood3', kd=(0.0,0.0,0.0,1.0), map_kd=fntex), \
                                    'Steel2':WFMat('Iron2', kd=(0.0,0.0,0.0,1.0), map_kd=fntex), \
                                    'Iron2':WFMat('Iron2', kd=(0.3,0.3,0.3,.5)), \
                                    'default':WFMat('default', kd=(0.0,1.0,0.0, 0.1)) }, \
                              location=(0.0,0.0,0.0)))
    c.stopRecord("FigurePerf.txt")
    #win3d.run()
    print('Hit : q to end the test')
    View3dWindow.MainLoop(maxDuration=60.0)

  def testDirectWindowPHF(self):
    winproc1 = View3dWindow(name='PHF', width=512, height=512)

    c = ChronoMem.start("test Blending")
    wg = readGeom(OBZ_FILE_PHF_LOWRES)
    winproc1.add(wg, location=(-1.0,0.0,0.0))
    
    fntex = 'srcdata/PoserRoot/Runtime/Textures/PHF-Fake-Texture.jpg'
    winproc1.add(OBZ_FILE_PHF_LOWRES, {'Skin':WFMat('', kd=(1.0,1.0,1.0,1.0), map_kd="srcdata/PoserRoot/Runtime/Textures/PHFemC1.jpg"), \
                                       'Nipples':WFMat('', kd=(0.2,0.0,0.0,1.0), map_kd=fntex), \
                                       'Tongue':WFMat('', kd=(0.0,.5,1.0)), \
                                       'InnerMouth':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Teeth':WFMat('', kd=(0.95,.95,1.0)), \
                                       'Lacrimal':WFMat('', kd=(0.0,.5,1.0)), \
                                       'EyelashBottom':WFMat('', kd=(0.0,.5,1.0)), \
                                       'EyelashTop':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Eyebrows':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Lips':WFMat('', kd=(0.0,.5,1.0)), \
                                       'MouthLining':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Eyeball':WFMat('', kd=(0.0,.0,.0)), \
                                       'Eyetrans':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Iris':WFMat('', kd=(0.0,.1,1.0)), \
                                       'Pupil':WFMat('', kd=(0.0,.0,.0)), \
                                       'Fingernails':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Toesnails':WFMat('Toesnails', kd=(0.0,.5,1.0)) }, (.0,0.0,0.0) )
            
    c.stopRecord("FigurePerf.txt")
    View3dWindow.MainLoop(maxDuration=30.0)
    
    # Again
    winproc1 = View3dWindow(name='PHF', width=512, height=512)
    wg = readGeom(OBZ_FILE_PHF_LOWRES)
    winproc1.add(wg, location=(-1.0,0.0,0.0))
    View3dWindow.MainLoop(maxDuration=30.0)



  def testMultiThread(self):

    RENDER_THR = threading.Thread(target=View3dWindow.MainLoop, kwargs={'maxDuration':30.0})
    RENDER_THR.start()
    
    winproc1 = View3dWindow(name='PHF', width=512, height=512)
    wg = readGeom(OBZ_FILE_PHF_LOWRES)
    winproc1.add(wg)
    
    time.sleep(1)
    fntex = 'srcdata/PoserRoot/Runtime/Textures/PHFemC1.jpg'
    winproc1.add(OBZ_FILE_PHF_LOWRES, {'Skin':WFMat('', map_kd=fntex), \
                                       'Nipples':WFMat('', map_kd=fntex), \
                                       'Tongue':WFMat('', kd=(0.0,.5,1.0)), \
                                       'InnerMouth':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Teeth':WFMat('', kd=(0.95,.95,1.0)), \
                                       'Lacrimal':WFMat('', kd=(0.0,.5,1.0)), \
                                       'EyelashBottom':WFMat('', kd=(0.0,.5,1.0)), \
                                       'EyelashTop':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Eyebrows':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Lips':WFMat('', kd=(0.0,.5,1.0)), \
                                       'MouthLining':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Eyeball':WFMat('', kd=(0.0,.0,.0)), \
                                       'Eyetrans':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Iris':WFMat('', kd=(0.0,.1,1.0)), \
                                       'Pupil':WFMat('', kd=(0.0,.0,.0)), \
                                       'Fingernails':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Toesnails':WFMat('Toesnails', kd=(0.0,.5,1.0)) }, (-1.0,0.0,0.0) )
            
    winproc2 = View3dWindow(name='Figure', width=640, height=400)
    winproc2.add(OBJ_FILE_ICOSAHEDRON,  { 'default':WFMat('default', kd=(0.3,0.0,0.0)), 'm2':WFMat('m2', kd=(0.0,0.8,0.0)) } , (1.0,0.0,0.0) )
    r2 = winproc2.add(OBJ_FILE_ICOSAHEDRON,  { 'default':WFMat('default', kd=(0.3,0.0,0.0)), 'm2':WFMat('m2', kd=(0.0,0.8,0.1)) } , (2.0,0.0,0.0) )
  
    time.sleep(5)
    
    winproc2.hide(r2)
    time.sleep(3)
    
    for i in range(10):      
      roid = winproc1.add(wg, { 'TROU':WFMat('TROU', kd=(1.0,0.0,0.0)), 'default':WFMat('default', kd=(0.0,0.1*i,0.0))}, location=(-1.0,0.0,-float(i)))
      winproc1.hide(roid)
      
    time.sleep(3)
    winproc1.show(roid)
    time.sleep(1)
    
    winproc2.onClose(0)    
    winproc1.onClose(0)    

    RENDER_THR.join()
    
    
  def testMultiProcess(self):
    winproc1 = View3dProcess(name='PHF', width=512, height=512)
    wg = readGeom(OBZ_FILE_PHF_LOWRES)
    winproc1.add(wg)
    
    time.sleep(1)
    fntex = 'srcdata/PoserRoot/Runtime/Textures/PHFemC1.jpg'
    winproc1.add(OBZ_FILE_PHF_LOWRES, {'Skin':WFMat('', map_kd=fntex), \
                                       'Nipples':WFMat('', map_kd=fntex), \
                                       'Tongue':WFMat('', kd=(0.0,.5,1.0)), \
                                       'InnerMouth':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Teeth':WFMat('', kd=(0.95,.95,1.0)), \
                                       'Lacrimal':WFMat('', kd=(0.0,.5,1.0)), \
                                       'EyelashBottom':WFMat('', kd=(0.0,.5,1.0)), \
                                       'EyelashTop':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Eyebrows':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Lips':WFMat('', kd=(0.0,.5,1.0)), \
                                       'MouthLining':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Eyeball':WFMat('', kd=(0.0,.0,.0)), \
                                       'Eyetrans':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Iris':WFMat('', kd=(0.0,.1,1.0)), \
                                       'Pupil':WFMat('', kd=(0.0,.0,.0)), \
                                       'Fingernails':WFMat('', kd=(0.0,.5,1.0)), \
                                       'Toesnails':WFMat('Toesnails', kd=(0.0,.5,1.0)) }, (-1.0,0.0,0.0) )
            
    winproc2 = View3dProcess(name='Figure', width=640, height=400)
    winproc2.add(OBJ_FILE_ICOSAHEDRON,  { 'default':WFMat('default', kd=(0.3,0.0,0.0)), 'm2':WFMat('m2', kd=(0.0,0.8,0.0)) } , (1.0,0.0,0.0) )
    r2 = winproc2.add(OBJ_FILE_ICOSAHEDRON,  { 'default':WFMat('default', kd=(0.3,0.0,0.0)), 'm2':WFMat('m2', kd=(0.0,0.8,0.1)) } , (2.0,0.0,0.0) )
  
    time.sleep(5)
    
    winproc2.hide(r2)
    time.sleep(3)
    
    for i in range(10):      
      roid = winproc1.add(wg, { 'TROU':WFMat('TROU', kd=(1.0,0.0,0.0)), 'default':WFMat('default', kd=(0.0,0.1*i,0.0))}, location=(-1.0,0.0,-float(i)))
      winproc1.hide(roid)
      
    time.sleep(3)
    winproc1.show(roid)
    time.sleep(1)
    
    winproc2.end()    
    winproc1.end()    
    
if __name__ == "__main__":
  #import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
