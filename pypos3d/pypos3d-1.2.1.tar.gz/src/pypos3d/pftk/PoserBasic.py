# -*- coding: utf-8 -*-
'''
Comme functions and consts for Poser file analysis.
Include Poser's vocabulary up to Poser 9 (partially for Poser 11)

Created on 1 mai 2020
@author: olivier
'''
import sys, traceback
import os.path
import copy
from collections import namedtuple
import platform
import importlib

import xlrd
from xlrd.sheet import ctype_text, XL_CELL_TEXT, XL_CELL_NUMBER, XL_CELL_EMPTY

from langutil import File, C_FAIL

# Test & Set
#    * @param s
#    * @param old
#    * @param ns
#    * @return
def TAS(s, old, ns): return ns if old == s else s

def isWindows(): return platform.system()=="Windows"

# Return a relative path to the Poser root directory with 
# system file separators replaced by ":" characters.
# 
# When the fileName is not "in" the poserRootDir, fileName is returned.
# 
# @param poserRootDir
# @param fileName
# @return
def buildRelPath(poserRootDir, fileName):
  res = fileName
  if poserRootDir:
    try:
      prdcpath = os.path.realpath(poserRootDir)
      tfcpath = os.path.realpath(fileName)

      if tfcpath.startswith(prdcpath):
        res = tfcpath[len(prdcpath):]
        res = res.replace(os.sep, ':')
    except IOError:
      res = None
      print('IOError in buildRelPath(%s, %s)', poserRootDir, fileName)

  return res


#    * Build a real path name.
#    * 
#    * @param poserRootDir
#    * @param poserPath
#    * @return a matched path or null in case of inconsistency (usually with DOS drive in *nix env)
def getRealPath(poserRootDir, poserPath):
  #  From time to time relative path are enclose in double-quote " characters
  if poserPath[0]=="\"" and poserPath[-1]=="\"":
    poserPath = poserPath[1:len(poserPath)-1]

  if (len(poserPath)>3) and (poserPath[1]==':') and (poserPath[0].isalpha()):
    #  We can suppose that the name contains the DOS drive letter
    #  In such case, it's a mess on non Windows OS!
    if isWindows():
      return poserPath

    #  Try to find the last part of poserRootDir in the path
    parts = poserRootDir.split("/")
    lastPart = parts[len(parts)-1] if len(parts)>=2 else parts[1]

    lpi = poserPath.find(lastPart)
    return poserRootDir + poserPath[lpi + len(lastPart):].replace('\\', os.sep) if (lpi >= 0) else poserPath

  #  Avoid *nix absolute path
  if poserPath[0]==os.sep:
    return poserPath
  
  if poserPath.find(':') >= 0:
    poserPath = poserPath.replace(':', os.sep)
  elif poserPath.find('\\') >= 0:
    poserPath = poserPath.replace('\\', os.sep)
  
  if poserPath[0]==os.sep:
    poserPath = poserPath[1:]
  elif len(poserPath)>2 and poserPath[0]=='.' and poserPath[1]==os.sep:
    poserPath = poserPath[2:]
    
  return poserPath if os.path.isfile(poserPath) else os.path.join(poserRootDir, poserPath)
 

# Return the index of a name, i.e. the leading ":n"
# 
#   * @param src string
#   * @return an int. 0 if no ':', -1 if the input string is null
def index(n):
  if n == None:
    return -1
  c = n.rfind(':')
  return int(n[c + 1:]) if (c >= 0) else 0
 
 
def nodeNameNo(n):
  '''
  Return the number at the end of the string.
  Return 1 if none
  '''
  for i,c in enumerate(n[::-1]):
    if not c.isdecimal(): break
  
  return int(n[-i:]) if i>0 else 1  
 
 
# Clean a name = Suppress le leading ":n" and trim (before and after)
#
# * @param src string
# * @return a cleaned string
def cleanName(src):
  src = src.strip()
  posc = src.find(':')
  return src[0:posc].strip() if (posc>=0) else src

def getPoserFileType(fn):
  pos = fn.rfind('.')
  if (pos > 0):
    ext = fn[pos+1:].lower()
    try:
      return PoserConst.PFT_EXT.index(ext)
    except ValueError:
      return C_FAIL

  return C_FAIL 

# Return true if the file type name matches a compressed form for Poser
def isCompressed(arg):
  if isinstance(arg, int):
    fileType = int(arg)
  elif isinstance(arg, str):
    fileType = getPoserFileType(arg)
  elif isinstance(arg, File):
    fileType = getPoserFileType(arg.getAbsolutePath())

  return (fileType >= 0) and (fileType < PoserConst.PFT_MAXTYPE) and ((fileType & 0x0001) == 0x0001)

def RemoveQuotes(s):
  if s and len(s)>=2:
    return s[1:-1] if ((s[0]=='"') and (s[-1]=='"')) or ((s[0]=="'") and (s[-1]=="'")) else s

  return s

def WBoolLine(fw, pfx, name, bval):
  fw.write(f"{pfx}{name} {'1' if bval else '0'}\n")

class PoserConst(object):
  C_EX_NOTCALL = 'pypos3d.pftk.error.NotCallable'
  # ========================================================== 
  # Return codes                                               
  # ========================================================== 

  # Bitmask to indicate that the figure contains an internal geometry 
  C_HAS_INTERNAL = 0x0021

  # Bitmask to indicate that the figure uses another file geometry 
  C_HAS_LOCAL_OBJFILE = 0x0022

  # Bitmask to indicate that the figure uses an alternate geometry 
  C_HAS_ALT_GEOM = 0x0024

  # File Size Differs 
  C_SIZE_CHANGED = 0x1001

  # Last Modification Date Differs 
  C_DATE_CHANGED = 0x1002

  # Bad figure index 
  C_BAD_INDEX         = -128
  C_BAD_QUALNAME      = -129

  # Actor not found in search operations 
  C_ACTOR_NOTFOUND    = -2
  C_MATERIAL_NOTFOUND = -130
  C_NODE_NOTFOUND     = -131

  # Already existing thing 
  C_EXISTS = 0x0F00

  # ========================================================== 
  # No Bounding 
  C_NO_BOUNDING = 0

  # Box Bounding 
  C_BOX_BOUNDING = 1

  # Sphere Bounding 
  C_SPHERE_BOUNDING = 2

  # Polytope Bounding 
  C_POLYTOPE_BOUNDING = 3

  # No Enhancement 
  C_NO_ENHANCEMENT = 0

  # AVG Enhancement. Based on average move of neighboors 
  C_AVG_ENHANCEMENT = 1

  # MLS Enhancement. Based on Mean Less Square calc 
  C_MLS_ENHANCEMENT = 2

  # Remove any 'BODY' const strings and replace them by a getRoot() as Figure level
  C_BODY = "BODY"

  C_UNIVERSE = "UNIVERSE"


  # ---------------------------------------------------------------------------- 
  # Token that represents links to files in a PoserFile 
  PREFVOC = [
        "readScript", # 0
        "figureResFile", # 1
        "objFileGeom", # 2
        "file", # 3 - In NodeInput, ...
        "bumpMap", # 4
        "reflectionMap", # 5
        "transparencyMap", # 6 
        "textureMap", # 7
        "morphBinaryFile", # 8 - morphBinaryFile PATH.pmd
        "injectPMDFileMorphs" # 9 - injectPMDFileMorphs JamesFBM.pmd
    ]

  PREFVOC_READSCRIPT, PREFVOC_FIGURERESFILE, PREFVOC_OBJFILEGEOM, PREFVOC_FILE,\
  PREFVOC_BUMPMAP, PREFVOC_REFLECTIONMAP, PREFVOC_TRANSPARENCYMAP, PREFVOC_TEXTUREMAP,\
  PREFVOC_MORPHBINARYFILE, PREFVOC_INJECTPMDFILEMORPHS = range(0,10)
  
  # Poser file types.<br>
  # First : uncompressed file type.
  # Next : compressed file type.
  PFT_OBJ, PFT_OBZ, \
  PFT_PZ2, PFT_P2Z, \
  PFT_PZ3, PFT_PZZ, \
  PFT_CR2, PFT_CRZ, \
  PFT_FC2, PFT_FCZ, \
  PFT_PP2, PFT_PPZ, \
  PFT_HR2, PFT_HRZ, \
  PFT_HD2, PFT_HDZ, \
  PFT_LT2, PFT_LTZ, \
  PFT_CM2, PFT_CMZ, \
  PFT_MC5, PFT_MZ5, \
  PFT_MC6, PFT_MCZ, *_ = range(0, 100)

  PFT_MAXTYPE = 0x00FF
  PFT_MASK = 0x00FE
  FFT_IMG = 0x0100
  FFT_UNKNOWN = 0xFFFF

  # Poser Language Versions names 
  POSER_V4 = "4.01"
  POSER_V5 = "5"
  POSER_V6 = "6"
  POSER_V7 = "7"
  POSER_V9 = "9"
  POSER_V11 = "11"

  # Poser file extensions.
  # ORDER shall not be changed !
  PFT_EXT = ( "obj", "obz", "pz2", "p2z", "pz3", "pzz", "cr2", "crz", "fc2", "fcz", "pp2", "ppz", "hr2", "hrz", "hd2", "hdz", "lt2", "ltz", "cm2", "cmz", "mc5", "mz5", "mc6", "mcz" )

  # Image file extensions.
  FFT_IMG_EXT = ( "jpg", "jpeg", "png", "gif", "tif", "tiff", "bmp" )

  #* Geometry definition types
  GT_NONE,GT_GLOBAL_OBJFILE,GT_LOCAL_OBJFILE,GT_INTERNAL,GT_ALTERNATE = range(5)
  GEOMTYPE = ( "None", "Main file", "Local file", "Internal", "Alternate" )
  GEOMPRINT = ( "None", "Grp", "File", "Int", "Alt" )

  # S_GLOBAL_OBJFILE_PFX = "20 "
  S_LOCAL_OBJFILE_PFX = "0 0 "
  
  C_NO_PARM = "NO_PARM"
  C_NO_NODE = "NO_NODE"
  C_NO_MAPG = '"NO_MAP"'
  C_NO_MAP = "NO_MAP"

  # Shader Node Code
  kNodeTypeCodeBLENDER  = 1000
  kNodeTypeCodeIMAGEMAP = 1001



