
import os 
import time, logging
try:
  import psutil
  PSUTIL = True
except:
  PSUTIL = False

OBJ_FILE_GREY_CUBE = "srcdata/cube_gris.obj"

OBJ_FILE_LIGHT = "srcdata/light.obj"

OBJ_FILE_DUPVERT_01 = "srcdata/CubesDupVerts-01.obj"

OBJ_FILE_DUPVERT_02 = "srcdata/CubesDupVerts-02.obj"

OBJ_FILE_RESSORT = "srcdata/ressort.obj"

OBJ_FILE_RESSORT_SIMPLE = "srcdata/ressort2800.obj"

OBJ_FILE_RED_CUBE = "srcdata/TU_Fusion_Cube.obj"

OBJ_FILE_GREEN_TRON = "srcdata/TU_Fusion_Tron.obj"

OBZ_FILE_PHF_LOWRES = "srcdata/PoserRoot/Runtime/Geometries/ProjectHuman/PHFemaleLowRes-Src.obz"

OBZ_FILE_PHF_LOWRES_SRC = "srcdata/PoserRoot/Runtime/Geometries/ProjectHuman/PHFemaleLowRes-Src.obz"

OBJ_FILE_SPHERE_HOLE = "srcdata/sphere_hole.obj"

OBJ_FILE_EARTH_HOLE = "srcdata/TerrePoignees+Trou.obj"

OBJ_FILE_TOP_HOLE = "srcdata/01top_hole.obj"

OBJ_FILE_ICOSAHEDRON = "srcdata/icosahedron.obj"

OBJ_FILE_GREY_CUBE_RES = "tures/cube_gris.obj"

OBZ_FILE_GREY_CUBE_RES = "tures/cube_gris.obz"

OBJ_FILE_RESSORT_SIMPLE_RES = "tures/ressort2800.obj"

OBZ_FILE_PHF_LOWRES_RES = "tures/PHFemaleLowRes.obz"

P7ROOT = "srcdata/PoserRoot"

PP2_VILLE_TEST = "srcdata/PoserRoot/Runtime/Librairies/Props/tu1/Ville_Test.pp2"

PP2_VILLE_TEST_MOD = "srcdata/PoserRoot/Runtime/Librairies/Props/tu1/Ville_Test_Mod.pp2"

PZZ_PHF_BUXOM_BARBARIAN_ROBE = "srcdata/scenes/v3_buxom_barbarian_robe.pzz"

PZZ_PHF_BUXOM_BARBARIAN2 = "srcdata/scenes/v3_buxom_barbarian2.pzz"

PZZ_PHF_BOOK_TOP = "srcdata/scenes/v3_book_top2.pzz"

PZ3_PHF_UGLY = "srcdata/scenes/v3_stump_ugly.pz3"

PZ3_PHF_ALTGEOM_ROBOT = "srcdata/scenes/phf_altThighRobot.pz3"

PZ3_PHF_ALTGEOM_ROBOT_RES = "tures/phf_altThighRobot.pz3"

PZ3_MAPMONDE_CHANNEL_01 = "srcdata/scenes/MapMonde+Prop+Channels-01.pz3"
PZ3_MAPMONDE_ALTGEOM = "srcdata/scenes/MapMonde+AltGeom.pz3"
CR2_MAPPINGCUBES_ALTGEOM = "srcdata/PoserRoot/Runtime/Librairies/Character/tv2/MappingCubes.cr2"
PZ3_MAPPINGCUBES_CLOTHE = "srcdata/scenes/MappingCubes+Clothe.pz3"

PZ3_FLAT_GRID_1 = "srcdata/scenes/Flat_Grid.pz3"

PZZ_V4_VOLUPTUOUS = "srcdata/scenes/V42+Voluptuous.pzz"

PZZ_V4_VOLUPTUOUS_LIGHT = "srcdata/scenes/V42+Voluptuous-Light.pz3"

OBJ_FILE_MAGNET_BARRE4PT = "srcdata/Magnet_Barre_4pt.obj"

OBJ_FILE_MAGNET_BARRE4PT_MORPH = "srcdata/Magnet_Barre_4pt_Morphed.obj"


def byte2Human(deltam):
  return str(deltam)+" bytes" if deltam<1024 else (  str(int(deltam/1024)) + " kbytes" if deltam<1024*1024 else str(int(deltam / 1024 / 1024)) + " Mbytes")


class ChronoMem(object):
  def __init__(self, testName):
    self.test = testName
    self.tf = 0.0
    if PSUTIL:
      self.process = psutil.Process(os.getpid())
      self.rss = self.process.memory_info().rss  # in bytes 
      self.data = self.process.memory_info().data

    self.t0 = time.perf_counter()
    
  @classmethod
  def start(cls, testName):
    return  ChronoMem(testName)
#
#  /**
#   * Stop the chrono, print the result and store it in a text file.
#   */
  def stopPrint(self):
    self.tf = time.perf_counter()
    if PSUTIL:
      self.process = psutil.Process(os.getpid())
      deltarss = self.process.memory_info().rss  - self.rss # in bytes 
      deltadata =  self.process.memory_info().data - self.data
      logging.info("CHRONO[{0:s}] dt={1:g}ms dRAM={2:s} dData={3:s}".format( self.test, 1000.0*(self.tf - self.t0),  byte2Human(deltarss), byte2Human(deltadata)))
    else:
      logging.info("CHRONO[{0:s}] dt={1:g}ms No psutil".format( self.test, 1000.0*(self.tf - self.t0)))
#
#  /**
#   * Stop the chrono, print the result and store it in a text file.
#   */
  def stopRecord(self, perfDBFN):
    self.stopPrint()
#
#    try
#      {
#      File f = new File(perfDBFN);
#      boolean shallInit = !f.exists() ;
#      
#      FileWriter fout = new FileWriter(perfDBFN, true);
#
#      PrintWriter prn = new PrintWriter(fout);
#
#      if(shallInit)
#        {
#        // Init the first line of the performance file
#        prn.println("# TestDate\tos.name\tos.version\tos.archi\tBits\tNbProc\tjava.sun.version\tTestName\tDuration\tMemUsed");
#        }
#
#      long deltam = memf - mem0;
#
#      Properties sp = System.getProperties();
#
#      prn.println("" + t0 + 
#                  "\t" + sp.getProperty("os.name") +
#                  "\t" + sp.getProperty("os.version")+
#                  "\t" + sp.getProperty("os.arch") + 
#                  "\t" + sp.getProperty("sun.arch.data.model") +
#                  "\t" + Runtime.getRuntime().availableProcessors()+
#                  "\t" + sp.getProperty("java.version") + 
#                  "\t" + test + "\t" + (tf - t0) + "\t" + deltam);
#
#      fout.close();
#      }
#    catch (IOException ioex)
#      {
#      ioex.printStackTrace();
#      }
#    }
#
#  }
