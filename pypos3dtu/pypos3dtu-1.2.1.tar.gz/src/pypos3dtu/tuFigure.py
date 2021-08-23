'''
Created on 12 mai 2020

@author: olivier
'''
import unittest
import logging, os.path
import sys, cProfile, pstats
import math

from pypos3dtu.tuConst import ChronoMem, P7ROOT, PZZ_PHF_BOOK_TOP, PZZ_PHF_BUXOM_BARBARIAN_ROBE, PZZ_PHF_BUXOM_BARBARIAN2, PZ3_PHF_UGLY, \
  PZ3_MAPMONDE_CHANNEL_01, PZ3_PHF_ALTGEOM_ROBOT, PZ3_PHF_ALTGEOM_ROBOT_RES, PZ3_MAPMONDE_ALTGEOM, CR2_MAPPINGCUBES_ALTGEOM, \
  PZ3_MAPPINGCUBES_CLOTHE

from langutil import C_OK, C_ERROR, C_FAIL, C_FILE_NOT_FOUND, LogStatus, UsageError
from pypos3d.wftk.WFBasic import Vector3d
from pypos3d.pftk.PoserBasic import PoserToken, PoserConst, readXLSFile, getRealPath, buildRelPath, cleanName
from pypos3d.pftk.StructuredAttribut import calcMapping_KDTree, ChannelMorphStatusList,\
  GenericTransform