class PoserObject(object):
  ''' Poser Object with common attributs. '''

  def __init__(self, *arg):
    ''' Create an empty PoserObject '''
    self._poserType = None
    self._name = None

  def read(self, st):
    pass

  def write(self, fw, pfx):
    pass

  # @return the name of the object.
  def getName(self): return self._name

  # Set the name.
  def setName(self, string):
    self._name = string

  #* @return Returns the poserType.
  def getPoserType(self):
    return self._poserType

  #* @param poserType The poserType to set.
  def setPoserType(self, poserType):
    self._poserType = poserType
  
  def toString(self): return self._poserType.token
        
PToken = namedtuple('PToken', ['token', 'isStructured', 'clazz', 'isDirect', 'defaultName'])
PToken.__new__.__defaults__ = ('',False,None,True,'') 

class PoserToken:
  ''' Poser class to manage Poser File language (token) and implementation modules. ''' 
  MODULES = [ 'pypos3d.pftk.SimpleAttribut', 'pypos3d.pftk.StructuredAttribut', 'pypos3d.pftk.GeomCustom', 'pypos3d.pftk.PoserMeshed', 'pypos3d.pftk.Figure' ]
  LOADED_MODULE = { }
  LOADED_CLASS = { }
  
  BADTOKEN = PToken('', False) # Illegal token
  E_addToMenu = PToken("addToMenu", False)
  E_attribute = PToken("attribute", False, None, False)
  E_bend = PToken("bend", False)
  E_animatableOrigin = PToken("animatableOrigin", False)
  E_collisionDetection = PToken("collisionDetection", False)
  E_displayOrigin = PToken("displayOrigin", False)
  E_displayMode = PToken("displayMode", False)
  E_customMaterial = PToken("customMaterial", False)
  E_uniqueInterp = PToken("uniqueInterp", False, None, False)
  E_con = PToken("con", False, None, False)
  E_lin = PToken("lin", False, None, False)
  E_br = PToken("br", False, None, False)
  E_version = PToken("version", True, 'StructuredAttribut', False)
  E_groups = PToken("groups", True, 'StructuredAttribut', False) # v5
  E_groupNode = PToken("groupNode", True, 'StructuredAttribut', False) # v 5
  E_keyLayer = PToken("keyLayer", True, 'StructuredAttribut', False) # v 5
  
  E_parmNode = PToken("parmNode", False, None, False) # v5
  E_collapsed = PToken("collapsed", False, None, False) # v4.2
  E_shaderTree = PToken("shaderTree", True, 'ShaderTree', False) # v 5
  E_node = PToken("node", True, 'Node', False) # v 5
  E_pos = PToken("pos", False, None, False) # v5
  E_showPreview = PToken("showPreview", False, None, True) # v5
  E_nodeInput = PToken("nodeInput", True, 'NodeInput', False) # v 5
  E_value = PToken("value", False) # v5
  E_parmR = PToken("parmR", False) # v5
  E_parmG = PToken("parmG", False) # v5
  E_parmB = PToken("parmB", False) # v5
  E_file = PToken("file", False) # v5
  E_backfaceCull = PToken("backfaceCull", False, None, False) # v5
  E_visibleInReflections = PToken("visibleInReflections", False, None, False) # v5
  E_visibleInRender = PToken("visibleInRender", False, None, False) # v5
  
  E_visibleInCamera = PToken("visibleInCamera", False, None, False) # v9
  E_visibleInIDL = PToken("visibleInIDL", False, None, False) # v9
  
  E_displacementBounds = PToken("displacementBounds", False, None, False) # v5
  E_shadingRate = PToken("shadingRate", False, None, False) # v5
  E_smoothPolys = PToken("smoothPolys", False, None, False) # v5
  
  E_smarParent = PToken("smartparent", False, None, False) # v5
  E_vertsGroup = PToken("vertsGroup", True, 'VertsGroup', False) # v 5
  
  E_stitchVertsGroupProperties = PToken("stitchVertsGroupProperties", True, 'StructuredAttribut', False) # v7
  E_U_Bend_Resistance = PToken("U_Bend_Resistance", False, None, False)
  E_V_Bend_Resistance = PToken("V_Bend_Resistance", False, None, False)
  E_U_Stretch_Resistance = PToken("U_Stretch_Resistance", False, None, False)
  E_V_Stretch_Resistance = PToken("V_Stretch_Resistance", False, None, False)
  E_Shear_Resistance = PToken("Shear_Resistance", False, None, False)
  E_U_Scal = PToken("U_Scale", False, None, False)
  E_V_Scal = PToken("V_Scale", False, None, False)
  E_Density = PToken("Density", False, None, False)
  E_Thickness = PToken("Thickness", False, None, False)
  
  
  E_Spring_Resistance = PToken("Spring_Resistance", False, None, False)
  E_Air_Damping = PToken("Air_Damping", False, None, False)
  E_Dynamic_Friction = PToken("Dynamic_Friction", False, None, False)
  E_Static_Friction = PToken("Static_Friction", False, None, False)
  E_Friction_Velocity_Cutoff = PToken("Friction_Velocity_Cutoff", False, None, False)
  E_Cloth_Cloth_Force = PToken("Cloth_Cloth_Force", False, None, False)
  E_U_Bend_Rate = PToken("U_Bend_Rate", False, None, False)
  E_V_Bend_Rate = PToken("V_Bend_Rate", False, None, False)
  E_Cloth_Cloth_Friction = PToken("Cloth_Cloth_Friction", False, None, False)
  E_Damping_Stretch = PToken("Damping_Stretch", False, None, False)
  E_get_friction_from_solid = PToken("get_friction_from_solid", False, None, False)
  E_Use_Edge_Springs = PToken("Use_Edge_Springs", False, None, False)
  E_anisotropic = PToken("anisotropic", False, None, False)
  
  E_shaderNodeParm = PToken("shaderNodeParm", True, 'GenericTransform', False) # v7
  
  E_rayTraceShadows = PToken("rayTraceShadows", False, None, False)
  E_depthMapShadows = PToken("depthMapShadows", False, None, False)
  E_shadowBlurRadius = PToken("shadowBlurRadius", False, None, False)
  E_shadowRaytraceSoftness = PToken("shadowRaytraceSoftness", False, None, False)
  E_shadowBiasMin = PToken("shadowBiasMin", False, None, False)
  E_doAmbientOc = PToken("doAmbientOc", False, None, False)
  E_ambientOcDist = PToken("ambientOcDist", False, None, False)
  E_ambientOcBias = PToken("ambientOcBias", False, None, False)
  E_ambientOcStrength = PToken("ambientOcStrength", False, None, False)
  E_atmosphereStrength = PToken("atmosphereStrength", False, None, False)
  
  E_userCreated = PToken("userCreated", False, None, False)
  E_toonTones = PToken("toonTones", False, None, False)
  
  E_FourPorts_p1 = PToken("FourPorts_p1", False, None, False)
  E_FourPorts_p2 = PToken("FourPorts_p2", False, None, False)
  E_FourPorts_p3 = PToken("FourPorts_p3", False, None, False)
  E_FourPorts_p4 = PToken("FourPorts_p4", False, None, False)
  
  E_ThreePortsBigLeft_p1 = PToken("ThreePortsBigLeft_p1", False, None, False)
  E_ThreePortsBigLeft_p2 = PToken("ThreePortsBigLeft_p2", False, None, False)
  E_ThreePortsBigLeft_p3 = PToken("ThreePortsBigLeft_p3", False, None, False)
  
  E_ThreePortsBigRight_p1 = PToken("ThreePortsBigRight_p1", False, None, False)
  E_ThreePortsBigRight_p2 = PToken("ThreePortsBigRight_p2", False, None, False)
  E_ThreePortsBigRight_p3 = PToken("ThreePortsBigRight_p3", False, None, False)
  
  E_ThreePortsBigTop_p1 = PToken("ThreePortsBigTop_p1", False, None, False)
  E_ThreePortsBigTop_p2 = PToken("ThreePortsBigTop_p2", False, None, False)
  E_ThreePortsBigTop_p3 = PToken("ThreePortsBigTop_p3", False, None, False)
  
  E_ThreePortsBigBottom_p1 = PToken("ThreePortsBigBottom_p1", False, None, False)
  E_ThreePortsBigBottom_p2 = PToken("ThreePortsBigBottom_p2", False, None, False)
  E_ThreePortsBigBottom_p3 = PToken("ThreePortsBigBottom_p3", False, None, False)
  
  E_TwoPortsLeftRight_p1 = PToken("TwoPortsLeftRight_p1", False, None, False)
  E_TwoPortsLeftRight_p2 = PToken("TwoPortsLeftRight_p2", False, None, False)
  
  E_TwoPortsTopBottom_p1 = PToken("TwoPortsTopBottom_p1", False, None, False)
  E_TwoPortsTopBottom_p2 = PToken("TwoPortsTopBottom_p2", False, None, False)
  
  E_aoSamples = PToken("aoSamples", False, None, False)
  E_aoDist = PToken("aoDist", False, None, False)
  E_aoBias = PToken("aoBias", False, None, False)
  E_aoAndIDL = PToken("aoAndIDL", False, None, False) # Poser 9
  E_productionFrame = PToken("productionFrame", False, None, False)
  
  E_autoScaleToView = PToken("autoScaleToView", False, None, False)
  E_resScale = PToken("resScale", False, None, False)
  E_reuseShadowMaps = PToken("reuseShadowMaps", False, None, False)
  E_useRenderer = PToken("useRenderer", False, None, False)
  E_hardwareShading = PToken("hardwareShading", False, None, False) # Poser 9
  E_hardwareShadingOptimization = PToken("hardwareShadingOptimization", False, None, False) # Poser 9
  E_hardwareShadows = PToken("hardwareShadows", False, None, False) # Poser 9
  E_previewDepthBufferOffset = PToken("previewDepthBufferOffset", False, None, False) # Poser 9
  E_previewTextureSize = PToken("previewTextureSize", False, None, False) # Poser 9
  E_previewTransLimitOn = PToken("previewTransLimitOn", False, None, False) # Poser 9
  E_transparencySort = PToken("transparencySort", False, None, False) # Poser 9
  E_previewTransLimit = PToken("previewTransLimit", False, None, False) # Poser 9
  
  E_doRealtimeAO = PToken("doRealtimeAO", False, None, False) # Poser 9
  E_realtimeAOBlurRadius = PToken("realtimeAOBlurRadius", False, None, False) # Poser 9
  E_realtimeAORes = PToken("realtimeAORes", False, None, False) # Poser 9
  E_realtimeAOStrength = PToken("realtimeAOStrength", False, None, False) # Poser 9
  E_realtimeShowBackfaces = PToken("realtimeShowBackfaces", False, None, False) # Poser 9
  E_sihouetteOutlineWidth = PToken("sihouetteOutlineWidth", False, None, False) # Poser 9
  
  E_wireframeLineEdge = PToken("wireframeLineEdge", False, None, False) # Poser 9
  E_toonEdgeLineWidth = PToken("toonEdgeLineWidth", False, None, False) # Poser 9
  
  E_giOnlyRender = PToken("giOnlyRender", False, None, False) # Poser 9
  E_giIntensity = PToken("giIntensity", False, None, False) # Poser 9
  E_giNumSamples = PToken("giNumSamples", False, None, False) # Poser 9
  E_giBounces = PToken("giBounces", False, None, False) # Poser 9
  E_giMaxError = PToken("giMaxError", False, None, False) # Poser 9
  E_giPassScale = PToken("giPassScale", False, None, False) # Poser 9
  E_useGI = PToken("useGI", False, None, False) # Poser 9
  
  E_useIrradianceCache = PToken("useIrradianceCache", False, None, False) # Poser 9
  E_hdriOutput = PToken("hdriOutput", False, None, False) # Poser 9
  E_gamma = PToken("gamma", False, None, False) # Poser 9
  E_useGamma = PToken("useGamma", False, None, False) # Poser 9
  
  E_toneMapper = PToken("toneMapper", False, None, False) # Poser 9
  E_toneGain = PToken("toneGain", False, None, False) # Poser 9
  E_toneExposure = PToken("toneExposure", False, None, False) # Poser 9
  E_subsurface = PToken("subsurface", False, None, False) # Poser 9
  
  E_settings = PToken("settings", True, 'StructuredAttribut', False)
  
  E_auto = PToken("auto", False, None, False)
  E_autoValue = PToken("autoValue", False, None, False)
  E_shadowRenderShadingRate = PToken("shadowRenderShadingRate", False, None, False)
  E_maxRayDepth = PToken("maxRayDepth", False, None, False)
  E_filterSize = PToken("filterSize", False, None, False)
  E_filterType = PToken("filterType", False, None, False)
  E_pixelSamples = PToken("pixelSamples", False, None, False)
  E_bucketSize = PToken("bucketSize", False, None, False)
  E_motionSamples = PToken("motionSamples", False, None, False)
  E_allowRayTracing = PToken("allowRayTracing", False, None, False)
  E_minShadingRate = PToken("minShadingRate", False, None, False)
  E_maxTextureRes = PToken("maxTextureRes", False, None, False)
  
  E_hairShadingRate = PToken("hairShadingRate", False, None, False)
  E_doShadows = PToken("doShadows", False, None, False)
  E_allowDisplacement = PToken("allowDisplacement", False, None, False)
  E_drawToonOutline = PToken("drawToonOutline", False, None, False)
  E_toonOutlineStyle = PToken("toonOutlineStyle", False, None, False)
  E_shadowOnlyRender = PToken("shadowOnlyRender", False, None, False)
  
  E_useP5renderer = PToken("useP5renderer", False, None, False)
  E_useDOF = PToken("useDOF", False, None, False)
  E_useSumAreaTables = PToken("useSumAreaTables", False, None, False)
  E_minDisplacementBounds = PToken("minDisplacementBounds", False, None, False)
  E_useTextureCache = PToken("useTextureCache", False, None, False)
  E_zipTextureCache = PToken("zipTextureCache", False, None, False)
  E_rayAccelerator = PToken("rayAccelerator", False, None, False)
  E_occlusionCulling = PToken("occlusionCulling", False, None, False)
  E_maxError = PToken("maxError", False, None, False)
  E_maxICSampleSize = PToken("maxICSampleSize", False, None, False)
  E_giStrength = PToken("giStrength", False, None, False)
  E_giSamples = PToken("giSamples", False, None, False)
  E_giDepth = PToken("giDepth", False, None, False)
  E_renderOptionsIndex = PToken("renderOptionsIndex", False, None, False)
  E_inputsCollapsed = PToken("inputsCollapsed", False, None, True)
  
  E_morphInfo = PToken("morphInfo", True, 'StructuredAttribut', False)
  E_morphPutty = PToken("morphPutty", True, 'StructuredAttribut', False)
  E_pin = PToken("pin", False, None, False)
  E_numWeights = PToken("numWeights", False, None, False)
  E_weights = PToken("weights", True, 'StructuredAttribut', False)
  E_w = PToken("w", False, None, False)
  E_caricatureFactor = PToken("caricatureFactor", False, None, False)
  
  E_textureInfo = PToken("textureInfo", True, 'StructuredAttribut', False)
  E_textureType = PToken("textureType", False, None, False)
  E_texturePhotoLineup = PToken("texturePhotoLineup", True, 'StructuredAttribut', False)
  
  E_frontImage = PToken("frontImage", True, 'FrontImage', False)
  E_loaded = PToken("loaded", False)
  E_cropRect = PToken("cropRect", False, None, False)
  E_numFeaturePoints = PToken("numFeaturePoints", False, None, False)
  E_featurePoints = PToken("featurePoints", True, 'StructuredAttribut', False)
  E_rotations = PToken("rotations", False, None, False)
  E_rotationsOffset = PToken("rotationsOffset", False, None, False)
  
  E_textureFile = PToken("textureFile", True, 'TextureFile', False)
  E_warped = PToken("warped", False)
  
  E_sideImage = PToken("sideImage", True, 'SideImage', False)
  
  E_bgShaderTree = PToken("bgShaderTree", True, 'StructuredAttribut', False)
  E_atmosShaderTree = PToken("atmosShaderTree", True, 'StructuredAttribut', False)
  E_faceRoom = PToken("faceRoom", True, 'StructuredAttribut', False)
  E_focusDistance = PToken("focusDistance", True, 'GenericTransform', False)
  E_fStop = PToken("fStop", True, 'GenericTransform', False)
  E_shutterOpen = PToken("shutterOpen", True, 'GenericTransform', False)
  E_shutterClose = PToken("shutterClose", True, 'GenericTransform', False)
  E_yon = PToken("yon", True, 'GenericTransform', False)
  E_rememberUndo = PToken("rememberUndo", False, None, False) # Poser 9
  
  E_depthMapStrength = PToken("depthMapStrength", True, 'GenericTransform', False)
  E_depthMapSize = PToken("depthMapSize", True, 'DepthMapSize', False)
  E_previewDepthMapSize = PToken("previewDepthMapSize", False, None, False) # Poser 9
  E_shadowSamples = PToken("shadowSamples", False, None, False) # Poser 9
  E_includeInOpenGL = PToken("includeInOpenGL", False, None, False) # Poser 9
  E_attenType = PToken("attenType", False, None, False) # Poser 9
  
  E_movieInfo = PToken("movieInfo", True, 'StructuredAttribut', False)
  E_light = PToken("light", True, 'Light', False)
  E_camera = PToken("camera", True, 'Camera', False)
  E_geomCustom = PToken("geomCustom", True, 'GeomCustom', False)
  E_alternateGeom = PToken("alternateGeom", True, 'AlternateGeom', False)
  E_geomChan = PToken("geomChan", True, 'GenericTransform', False)
  E_clothDynamicsParm = PToken("clothDynamicsParm", True, 'GenericTransform', False)
  E_channels = PToken("channels", True, 'StructuredAttribut', False)
  
  E_liteFalloffStart = PToken("liteFalloffStart", True, 'GenericTransform', False)
  E_liteFalloffEnd = PToken("liteFalloffEnd", True, 'GenericTransform', False)
  E_liteAttenStart = PToken("liteAttenStart", True, 'GenericTransform', False)
  E_liteAttenEnd = PToken("liteAttenEnd", True, 'GenericTransform', False)
  
  E_rotateX = PToken("rotateX", True, 'GenericTransform', False, 'xrot')
  E_rotateY = PToken("rotateY", True, 'GenericTransform', False, 'yrot')
  E_rotateZ = PToken("rotateZ", True, 'GenericTransform', False, 'zrot')
  E_keys = PToken("keys", True, 'Keys', False)
  E_kdIntensity = PToken("kdIntensity", True, 'GenericTransform', False)
  E_propagatingScale = PToken("propagatingScale", True, 'GenericTransform', False, 'scale')
  E_propagatingScaleX = PToken("propagatingScaleX", True, 'GenericTransform', False, 'xScale')
  E_propagatingScaleY = PToken("propagatingScaleY", True, 'GenericTransform', False, 'yScale')
  E_propagatingScaleZ = PToken("propagatingScaleZ", True, 'GenericTransform', False, 'zScale')
  E_translateX = PToken("translateX", True, 'GenericTransform', False, 'xtran')
  E_translateY = PToken("translateY", True, 'GenericTransform', False, 'ytran')
  E_translateZ = PToken("translateZ", True, 'GenericTransform', False, 'ztran')
  E_scale = PToken("scale", True, 'GenericTransform', False, 'Scale')
  E_scaleX = PToken("scaleX", True, 'Scale', False, 'xScale')
  E_scaleY = PToken("scaleY", True, 'Scale', False, 'yScale')
  E_scaleZ = PToken("scaleZ", True, 'Scale', False, 'zScale')
  E_visibility = PToken("visibility", True, 'GenericTransform', False)
  
  E_kdRed = PToken("kdRed", True, 'GenericTransform', False)
  E_kdGreen = PToken("kdGreen", True, 'GenericTransform', False)
  E_kdBlue = PToken("kdBlue", True, 'GenericTransform', False)
  E_Kd = PToken("Kd", False, None, False)
  E_Ks = PToken("Ks", False, None, False)
  E_Ns = PToken("Ns", False, None, False)
  E_antialiasing = PToken("antialiasing", False, None, False)
  E_textureStrength = PToken("textureStrength", False, None, False)
  E_objFileGeom = PToken("objFileGeom", False)
  E_objFile = PToken("objFile", False)
  E_useTexture = PToken("useTexture", False, None, False)
  E_useBump = PToken("useBump", False, None, False)
  E_castShadows = PToken("castShadows", False, None, False)
  E_renderOver = PToken("renderOver", False, None, False)
  E_toNewWindow = PToken("toNewWindow", False, None, False)
  
  E_newWinWidth = PToken("newWinWidth", False, None, False)
  E_newWinHeight = PToken("newWinHeight", False, None, False)
  E_newWinDPI = PToken("newWinDPI", False, None, False)
  E_setGeomHandlerOffset = PToken("setGeomHandlerOffset", False, None, False)
  
  E_focal = PToken("focal", True, 'GenericTransform', False)
  E_hither = PToken("hither", True, 'GenericTransform', False)
  
  E_camAutoFocal = PToken("camAutoFocal", True, 'GenericTransform', False)
  E_camAutoScale = PToken("camAutoScale", True, 'GenericTransform', False)
  E_camAutoCenterX = PToken("camAutoCenterX", True, 'GenericTransform', False)
  E_camAutoCenterY = PToken("camAutoCenterY", True, 'GenericTransform', False)
  E_camAutoCenterZ = PToken("camAutoCenterZ", True, 'GenericTransform', False)
  
  E_valueParm = PToken("valueParm", True, 'GenericTransform', False)
  E_xOffsetA = PToken("xOffsetA", True, 'GenericTransform', False, 'xOffsetA')
  E_yOffsetA = PToken("yOffsetA", True, 'GenericTransform', False, 'yOffsetA')
  E_zOffsetA = PToken("zOffsetA", True, 'GenericTransform', False, 'zOffsetA')
  E_xOffsetB = PToken("xOffsetB", True, 'GenericTransform', False, 'xTranB')
  E_yOffsetB = PToken("yOffsetB", True, 'GenericTransform', False, 'yTranB')
  E_zOffsetB = PToken("zOffsetB", True, 'GenericTransform', False, 'zTranB')
  
  E_taperX = PToken("taperX", True, 'GenericTransform', False)
  E_taperY = PToken("taperY", True, 'GenericTransform', False)
  E_taperZ = PToken("taperZ", True, 'GenericTransform', False)
  
  E_smoothScaleX = PToken("smoothScaleX", True, 'GenericTransform', False)
  E_smoothScaleY = PToken("smoothScaleY", True, 'GenericTransform', False)
  E_smoothScaleZ = PToken("smoothScaleZ", True, 'GenericTransform', False)
  E_smoothZones = PToken("smoothZones", False, None, False)
  
  E_deltas = PToken("deltas", True, 'Deltas', False)
  E_indexes = PToken("indexes", False)
  E_numbDeltas = PToken("numbDeltas", False)
  
  E_enabled = PToken("enabled", False)  # PoserV9 in targetGeom
  E_primaryParm = PToken("primaryParm", False, None, False) # PoserV9 in targetGeom
  E_useBulgeMapLeft = PToken("useBulgeMapLeft", False, None, False) # PoserV9 in targetGeom
  E_useBulgeMapRight = PToken("useBulgeMapRight", False, None, False) # PoserV9 in targetGeom
  E_usingGroups = PToken("usingGroups", False, None, False) # PoserV9 in targetGeom
  
  E_lineLength = PToken("lineLength", False, None, False)
  E_density = PToken("density", False, None, False)
  E_minRadius = PToken("minRadius", False, None, False)
  E_maxRadius = PToken("maxRadius", False, None, False)
  E_lineRandomness = PToken("lineRandomness", False, None, False)
  E_strokeHeadLength = PToken("strokeHeadLength", False, None, False)
  E_strokeTailLength = PToken("strokeTailLength", False, None, False)
  E_colorRandom = PToken("colorRandom", False, None, False)
  E_crossHatch = PToken("crossHatch", False, None, False)
  E_opacity = PToken("opacity", False, None, False)
  E_totalNormCutOff = PToken("totalNormCutOff", False, None, False)
  E_colorSegCutOff = PToken("colorSegCutOff", False, None, False)
  E_britenessSegCutOff = PToken("britenessSegCutOff", False, None, False)
  E_britenessLoSegCutOff = PToken("britenessLoSegCutOff", False, None, False)
  E_coloredLines = PToken("coloredLines", False, None, False)
  E_brushStyle = PToken("brushStyle", False, None, False)
  
  E_inkyParent = PToken("inkyParent", False, None, False)
  E_nonInkyParent = PToken("nonInkyParent", False, None, False)
  E_handGrasp = PToken("handGrasp", True, 'GenericTransform', False)
  E_thumbGrasp = PToken("thumbGrasp", True, 'GenericTransform', False)
  E_handSpread = PToken("handSpread", True, 'GenericTransform', False)
  
  E_figure = PToken("figure", True, 'FigureDescription', False)
  E_root = PToken("root", False, None, True)
  E_addChild = PToken("addChild", False, 'AddChildSA', False)
  E_skinType = PToken("skinType", False, None, False) # Poser 9
  
  E_inkyChain = PToken("inkyChain", True, 'InkyChain', False)
  E_addLink = PToken("addLink", False, None, False)
  E_goal = PToken("goal", False, None, False)
  E_linkWeight = PToken("linkWeight", False, None, False)
  E_linkParms = PToken("linkParms", False, 'LinkParmsSA', False)
  
  E_defaultPick = PToken("defaultPick", False, None, False)
  E_displayOn = PToken("displayOn", False, None, False)
  E_weld = PToken("weld", False, 'AddChildSA', False)
  
  E_doc = PToken("doc", True, 'DocDescription', False)
  E_dimensions = PToken("dimensions", False)
  E_screenPlace = PToken("screenPlace", False)
  E_useLimits = PToken("useLimits", False, None, False)
  E_headGuides = PToken("headGuides", False, None, False)
  E_horizon = PToken("horizon", False, None, False)
  E_vanishingLines = PToken("vanishingLines", False, None, False)
  E_hipShoulder = PToken("hipShoulder", False, None, False)
  E_drawBackfacing = PToken("drawBackfacing", False, None, False) # Poser 9
  E_groundDisplay = PToken("groundDisplay", False, None, False)
  E_depthCue = PToken("depthCue", False, None, False)
  E_boxesAlways = PToken("boxesAlways", False, None, False)
  E_bgPicOn = PToken("bgPicOn", False, None, False)
  E_handLockOn = PToken("handLockOn", False, None, False)
  E_loopInterpolation = PToken("loopInterpolation", False, None, False)
  E_quatInterpolation = PToken("quatInterpolation", False, None, False)
  E_doBalance = PToken("doBalance", False, None, False)
  E_fastTracking = PToken("fastTracking", False, None, False)
  E_groundShadows = PToken("groundShadows", False, None, False)
  E_bendBodies = PToken("bendBodies", False, None, False)
  E_fgColor = PToken("fgColor", False, None, False)
  E_bgColor = PToken("bgColor", False, None, False)
  E_shadowColor = PToken("shadowColor", False, None, False)
  E_paperTexture = PToken("paperTexture", False, None, False)
  E_addActor = PToken("addActor", False, None, False)
  E_pickActor = PToken("pickActor", False, None, False)
  E_addLight = PToken("addLight", False, None, False)
  E_addCamera = PToken("addCamera", False, None, False)
  E_rightCamera = PToken("rightCamera", False, None, False)
  E_leftCamera = PToken("leftCamera", False, None, False)
  E_posingCamera = PToken("posingCamera", False, None, False)
  E_faceCamera = PToken("faceCamera", False, None, False)
  E_rHandCamera = PToken("rHandCamera", False, None, False)
  E_lHandCamera = PToken("lHandCamera", False, None, False)
  E_topCamera = PToken("topCamera", False, None, False)
  E_frontCamera = PToken("frontCamera", False, None, False)
  E_mainCamera = PToken("mainCamera", False, None, False)
  E_auxCamera = PToken("auxCamera", False, None, False)
  E_dollyCamera = PToken("dollyCamera", False, None, False)
  E_useCamera = PToken("useCamera", False, None, False)
  
  E_illustrationParms = PToken("illustrationParms", True, 'StructuredAttribut', False)
  E_combineGradient = PToken("combineGradient", False, None, False)
  E_thresholdGradient = PToken("thresholdGradient", False, None, False)
  E_combineColor = PToken("combineColor", False, None, False)
  E_overBlack = PToken("overBlack", False, None, False)
  E_autoDensity = PToken("autoDensity", False, None, False)
  E_normalSegCutOff = PToken("normalSegCutOff", False, None, False)
  E_bgStyle = PToken("bgStyle", False, None, False)
  E_useUVspace = PToken("useUVspace", False, None, False)
  E_autoSpacing = PToken("autoSpacing", False, None, False)
  E_colorBlend = PToken("colorBlend", False, None, False)
  E_liteFactor1 = PToken("liteFactor1", False, None, False)
  E_liteFactor2 = PToken("liteFactor2", False, None, False)
  E_liteFactor3 = PToken("liteFactor3", False, None, False)
  E_rootActor = PToken("rootActor", False, None, False)
  
  E_fgStrokeParms = PToken("fgStrokeParms", True, 'StructuredAttribut', False)
  E_bgStrokeParms = PToken("bgStrokeParms", True, 'StructuredAttribut', False)
  E_edgeStrokeParms = PToken("edgeStrokeParms", True, 'StructuredAttribut', False)
  
  E_targetGeom = PToken("targetGeom", True, 'GenericTransform', False)
  E_pointAtParm = PToken("pointAtParm", True, 'GenericTransform', False)
  E_pointAtTarget = PToken("pointAtTarget", False, None, False)
  E_twistX = PToken("twistX", True, 'GenericTransform', False)
  E_twistY = PToken("twistY", True, 'GenericTransform', False)
  E_twistZ = PToken("twistZ", True, 'GenericTransform', False)
  E_jointX = PToken("jointX", True, 'GenericTransform', False)
  E_jointY = PToken("jointY", True, 'GenericTransform', False)
  E_jointZ = PToken("jointZ", True, 'GenericTransform', False)
  E_renderDefaults = PToken("renderDefaults", True, 'StructuredAttribut', False)
  E_curve = PToken("curve", True, 'GenericTransform', False)
  
  E_sphereZoneProp = PToken("sphereZoneProp", True, 'SphereZoneProp', False)
  E_baseProp = PToken("baseProp", True, 'BaseProp', False)
  E_magnetDeformerProp = PToken("magnetDeformerProp", True, 'MagnetDeformerProp', False)
  E_deformerPropChan = PToken("deformerPropChan", True, 'GenericTransform', False)
  E_deformerProp = PToken("deformerProp", False, None, False)
  E_deformTarget = PToken("deformTarget", False, None, False)
  E_addZone = PToken("addZone", False, None, False)
  E_newFalloffCurve = PToken("newFalloffCurve", False, None, False)
  E_falloffCpt = PToken("falloffCpt", False, None, False)
  E_buildSphere = PToken("buildSphere", False, None, False)
  E_endFalloffCurve = PToken("endFalloffCurve", False, None, False)
  E_transformPerVertex = PToken("transformPerVertex", False, None, False)
  
  E_curveProp = PToken("curveProp", True, 'CurveProp', False)
  E_numControlPts = PToken("numControlPts", False, None, False)
  E_pt = PToken("pt", False, None, False)
  E_calcCurve = PToken("calcCurve", False, None, False)
  
  E_waveDeformerProp = PToken("waveDeformerProp", True, 'WaveDeformerProp', False)
  E_wavePhase = PToken("wavePhase", True, 'GenericTransform', False)
  E_waveAmplitude = PToken("waveAmplitude", True, 'GenericTransform', False)
  E_waveLength = PToken("waveLength", True, 'GenericTransform', False)
  E_waveStretch = PToken("waveStretch", True, 'GenericTransform', False)
  E_waveAmplitudeNoise = PToken("waveAmplitudeNoise", True, 'GenericTransform', False)
  E_waveFrequency = PToken("waveFrequency", True, 'GenericTransform', False)
  E_waveSinusoidal = PToken("waveSinusoidal", True, 'GenericTransform', False)
  E_waveRectangular = PToken("waveRectangular", True, 'GenericTransform', False)
  E_waveTriangular = PToken("waveTriangular", True, 'GenericTransform', False)
  E_waveTurbulence = PToken("waveTurbulence", True, 'GenericTransform', False)
  E_waveOffset = PToken("waveOffset", True, 'GenericTransform', False)
  E_waveType = PToken("waveType", False, None, False)

  E_coneForceFieldProp = PToken("coneForceFieldProp", True, 'ConeForceFieldProp', False)
  E_forceAmplitude = PToken("forceAmplitude", True, 'GenericTransform', False)
  E_simpleFloat = PToken("simpleFloat", True, 'GenericTransform', False)
  E_subType = PToken("subType", False, None, False)


  E_otherActor = PToken("otherActor", False, None, False)
  E_matrixActor = PToken("matrixActor", False, None, False)
  E_center = PToken("center", False, None, False)
  E_startPt = PToken("startPt", False, None, False)
  E_endPt = PToken("endPt", False, None, False)
  E_flipped = PToken("flipped", False) # flipped may be followed by a boolean value.
  E_angles = PToken("angles", False, None, False)
  E_posBulgeLeft = PToken("posBulgeLeft", False, None, False)
  E_posBulgeRight = PToken("posBulgeRight", False, None, False)
  E_negBulgeLeft = PToken("negBulgeLeft", False, None, False)
  E_negBulgeRight = PToken("negBulgeRight", False, None, False)
  E_doBulge = PToken("doBulge", False, None, False)
  E_jointMult = PToken("jointMult", False, None, False)
  E_sphereMatsRaw = PToken("sphereMatsRaw", False, 'SphereMathsRaw', False)
  
  E_doShadow = PToken("doShadow", False, None, False)
  E_depthCamera = PToken("depthCamera", False, None, False)
  E_lightOn = PToken("lightOn", False, None, False)
  E_forceLimits = PToken("forceLimits", False)
  E_min = PToken("min", False)
  E_max = PToken("max", False)
  E_tMin = PToken("tMin", False, None, True)
  E_tMax = PToken("tMax", False, None, True)
  E_tExpo = PToken("tExpo", False, None, True)
  E_ksIgnoreTexture = PToken("ksIgnoreTexture", False, None, True)
  E_reflectThruLights = PToken("reflectThruLights", False, None, True)
  E_reflectThruKd = PToken("reflectThruKd", False, None, True)
  E_bumpStrength = PToken("bumpStrength", False, None, True)
  E_NsExponent = PToken("NsExponent", False, None, True)
  E_static = PToken("static", False, None, False)
  E_lightType = PToken("lightType", False, None, False)
  E_k = PToken("k", False, 'KSA', False)
  E_sl = PToken("sl", False, None, False)
  E_spl = PToken("spl", False, 'OffSA', False)
  E_valueOpDeltaAdd = PToken("valueOpDeltaAdd", False, 'ValueOpDelta', False)
  E_valueOpPlus = PToken("valueOpPlus", False, 'ValueOpDelta', False)
  E_valueOpMinus = PToken("valueOpMinus", False, 'ValueOpDelta', False)
  E_valueOpTimes = PToken("valueOpTimes", False, 'ValueOpDelta', False)
  E_valueOpDivideBy = PToken("valueOpDivideBy", False, 'ValueOpDelta', False)
  E_valueOpDivideInto = PToken("valueOpDivideInto", False, 'ValueOpDelta', False)
  E_valueOpKey = PToken("valueOpKey", False, 'ValueOpDelta', False)
  
  E_beginValueKeys = PToken("beginValueKeys", False, None, False)
  E_endValueKeys = PToken("endValueKeys", False, None, False)
  E_valueKey = PToken("valueKey", False, None, False)
  
  E_interpStyleLocked = PToken("interpStyleLocked", False) # 2015-10-30 : Converted to direct)
  E_cameraModel = PToken("cameraModel", False, None, False)
  E_staticValue = PToken("staticValue", False) # 2015-10-30 : Converted to direct )
  E_algorithm = PToken("algorithm", False, None, False)
  E_trackingScale = PToken("trackingScale", False)
  E_trackingScaleMult = PToken("trackingScaleMult", False, None, False)
  E_blendType = PToken("blendType", False, None, False)
  E_castsShadow = PToken("castsShadow", False)
  E_includeInDepthCue = PToken("includeInDepthCue", False)
  E_initValue = PToken("initValue", False)
  E_dynamicsLock = PToken("dynamicsLock", False)
  E_figureResFile = PToken("figureResFile", False, 'FigureResFile', False)
  E_hidden = PToken("hidden", False)
  E_actor = PToken("actor", True, 'PoserActor', False)
  E_controlProp = PToken("controlProp", True, 'ControlProp', False)
  E_prop = PToken("prop", True, 'PoserProp', False)
  E_material = PToken("material", True, 'PoserMaterial', False)
  E_presetMaterial = PToken("presetMaterial", True, 'PoserMaterial', False)
  E_numFrames = PToken("numFrames", False, None, False)
  E_loopStart = PToken("loopStart", False, None, False)
  E_loopEnd = PToken("loopEnd", False, None, False)
  E_currentFrame = PToken("currentFrame", False, None, False)
  E_framesPerSec = PToken("framesPerSec", False, None, False)
  E_outputWidth = PToken("outputWidth", False, None, False)
  E_outputHeight = PToken("outputHeight", False, None, False)
  E_parent = PToken("parent", False)
  E_outputFramesPerSec = PToken("outputFramesPerSec", False, None, False)
  E_outputStartFrame = PToken("outputStartFrame", False, None, False)
  E_outputEndFrame = PToken("outputEndFrame", False, None, False)
  E_useCustomFramesPerSec = PToken("useCustomFramesPerSec", False, None, False)
  E_renderStyle = PToken("renderStyle", False, None, False)
  E_outputType = PToken("outputType", False, None, False)
  E_res = PToken("res", False, None, False)
  E_movieName = PToken("movieName", False, None, False)
  E_loopMode = PToken("loopMode", False, None, False) # Poser 9
  E_bgMovieOn = PToken("bgMovieOn", False, None, False)
  E_number = PToken("number", False, None, False)
  E_name = PToken("name", False)
  E_geomResource = PToken("geomResource", False, None, False)
  E_locked = PToken("locked", False)
  
  E_0 = PToken("0", False, None, False) # Could be an error ?
  E_textureMap = PToken("textureMap", False, 'TextureMapSA', False)
  E_backgroundFile = PToken("backgroundFile", False, 'TextureMapSA', False)
  E_bumpMap = PToken("bumpMap", False, 'TextureMapSA', False)
  E_reflectionMap = PToken("reflectionMap", False, 'TextureMapSA', False)
  E_transparencyMap = PToken("transparencyMap", False, 'TextureMapSA', False)
  E_reflectionStrength = PToken("reflectionStrength", False, None, True)
  
  E_allowsBending = PToken("allowsBending", False, None, False)
  E_figureType = PToken("figureType", False, None, False)
  E_origFigureType = PToken("origFigureType", False, None, False)
  E_canonType = PToken("canonType", False, None, False)
  E_conforming = PToken("conforming", False, None, False)
  E_conformingTarget = PToken("conformingTarget", False)
  
  E_useZBuffer = PToken("useZBuffer", False)
  E_creaseAngle = PToken("creaseAngle", False)
  
  E_realTimeMode = PToken("realTimeMode", False, None, False)
  E_antiAlias = PToken("antiAlias", False, None, False)
  E_motionBlur = PToken("motionBlur", False, None, False)
  E_mBlurAmount = PToken("mBlurAmount", False, None, False)
  E_flashInfo = PToken("flashInfo", True, 'StructuredAttribut', False)
  E_numColors = PToken("numColors", False, None, False)
  E_customColors = PToken("customColors", False, None, False)
  E_color = PToken("color", False, None, False)
  
  E_quantOptions = PToken("quantOptions", False, None, False)
  E_quantFrame = PToken("quantFrame", False, None, False)
  E_overlapColors = PToken("overlapColors", False, None, False)
  E_outerLines = PToken("outerLines", False, None, False)
  E_innerLines = PToken("innerLines", False, None, False)
  E_lineWidth = PToken("lineWidth", False, None, False)
  E_autoPlay = PToken("autoPlay", False, None, False)
  
  E_storageOffset = PToken("storageOffset", False, None, False)
  E_geomHandlerGeom = PToken("geomHandlerGeom", False)
  E_endPoint = PToken("endPoint", False)
  E_origin = PToken("origin", False)
  E_orientation = PToken("orientation", False)
  E_on = PToken("on", False)
  E_off = PToken("off", False)
  E_sm = PToken("sm", False, 'OffSA', False)
  E_calcWeights = PToken("calcWeights", False, 'OffSA', False)
  E_KdColor = PToken("KdColor", False, None, True)
  E_KaColor = PToken("KaColor", False, None, True)
  E_KsColor = PToken("KsColor", False, None, True)
  E_ReflectionColor = PToken("ReflectionColor", False, None, True)
  E_TextureColor = PToken("TextureColor", False, None, True)
  
  E_port = PToken("port", False, None, False) # Use a Quad attribut
  E_d = PToken("d", False, None, False)
  E_readScript = PToken("readScript", False, None, False)
  # Use a Quad attribut   // Use a Quad attribut
  
  E_hairGrowthGroup = PToken("hairGrowthGroup", True, 'HairGrowthGroup', False)
  E_hairProp = PToken("hairProp", True, 'HairProp', False)
  E_hairDynamicsParm = PToken("hairDynamicsParm", True, 'GenericTransform', False)
  E_hairCacheFile = PToken("hairCacheFile", False, None, False)
  E_baseActor = PToken("baseActor", False, None, False)
  E_pullDown = PToken("pullDown", False, None, False)
  E_pullBack = PToken("pullBack", False, None, False)
  E_pullLeft = PToken("pullLeft", False, None, False)
  E_populationCount = PToken("populationCount", False, None, False)
  E_populationDensity = PToken("populationDensity", False, None, False)
  E_totalArea = PToken("totalArea", False, None, False)
  E_vertsPerHair = PToken("vertsPerHair", False, None, False)
  E_turbStrength = PToken("turbStrength", False, None, False)
  E_turbScale = PToken("turbScale", False, None, False)
  E_turbDelay = PToken("turbDelay", False, None, False)
  E_showPopulated = PToken("showPopulated", False, None, False)
  E_doCollisions = PToken("doCollisions", False, None, False)
  E_widthRange = PToken("widthRange", False, None, False)
  E_lengthRange = PToken("lengthRange", False, None, False)
  E_clumpiness = PToken("clumpiness", False, None, False)
  E_gravityK = PToken("gravityK", False, None, False)
  E_maxRotLenDelta = PToken("maxRotLenDelta", False, None, False)
  E_springK = PToken("springK", False, None, False)
  E_overallDamping = PToken("overallDamping", False, None, False)
  E_springDamping = PToken("springDamping", False, None, False)
  E_selfForce = PToken("selfForce", False, None, False)
  E_stiffExpo = PToken("stiffExpo", False, None, False)
  E_keepLengths = PToken("keepLengths", False, None, False)
  E_weightVertPct = PToken("weightVertPct", False, None, False)
  E_customData = PToken("customData", True, "CustomData", False)
  # PToken.E_frontImage = PoserToken("frontImage", True, FrontImage.__class__)
  # Not used Anymore E_data = PToken("data", False, None, False)
  E_weightMap = PToken("weightMap", True, "WeightMap", False) # Poser9
  E_Zones = PToken("zones", True, "Zones", False) # Poser9
  E_WeightMapZone = PToken("weightmapzone", True, "WeightMapZone", False) # Poser9
  E_sphereZone = PToken("spherezone", True, 'SphereZone', False)
  E_capsuleZone = PToken("capsulezone", True, 'CapsuleZone', False)
  E_active = PToken("active", False, None, False)
  E_math = PToken("math", False, None, False)
  E_mapname = PToken("mapname", False, None, False)
  E_outCapRadR = PToken("outCapRadR", False, None, False)
  E_outCapRadL = PToken("outCapRadL", False, None, False)
  E_outCylRadR = PToken("outCylRadR", False, None, False)
  E_outCylRadL = PToken("outCylRadL", False, None, False)
  E_inCapRadR = PToken("inCapRadR", False, None, False)
  E_inCapRadL = PToken("inCapRadL", False, None, False)
  E_inCylRadR = PToken("inCylRadR", False, None, False)
  E_inCylRadL = PToken("inCylRadL", False, None, False)
  E_outLenR = PToken("outLenR", False, None, False)
  E_outLenL = PToken("outLenL", False, None, False)
  E_inLenR = PToken("inLenR", False, None, False)
  E_inLenL = PToken("inLenL", False, None, False)
  E_matrices = PToken("matrices", False, 'SphereMathsRaw', False)
  
  # Channel initialization:
  #    PoserType, isStatic, min, max, initValue, order XYZ, ZXY, YZX, TrackingScale
  MINIMAL_CHANNELS = [ \
      # The Origin of the actor (i.e. Barycentre)
      [E_xOffsetA,   True,  -10.0, 10.0, 0.0,   0,   1,   2, 0.1], \
      [E_yOffsetA,   True,  -10.0, 10.0, 0.0,   1,   2,   0, 0.1], \
      [E_zOffsetA,   True,  -10.0, 10.0, 0.0,   2,   0,   1, 0.1], \

      [E_scale,      False,  0.1, 100.0, 1.0,   3,   3,   3, 0.01], \
      [E_scaleX,     False,  0.1, 100.0, 1.0,   4,   5,   6, 0.01], \
      [E_scaleY,     False,  0.1, 100.0, 1.0,   5,   6,   4, 0.01], \
      [E_scaleZ,     False,  0.1, 100.0, 1.0,   6,   4,   5, 0.01], \
      
      [E_rotateX,    False, -180.0,  180.0, 0.0,   7,   8,   9, 1.0], \
      [E_rotateY,    False, -180.0,  180.0, 0.0,   8,   9,   7, 1.0], \
      [E_rotateZ,    False, -180.0,  180.0, 0.0,   9,   7,   8, 1.0], \

      # The oppositte vector to Barycentre
      [E_xOffsetB,   True,  -10.0, 10.0, 0.0,  10,  11,  12, 0.1], \
      [E_yOffsetB,   True,  -10.0, 10.0, 0.0,  11,  12,  10, 0.1], \
      [E_zOffsetB,   True,  -10.0, 10.0, 0.0,  12,  10,  11, 0.1], \
      
      [E_translateX, False, -10.0, 10.0, 0.0,  13,  14,  15, 0.01], \
      [E_translateY, False, -10.0, 10.0, 0.0,  14,  15,  13, 0.01], \
      [E_translateZ, False, -10.0, 10.0, 0.0,  15,  13,  14, 0.01], \
      ]

  # Channel initialization:
  #    PoserType, isStatic, min, max, initValue,       order XYZ, ZXY, YZX
  MINIMAL_BODY_CHANNELS = [ \
      # The Origin of the actor (i.e. Barycentre)
      [E_xOffsetA,   True,  -1000.0, 1000.0,  0.0,   0,   1,   2, 0.1], \
      [E_yOffsetA,   True,  -1000.0, 1000.0, 0.74,   1,   2,   0, 0.1], \
      [E_zOffsetA,   True,  -1000.0, 1000.0,  0.0,   2,   0,   1, 0.1], \

      [E_propagatingScale,      False,     0.1, 1000.0, 1.0,   3,   3,   3, 0.01], \
      [E_propagatingScaleX,     False,     0.1, 1000.0, 1.0,   4,   5,   6, 0.01], \
      [E_propagatingScaleY,     False,     0.1, 1000.0, 1.0,   5,   6,   4, 0.01], \
      [E_propagatingScaleZ,     False,     0.1, 1000.0, 1.0,   6,   4,   5, 0.01], \
      
      [E_rotateX,    False,  -180.0,  180.0, 0.0,   7,   8,   9, 1.0], \
      [E_rotateY,    False,  -180.0,  180.0, 0.0,   8,   9,   7, 1.0], \
      [E_rotateZ,    False,  -180.0,  180.0, 0.0,   9,   7,   8, 1.0], \

      # The oppositte vector to Barycentre
      [E_xOffsetB,   True,  -1000.0, 1000.0, 0.0,  10,  11,  12, 0.1], \
      [E_yOffsetB,   True,  -1000.0, 1000.0, 0.0,  11,  12,  10, 0.1], \
      [E_zOffsetB,   True,  -1000.0, 1000.0, 0.0,  12,  10,  11, 0.1], \
      
      [E_translateX, False, -1000.0, 1000.0, 0.0,  13,  14,  15, 0.01], \
      [E_translateY, False, -1000.0, 1000.0, 0.0,  14,  15,  13, 0.01], \
      [E_translateZ, False, -1000.0, 1000.0, 0.0,  15,  13,  14, 0.01], \
      ]
  
  ORENTATIONS = { 'xyz':5, 'yzx':7, 'zxy':6 }
  
  SCALES  = (E_scale, E_scaleX, E_scaleY, E_scaleZ,\
            E_propagatingScale, E_propagatingScaleX, E_propagatingScaleY, E_propagatingScaleZ)
  
  ROT     = (E_rotateX, E_rotateY, E_rotateZ)
  TRANS   = (E_translateX, E_translateY, E_translateZ)
  OFFSETA = (E_xOffsetA, E_yOffsetA, E_zOffsetA)
  OFFSETB = (E_xOffsetB, E_yOffsetB, E_zOffsetB)

  @classmethod
  def setInitVect(clz, lst, props, v):
    ch = next(t for t in lst if t[0]==props[0])
    ch[4] = v.x
    ch = next(t for t in lst if t[0]==props[1])
    ch[4] = v.y
    ch = next(t for t in lst if t[0]==props[2])
    ch[4] = v.z

  @classmethod
  def getMinimalChannels(cls, axisOrder='xyz', isBody=False):
    '''
    Return the list of ordered channels to create either for an actor or 
    for the Root actor (usually BODY)
    '''
    # Get a copy of the default channels (we will modify the content)
    lstChan = copy.deepcopy(PoserToken.MINIMAL_BODY_CHANNELS if isBody else PoserToken.MINIMAL_CHANNELS )
    # Sort the Channel table according to actor orientation
    col = PoserToken.ORENTATIONS[axisOrder]
    lstChan.sort(key=lambda t: t[col])
    return lstChan