from pypos3d.pftk.GeomCustom import GeomCustom
from pypos3d.pftk.PoserMeshed import ReportOption
from pypos3d.pftk.PoserFile import PoserFile
from pypos3d.wftk.WaveGeom import readGeom, WaveGeom, WFMat
from pypos3d.pftk.ChannelImportAnalysis import ChannelDescriptor, FigurePart, nextWord

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


  def testLogStatus(self):
    
    c = LogStatus()
    c.info('Information {:s}', 'chaine 0')
    c.status(C_OK, 'test {:s}', 'chaine 1')
    c.logCond(True, 'The Result {:s} is {:d}', 'test', 45)
    c.logCond(False, 'The Result {:s} is {:d}', 'test', -45.1, 654, 54,54)
    
    fp = FigurePart()
    fp.logCond(True, 'The Result {:s} is {:d}', 'test', 45)


  def testMechaCreateB17(self):
    pf = PoserFile('srcdata/Empty.pz3')
    fig = pf.createFigure()
    self.assertEqual(fig.getBodyIndex(), 1)
    
    # Load the Source Wavegeom
    wg = readGeom('srcdata/b17-exp.obj')
    #FigurePart'partType, lev,       name,    printName,ge,                 geomGroup,        oplst,            trans,             rot,            orient,         center, hidden, addToMenu
    lstParts = [
      FigurePart('fig',  0,             '',    'B17G',  'tures/b17g.obj',          '',           '',                '',                 '', '',                  '', '', ''),
      FigurePart('act',  0,         'BODY',    'BODY',  wg,                     None,            (),               '',               '', '',                  '', '', '1'),
      FigurePart('act',  1,     'Fuselage','Fuselage',  wg,  wg.getGroup('Fuselage'),      ('add',),               '',               '', '',   '', '', '1'),
      FigurePart('geom',-1,            '',         '',  wg,     wg.getGroup('lWing'),  ('combine',),               '',               '', '', '', '', ''),
      FigurePart('geom',-1,            '',         '',  wg, wg.getGroup('lNacelle1'),      ('add',),          '',               '', '', '', '', ''),
      FigurePart('geom',-1,            '',         '',  wg, wg.getGroup('lNacelle2'),      ('add',),          '',               '', '', '', '', ''),
      FigurePart('geom',-1,            '',         '',  wg,     wg.getGroup('rWing'),  ('combine',),               '',               '', '', '', '', ''),
      FigurePart('geom',-1,            '',         '',  wg, wg.getGroup('lNacelle1'),      ('add',),          'symyz',               '', '', '', '', ''),
      FigurePart('geom',-1,            '',         '',  wg, wg.getGroup('lNacelle2'),      ('add',),          'symyz',               '', '', '', '', ''),

      FigurePart('act',  2,     'Engine1',  'Engine1',  wg,     wg.getGroup('R1820'),      ('add',), '(2.39856, 0.888098, 3.144764)',    '', '',                  '', '', '1'),
      FigurePart('geom',-1,            '',         '',  wg, wg.getGroup('R1820_Cylindre'), ('combine',),      '',               '', '', '', '', ''),
      FigurePart('geom',-1,            '',         '',  wg, wg.getGroup('R1820_Cylindre'), ('combine',),      '', '(0.0,0.0,360.0/9.0)', '', '(0.0,0.0,0.0)', '', ''),    
      FigurePart('geom',-1,            '',         '',  wg, wg.getGroup('R1820_Cylindre'), ('combine',),      '', '(0.0,0.0,2*360.0/9.0)', '', '(0.0,0.0,0.0)', '', ''),    
      FigurePart('act',  3,  'Properler1','Properler',  wg, wg.getGroup('Spinner'),        ('add',),    'moveto:face=Normal:(0.0,0.0,0.356)', '', 'zxy,face=Normal', 'face=Normal',  '', '1'),
      FigurePart('geom',-1,            '',         '',  wg, wg.getGroup('Properler'),      ('combine', ),           '',               '', '',   '', '', '1'),
      FigurePart('act',  2,     'Engine2',  'Engine2',  None,                'R1820',    ('reuse',),    '(1.130354, 0.783801, 3.328127)', '', '',  '', '', '1'),
      FigurePart('act',  3,  'Properler2','Properler',  None,              'Spinner',    ('reuse',),    'moveto:Engine2:face=Normal:(0.0,0.0,0.149+0.207)','',   'zxy,face=Normal',   'face=Normal', '', '1'),
      ]
    
    c = ChronoMem.start("Create B17G")
    ret = fig.createMechanical(lstParts, optimize=False)
    c.stopRecord("WaveFrontPerf.txt")
    self.assertEqual(ret, C_OK)
    pf.save('tures/b17g-gen.pz3')


  def testMechaCreateF4U1(self):    
    pf = PoserFile('srcdata/Empty.pz3')
    fig = pf.createFigure()
    self.assertEqual(fig.getBodyIndex(), 1)
    
    # Load the Source Wavegeom
    wg = readGeom('srcdata/f4u-exp.obj')
    
    #FigurePart'partType, lev,       name,    printName,ge,                 geomGroup,        oplst,            trans,             rot,            orient,         center, hidden, addToMenu
    lstParts = [
      FigurePart('fig',  0,             '',     'F4U', 'tures/f4u1.obj',          '',           '',               '',                 '',                '',                  '', '', ''),
      FigurePart('act',  0,         'BODY',     'BODY', wg,             None,                   (),               '',                 '',                '',                  '', '', '1'),
      FigurePart('act',  1,     'Fuselage', 'Fuselage', wg,        wg.getGroup('WingsC'), ('add',),               '',                 '',             'zxy',   '', '', '1'),
      FigurePart('act',  2,     'GearRear',         '', wg,      wg.getGroup('GearRear'), ('add',),               '',                 '', 'xyz,face=Normal', 'face=Normal', '', ''),
      FigurePart('act',  2,     'lGearLeg',         '', wg,      wg.getGroup('lGearLeg'), ('add',),               '',                 '', 'yzx,face=Normal', 'face=Normal', '', ''),
      FigurePart('act',  2,'lGearActuator',         '', wg, wg.getGroup('lGearActuator'), ('add',),               '',                 '', 'yzx,face=Normal', 'face=Normal', '', ''),
      FigurePart('act',  2,   'lUpDragLnk',   'Helice', wg,    wg.getGroup('lUpDragLnk'), ('add',),               '',                 '', 'xyz',                  '(1.67836, 1.548692, 1.229745)', '', '1'),
      FigurePart('act',  3,  'lDwnDragLnk',   'Helice', wg,   wg.getGroup('lDwnDragLnk'), ('add',),               '',                 '', '',                  '', '', '1'),

      ]
    
    c = ChronoMem.start("Create F4U")
    ret = fig.createMechanical(lstParts, optimize=False)
    c.stopRecord("WaveFrontPerf.txt")
    self.assertEqual(ret, C_OK)
    pf.save('tures/f4u1-gen.pz3')



  def testMechaCreateP51D(self):    
    pf = PoserFile('srcdata/Empty.pz3')
    fig = pf.createFigure()
    self.assertEqual(fig.getBodyIndex(), 1)
    
    # Load the Source Wavegeom
    wg = readGeom('srcdata/p51d-exp.obj')
    
    wg.unTriangularize(maxsin=0.02)
    wgBomb = WaveGeom()
    wgBomb.addGroup(wg.getGroup('lBomb'))
    wgBomb.save('tures/lBomb.obj')
    wgTank = WaveGeom()
    wgTank.addGroup(wg.getGroup('lTank'))
    wgTank.save('tures/lTank.obj')
    
    wg.removeGroup('lBomb')
    wg.removeGroup('lTank')
    
    # Load a file for the materials
    pm = PoserFile('srcdata/PoserRoot/Runtime/Librairies/Props/neilwil_P-51D/Canopy.pp2')
    pw = WFMat.readMtl('srcdata/p51d-work.mtl')
    
    pm2 = PoserFile('srcdata/Tempest-basic.cr2')
    tempest = pm2.getLstFigure()[0]
    
    #FigurePart'partType, lev,       name,    printName,ge,                 geomGroup,        oplst,            trans,             rot,            orient,         center, hidden, addToMenu
    lstParts = [
      FigurePart( 'fig',  0,          '',       'P51D', 'tures/p51d.obj',          '',           '',               '',                 '',                '',                  '', '', ''),
      FigurePart( 'act',  0,      'BODY',       'BODY', wg,        None,                   ('add',),               '',                 '',                '',                  '', '', '1'),
      FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   wg.getGroup('Fuselage'),           '',               '',                 '',             'zxy',   'face=Normal', '', '1'),
      FigurePart('geom',  1,          '',           '', wg,      wg.getGroup('Wings'), ('combine',),               '',                 '',                '', '', '', ''),
      FigurePart( 'geo',  1,          '',           '', wg,     wg.getGroup('Cooler'), ('combine',),               '',                 '',                '', '', '', ''),
      FigurePart( 'act',  2, 'Properler',     'Helice', wg,  wg.getGroup('Properler'),           '',               '',                 '', 'zxy,face=Normal',                  '', '', '1'),
      FigurePart('geom',  1,          '',           '', wg,    wg.getGroup('Spinner'), ('combine',),               '',                 '',                '', '', '', ''),
      FigurePart( 'act',  2,    'Canopy',     'Canopy', wg,     wg.getGroup('Canopy'),           '',               '',                 '',                '',                  '', '', '1'),
      FigurePart( 'act',  2,'Gouvernail',     'Rudder', wg, wg.getGroup('Gouvernail'),           '',               '',                 '', 'yzx,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  2,  'Elevator',   'Elevator', wg,   wg.getGroup('Elevator'),           '',               '',                 '', 'xyz,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  2,     'lFlap',  'Letf Flap', wg,      wg.getGroup('lFlap'),           '',               '',                 '', 'xyz,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  2,     'rFlap', 'Right Flap', wg,      wg.getGroup('rFlap'),           '',               '',                 '', 'xyz,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  2,    'lVolet',     'lVolet', wg,     wg.getGroup('lVolet'),           '',               '',                 '', 'xyz,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  2,    'rVolet',     'rVolet', wg,     wg.getGroup('rVolet'),           '',               '',                 '', 'xyz,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  2,     'lRack',  'Left Rack', wg,      wg.getGroup('lRack'),           '',               '',                 '', '',              '', '', '1'),
      FigurePart( 'act',  3,     'lBomb',  'Left Bomb', wgBomb, wgBomb.getGroup('lBomb'),        '',               '',                 '', '',              '', '', '1'),
      FigurePart( 'act',  3,     'lTank',  'Left Tank', wgTank, wgTank.getGroup('lTank'),        '',               '',                 '', '',              '', '', '1'),


      #Inconsistent level
      FigurePart( 'act',  5,     'rRack', 'Right Rack', wg,      wg.getGroup('lRack'),           '', 'symyz:Fuselage',                 '', '',              '', '', '1'),
      
      FigurePart( 'act',  2,     'rRack', 'Right Rack', wg,      wg.getGroup('lRack'),           '', 'symyz:Fuselage',                 '', '',              '', '', '1'),
      
      # No need for any 'symetry' because in the  original Geom the Bomb is correctly positioned with regard to its parent.
      FigurePart( 'act',  3,     'rBomb', 'Right Bomb', wgBomb, wgBomb.getGroup('lBomb'),        '',               '',                 '', '',              '', '', '1'),
      FigurePart( 'act',  3,     'rTank', 'Right Tank', wgTank, wgTank.getGroup('lTank'),        '',               '',                 '', '',              '', '', '1'),

      FigurePart( 'act',  2,  'lGearLeg',   'TrainAVG', wg,   wg.getGroup('lGearLeg'),           '',               '',                 '', 'yzx,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  3,    'lWheel',    'RoueAVG', wg,     wg.getGroup('lWheel'),           '',               '',                 '', 'xyz,face=Black',   'face=Black', '', '1'),
      FigurePart( 'act',  3,    'lfTrap',     'lfTrap', wg,     wg.getGroup('lfTrap'),           '',               '',                 '', '', 'face=Normal', '', '1'),
      FigurePart( 'act',  2,    'liTrap',     'liTrap', wg,     wg.getGroup('liTrap'),           '',               '',                 '', '', 'face=Normal', '', '1'),
      
      FigurePart( 'act',  2,  'rGearLeg',   'TrainAVD', wg,   wg.getGroup('rGearLeg'),           '',               '',                 '', 'yzx,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  3,    'rWheel',    'RoueAVD', wg,     wg.getGroup('lWheel'),           '', 'Symyz:Fuselage',  '(0.0,180.0,0.0)', 'xyz,face=Black',   'face=Black', '', '1'),
      FigurePart( 'act',  3,    'rfTrap',     'rfTrap', wg,     wg.getGroup('rfTrap'),           '',               '',                 '', '', 'face=Normal', '', '1'),
      FigurePart( 'act',  2,    'riTrap',     'riTrap', wg,     wg.getGroup('riTrap'),           '',               '',                 '', '', 'face=Normal', '', '1'),
      
      FigurePart( 'act',  2,  'RearGear',   'TrainArr', wg,   wg.getGroup('RearGear'),           '',               '',                 '', 'yzx,face=Normal', 'face=Normal', '', '1'),
      FigurePart( 'act',  2, 'lRearTrap',  'lRearTrap', wg,  wg.getGroup('lRearTrap'),           '',               '',                 '', '', 'face=Normal', '', '1'),
      FigurePart( 'act',  2, 'rRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', '', 'face=Normal', '', '1'),
      FigurePart( 'mat',  0,     'Glass',           '', pm,  pm.findMeshedObject('Canopy'),      '',               '',                 '', '',            '', '', '1'),      
      FigurePart( 'mat',  0,         '*',           '', pm,  pm.findMeshedObject('Canopy'),      '',               '',                 '', '',            '', '', '1'),      
      FigurePart( 'mat',  0,         '*',           '', pw,             None,      '',               '',                 '', '',            '', '', '1')      ,
      FigurePart( 'mat',  0,         '*',           '', None, tempest,      '',               '',                 '', '',            '', '', '1')      ,

      # Dictionnary to select and overload some material
      FigurePart( 'mat',  0, '{ sFSdd }',           '', pm,  pm.findMeshedObject('Canopy'),      '',               '',                 '', '',            '', '', '1'),      
      FigurePart( 'mat',  0, '{ "MatSource":"MatDest", }', '', pm,  pm.findMeshedObject('Canopy'),      '',               '',                 '', '',            '', '', '1'),      
      FigurePart( 'mat',  0, '{ "Canopy_auv":"Canopy", }', '', pm,  pm.findMeshedObject('Canopy'),      '',               '',                 '', '',            '', '', '1'),      
      
      # Command Error
      FigurePart( 'err',  0,         '*',           '', pw,             None,      '',               '',                 '', '',            '', '', '1')      ,
      ]
    
    ret = fig.createMechanical(lstParts, optimize=False)
    self.assertEqual(ret, C_FAIL)
    pf.save('tures/p51d.pz3')

    ret = fig.hasMultipleGeom()
    self.assertEqual(ret, 0)


  def testMechaCreateP51DFrom0(self):
    ''' Start with an empty geom '''    
    pf = PoserFile('srcdata/Empty.pz3')
    fig = pf.createFigure()
    self.assertEqual(fig.getBodyIndex(), 1)
    
    # Load the Source Wavegeom
    wg = readGeom('srcdata/p51d-exp.obj')
 
    #FigurePart'partType, lev,       name,    printName,ge,                 geomGroup,        oplst,            trans,             rot,            orient,         center, hidden, addToMenu
    lstParts = [
      FigurePart( 'fig',  0,          '',       'P51D', 'tures/p51d.obj',          '',           '',               '',                 '',                '',                  '', '', ''),
      FigurePart( 'act',  0,      'BODY',       'BODY', None,       None,                         '',               '',                 '',                '',                  '', '', '1'),
      FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   wg.getGroup('Fuselage'),     ('add',),               '',                 '',             'zxy',   'face=Normal', '', '1'),
      FigurePart('geom',  1,          '',           '', wg,      wg.getGroup('Wings'), ('combine',),               '',                 '',                '', '', '', ''),
      FigurePart( 'geo',  1,          '',           '', wg,     wg.getGroup('Cooler'), ('combine',),               '',                 '',                '', '', '', ''),
      FigurePart( 'act',  2, 'Properler',     'Helice', wg,  wg.getGroup('Properler'),     ('add',),               '',                 '', 'zxy,face=Normal',                  '', '', '1'),
      FigurePart( 'act',  2, 'lRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', 'face=Normal', '', '', '1'),
      FigurePart( 'act',  2, 'rRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', '(1.0,0.0,  2.0)', '', '', '1'),
      FigurePart( 'act',  2, 'zRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', 'xyz,(1.0,0.0,  2.0)', '', '', '1'),
      FigurePart( 'act',  2, 'eRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', 'daube,(1.0,0.0,  2.0)', '', '', '1'),
      ]
    ret = fig.createMechanical(lstParts, optimize=True)
    self.assertEqual(ret, C_FAIL)
    pf.save('tures/p51d-from0.pz3')

    ret = fig.hasMultipleGeom()
    self.assertEqual(ret, 0)

  def testMechaCreateCaudron460(self):    
    pf = PoserFile('srcdata/Empty.pz3')
    fig = pf.createFigure()
    self.assertEqual(fig.getBodyIndex(), 1)
    
    # Load the Source Wavegeom
    wgF1 = readGeom('srcdata/Caudron460-Exp.obj')
    grpFuselage = wgF1.getGroup('Fuselage')
    grpWings = wgF1.getGroup('Wings')
    grpHelice = wgF1.getGroup('Properler')
    grplLowLeg = wgF1.getGroup('lLowLeg')
    
    #FigurePart'partType, lev,       name,    printName,                geom,   geomGroup,     oplst, trans, rot,            orient,              center, hidden, addToMenu
    lstParts = [
      FigurePart( 'fig',  0,          '', 'Caudron460', 'tures/caudron.obj',          '',           '',    '',  '',                '',                  '', '', ''),
      FigurePart( 'act',  0,      'BODY',       'BODY',                wgF1,        None,     ('add',),    '',  '',                '',                  '', '', '1'),
      FigurePart( 'act',  1,  'Fuselage',   'Fuselage',                wgF1, grpFuselage,           '',    '',  '',             'xyz', 'face=Material.001', '', '1'),
      FigurePart('geom',  1,          '',           '',                wgF1,    grpWings, ('combine',),    '',  '',                '', '', '', ''),
      FigurePart( 'act',  2, 'Properler',     'Helice',                wgF1,   grpHelice,           '',    '',  '', 'xyz,face=Normal',                  '', '', '1'),
      FigurePart( 'act',  2,   'lLowLeg','TrainAVGBas',                wgF1,   grplLowLeg,          '',    '',  '', 'yzx,face=Normal',       'face=Normal', '', '1'),
      FigurePart( 'act',  2,   'rLowLeg','TrainAVDBas',                wgF1,   grplLowLeg,          '', 'Symxy:Fuselage',  '(0.0,180.0,0.0)', 'yzx,face=Normal',       'face=Normal', '', '1'),
      ]
    
    ret = fig.createMechanical(lstParts, optimize=True)
    self.assertEqual(ret, C_OK)
    pf.save('tures/caudron1.pz3')

  def testMechaCreateP403(self):    
    ''' Test with an empty geom '''
    pf = PoserFile('srcdata/Empty.pz3')
    fig = pf.createFigure()
    self.assertEqual(fig.getBodyIndex(), 1)
    
    # Load the Source Wavegeom
    wgF1 = readGeom('srcdata/LL-403.obj')
    
    #FigurePart'partType, lev,       name,    printName,                geom,   geomGroup,     oplst, trans, rot,            orient,              center, hidden, addToMenu
    lstParts = [
      FigurePart( 'fig',  0, '', 'Peugeot 403', 'tures/TUp403.obj',          '',           '',    '',  '',                '',                  '', '', ''),
      FigurePart( 'act',  0, 'BODY',    'BODY',   None,        None,     '',    '',  '',                '',                  '', '', '1'),
      FigurePart( 'act',  1, 'Chassis', 'Chassis',        wgF1, wgF1.getGroup('Chassis'), ('add', ),    '',  '',                 '', '', '', '1'),
      FigurePart('geom',  1,        '',           '',     wgF1, wgF1.getGroup('Pedales'), ('combine',), '',  '',                 '', '', '', ''),
      FigurePart( 'act',  2, 'Volant',  'Steering Wheel', wgF1, wgF1.getGroup('Volant'),  ('add',),     '',  '', 'yzx,face=Normale', 'face=Normale', '', '1'),
      ]
    
    ret = fig.createMechanical(lstParts, optimize=True)
    self.assertEqual(ret, C_OK)
    pf.save('tures/TUp403.pz3')


  def testFigurePart(self):
    ''' Test Various Syntax cases in FigurePart Def '''    
    pf = PoserFile('srcdata/Empty.pz3')
    fig = pf.createFigure()
    self.assertEqual(fig.getBodyIndex(), 1)
    
    # Load the Source Wavegeom
    wg = readGeom('srcdata/p51d-exp.obj')
 
    grpFuselage = wg.getGroup('Fuselage')

    #FigurePart'partType, lev,   ,     name,    printName,                geom,   geomGroup,     oplst, 
    #               trans,              rot,       orient,  center, hidden, addToMenu
    fp = FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   grpFuselage,     ('add',),\
                     '',                 '',           '',   '', '', '1')
    bc = fp.getBaryCentre()
    ao, vOrient = fp.getOrientation()
    vri = fp.getRotation()
    tr = fp.getTranslation(fig, bc)
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=xyz vOrient:V(0,0,0) Center:P(-0.00120433,0.0809057,0.106836) Rot:V(0,0,0) Trans:P(0,0,0)')

    fp = FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   grpFuselage,     ('add',),               \
                     '',                 '',        'zxy',   'face=Normal', '', '1')
    bc = fp.getBaryCentre()
    ao, vOrient = fp.getOrientation()
    vri = fp.getRotation()
    tr = fp.getTranslation(fig, bc)
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=zxy vOrient:V(0,0,0) Center:P(9.34e-05,0.0702938,0.29371) Rot:V(0,0,0) Trans:P(0,0,0)')

    fp = FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   grpFuselage,     ('add',),               \
                     '(0.0,0.0,0.0)',    '(0.0,0.0,0.0)',        'zxy,(45.0, 50.0, 0.0)',   '(1.0, -1.0, 0.0)', '', '1')
    bc = fp.getBaryCentre()
    ao, vOrient = fp.getOrientation()
    vri = fp.getRotation()
    tr = fp.getTranslation(fig, bc)
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=zxy vOrient:V(45,50,0) Center:P(1,-1,0) Rot:V(0,0,0) Trans:P(0,0,0)')

    fp = FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   grpFuselage,     ('add',),               \
                     '',                 '',        'zxy,face=Normal',   '', '', '1')
    bc = fp.getBaryCentre()
    ao, vOrient = fp.getOrientation()
    vri = fp.getRotation()
    tr = fp.getTranslation(fig, bc)
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=zxy vOrient:V(-4.9894e-12,0,0) Center:P(-0.00120433,0.0809057,0.106836) Rot:V(0,0,0) Trans:P(0,0,0)')
    
    fp = FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   grpFuselage,     ('add',),               \
                     'moveto:(1.0, 1.0, 1.0)',      '',        'zxy,face=Normal',   '', '', '1')
    bc = fp.getBaryCentre()
    ao, vOrient = fp.getOrientation()
    vri = fp.getRotation()
    tr = fp.getTranslation(fig, bc)
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=zxy vOrient:V(-4.9894e-12,0,0) Center:P(-0.00120433,0.0809057,0.106836) Rot:V(0,0,0) Trans:P(1.0012,0.919094,0.893164)')
    
    # Input Degraded Cases
    #FigurePart'partType, lev,   ,     name,    printName,                geom,   geomGroup,     oplst, 
    #               trans,              rot,       orient,  center, hidden, addToMenu
    fp = FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   grpFuselage,     ('add',),\
                     '(',                 '(',           '(',   ')', '', '1')
    
    with self.assertRaises(UsageError):
      bc = fp.getBaryCentre()
    
    with self.assertRaises(UsageError):    
      ao, vOrient = fp.getOrientation()
      
    with self.assertRaises(UsageError):
      vri = fp.getRotation()
    
    with self.assertRaises(UsageError):
      tr = fp.getTranslation(fig, bc)
    
    #FigurePart'partType, lev,   ,     name,    printName,                geom,   geomGroup,     oplst, 
    #               trans,              rot,       orient,  center, hidden, addToMenu
    fp = FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   grpFuselage,     ('add',),\
                     '(a,)',         '(1.0, 5, qa)',    '(math.acos(5.0), 0, 0)',   '(1/,1,1)', '', '1')
    
    with self.assertRaises(UsageError):
      bc = fp.getBaryCentre()
    
    with self.assertRaises(UsageError):    
      ao, vOrient = fp.getOrientation()
      
    with self.assertRaises(UsageError):
      vri = fp.getRotation()
    
    with self.assertRaises(UsageError):
      tr = fp.getTranslation(fig, bc)
    
    fp = FigurePart( 'act',  1,  'Fuselage',   'Fuselage', wg,   grpFuselage,     ('add',),\
                     '(a,)',         '(1.0, 5, qa)',    '456',   '(1/,1,1)', '', '1')
    
    with self.assertRaises(UsageError):    
      ao, vOrient = fp.getOrientation()

    grpProp = wg.getGroup('Properler')

    fp = FigurePart( 'act',  1,  'Properler',   'Properler', wg,   grpProp,     ('add',),\
                     'moveto:symxy',         '(1.0, 5, qa)',    '456',   '(1/,1,1)', '', '1')

    with self.assertRaises(UsageError):
      tr = fp.getTranslation(fig, bc)

    fp = FigurePart( 'act',  1,  'Properler',   'Properler', wg,   grpProp,     ('add',),\
                     'symxy:moveto',         '(1.0, 5, qa)',    '456',   '(1/,1,1)', '', '1')

    with self.assertRaises(UsageError):
      tr = fp.getTranslation(fig, bc)


    fp = FigurePart( 'act',  1,  'Properler',   'Properler', wg,   grpProp,     ('add',),\
                     'NotAnActorAlone',         '(1.0, 5, qa)',    '456',   '(1/,1,1)', '', '1')

    with self.assertRaises(UsageError):
      tr = fp.getTranslation(fig, bc)

    fp = FigurePart( 'act',  1,  'Properler',   'Properler', wg,   grpProp,     ('add',),\
                     'face=toto',         '(1.0, 5, qa)',    '456',   '(1/,1,1)', '', '1')

    with self.assertRaises(UsageError):
      tr = fp.getTranslation(fig, bc)

    fp = FigurePart( 'act',  1,  'Properler',   'Properler', wg,   grpProp,     ('add',),\
                     'moveto:(synttac, 0)',         '(1.0, 5, qa)',    '456',   '(1/,1,1)', '', '1')

    with self.assertRaises(UsageError):
      tr = fp.getTranslation(fig, bc)
      

    fp = FigurePart( 'act',  1,  'Properler',   'Properler', wg,   grpProp,     ('add',),\
                     'moveto:NotAnActor',         '(1.0, 5, qa)',    '456',   '(1/,1,1)', '', '1')
    with self.assertRaises(UsageError):
      tr = fp.getTranslation(fig, bc)

    # Load the Source Wavegeom
    wg2 = readGeom('srcdata/b17-exp.obj')
    #FigurePart'partType, lev,       name,    printName,ge,                 geomGroup,        oplst,            trans,             rot,            orient,         center, hidden, addToMenu
    lstParts = [
      FigurePart('fig',  0,             '',    'B17G',  'tures/b17g.obj',          '',           '',                '',                 '', '',                  '', '', ''),
      FigurePart('act',  0,         'BODY',    'BODY',  wg2,                    None,            (),               '',               '', '',                  '', '', '1'),
      FigurePart('act',  1,     'Fuselage','Fuselage',  wg2,wg2.getGroup('Fuselage'),      ('add',),               '',               '', '',   '', '', '1'),
      FigurePart('act',  2,     'Engine1',  'Engine1',  wg2,   wg2.getGroup('R1820'),      ('add',), '(2.39856, 0.888098, 3.144764)',    '', '',                  '', '', '1'),
      FigurePart('act',  3,  'Properler1','Properler',  wg2, wg2.getGroup('Spinner'),        ('add',),    'moveto:face=Normal:(0.0,0.0,0.356)', '', 'zxy,face=Normal', 'face=Normal',  '', '1'),
      FigurePart('act',  2,     'Engine2',  'Engine2',  None,                'R1820',    ('reuse',),    '(1.130354, 0.783801, 3.328127)', '', '',  '', '', '1'),
      FigurePart('act',  3,  'Properler2','Properler',  None,              'Spinner',    ('reuse',),    'moveto:Engine2:face=Normal:(0.0,0.0,0.149+0.207)','',   'zxy,face=Normal',   'face=Normal', '', '1'),
      FigurePart('act',  3,  'Properler2','Properler',  None,              'Spinner',    ('reuse',),    'moveto:Engine2:face=Normal:(0.0,0.0,0.14/)','',   'zxy,face=Normal',   'face=Normal', '', '1'),
      FigurePart('act',  3,  'Properler3','Properler',  None,              'Spinner',    ('reuse',),    'moveto:face=BADNormal:(0.0,0.0,0.149+0.207)','',   'zxy,face=Normal',   'face=Normal', '', '1'),
      FigurePart('act',  3,  'Properler3','Properler',  None,              'Spinner',    ('reuse',),    'symxy:face=Normal:(0.0,0.0,0.149)','',   'zxy,face=Normal',   'face=Normal', '', '1'),
      FigurePart('act',  3,  'Properler2','Properler',  None,              'Spinner',    ('reuse',),    'Engine2:face=Normal:(0.0,0.0,0.1)','',   'zxy,face=Normal',   'face=Normal', '', '1'),
      ]
    
    c = ChronoMem.start("Create B17G with errors")
    ret = fig.createMechanical(lstParts, optimize=False)
    self.assertEqual(ret, C_FAIL)

    
    
      # FigurePart('geom',  1,          '',           '', wg,      wg.getGroup('Wings'), ('combine',),               '',                 '',                '', '', '', ''),
      # FigurePart( 'act',  2, 'Properler',     'Helice', wg,  wg.getGroup('Properler'),     ('add',),               '',                 '', 'zxy,face=Normal',                  '', '', '1'),
      # FigurePart( 'act',  2, 'lRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', 'face=Normal', '', '', '1'),
      # FigurePart( 'act',  2, 'rRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', '(1.0,0.0,  2.0)', '', '', '1'),
      # FigurePart( 'act',  2, 'zRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', 'xyz,(1.0,0.0,  2.0)', '', '', '1'),
      # FigurePart( 'act',  2, 'eRearTrap',  'rRearTrap', wg,  wg.getGroup('rRearTrap'),           '',               '',                 '', 'daube,(1.0,0.0,  2.0)', '', '', '1'),
    
    grpCooler = wg.getGroup('Cooler')
    fp = FigurePart( 'geo',  1,          '',           '', wg,     grpCooler, ('combine',),\
                     '',                 '',                '', '', '', '')
    bc = fp.getBaryCentre(grpCooler)
    ao, vOrient = fp.getOrientation(grpCooler)
    vri = fp.getRotation(grpCooler)
    tr = fp.getTranslation(fig, bc, grpCooler)
    print(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}")
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=xyz vOrient:V(0,0,0) Center:P(9.34688e-05,0.0162765,-0.0150443) Rot:V(0,0,0) Trans:P(0,0,0)')

    fp = FigurePart( 'geo',  1,          '',           '', wg,     grpCooler, ('combine',),\
                     'symxy',                 '',                '', '', '', '')
    bc = fp.getBaryCentre(grpCooler)
    ao, vOrient = fp.getOrientation(grpCooler)
    vri = fp.getRotation(grpCooler)
    tr = fp.getTranslation(fig, bc, grpCooler)
    print(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}")
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=xyz vOrient:V(0,0,0) Center:P(9.34688e-05,0.0162765,-0.0150443) Rot:V(0,0,0) Trans:P(0,0,0.0300885)')

    fp = FigurePart( 'geo',  1,          '',           '', wg,     grpCooler, ('combine',),\
                     'symyz',                 '',                '', '', '', '')
    bc = fp.getBaryCentre(grpCooler)
    ao, vOrient = fp.getOrientation(grpCooler)
    vri = fp.getRotation(grpCooler)
    tr = fp.getTranslation(fig, bc, grpCooler)
    print(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}")
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=xyz vOrient:V(0,0,0) Center:P(9.34688e-05,0.0162765,-0.0150443) Rot:V(0,0,0) Trans:P(-0.000186938,0,0)')


    fp = FigurePart( 'geo',  1,          '',           '', wg,     grpCooler, ('combine',),\
                     'symzx',                 '',                '', '', '', '')
    bc = fp.getBaryCentre(grpCooler)
    ao, vOrient = fp.getOrientation(grpCooler)
    vri = fp.getRotation(grpCooler)
    tr = fp.getTranslation(fig, bc, grpCooler)
    print(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}")
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc} Rot:{vri} Trans:{tr}", \
                     'Axes=xyz vOrient:V(0,0,0) Center:P(9.34688e-05,0.0162765,-0.0150443) Rot:V(0,0,0) Trans:P(0,-0.032553,0)')


    fp = FigurePart( 'geo',  1,          '',           '', wg,     grpCooler, ('combine',),\
                     'daue??',                 '',                '', '', '', '')
    bc = fp.getBaryCentre(grpCooler)
    ao, vOrient = fp.getOrientation(grpCooler)
    vri = fp.getRotation(grpCooler)
    with self.assertRaises(UsageError):    
      tr = fp.getTranslation(fig, bc, grpCooler)

  
  def testFigurePartNormale(self):
    ''' Test Various cases in FigurePart Def on Normal computations '''    
    pf = PoserFile('srcdata/Empty.pz3')
    fig = pf.createFigure()
    self.assertEqual(fig.getBodyIndex(), 1)
    
    # Load the Source Wavegeom
    wg = readGeom('srcdata/b17-tu-normal.obj')
 
    #FigurePart'partType, lev,   ,     name,    printName,                geom,   geomGroup,     oplst, 
    #               trans,              rot,       orient,  center, hidden, addToMenu
    lGearLeg = wg.getGroup('lGearLeg')
    fp = FigurePart( 'act',  1,  'lGearLeg',   'lGearLeg', wg,   lGearLeg,     ('add',),\
                     '',                 '',   'yzx,face=Normal',   'face=Normal', '', '1')
    ao, vOrient = fp.getOrientation()
    self.assertEqual(ao, 'yzx')
    self.assertAlmostEqual(vOrient.x,-18.52, delta=1e-5)
    self.assertAlmostEqual(vOrient.y,   0.0, delta=1e-5)
    self.assertAlmostEqual(vOrient.z,   0.0, delta=1e-5)
  
    lLowLeg = wg.getGroup('lLowLeg')
    fp = FigurePart( 'act',  1,  'lLowLeg',   'lLowLeg', wg,   lLowLeg,     ('add',),\
                     '',                 '',   'yzx,face=Normal',   'face=Normal', '', '1')
    bc = fp.getBaryCentre()
    ao, vOrient = fp.getOrientation()
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc}", \
                     'Axes=yzx vOrient:V(-18.52,0,-7.9043e-07) Center:P(1.03507,0.490887,2.56077)')

    lGearDrag = wg.getGroup('lGearDrag')
    fp = FigurePart( 'act',  1,  'lGearDrag',   'lGearDrag', wg,   lGearDrag,     ('add',),\
                     '',                 '',   'zxy,face=Normal',   'face=Normal', '', '1')
    bc = fp.getBaryCentre()
    ao, vOrient = fp.getOrientation()
    self.assertEqual(f"Axes={ao} vOrient:{vOrient} Center:{bc}", \
                     'Axes=zxy vOrient:V(-18.52,8.53774e-07,0) Center:P(1.03507,0.528505,3.23315)')

    lBombTrap = wg.getGroup('lBombTrap')
    fp = FigurePart( 'act',  1,  'lBombTrap',   'lBombTrap', wg,   lBombTrap,     ('add',),\
                     '',                 '',   'xyz,face=Normal',   'face=Normal', '', '1')
    ao, vOrient = fp.getOrientation()
    self.assertEqual(ao, 'xyz')
    self.assertAlmostEqual(vOrient.x,    0.0, delta=1e-6)
    self.assertAlmostEqual(vOrient.y, -0.144994,delta=1e-6)
    self.assertAlmostEqual(vOrient.z, 0.0, delta=1e-5)



    rBombTrap = wg.getGroup('rBombTrap')
    fp = FigurePart( 'act',  1,  'rBombTrap',   'rBombTrap', wg,   rBombTrap,     ('add',),\
                     '',                 '',   'xyz,face=Normal',   'face=Normal', '', '1')
    ao, vOrient = fp.getOrientation()
    self.assertEqual(ao, 'xyz')
    self.assertAlmostEqual(vOrient.x,      0.0, delta=1e-6)
    self.assertAlmostEqual(vOrient.y, -0.1449916, delta=1e-6)
    self.assertAlmostEqual(vOrient.z,   180.0, delta=1e-6)

    fp = FigurePart( 'act',  1,  'rBombTrap',   'rBombTrap', wg,   rBombTrap,     ('reuse',),\
                     '',                 '',   'yzx,face=Normal',   'face=Normal', '', '1')
    ao, vOrient = fp.getOrientation()
    self.assertEqual(ao, 'yzx')
    self.assertAlmostEqual(vOrient.x, 90.0, delta=1e-6)
    self.assertAlmostEqual(vOrient.y,      0.0, delta=1e-6)
    self.assertAlmostEqual(vOrient.z, 89.855008, delta=1e-5)
  

    fp = FigurePart( 'act',  1,  'rBombTrap',   'rBombTrap', wg,   rBombTrap,     ('reuse',),\
                     '',                 '',   'zxy,face=Normal',   'face=Normal', '', '1')
    ao, vOrient = fp.getOrientation()
    self.assertEqual(ao, 'zxy')
    self.assertAlmostEqual(vOrient.x,  0.0, delta=1e-3)
    self.assertAlmostEqual(vOrient.y, -89.855,delta=1e-5)
    self.assertAlmostEqual(vOrient.z, 0.0, delta=1e-5)

    fp = FigurePart( 'act',  1,  'rBombTrap',   'rBombTrap', wg,   rBombTrap,     ('reuse',),\
                     '',                 '',   'zxy,face=NOTAMATERIAL',   'face=Normal', '', '1')
    with self.assertRaises(UsageError):    
      ao, vOrient = fp.getOrientation()
  
  #
  # Test with Sasha Character (for weightMap in Poser 9)
  # From http://sasha-16.forumprofi.de/
  def testLoadSasha16(self):
    POSERROOT = '/home/olivier/vol32G/Poser7'

    c = ChronoMem.start("PoserFile.read-Sasha16.pz3")
    sc1 = PoserFile('/home/olivier/vol32G/VIE/Sasha16-Base.pz3', True)  
    lf = sc1.getLstFigure()
    f = lf[0]
  
    pa = f.findActor("lThigh:1")
    self.assertTrue(pa!=None, 'ok')
    c.stopPrint()
  
    lstch = ['PHMFaceSquare', 'PBMBreastsDiameter', 'PBMTorsoThickness', 'PHMTeethCanineSharpTop', \
    'PBMNavelGone', 'PBMGluteCreaseL', 'PBMFeetArch', 'PBMThighsThickness', 'PHMLacrimalSizeR', \
    'PHMLipsMaria', 'PHMLipTopDepth', 'PHMEarUp-DownR', 'PHMLipTopCenterHeight', 'PHMLipTopCurves',\
     'FBMDefinition', 'PBMInhale', 'PHMBrowDepth', 'PBMToesSmallUp-DownR', 'PHMLipBottomMidDefine',\
     'PBMBreastInR', 'PBMLineaAlba', 'PHMEarsShapeHelix', 'PHMNoseWidth', 'PBMBreastOutL',\
     'PHMEyesIrisAlign', 'PHMEyeWrinkleL', 'PHMLipBottomEdgeHeight', 'PBMBreastsCleavage',\
     'PBMThighsTone', 'PBMToeBigCurlR', 'PHMEyesHeightInner', 'PHMLipTopEdgeHeight',\
     'PHMLashesBottomCurl', 'PHMCheekDimpleCreaseL', 'PBMShinsThickness', 'PBMArmSize',\
     'PHMLipTopEdgeCurve', 'PBMBreastDownR', 'PBMBreastsFlatten', 'PHMNoseTipHeight', 'PHMLipsMonique',\
     'PBMBreastsPerk', 'PHMBecky', 'FBMEmaciated', 'PHMBrowDefine', 'PHMBrowSmooth', 'PHMNoseDepth',\
     'PHMFaceLong', 'PBMToesPointed', 'FBMThin', 'PHMEyeLidsBottomOutHeight', 'PHMNoseTwist', 'PHMLipBottomThickness', 'PHMPhiltrumDepth', 'PHMEarlobesSize', 'PHMEyeWrinkleR', 'PHMHeadYoung', 'FBMAmazon',\
     'PHMNoseBridgeWidth', 'PBMBreastsImplant', 'FHMPaul', 'PBMBellyThin', 'PHMEyeLidsTopOutHeight',\
     'PBMNipplesDepth', 'PHMEyeDepthL', 'PHMEyesAlmondInner', 'PHMChinCrease', 'PHMEyesIrisSize', 'PHMHeadMaria', 'PBMGluteRaiseL', 'PHMHeadHairShort', 'PHMEarsShape', 'PHMNosePinch', 'PHMNoseRound', 'PHMEarsFront-Back', 'PHMEyesPuffyBottom', 'PHMEyeBaggyR', 'PHMEyeDepthR', 'PBMSternumWidth', 'PBMShouldersThickness', 'FBMHeavy', 'PHMEyesSlant', 'PBMBreastOutR', 'PHMLacrimalsSimple', 'FHMGeorge', 'PHMNoseBridgeHeight',\
     'PBMNavelHorizontal', 'PHMLipTopPeak', 'PHMEyeLidsBottomSmooth', 'PHMPhiltrumCurve', 'PHMLacrimalsPinch', 'PHMNoseBridgeDepth', 'PHMMouthWidth', 'PHMNoseSlope', 'PHMHeadSerena', 'PBMPregnant', 'PHMNoseSize', 'PHMNostrilsCreaseDepth', 'FBMPearFigure', 'PBMToeBigCurlL', 'PHMEyesAlmondOuter', 'PHMNoseSeptumHeight',\
     'PHMLipTopThickness', 'PHMEyeLidsBottomDefine', 'PHMCheeksHigh', 'PHMEarUp-DownL', 'PHMNoseBridgeThickness', 'PHMCheekDimpleR', 'PHMPhiltrumStrength', 'PHMForeheadDefine', 'PBMToeBigUp-DownL',\
     'PHMLipsBrigette', 'PHMEyesFoldDown', 'PHMLashesIrregular', 'PHMNoseDefine', 'PHMHeadHairBun',\
     'PHMFaceHeart', 'PBMLoveHandleR', 'PHMEyeBaggyL', 'PHMLashesTopPoint', 'PHMCheeksDefine',\
     'PBMBreastUpL', 'PBMNeckThickness', 'FBMMale', 'PHMNostrilsFleshSize', 'PHMLacrimalSizeL',\
     'PHMCheeksDepth', 'PHMEyesHeightOuter', 'PBMNipples', 'FHMJohn', 'PHMMouthCornerDepth',\
     'PHMNostrilsHoleHeight', 'PHMJawCurve', 'PHMJawHeight', 'PHMChinCleft', 'PHMEyesPuffyTop',\
     'PHMEyeLidsBottomInHeight', 'PBMHipsSpandex', 'PHMEarsSize', 'PHMEyesIrisBulge', 'PHMJawAngle',\
     'PHMHeadKerstin', 'PHMEarlobesAttached', 'PHMEyesPupilDialate', 'PHMMouthHeight', 'PBMBreastsSize',\
     'PBMAbsHeightL', 'PBMBreastUpR', 'PBMToeBigSide-SideR', 'PHMLipTopCrease', 'PBMHipsSize',\
     'PHMEyeLidsHeavyTop', 'PHMBrowNarrow', 'PHMLashesLength', 'PHMLipBottomDepth', 'PHMTeethTopSize',\
     'PBMBellySmooth', 'PBMGenitalCrease', 'PHMCheekDimpleL', 'PHMCheeksDimpleCrease', 'PBMBreastsNatural',\
     'FBMFitness', 'PBMNipplesHeight', 'PHMCraniumSlope', 'PHMEyeHeightR', 'PHMCheekBonesSize', 'PBMNailsLength', 'PBMAreolaOut', 'PBMBreastInL', 'PHMFaceSize', 'PBMNipplesBig', 'PHMJawCornerWidth', 'PHMHeadEva',\
     'PHMChinDepth', 'PHMHeadMonique', 'PHMEyesSize', 'PHMEyesSunken', 'PHMEarsElfLong', 'PHMOlivia',\
     'PHMEyeSlantL', 'PHMEarlobesLength', 'PHMChinSize', 'PBMAreolaPerk', 'FBMYoung', 'PBMToesSmallUp-DownL', 'PHMBrowHeavy', 'PHMCheeksSink', 'PHMJawSize', 'PHMEmma', 'PHMMouthSize', 'PHMTeethWisdomBottomGone',\
     'PHMEyesWrinkle', 'PBMFeetForShoe', 'PHMNostrilsWidth', 'PBMBreastDownL', 'PBMToeBigSide-SideL',\
     'PHMEyeLidsHeavyBottom', 'PBMTummyOut', 'PHMFaceFull', 'PHMEyeFoldsHeight', 'PBMNavelHeight',\
     'PBMAbsHeightR',\
     'PHMEyesPupilSlit', 'PHMEarsUp-Down', 'PHMCheeksDimple', 'PHMLisa', 'PHMTeethBottomSize', 'PHMJawDefine', 'PHMNoseBump', 'FBMVoluptuous', 'PHMLashesTopCurl', 'PHMLipsSerena', 'PHMTemples', 'PHMCheekBonesWidth', 'PBMWaistWidth', 'PHMEyeWidthR', 'PHMEarsIn-Out', 'PHMEarSizeL', 'PHMEyeSlantR', 'PHMNoseHeight',\
     'PBMGluteRaiseR', 'PHMHeadBrigette', 'PHMHeadOld', 'PHMEarIn-OutR', 'FBMBulk', 'PHMBrowsArch', 'PHMLipsKerstin', 'PBMBreastsCleavageWidth', 'PHMEyesHeight', 'PHMEarIn-OutL', 'FBMBodyBuilder', 'PBMNavelDepth',\
     'PHMNoseSeptumWidth', 'PBMLoveHandleL', 'PHMEarSizeR', 'PHMTeethIrregular', 'PBMBreastsDroop',\
     'PHMEyesFoldSmooth', 'PHMCheekDimpleCreaseR', 'PHMLipTopMidDefine', 'PHMChinWidth', 'PHMEyesCorneaBulge', 'PBMGluteCreaseR', 'PBMGlutesDimpleDepth', 'PBMToeBigUp-DownR', 'PHMEyesDepth', 'PHMEyeWidthL',\
     'PHMNoseFleshFull', 'PBMSternumHeight',\
     'PBMHipsCrest', 'PBMStomachDepth', 'PHMFaceRound', 'PHMNoseSide-Side', 'PBMGlutesSize',\
     'PBMBreastsHangForward', 'PHMLipBottomCrease', 'PHMNoseTipDepth', 'PBMBreastsLarge', 'PBMNavelSize', 'PHMTeethTopGap', 'PHMNoseTipUp-Down', 'PHMLipBottomWidth', 'PHMLacrimalsSize', 'PBMForearmsThickness',\
     'PBMNailsGone', 'PBMTrapsSize', 'PBMToesSmallIn', 'PHMNostrilsHoleSize', 'PHMFaceMidDepth',\
     'PHMEyeLidsTopInHeight', 'PHMNoseLargeWidth', 'PBMLatsSize', 'PHMNostrilsHeight', 'PBMAreolaSize',\
     'PHMPhiltrumWidth', 'PHMEyesIrisConvexity', 'PHMLipsCurve', 'PBMBellyThickness', 'PHMSamantha',\
     'PHMLipBottomOutDefine', 'PHMLipTopOutDefine', 'PHMPhiltrumSlant', 'PHMEyesWidth', 'PHMEarsElf',\
     'PHMNoseRidgeWidth', 'PHMFaceBottomDepth', 'PHMEyeHeightL', 'PHMForeheadFlat', 'PHMLipsEva',\
     'PHMTeethWisdomTopGone', 'PHMTeethCanineSharpBottom', 'PHMCheeksCrease', 'PHMFaceFlat',\
     'PBMNavelVertical']
    
    #lstch = ['PBMArmSize', ]

    # Read figure's main geometry
    realfn = os.path.join(POSERROOT, 'Runtime/Geometries/0Zephyr/S16Test/S16Model2.obj')
    body = f.getFigResFile().getGeomCustom(POSERROOT)
    body.findApplyDelta(f.getBodyIndex(), sc1, lstch)
    # Create new OBJ file with the GIVEN name
    ret = body.writeOBJ(realfn)
    self.assertEqual(ret, C_OK)
            
    # Record the OBJ file in the PoserObject for BODY:n
    f.setFigResFileGeom(buildRelPath(POSERROOT, realfn))
    sc1.cleanNonNullDelta(f.getBodyIndex(), setTargetMorph=lstch)
  
    c = ChronoMem.start("PoserFile.read-Sasha16.cr2")
    sc1.writeFile('tures/Sasha16-opt.pz3')
    c.stopPrint()
    
    
    

  def testFindActor(self):
    sc1 = PoserFile(PZZ_PHF_BOOK_TOP)

    c = ChronoMem.start("PoserFile.read-PHF-LoRes.cr2")
    lf = sc1.getLstFigure()

    f = lf[0]

    pa = f.findActor("babname")
    self.assertTrue(pa == None)

    pa = f.findActor("rHand:1")
    self.assertTrue(pa != None)

    pa = f.findActor("lHand", withIndex=False)
    self.assertTrue(pa != None)
    c.stopRecord("PoserFilePerf.txt")