Lang = { getattr(PoserToken, ex).token : getattr(PoserToken, ex) for ex in dir(PoserToken) if ex[0:2]=='E_' }
LangList = [ getattr(PoserToken, ex) for ex in dir(PoserToken) if ex[0:2]=='E_' ]
LowerLangName = { getattr(PoserToken, ex):getattr(PoserToken, ex).token.lower()  for ex in dir(PoserToken) if ex[0:2]=='E_' }
LowerChanTypes = { getattr(PoserToken, ex).token.lower():getattr(PoserToken, ex)  for ex in dir(PoserToken) if ex[0:2]=='E_' and getattr(PoserToken, ex).clazz=='GenericTransform' }

# In Python: Implemented by a module level function in the highest 
# Module of this object model
def create(ptk, name):
  ''' Create a Structured or a Simple Attribut '''
  class_ = None
  classNameToLoad = ptk.clazz
  
  try:
    if not classNameToLoad:
      if ptk.isStructured:
        # Illegal case should not append
        raise(Exception("Token({0:s}) - null Class for a Structured".format(ptk.token)))      
      else:
        classNameToLoad = 'SimpleAttribut'
      
    class_ = PoserToken.LOADED_CLASS[classNameToLoad]
      
  except KeyError:
    # print("Token({0:s}) - Class to be loaded".format(ptk.token, ptk.clazz if ptk.clazz else ''))
    
    for modulename in PoserToken.MODULES:
      try:
        module = PoserToken.LOADED_MODULE[modulename]
      except KeyError:
        # Useless now: print("Loading:" + modulename)
        module = importlib.import_module(modulename)
        PoserToken.LOADED_MODULE.update( { modulename : module })
      
      try:
        class_ = getattr(module, classNameToLoad)
        PoserToken.LOADED_CLASS.update( { classNameToLoad : class_ })
        break
      except AttributeError:
        #print('Not the right module - Attribut Error on [{0:s}]:{1:s}'.format(ptk.token, ptk.clazz))
        pass
  
  if class_:    
    try:
      sa = class_()    
      sa.setName(name)
      sa.setPoserType(ptk)
    except:
      #exc_type, exc_value, exc_traceback = sys.exc_info() #ioex.printStackTrace()
      print('Instanciantion Error on [{0:s}]:{1:s}'.format(ptk.token, ptk.clazz if ptk.clazz else 'default' ))
      #print(repr(traceback.extract_tb(exc_traceback)))
      traceback.print_last()
  else:
    print('No module for [{0:s}]:{1:s}'.format(ptk.token, ptk.clazz))
    sa = None
      
  return sa