#
  def testCreateChannelMorphList(self):
    sc1 = PoserFile(PZZ_PHF_BUXOM_BARBARIAN2)
    lf = sc1.getLstFigure()
    f = lf[0]
    csl = f.createChannelMorphList(None)
    self.assertTrue(csl != None)
    self.assertEquals(csl, f.getChannelMorphList())
    
#
  def testCreateDeltas(self):
    sc1 = PoserFile(PZZ_PHF_BUXOM_BARBARIAN_ROBE)
    lf = sc1.getLstFigure()
    v3 = lf[0]
    top = lf[1]
    ropt = ReportOption( Vector3d(), 0.01, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, False, 0.6)
    res = top.createDeltas("badrep", v3, None, None, ropt)
    self.assertEquals(res, C_ERROR)

    hs = { "PBMBuxom" }

    c = ChronoMem.start("PoserFile.createDeltas_NOEN")
    res = top.createDeltas(P7ROOT, v3, None, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEquals(res, C_OK)
    sc1.writeZ("tures/v3_buxom_barbarian_robe+deltas.pzz")

    sc1 = PoserFile(PZZ_PHF_BUXOM_BARBARIAN_ROBE)
    lf = sc1.getLstFigure()
    v3 = lf[0]
    top = lf[1]
    
    c = ChronoMem.start("PoserFile.createDeltas_MLSEN")
    ropt = ReportOption( Vector3d(), 0.01, PoserConst.C_MLS_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6)
    res = top.createDeltas(P7ROOT, v3, None, hs, ropt)
    c.stopRecord("FigurePerf.txt")

    self.assertEquals(res, C_OK)
    sc1.writeZ("tures/v3_buxom_barbarian_robe+MLSdeltas.pzz")

  def testCreateDeltaCubes(self):
    sc1 = PoserFile(PZ3_MAPPINGCUBES_CLOTHE)
    lf = sc1.getLstFigure()
    fig = lf[0]
    top = sc1.getLstProp()[0]

    hs = { "Enlarge" }

    c = ChronoMem.start("PoserFile.createDeltas_NOEN")
    ropt = ReportOption( Vector3d(), 0.0, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6)
    res = top.createDeltas(P7ROOT, fig, hs, ropt)
    #--> No Delta : OK
    c.stopRecord("FigurePerf.txt")
    self.assertEquals(res, C_OK)
    sc1.writeZ("tures/MappingCubes+Clothe+deltas.pzz")


    sc1 = PoserFile(PZ3_MAPPINGCUBES_CLOTHE)
    fig = sc1.getLstFigure()[0]
    top = sc1.getLstProp()[0]
    c = ChronoMem.start("PoserFile.createDeltas_NOEN")
    ropt = ReportOption( Vector3d(), 0.1, PoserConst.C_MLS_ENHANCEMENT, PoserConst.C_BOX_BOUNDING, True, 0.6, 0.0001)
    res = top.createDeltas(P7ROOT, fig, hs, ropt)
    #
    c.stopRecord("FigurePerf.txt")
    self.assertEquals(res, C_OK)
    sc1.writeZ("tures/MappingCubes+Clothe+deltas.pzz")

  def testCreateDeltasFromProp(self):
    pf = PoserFile('srcdata/scenes/MappingCubes+Clothe+Wind.pz3')
    srcpf = PoserFile('srcdata/scenes/MappingCubes.pz3')
    fig = pf.getLstFigure()[0]
    
    pc1 = srcpf.findMeshedObject('c1')
    
    hs = { "Enlarge2" }

    c = ChronoMem.start("PoserFile.createDeltas_Prop")
    ropt = ReportOption( Vector3d(), 0.0001, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6)
    res = fig.createDeltas(P7ROOT, pc1, None, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEquals(res, C_OK)



  def testPtMapping(self):
    curPoserObject = PoserFile(CR2_MAPPINGCUBES_ALTGEOM)

    # Find the actor      
    refMeshedObj = curPoserObject.findActor("c1:1")
    # Extract and load alternate geoms
    lstAltG = refMeshedObj.getAltGeomList()
    lstCurGeom = [ ]
    for altg in lstAltG:
      rfn = altg.getGeomFileName()
      gc = GeomCustom(getRealPath(P7ROOT, rfn))
      lstCurGeom.append(gc)

    lstRefGeom = [ refMeshedObj.getBaseGeomCustom(P7ROOT), ]

    for srcGC in lstCurGeom:
      srcWG = srcGC.getWaveGeom()

      # tabMapping = PtMapping.calcMapping(srcWG, lstRefGeom, ropt.translation, ropt.maxDist)
      tabMapping = calcMapping_KDTree(srcWG, lstRefGeom, Vector3d(), 0.0001)
      #print(str(tabMapping))
      self.assertEqual(len(tabMapping), 8)
      for tm in tabMapping:
        self.assertEqual(tm.srcNo, tm.refNo)
  

  def testReportDelta2(self):
    sc1 = PoserFile(CR2_MAPPINGCUBES_ALTGEOM)
    lf = sc1.getLstFigure()
    mm = lf[0]
    
    ropt = ReportOption( Vector3d(), 0.01, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, False, 0.6, 0.0001)
    g = mm.findActor('c1:1')
    
    res = g.createAlternateDeltas(P7ROOT, [], ropt)
    self.assertEquals(res, C_ERROR)
    
    res = g.createAlternateDeltas('/error', [ 'EnLarge' ], ropt)
    self.assertEquals(res, C_FILE_NOT_FOUND)
    
    
    sc1 = PoserFile(CR2_MAPPINGCUBES_ALTGEOM)
    lf = sc1.getLstFigure()
    mm = lf[0]
    ropt = ReportOption( Vector3d(), 0.01, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, False, 0.6, 0.0001)
    g = mm.findActor('c1:1')
    c = ChronoMem.start("Figure.createDeltas_NOEN")
    res = g.createAlternateDeltas(P7ROOT, { "Enlarge" }, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEquals(res, C_OK)
    sc1.writeFile("tures/MappingCubes-Morphed.cr2")
    


  def testReportDeltas(self):
    sc1 = PoserFile(PZ3_MAPMONDE_ALTGEOM)
    lf = sc1.getLstFigure()
    mm = lf[0]
    
    ropt = ReportOption( Vector3d(), 0.01, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, False, 0.6, 0.0001)

    hs = { "Vagues" }

    c = ChronoMem.start("Figure.createDeltas_NOEN")
    g = mm.findActor('Globe:1')
    res = g.createAlternateDeltas(P7ROOT, hs, ropt)
    c.stopRecord("FigurePerf.txt")
    self.assertEquals(res, C_OK)
    sc1.writeFile("tures/MapMonde+ReportVagues.pz3")
    


  def testHideAfter(self):
    sc1 = PoserFile(PZZ_PHF_BUXOM_BARBARIAN_ROBE)
    v3 = sc1.getLstFigure()[0]

    pa = v3.findActor("rForeArm:1")
    v3.hideAfter(pa, True)
    d = v3.getDescendant(pa)
    ld = str([ a.getName() for a in d ] )
    #print(ld)
    self.assertEqual(ld, "['rHand:1', 'rThumb1:1', 'rThumb2:1', 'rThumb3:1', 'rIndex1:1', 'rIndex2:1', 'rIndex3:1', 'rMid1:1', 'rMid2:1', 'rMid3:1', 'rRing1:1', 'rRing2:1', 'rRing3:1', 'rPinky1:1', 'rPinky2:1', 'rPinky3:1']")
    self.assertTrue(d[0]._hidden, "Hidden 0 OK")

    pa = v3.findActor("lForeArm:1")
    v3.hideAfter(pa, False)

    sc1.writeZ("tures/hideAfter.pzz")

  def testDeleteAfter(self):
    sc1 = PoserFile('srcdata/scenes/v3_buxom_barbarian_robe.pz3')
    v3 = sc1.getLstFigure()[0]

    pa = v3.findActor("rForeArm:1")
    #print(v3.getDescendant(pa))
    v3.delete(pa)
    self.assertEqual(len(v3.getDescendant(pa)), 0,"Empty Desc")

    pa = v3.findActor("lForeArm:1")
    v3.delete(pa)
    self.assertEqual(len(v3.getDescendant(pa)), 0,"Empty Desc")
    l = v3.getDescendant(v3.findActor("chest:1"))
    ls = str([ a.getName() for a in l ] )
    # print(ls)
    self.assertEqual(ls, "['neck:1', 'head:1', 'lEye:1', 'rEye:1', 'rCollar:1', 'rShldr:1', 'lCollar:1', 'lShldr:1', 'rBreast1:1', 'lBreast1:1', 'lBreast2:1', 'rBreast2:1']")
    self.assertEqual(len(v3.getDescendant(v3.findActor("chest:1"))), 12, "Chest Desc")
    
    mat = v3.getLstMaterial()[0]
    ret = v3.delete(mat)
    self.assertEquals(ret, C_OK)
    ret = v3.delete(mat)
    self.assertEquals(ret, C_FAIL)
    ret = v3.delete(WaveGeom())
    self.assertEquals(ret, C_ERROR)
    
    
    res = v3.cleanAllChannel("PBMBar")
    
    #TODO : Add another cleanAllChannel
    res = v3.cleanAllChannel("PHF") 
    
    # Useless function
    v3.cleanMagnetMaterial()
    

  def testGetDescendant(self):
    sc1 = PoserFile(PZZ_PHF_BUXOM_BARBARIAN_ROBE)
    v3 = sc1.getLstFigure()[0]

    ls = v3.getDescendant("hip")
    self.assertEquals(str(ls[0:11]), "['abdomen:1', 'chest:1', 'neck:1', 'head:1', 'lEye:1', 'rEye:1', 'rCollar:1', 'rShldr:1', 'rForeArm:1', 'rHand:1', 'rThumb1:1']") 

    pa = v3.findActor("rHand:1")
    la = v3.getDescendant(pa)
    self.assertEquals(len(la), 15)
    self.assertEquals(la[0].getName(), "rThumb1:1")
    self.assertEquals(la[14].getName(), "rPinky3:1")

    v3.setPrintName("toto")
    self.assertEquals(v3.getPrintName(), "toto")

    # QualifiedChannelName = [ActorName [':' bodyIndex] '.' ]ChannelName
    gt = v3.getChannel(pa, 'Shadock')
    self.assertEquals(gt, None)
    
    pa = v3.findActor("neck:1")
    gt = v3.getChannel(pa, 'PBMBarbarian2')
    self.assertEquals(gt.getName(), 'PBMBarbarian2')
    
    gt = v3.getChannel(None, 'neck.PBMBarbarian2')
    self.assertEquals(gt.getName(), 'PBMBarbarian2')

    gt = v3.getChannel(None, 'neck:1.PBMBarbarian2')
    self.assertEquals(gt.getName(), 'PBMBarbarian2')



  def testStump(self):
    sc1 = PoserFile(PZZ_PHF_BUXOM_BARBARIAN_ROBE)
    v3 = sc1.getLstFigure()[0]

    res = v3.stump(None, P7ROOT, "srcdata/v3_rForeArmvmassive.obj", False, False, False)
    self.assertEquals(res, PoserConst.C_ACTOR_NOTFOUND)

    pa = v3.findActor("rForeArm:1")
    res = v3.stump(pa, P7ROOT, "srcdata/v3_rForeArmvmassive.obj", False, False, False)
    self.assertEquals(res, C_OK)

    pa = v3.findActor("lForeArm:1")
    res = v3.stump(pa, P7ROOT, "srcdata/v3_lForeArmvmassive.obj", False, True, True)
    self.assertEquals(res, C_OK)

    sc1.writeZ("tures/stump.pzz")

#
  def testExtractGeometryStringListOfPoserActorChannelMorphStatusList(self):
    sc1 = PoserFile(PZ3_PHF_UGLY)
    v3 = sc1.getLstFigure()[0]

    lstch = v3.createChannelMorphList(None)

    lstpa = v3.getActors()[4:7] # .subList(2, 5)

    c = ChronoMem.start("PoserFile.extractGeometry-v3")
    lg = v3.extractGeometry(P7ROOT, lstpa, lstch)

    self.assertEquals(261, lg[0].getWaveGeom().getCoordListLength())
    self.assertEquals(728, lg[1].getWaveGeom().getCoordListLength())
    self.assertEquals(194, lg[2].getWaveGeom().getCoordListLength())

    c.stopRecord("FigurePerf.txt")



  def testExtractGeometryStringChannelMorphStatusList(self):
    sc1 = PoserFile(PZ3_PHF_UGLY)
    v3 = sc1.getLstFigure()[0]

    lstch = v3.createChannelMorphList(None)

    c = ChronoMem.start("PoserFile.extractGeometry-v3")
    lg = v3.extractGeometry("", None, lstch)
    c.stopRecord("FigurePerf.txt")

    self.assertTrue(lg == None)

    c = ChronoMem.start("PoserFile.extractGeometry-v3")
    lg = v3.extractGeometry(P7ROOT, lstch=lstch)
    c.stopRecord("FigurePerf.txt")
    self.assertTrue(lg != None)

    POSERROOT = "srcdata/PoserRoot"
    
    # Prepare the figure with individual .obj files to be able to import them
    extFile = PoserFile('srcdata/PoserRoot/Runtime/Librairies/Character/BootsExt.cr2')
    destFig = extFile.getLstFigure()[0]

    boucler = destFig.findProp('SBootsVic-Boucle:1')
    bouclel = destFig.findProp('SBootsVic-Boucle 1:1')

    ngc = destFig.extractGeometry(POSERROOT, lstpa=[bouclel, boucler])
    self.assertTrue(ngc != None)
    outMapLst = ngc[0].fusion(lg)



  def testGetMorphedMesh(self):
    sc1 = PoserFile(PZ3_PHF_UGLY)
    v3 = sc1.getLstFigure()[0]

    #    ChannelMorphStatusList lstch
    lstch = v3.createChannelMorphList(None)
    
    #lstch.saveSelected('tures/ccml.json')
    #lstch2 = ChannelMorphStatusList.loadList('tures/ccml.json')

    g = v3.getMorphedMesh("", lstch)
    self.assertTrue(g == None)

    c = ChronoMem.start("PoserFile.getMorphedMesh-v3")
    g = v3.getMorphedMesh(P7ROOT, lstch)
    c.stopRecord("FigurePerf.txt")
    self.assertTrue(g != None)

  def testGetMorphdeMeshWW(self):
    sc1 = PoserFile('/home/olivier/mdl/Whirlwind-full.pz3')
    destActors = sc1.findAllMeshedObject('Whirlwind')
    g = destActors[0].getMorphedMesh(P7ROOT, -1, None)

    fn = g.getGroupName()
    if (fn == None) or (fn==""):
      fn = g.getName()
    fn = cleanName(fn) 
    ret = g.writeOBJ('.' + os.sep + fn + '-ext.obj')
 

    

  def testRename(self):
    sc1 = PoserFile(PZ3_MAPMONDE_CHANNEL_01)
    f1 = sc1.getLstFigure()[0]

    ls = f1.getDescendant("Pied")
    self.assertEquals(str(ls), "['Globe:1']")

    a2 = f1.getActors()[4]
    f1.rename(a2, "Boule", "The Earth")

    ls = f1.getDescendant("Pied")
    self.assertEquals(str(ls), "['Boule:1']")

    sc1.writeFile("tures/PZ3_MAPMONDE_CHANNEL_01_RENAMED.pz3")

  def testCreatePropagation(self):
    sc1 = PoserFile(PZ3_MAPMONDE_CHANNEL_01)
    f1 = sc1.getLstFigure()[0]

    res = f1.createPropagation("BadActor:5", "TST_Rotate1", PoserToken.E_rotateX, 10.0)
    self.assertEquals(C_FAIL, res)

    upperActor = f1.findActor("BODY:1")

    res = f1.createPropagation(upperActor, "TST_Rotate2", PoserToken.E_baseProp, 10.0)
    self.assertEquals(C_FAIL, res)

    res = f1.createPropagation(upperActor, "TST_Rotate", PoserToken.E_rotateX, 10.0)
    self.assertEquals(C_OK, res)

    res = f1.createPropagation(upperActor, "TST_Rotate", PoserToken.E_rotateY, 1.0)
    self.assertEquals(C_OK, res)

    sc1.writeFile("tures/PZ3_MAPMONDE_CHANNEL_01_PROPAG.pz3")

    res = f1.addDrivenVisibility()
    self.assertEquals(C_OK, res)
    
    lstres=[]
    pm = f1.getLstMaterial()[0]
    res = f1.checkMaterialUsage(pm, P7ROOT, lstres)
    self.assertEquals(C_OK, res)

    f1.addMasterChannel("DAUBEChan", "xtran")


  def testimportedChannels1(self):
    scm = PoserFile(PZ3_PHF_ALTGEOM_ROBOT)
    lfm = scm.getLstFigure()
    v4m = lfm[0]

    ltst = ([ 'a', ], [ 'b', ])

    cia = v4m.checkImportedChannels(ltst, P7ROOT + "/Runtime/Geometries/ProjectHuman")
    self.assertEquals(cia, None)

    strTbl = readXLSFile("srcdata/tualtphf1.xls")

    self.assertFalse("", strTbl == None)

    cia = v4m.checkImportedChannels(strTbl, P7ROOT + "/Runtime/Geometries/ProjectHuman")

    self.assertEquals(cia.ts[0][0], C_OK)
    
    ret = v4m.importChannels(cia.lstChan, P7ROOT)

    scm.writeFile(PZ3_PHF_ALTGEOM_ROBOT_RES)


  
  def testcheckImportedChannels2(self):
    '''
    Error case, suggested by Zephyr11
    '''
    scm = PoserFile(PZ3_PHF_ALTGEOM_ROBOT)
    lfm = scm.getLstFigure()
    v4m = lfm[0]

    strTbl = readXLSFile("srcdata/tuetude2.xls")

    self.assertFalse(strTbl == None)

    cia = v4m.checkImportedChannels(strTbl, P7ROOT + "/Runtime/Geometries")

    self.assertEqual(cia.ts[0][0], C_OK)
    self.assertEqual(cia.ts[6][0], C_FAIL)
    self.assertEqual(C_FILE_NOT_FOUND, cia.ts[0][3])



  def testImportChannelsNew(self):
    scm = PoserFile('srcdata/Tempest-basic.cr2')
    lfm = scm.getLstFigure()
    fig = lfm[0]
    
    lstCd = [
      #                 no, actorName, chanTypeName, chanName,    printName,  initValue, minValue, maxValue. trackingScale, lstAltFiles, lstOps, groupName, altGeom
      ChannelDescriptor( 1, 'BODY',     'valueParm', 'OpenCanopy', '',         0.0,   0.0, 1.0, 0.05, [], []),
      ChannelDescriptor( 2, 'BODY',     '',          'Train',      '',         0.0,   0.0, 1.0, 0.05, [], []),
      ChannelDescriptor( 3, 'BODY',     'valueParm', 'Palonnier',  '',         0.0, -70.0, 70.0, 0.05, [], []),
      ChannelDescriptor( 4, 'BODY',     'valueParm', 'GouvProf',   'Gouv Dir', 0.0, -45.0, 45.0, 0.05, [], []),
      ChannelDescriptor( 5, '??',       'valueParm', 'MancheGD',   '',         0.0, -70.0, 70.0, 0.05, [], []),
      ChannelDescriptor( 6, 'BODY',     'valueParm', 'MancheGD',   '',         0.0, -70.0, 70.0, 0.05, [], []),
      ChannelDescriptor( 7, 'Fuselage', 'valueParm', 'FuseHR',     '',         0.0,   0.0,  0.0, 0.05, \
                        ['IGNORED', ], ['? BODY:1.FuselageHR ((0,0), (,1,))', ]),
      ChannelDescriptor( 8, 'Fuselage', 'geomChan', 'FuseHR',     '',         0.0,   0.0,  0.0, 0.05, \
                        ['NOTFOUND.obj', ], ['? BODY:1.FuselageHR ((0,0), (,1,))', ]),
      ChannelDescriptor( 8, 'Fuselage', 'geomChan', 'FuseHR',     '',         0.0,   0.0,  0.0, 0.05, \
                        ['Tempest-FuselageHR.obj', ], ['? BODY:1.FuselageHR ((0,0), (,1,))', ]),
      ChannelDescriptor( 9, 'Fuselage', 'geomChan', 'FuseHR',     '',         0.0,   0.0,  0.0, 0.05, \
                        ['Tempest-FuselageHR.obj', ], ['? BODY:1.FuselageHR ((0,0), (1,1))', ]),
      ChannelDescriptor(10, 'Gouvernail','yrot',     'yrot',   '',         0.0, -70.0, 70.0, 0.05, [], ['qddqs*BODY:1.Palonnier', ]),
      ChannelDescriptor(11, 'Gouvernail','yrot',     'yrot',   '',         0.0, -70.0, 70.0, 0.05, [], ['+1.0*BODY:1.Palonnier', ]),
      ChannelDescriptor(12, 'Properler','geomChan',  'PropGeom',   '',         0.0, 0.0, 0.0, 1.0, 
                        ['Tempest_prop_bl.obj', 'Tempest_noprop.obj' ], \
                        ['? ProperlerType ((0,0), (1,1), (2,2))', ]),
      ChannelDescriptor(13, 'Gouvernail', 'targetgeom', 'Morph',   '',     0.0, 0.0, 0.0, 1.0, 
                        ['Tempest_prop_bl', ], \
                        [ ], groupName='', altGeomNo=0),
      ChannelDescriptor(14, 'Fuselage', '', 'xrot',     '',         0.0,   0.0,  0.0, 0.05),

      # Add a ShaderNode
      ChannelDescriptor(15,     'BODY', 'shaderNodeParm', 'transTrain',     '',   0.0,   0.0,  1.0, 0.05, lstOps = ['? BODY.Train ((0, 0.0), (1, 1.0))' ], \
                        groupName='.sfghqfgh'),
      ChannelDescriptor(15,     'BODY', 'shaderNodeParm', 'transTrain',     '',   0.0,   0.0,  1.0, 0.05, lstOps = ['? BODY.Train ((0, 0.0), (1, 1.0))' ], \
                        groupName='Tempsl.PoserSurface.Transparency'),
      ChannelDescriptor(15,     'BODY', 'shaderNodeParm', 'transTrain',     '',   0.0,   0.0,  1.0, 0.05, lstOps = ['? BODY.Train ((0, 0.0), (1, 1.0))' ], \
                        groupName='Tempest_gls.Plus.Transparency'),
      ChannelDescriptor(15,     'BODY', 'shaderNodeParm', 'transTrain',     '',   0.0,   0.0,  1.0, 0.05, lstOps = ['? BODY.Train ((0, 0.0), (1, 1.0))' ], \
                        groupName='Tempest_gls.PoserSurface.sfghqfgh'),
      
      ChannelDescriptor(15,     'BODY', 'shaderNodeParm', 'transTrain',     '',   0.0,   0.0,  1.0, 0.05, lstOps = ['? BODY.Train ((0, 0.0), (1, 1.0))' ], \
                        groupName='Tempest_gls.PoserSurface.Transparency'),
      ]
    
    lstRes = [ c.checkLink(fig, dirPathList='srcdata/PoserRoot/Runtime/Geometries/Caparros_Aircrafts/Tempest/:/tmp') for c in lstCd ]
    self.assertEqual(lstRes, [C_OK, C_OK, C_OK, C_OK, PoserConst.C_ACTOR_NOTFOUND, C_OK, C_FAIL, C_FILE_NOT_FOUND, C_FAIL, C_OK, C_FAIL, C_OK, C_OK, C_OK, C_OK, \
                              PoserConst.C_BAD_QUALNAME, PoserConst.C_MATERIAL_NOTFOUND, PoserConst.C_NODE_NOTFOUND, PoserConst.C_NODE_NOTFOUND, C_OK])
      
      
    self.assertEqual(ChannelDescriptor( 7, 'Fuselage', 'valueParm', 'FuseHR', lstOps=['? ((0,0), (1,.05))', ]).checkLink(fig, dirPathList='srcdata/PoserRoot/Runtime/Geometries/Caparros_Aircrafts/Tempest/:/tmp'), C_FAIL)
    self.assertEqual(ChannelDescriptor( 7, 'Fuselage', 'valueParm', 'FuseHR', lstOps=['? .Fuse+lageHR ((0,0), (1,.05))', ]).checkLink(fig, dirPathList='srcdata/PoserRoot/Runtime/Geometries/Caparros_Aircrafts/Tempest/:/tmp'), C_FAIL)
  
      
    ret = fig.importChannels(lstCd, P7ROOT)
    self.assertEqual(ret, C_OK)
    
    ret = fig.hasMultipleGeom()
    self.assertEqual(ret, 0)

    lstUse = []
    ret = fig.checkMaterialUsage('Tempest_prbl', P7ROOT, lstUse)
    self.assertEqual(ret, C_OK)
    self.assertEqual(str(lstUse), "[['Properler:1', 'Main file', 'Properler:1 [internal : 1902 vertex']]")
    scm.save('srcdata/results/Tempest+channels.cr2')
    
    n,l = nextWord('')
    self.assertEqual(n, None)

  def testFindApplyDelta(self):    

    # Find Apply Delta on a Prop
    pf = PoserFile('srcdata/scenes/Flat_Grid.pz3')
    grid = pf.findMeshedObject('Flat_Grid')
    initgc = grid.getBaseGeomCustom(P7ROOT)
    initCL = initgc.getWaveGeom().getCoordList()
    resgc = grid.getMorphedMesh(P7ROOT, grid, set( [ 'Bosse 1', 'Bosse 2'] ))
    resCL = resgc.getWaveGeom().getCoordList()
    
    self.assertEqual(initCL[0], resCL[0])
    self.assertAlmostEqual(initCL[6997].x, resCL[6997].x, delta=1e-6)
    self.assertAlmostEqual(initCL[6997].y, resCL[6997].y - 0.00569722100000001, delta=1e-6)
    self.assertAlmostEqual(initCL[6997].z, resCL[6997].z, delta=1e-6)
    
    realfn = os.path.join(P7ROOT, 'Runtime/Geometries/phf-morphed.obj')
    pf = PoserFile('srcdata/scenes/v3_findApply.pz3')
    lstch = set( [ 'PBMVoluptuous' ] )

    destFig = pf.getLstFigure()[0]
    
    # Read figure's main geometry
    body = destFig.getFigResFile().getGeomCustom(P7ROOT)
    
    body.findApplyDelta(destFig.getBodyIndex(), pf, lstch)
    
    # Create new OBJ file with the GIVEN name
    body.writeOBJ(realfn)
          
    # Record the OBJ file in the PoserObject for BODY:n
    destFig.setFigResFileGeom(buildRelPath(P7ROOT, realfn))
    
    pf.cleanNonNullDelta(destFig.getBodyIndex(), setTargetMorph=lstch)

    pf.writeFile('tures/v3_findApplyRes.pz3')
    
    
    
    

  def testGetters(self):
    pf = PoserFile('srcdata/scenes/v3_findApply.pz3')
    lstch = set( [ 'PBMVoluptuous' ] )

    destFig = pf.getLstFigure()[0]
    destFig.getBodyIndex()
    destFig.setBodyIndex(1)
    
    self.assertEqual(len(destFig.getActors()), 14)

    self.assertEqual(len(destFig.getProps()), 2)

    destFig.setPrintName("toto")
    self.assertEqual(destFig.getPrintName(), "toto")
    
    p = destFig.findProp('toto')
    p = destFig.findProp('GROUND')
    m = destFig.getMaterial('daube')
    m = destFig.getMaterial('Preview')
    l = destFig.getActiveGeometry(P7ROOT, [])
    destFig.hasMultipleGeom()

    destFig.setPrintName("New Print Name")


  def testSequence(self):
    POSERROOT = "srcdata/PoserRoot"
    UNITCHR = 'tures/Boots.cr2'
    
    # Prepare the figure with individual .obj files to be able to import them
    extFig = PoserFile('srcdata/PoserRoot/Runtime/Librairies/Character/Boots.cr2')
    destFig = extFig.getLstFigure()[0]
    # Read figure's main geometry
    for destActor in [ destFig.findActor(s) for s in ('lShinBoots:2', 'lFootBoots:2', 'lToeBoots:2', 'rShinBoots:2', 'rFootBoots:2', 'rToeBoots:2') ]:
      g = destActor.getBaseGeomCustom(POSERROOT)
      realfn = 'tures/{:s}.obj'.format(destActor.getName()[:-2])
      g.writeOBJ(realfn)
      destActor.setBaseMesh(POSERROOT, realfn)

    extFig.writeFile(UNITCHR)
    
    sc1 = PoserFile(PZZ_PHF_BOOK_TOP)
    destFig = sc1.getLstFigure()[0]
    
    extFig = PoserFile(UNITCHR)
    boot = extFig.findActor('lShinBoots:2')    
    ret = destFig.attachActor(sc1.findActor('lShin:1'), boot)
    self.assertEqual(ret, C_OK)
     
    extFig = PoserFile(UNITCHR)
    boot = extFig.findActor('rShinBoots:2')    
    ret = destFig.attachActor(sc1.findActor('rShin:1'), boot)
    self.assertEqual(ret, C_OK)
  
    # Create the valueParm at body level
    bodyAct = destFig.findActor('BODY:1')
    bodyAct.updateOrCreateVP('isAlien', minVal=0.0, maxVal=1.0, applyLimits=True, isHidden=False)
  
    magnf = PoserFile("srcdata/PoserRoot/Runtime/Librairies/Props/PHFAlienMagnet.pp2")
    for base,magn,zone in zip(*[iter(magnf.getLstProp())]*3):
      destFig.addMagnet(base, magn, zone, 'isAlien')

    destFig.addMasterChannel("DAUBEChan", "Alien")

    destFig.cleanMagnetMaterial()
    
    sc1.writeFile('tures/v3_book_top+Magnet.pz3')  
  
    # Extra Unit Test
    # Prop Remove : asymmetric top:1
    pp = destFig.findProp('asymmetric top:1')
    ret = destFig.delete(pp)
    self.assertEqual(ret, C_OK)
    
    ret = destFig.delete(pp)
    self.assertEqual(ret, C_FAIL)
    
  # Attach Actor with external valueParm
  def testAttachActor(self):
    POSERROOT = "srcdata/PoserRoot"
    UNITCHR = 'tures/BootsExt.cr2'
    
    # Prepare the figure with individual .obj files to be able to import them
    extFile = PoserFile('srcdata/PoserRoot/Runtime/Librairies/Character/BootsExt.cr2')
    destFig = extFile.getLstFigure()[0]
    # Read figure's main geometry
    for destActor in [ destFig.findActor(s) for s in ('lShinBoots:1', 'lFootBoots:1', 'lToeBoots:1', 'rShinBoots:1', 'rFootBoots:1', 'rToeBoots:1') ]:
      g = destActor.getBaseGeomCustom(POSERROOT)
      realfn = 'tures/{:s}.obj'.format(destActor.getName()[:-2])
      g.writeOBJ(realfn)
      destActor.setBaseMesh(POSERROOT, realfn)
      
      self.assertEqual(destActor.getIndex(), 1)

    boucler = destFig.findProp('SBootsVic-Boucle:1')
    self.assertEqual(boucler.getIndex(), 1)
    bouclel = destFig.findProp('SBootsVic-Boucle 1:1')
    self.assertEqual(bouclel.getIndex(), 1)

    morphpic = bouclel.getChannel('pic')
    morphpic.removeDeltas()
    
    # Copy GenericTransform   
    morphpic = boucler.getChannel('pic')
    gt = GenericTransform()
    gt.copy(morphpic)
    self.assertEqual(len(gt.getDeltas().deltaSet), 9)
    
    # Report 'Pic' Morph on Left Boucle
    ropt = ReportOption( Vector3d(), 0.025, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6, 0.0)
    ret = bouclel.createDeltas(POSERROOT, boucler, {'Pic'}, ropt)
    morphpic = bouclel.getChannel('pic')
    gt = GenericTransform()
    gt.copy(morphpic)
    self.assertEqual(len(gt.getDeltas().deltaSet), 9)
    
    gt.toStatic()
    
    #  def optimizeDeltas(self, refNorm):
    morphpic.optimizeDeltas(0.001)
    self.assertEqual(len(morphpic.getDeltas().deltaSet), 8)
    extFile.writeFile(UNITCHR)
    
    sc1 = PoserFile(PZZ_PHF_BOOK_TOP)
    destFig = sc1.getLstFigure()[0]
    
    ic = destFig._inkyChains[0]
    goal = ic.findAttribut(PoserToken.E_goal)
    self.assertEqual(goal.getName(), 'goal')
    
    al = ic.findAttribut(PoserToken.E_addLink, 'lShin:1')
    self.assertEqual(al, None)

    al = ic.findAttribut(PoserToken.E_addLink, 'addLink')
    self.assertEqual(al.getValue(), 'lThigh:1')
    
    al = ic.getAttribut('toto')
    self.assertEqual(al, None)

    r = ic.deleteAttribut('toto')
    self.assertFalse(r)
    
    al = ic.getAttribut('addLink')
    self.assertEqual(al.getValue(), 'lThigh:1')
    
    
    extFile = PoserFile(UNITCHR)
    boot = extFile.findActor('lShinBoots:1')    
    ret = destFig.attachActor(sc1.findActor('lShin:1'), boot)
    self.assertEqual(ret, C_OK)
     
    extFile = PoserFile(UNITCHR)
    boot = extFile.findActor('rShinBoots:1')    
    ret = destFig.attachActor(sc1.findActor('rShin:1'), boot)
    self.assertEqual(ret, C_OK)
  
    sc1.writeFile('tures/v3_book_top+Magnet+H.pz3')  


  def checkMatUsage(self):
    pf = PoserFile('srcdata/scenes/MappingCubes+Clothe+Wind.pz3')
    fig = pf.getLstFigure()[0]

    lstres=[]
    res = fig.checkMaterialUsage('default', P7ROOT, lstres)
    self.assertEquals(C_OK, res)
    self.assertEquals(str(lstres), "[['c0:1', 'Main file', 'c0:1 [internal : 8 vertex'], ['c1:1', 'Main file', 'c1:1 [internal : 8 vertex'], ['c1:1', 'Main file', 'c1:1 [internal : 8 vertex']]")

    # Test with some alternate geoms
    pf = PoserFile('srcdata/scenes/MappingCubes+Clothe.pz3')
    lstres=[]
    res = fig.checkMaterialUsage('default', P7ROOT, lstres)
    self.assertEquals(C_OK, res)
    self.assertEquals(str(lstres), "[['c0:1', 'Main file', 'c0:1 [internal : 8 vertex'], ['c1:1', 'Main file', 'c1:1 [internal : 8 vertex'], ['c1:1', 'Main file', 'c1:1 [internal : 8 vertex']]")
    


  def createChannelMorphList(self, stm):
    lstCS = ChannelMorphStatusList()
    pf = PoserFile('srcdata/scenes/MappingCubes+Clothe+Wind.pz3')
    fig = pf.getLstFigure()[0]
    
    
  
  def testChannelLinks(self):
    pf = PoserFile('srcdata/scenes/v3_findApply.pz3')
    destFig = pf.getLstFigure()[0]
    
    lstRes=[]
    for fig in pf.getLstFigure():
      #lstRes.append(FIG_HEADER)
      lstRes.append( [ '#', '', '', fig.getPrintName(), '', '', fig.getPrintName(), fig.getFigResFile().getValue() ] )


    c = ChronoMem.start("Figure-ChannelDest")

    opt = 4
    for pmo in destFig.getActors():
      for gt in pmo.getChannels():
        if opt>2:        
          qn, nbdeltas, labdesc, labparent = pf.printChannelLinks(gt)
          if labdesc or labparent:
            print('Channel[{:s}] : desc={:d} ({:s}) parent=({:s})'.format(qn, nbdeltas, labdesc, labparent))
            
    c.stopRecord("FigurePerf.txt")
        
  def checkLinks(self):
    c = ChronoMem.start("PoserFile.checkLinks")
    sc1 = PoserFile('srcdata/scenes/MappingCubes+Clothe+Errors.pz3', True)  

    c.stopRecord("FigurecheckLinks.txt")
  
  
if __name__ == "__main__":
    unittest.main()
    
    