#  private static void readXLSLine(HSSFRow row, String[][] desttab, int rowid, int nbcols)
def __readXLSLine(sheet, desttab, rowid, nbcols):
  desttab.append([ ])

  for c in range(0, nbcols):
    value = None
    cell = sheet.cell(rowid, c)
    if not cell:
      print("CELL col(c)=" + str(c) + " VALUE=NULL")
    else:
      if cell.ctype==XL_CELL_TEXT:
        value = cell.value
      elif cell.ctype==XL_CELL_NUMBER:
        value = str(cell.value)
      elif cell.ctype==XL_CELL_EMPTY:
        value = None
      else:
        #XL_CELL_DATE:'xldate', 
        #XL_CELL_BOOLEAN:'bool', 
        #XL_CELL_ERROR:'error', 
        #XL_CELL_BLANK:'blank'}
        cell_type_str = ctype_text.get(cell.ctype, 'unknown type')
        print('Not Managed({0:d},{1:d}) : {2:s}'.format(rowid,c,cell_type_str))

    desttab[rowid].append(value)

# XL (xls) file reader. This method reads the first sheet and converts it into 
#  a string table
#  public static String[][] readXLSFile(String filename)
def readXLSFile(filename):
  book = xlrd.open_workbook(filename)
 
  if (not book) or (book.nsheets==0):
    return None

  # Just import the first sheet
  k = 0
  #HSSFSheet sheet = wb.getSheetAt(k);
  sheet = book.sheet_by_index(k)
  rows = sheet.nrows
  print("Sheet " + str(k) + " \"" + book.sheet_names()[k] + "\" has " + str(rows) + " row(s).")

  tabres = [ ] # new String[rows][];

  # The number of columns of the first row should be the size of the table
  row0 = sheet.row_values(0)
  nbcols = len(row0) #row0.getPhysicalNumberOfCells();

  __readXLSLine(sheet, tabres, 0, nbcols)

  for r in range(1, rows):
    row = sheet.row_values(r)
    if row:
      __readXLSLine(sheet, tabres, r, nbcols)

  return tabres
  

if __name__ == '__main__':
  for tk in LangList[1:]:
      attr = create(tk, 'toto')
      print('Object({0:s}) size={1:d}'.format(tk.token, sys.getsizeof(attr)))
      try:
        attr.write(sys.stdout,'')
      except Exception as e:
        if e.args[0]==PoserConst.C_EX_NOTCALL:
          attr.writeDef(sys.stdout, '')
          attr.writeData(sys.stdout,'')
        else:
          traceback.print_last()
        
        






