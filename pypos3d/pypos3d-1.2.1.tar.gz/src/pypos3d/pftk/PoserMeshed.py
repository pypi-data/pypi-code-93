# -*- coding: utf-8 -*-
# package: pftk.poser.kern
from collections import namedtuple
import logging
#import traceback, sys

from langutil import RemoveExt, C_FAIL, C_OK, C_ERROR, C_FILE_NOT_FOUND, UsageError
from pypos3d.wftk.WFBasic import C_BAD_DELTAINDEX, C_BAD_DELTACOUNT, C_NODELTA, Vector3d, Point3d
from pypos3d.wftk.PoserFileParser import PoserFileParser, ParsingErrorException
from pypos3d.pftk.PoserBasic import PoserConst, PoserToken, PToken, buildRelPath, getRealPath, index, TAS, WBoolLine, create, Lang
from pypos3d.pftk.GeomCustom import GeomCustom
from pypos3d.pftk.StructuredAttribut import StructuredAttribut, AlternateGeom, Deltas, ValueOpDelta, ChannelMorphStatus, \
    GenericTransform, ChannelMorphStatusList, findNewDelta, filterLength, calcMapping_KDTree, CustomData, DeltaPoint


#
# Options of the report algorithm
# 
ReportOption = namedtuple('ReportOption', ['translation', \
  'maxDist', # Value changed to fit a good sphere for DAZ characters \
  'enhance',\
  'boundingType',\
  'useVicinityLoop',\
  'alpha',\
  'minVectLen'])

ReportOption.__new__.__defaults__ = ( Vector3d(), 0.025, PoserConst.C_NO_ENHANCEMENT, PoserConst.C_NO_BOUNDING, True, 0.6, 0.001)

#  
class PoserMeshedObject(StructuredAttribut):
  ''' A PoserMeshedObject represents either a Prop, an Actor, a Camera, a Light or hairs in a Poser File. '''

  def __init__(self, Name=None):
    super(PoserMeshedObject, self).__init__(Name)

    #  Figure Object (may be null) 
    self._fig = None
    self._pmName = ''
    self._hidden = False
    self._visible = True #  On
    self._bend = True #  1
  
    #  Poser V9 attribut 
    self._animatableOrigin = False
    self._dynamicsLock = True #        0
  
    #  Poser V9 attribut 
    self._collisionDetection = False
    self._addToMenu = True #     1
    self._castsShadow = True #       1
    self._includeInDepthCue = True #         1
    self._useZBuffer = True #        1
    self._parent = None
    self._conformingTarget = None
    self._creaseAngle = 80.0
  
    #  Storage class of the mesh 
    self._geomType = PoserConst.GT_NONE
  
    #  Geom Groupname when geomType is GLOBAL_OBJFILE 
    self._geomGroupName = None
  
    #  Geom filename when geomType is LOCAL_OBJFILE, formated like Poser with ':' or ""  
    self._geomFileName = None
  
    #  Base Geometry
    self._geomCustom = None
    self._geom = None
  
    #  FigureResFile with a path (relative) 
    self._FRF = None
  
    #  Channels = Ordered Dictionary of Channels (only GenericTransform) - Never null 
    #  { ChannelName in lower char : GenericTransform }
    self._channels = { }
    #  Store the group presentation of channels 
    self._groups = None
  
    #  endPoint position 
    self._endPoint = None
  
    #  origin of the mesh 
    self._origin = None
  
    #  orientation of the mesh 
    self._orientation = None
    self._displayOrigin = False
    self._displayMode = None #  USEPARENT
    self._customMaterial = 0
    self._locked = False
    self._lstAltGeom = [ ]  # For Python, never null
    self._lstWMap = [ ] # List of Weight Maps (could be implemented with a ordered dict)

    self._customData = None # Contain a Dictionnary of 'key' : custData()
  
    #  Name + Mesh definition
    self._printName = None
    self._pf = None


  def setFigureResFile(self, frf):
    self._FRF = frf

  def getFigureResFile(self): return self._FRF

  def setPoserFile(self, pf):
    self._pf = pf

  def getPoserFile(self): return self._pf

  def getChannels(self): 
    ''' Return a View on the channels '''
    return self._channels.values()

  def getGeomType(self): return self._geomType

  def setGeomType(self, gt):
    self._geomType = gt

  def getGeomGroupName(self): return self._geomGroupName

  def setGeomGroupName(self, gn):
    self._geomGroupName = gn

  def getGeomFileName(self): return self._geomFileName

  def getGeomCustom(self): return self._geomCustom

  def setGeomFileName(self, fn):
    self._geomFileName = fn

  def setFigure(self, fig):
    self._fig = fig

  def getFigure(self): return self._fig


  def getMaterial(self, matName:'str', inCustom=False):
    ''' Return the named material (None if it does not exists).
    Limit search to CustomMaterial if inCustom=True
    '''
    mat = None
    
    if self.getCustomMaterial():
      mat = next( (m for m in self.getLstAttr() \
                  if (m.getPoserType()==PoserToken.E_material) and (matName=='*' or matName==m.getName())), None)
        
    if not mat and not inCustom and self.getFigure():
      mat = self.getFigure().getMaterial(matName)
          
    return mat

  # Return the list of alternate geom (never null in Python)
  def getAltGeomList(self): return self._lstAltGeom

  #    
  def addAltGeom(self, ag=None, altGeomFile=None, poserRootDir=None, pos=-1):
    ''' Add an alternate Geometry, if it does not already exists.
    Returns
    -------
    int
      C_OK, C_FAIL if the geometrie was already existing, C_ERROR in cas of file pb
    '''
    ret = C_OK
    if not ag:
      try:
        relPath = buildRelPath(poserRootDir, altGeomFile.getCanonicalPath())

        for agold in self.getAltGeomList():
          if agold.getGeomFileName()==relPath:
            return C_FAIL

        ag = AlternateGeom()
        ag.setPoserType(PoserToken.E_alternateGeom)
        n = RemoveExt(altGeomFile.getName())
        ag.setName(n)
        ag.setPrintName(n)
        ag.setGeomFileName(relPath)

      except IOError:
        ret = C_ERROR

   
    #  Add the AlternateGeom to the specified position
    if pos>=0:
      self._lstAltGeom.insert(pos, ag)
    else:
      self._lstAltGeom.append(ag)

    #  Fix internal indexes
    self.indexAltGeom()
    return ret

  def indexAltGeom(self): #  Fix internal indexes
    for i,a in enumerate(self._lstAltGeom):
      a.setNo(i)

  # 
  # Move an alternate Geometrie to an upper position
  # @return C_OK, C_FAIL if the geometrie was already existing, 
  #         PoserConst.C_ERROR in case data inconsistency
  #    
  def moveAltGeom(self, ag):
    ret = self.removeAltGeom(ag)
    if ret == C_OK:
      ret = self.addAltGeom(ag, ag.getNo())
    return ret

  # 
  # Remove an alternate Geometrie
  # @return C_OK, C_FAIL if the alt geometrie was not existing
  #    
  def removeAltGeom(self, ag):
    res = C_OK
    try:
      self.getAltGeomList().remove(ag)
      self.indexAltGeom()
    except:
      res = C_FAIL

    return res

  # 
  # Return the alternate geom channel. Null if none
  #    
  def getAltGeomChannel(self):
    return next( (gt for gt in self.getChannels() if gt.getPoserType()==PoserToken.E_geomChan), None)


  def getChannel(self, channelName):
    return self._channels.get(channelName.lower())
  
  # Find the GenericTransform that represents a TargetGeom and that has the
  # given "channelName"
  # @param channelName
  #          Channel Name to look for.
  # @return Null if not found.
  def getTargetGeom(self, channelName):
    gt = self._channels.get(channelName.lower())
    return gt if gt and (gt.getPoserType()==PoserToken.E_targetGeom) else None

  # 
  # Find the GenericTransform that represents the given "channelName" or PoserToken
  # @param channelName
  #          Channel Name to look for.
  # @return Null if not found.
  def getGenericTransform(self, channel:'Name Or PoserToken'):
    return next( (gt for gt in self.getChannels() if gt.getPoserType()==channel), None) if isinstance(channel, PToken) \
                  else self._channels.get(channel.lower())
    

  # 
  # Update or create a targetGeom and create a dependency to the body homonyme valueParm (if bodyLinked=true)
  #
  # @param channelName
  #    *          TargetGeom name
  # @param targetFigureName
  #    *          Referenced Figure Name
  # @param srcWG
  #    *          Concerned WaveGeom
  # @param lstNewDeltas
  #    *          List of deltas
  # @param bodyIdx
  #    *          Body index of the referenced figure (silly)
  #    
  #     updateOrCreate(String channelName, String targetFigureName, WaveGeom3d srcWG, lstNewDeltas, bodyIdx, bodyLinked)
  # def updateOrCreate_0(self, channelName, targetFigureName, srcWG, lstNewDeltas, bodyIdx):
  def updateOrCreate(self, channelName, targetFigureName, srcWG, setNewDeltas, bodyIdx, bodyLinked=True):
    gt = self._channels.get(channelName.lower())
    if not gt or (gt.getPoserType()!=PoserToken.E_targetGeom): #  Create the missing targetGeom
      if bodyLinked:
        gt = GenericTransform(PoserToken.E_targetGeom, channelName, targetFigureName, \
                              self.getFigure().getRoot() if targetFigureName else None,\
                              channelName if targetFigureName else None)
                              #None if not targetFigureName else "BODY:" + str(bodyIdx),\
                              #None if not targetFigureName else channelName)
      else:
        gt = GenericTransform(PoserToken.E_targetGeom, channelName)
        #  Do not add a prefix to printable name (old P4 Stuff)
        gt.setPrintName(channelName[3:] if (channelName.startswith("PBM") or channelName.startswith("FBM")) else channelName)
        gt.addKeyFrame(0, 0.0)
        #  Default keys are static=0
        gt.setInterpStyleLocked(0)

      self.addAttribut(gt)

    gt.getDeltas().deltaSet = setNewDeltas # [ delta for delta in lstNewDeltas ] )
    gt.setNumbDeltas(len(srcWG.coordList))
    return gt

  # 
  # Update or create a valueParm and initializes it
  # @param channelName ValueParm name
  def updateOrCreateVP(self, channelName, minVal=0.0, maxVal=1.0, applyLimits=True, isHidden=False):
    vp = self._channels.get(channelName.lower())
    if not vp or (vp.getPoserType()!=PoserToken.E_valueParm):
      #  Create the missing valueParm
      vp = GenericTransform(PoserToken.E_valueParm, channelName)
      #  Do not add a prefix to printable name (old P4 Stuff)
      vp.setPrintName(channelName[3:] if (channelName.startswith("PBM") or channelName.startswith("FBM")) else channelName)
      vp.addKeyFrame(0, 0.0)
      #  Default keys are static=0
      vp.setInterpStyleLocked(0)
      self.addAttribut(vp)

    vp.setMin(minVal)
    vp.setMax(maxVal)
    vp.setForceLimits(1 if applyLimits else 0)
    vp.setHidden(isHidden)
    return vp

  

  def createDefaultChannels(self, fp:'FigurePart'):
    ''' Create the 16 minimal channels for this actor and initialize them according to the 4 textual parameters.
    Textual parameters are supposed to be 'stripped'
    
    Parameters
    ----------
    fp: FigurePart
      Description of the actor.
      Used fields are: geomGroup, translation, rotation, orientation, center
    
    Return
    ------
    int : Return Code
    
    '''
    ret = C_OK
    
    try:
      AxisOrder, vOrient = fp.getOrientation()
      
      # Get a copy of the default channels (we will modify the content)
      lstChan = PoserToken.getMinimalChannels(AxisOrder, not fp.geomGroup)
      
      # Compute Actor's center
      bc = fp.getBaryCentre()
        
      # Set the Origin and Copy it in the static channels xOffset...
      self.setOrigin(bc)
      PoserToken.setInitVect(lstChan, PoserToken.OFFSETA, bc)
      PoserToken.setInitVect(lstChan, PoserToken.OFFSETB, Point3d(bc).neg())
  
      # Set Actor's orientation
      self.setOrientation(vOrient)
      
      # Manage Translation
      tr = fp.getTranslation(self.getFigure(), bc, actor=self)
      PoserToken.setInitVect(lstChan, PoserToken.TRANS, tr)
        
      # Manage Rotation
      vri = fp.getRotation()
      PoserToken.setInitVect(lstChan, PoserToken.ROT, vri)
        
      # Create the list of channels
      for gtdef in lstChan:    
        vp = GenericTransform.createFrom(gtdef)
        self.addAttribut(vp)

    except UsageError:
      #exc_type, exc_value, exc_tb = sys.exc_info()
      #traceback.print_exception(exc_type, exc_value, exc_tb)       
      ret = fp.ret

    return ret


  def CreateShaderNodeP(self, channelName, isHidden=False):
    snp = self.updateOrCreateVP(channelName, minVal=0.0, maxVal=1.0, applyLimits=True, isHidden=isHidden)
    snp.setPoserType(PoserToken.E_shaderNodeParm)
    return snp
  
  def CreateDeformerP(self, channelName, zoneName, deformerName, isHidden=False):
    snp = self.updateOrCreateVP(channelName, minVal=-100.0, maxVal=100.0, applyLimits=True, isHidden=isHidden)
    snp.setPoserType(PoserToken.E_deformerPropChan)

    # Create Deformer Channel special attributs
    az = create(PoserToken.E_addZone, PoserToken.E_addZone.token)
    az.setValue('1 ' + zoneName)
    snp.addAttribut(az)

    dp = create(PoserToken.E_deformerProp, PoserToken.E_deformerProp.token)
    dp.setValue(deformerName)
    snp.addAttribut(dp)
    return snp
  

  def getBaseMesh(self, poserRootDir):
    if self._geom == None:
      self._geom = self.getBaseGeomCustom(poserRootDir).getWaveGeom()
    return self._geom
 
  def printBaseGeomCustom(self):
    ''' Return a printable string representing the geometry '''
    s = PoserConst.GEOMPRINT[self._geomType]
    if self._geomType==PoserConst.GT_GLOBAL_OBJFILE:
      # geomHandlerGeom 13 hip
      s = PoserConst.GEOMPRINT[self._geomType] + '[' + self._FRF.getValue() + ', ' + self._geomGroupName + ']'
    elif self._geomType==PoserConst.GT_LOCAL_OBJFILE:
      # objFileGeom 0 0 :Runtime:Geometries:Marforno:Elaya:Lamp.obj          
      s = PoserConst.GEOMPRINT[self._geomType] + '[' + self._geomFileName + ']'
    else: # Alternate should not appear here
      s = PoserConst.GEOMPRINT[self._geomType]
    return s


  def initBaseGeomCustom(self, wg:'WaveGeom'):
    ''' Initialize the internal GeomCustom for a GT_LOCAL_OBJFILE '''
    if self._geomType==PoserConst.GT_LOCAL_OBJFILE:
      self._geomCustom = GeomCustom(src=wg)
  
  def getBaseGeomCustom(self, poserRootDir):
    ''' Return the Geometry definition of the object. Without applying any morph.
    Returns
    -------
    GeomCustom
      The GeomCustom object containing the WaveGeom3d
    '''
    if not self._geomCustom:
      if (self._geomType==PoserConst.GT_NONE) or (self._geomType==PoserConst.GT_INTERNAL):
        pass
      elif self._geomType==PoserConst.GT_GLOBAL_OBJFILE:
        # geomHandlerGeom 13 hip
        gc = self._FRF.getGeomCustom(poserRootDir)
        self._geomCustom = gc.extractSortGeom(self._geomGroupName, self._geomType) if gc else None

      elif self._geomType==PoserConst.GT_LOCAL_OBJFILE:
        # objFileGeom 0 0 :Runtime:Geometries:Marforno:Elaya:Lamp.obj          
        self._geomCustom = GeomCustom(getRealPath(poserRootDir, self._geomFileName))
      else:
        logging.warning("Unknown GeomType")

    return self._geomCustom

  # TODO: Take into account new installation type (Root = Runtime)
  def getMorphedMesh(self, poserRootDir, bodyIdx, lstch):
    ''' Return a mesh morphed with the selected channels.
    Parameters
    ----------
    poserRootDir : str
      Base location of Poser Installation.
    bodyIdx : int
      Index of the figure in the poser file.
      Useless for a global prop
    lstch : List of channels.
      ChannelMorphStatusList or set of channel names
    Returns
    -------
    GeomCustom
      Return null when the object has no geometry (BODY case for example)
    '''
    resgc = None
    basegc = None
    stm = lstch.getChannelSet() if isinstance(lstch, ChannelMorphStatusList) else lstch

    # Avoid the BaseGeomCustom Extraction
    if self._geomType == PoserConst.GT_GLOBAL_OBJFILE:
      basegc = self._FRF.getGeomCustom(poserRootDir)
      copygc = GeomCustom(basegc)

      copygc.findApplyDelta(bodyIdx, self._pf, stm)
      resgc = copygc.extractSortGeom(self._geomGroupName, self._geomType)
    else:
      basegc = self.getBaseGeomCustom(poserRootDir)
      resgc = GeomCustom(basegc)
      resgc.findApplyDelta(self, self._pf, stm)
    return resgc

  def setBaseMesh(self, poserRootDir, objFileName):
    self._geomType = PoserConst.GT_LOCAL_OBJFILE
    self._geomFileName = buildRelPath(poserRootDir, objFileName)

    # 20080502 : Force Geometry reload
    self._geomCustom = None
    self._printName = None

  def getPrintName(self): return self._pmName

  def setPrintName(self, pm):
    self._pmName = pm

  def setName(self, n):
    super(PoserMeshedObject, self).setName(n)
    self._printName = None

  def getDisplayName(self):
    if self._printName == None:
      if not self._geomCustom:
        if self.getName().startswith(PoserConst.C_BODY):
          objdef = "none" if (self._FRF == None) else self._FRF.getValue()
        else:
          objdef = self._geomGroupName if self._geomType==PoserConst.GT_GLOBAL_OBJFILE else self._geomFileName
      else:
        objdef = "internal : " + str(self._geomCustom.getWaveGeom().getCoordListLength()) + " vertex"

      self._printName = self.getName() + " [" + objdef if objdef else 'None' + "]"
    return self._printName

  def isVisible(self): return self._visible

  def setVisible(self, v):
    self._visible = v

  def isHidden(self): return self._hidden

  def setHidden(self, b):
    self._hidden = b

  def isBend(self): return self._bend

  def setBend(self, b):
    self._bend = b

  def isAddToMenu(self):
    return self._addToMenu

  def setAddToMenu(self, b):
    self._addToMenu = b

  def isDisplayOrigin(self):
    return self._displayOrigin

  def setDisplayOrigin(self, b):
    self._displayOrigin = b

  def setDisplayMode(self, d:'str'):
    self._displayMode = d

  def getDisplayMode(self):
    return self._displayMode

  def getCreaseAngle(self):
    return self._creaseAngle

  def setCreaseAngle(self, d):
    self._creaseAngle = d

  def getEndPoint(self):
    return self._endPoint

  def setEndPoint(self, v):
    self._endPoint = v

  def getParent(self):
    return self._parent

  def setParent(self, p):
    self._parent = p

  def getConformingTarget(self):
    return self._conformingTarget

  def setConformingTarget(self, target):
    self._conformingTarget = target

  def getCustomMaterial(self):
    return self._customMaterial

  def setCustomMaterial(self, v):
    self._customMaterial = v

  def isLocked(self):
    return self._locked

  def getOrigin(self):
    return self._origin

  def setOrigin(self, v):
    self._origin = v

  def getOrientation(self):
    return self._orientation

  def setOrientation(self, v):
    self._orientation = v
    
  # Customer Data Management
  def setCustomData(self, key, val, withPose=0, withMat=0):
    if not self._customData:
      self._customData = CustomData()
      
    self._customData.set(key, val, withPose, withMat)

  def getCustomData(self, key=None):
    ''' Return figure's custom data.
    if key is null : return the underlying dictionnary key:custData(val, withPose, withMath)
    if key is not null : return the stored cusData
    '''
    if not self._customData:
      return None
      
    return self._customData.get(key) if key else self._customData._data

  def hasCustomData(self):
    return self._customData!=None

  def setCastsShadow(self, b):
    self._castsShadow = b

  # Create in the current MeshedObject the best deltas for the list of morph
  # targets.
  # @param poserRootDir 	To find the .OBJ files
  # @param refMeshedObj         Figure that contains initial deltas
  # @param translation          Translation between original MeshedObject and its localization in
  # this.
  # @param maxDist              Maximal distance to take a point into account. If null, no maxDist
  # are applied.
  # @param setTargetMorph       List of morphs to create
  # @param alpha                Influence of distant point (less that one). alpha = 0.6 is usually
  # a good value.
  # @return C_OK when result is correct. C_ERROR when parameters are not correct.
  def createDeltas(self, poserRootDir, refObj, setTargetMorph, ropt):
    ''' Create for the current Actor the best deltas for the list of morph targets.
    This implementation starts with an extracted refFigure for optimisation purpose.

    Parameters
    ----------
    poserRootDir : str
      Root Dir of the installation (to find the .OBJ files)

    refFigure : str
       name of the figure that contains initial deltas

    setTargetMorph : set or list of str
      Morphs' names to create
      
    ropt : ReportOption
      Tuple of options for the report algorithm

    Returns
    -------
    int
      C_OK : Success
      C_ERROR : Error in parameters
      C_FILE_NOTFOUND : Some WaveFront files were not found
    '''
    ret = C_OK
    
    if not setTargetMorph:
      return C_ERROR

    lstCurGeom = [ self.getBaseGeomCustom(poserRootDir), ]
    
    if isinstance(refObj, PoserMeshedObject):
      # Extract and Sort GeomCustom to get single numbered groups
      lstRefGeom = [ refObj.getBaseGeomCustom(poserRootDir), ]
    else: # refObj should be a Figure instance
      refPoserObject = refObj.getPoserFile()
      lstRefGeom = refPoserObject.extractAll(poserRootDir, refObj.getBodyIndex(), None)

    if not min( [ gc.isValid() for gc in lstCurGeom+lstRefGeom ] ):
      return C_FILE_NOT_FOUND

    for srcGC in lstCurGeom:
      srcWG = srcGC.getWaveGeom()

      tabMapping = calcMapping_KDTree(srcWG, lstRefGeom, ropt.translation, ropt.maxDist)
      
      self.findReportDeltas(refObj, srcGC, srcWG, tabMapping, setTargetMorph, ropt)

    return ret


  def findReportDeltas(self, refObj, srcGC, srcWG, tabMapping, setTargetMorph, ropt, checkBODYParm=False):
    ''' Optimization function. (Would be protected in Java)
    '''
    # Foreach morph target ==> Exploit tabMapping for srcGC
    for channelName in setTargetMorph:
      logging.info("Creating deltas for %s.%s", srcGC.getName(), channelName)
      setFoundDeltas = findNewDelta(tabMapping, refObj, channelName)
      setNewDeltas = { }

      # Local Enhancement
      Deltas.enhancement(srcWG, setFoundDeltas, setNewDeltas, ropt.enhance, ropt.boundingType, ropt.useVicinityLoop, ropt.alpha)
      if len(setNewDeltas) > 0:
        # Filter the result list to remove too short vectors
        lstFinalDeltas = filterLength(setNewDeltas, ropt.minVectLen)

        self.updateOrCreate(channelName, None, srcWG, lstFinalDeltas, 0)

        if checkBODYParm:
          self.getFigure().updateOrCreateValueParm(channelName)
          
        logging.info("Deltas created for %s.%s : %d", srcGC.getName(), channelName, len(lstFinalDeltas))
      else:
        logging.warn("No Delta created for %s.%s", srcGC.getName(), channelName )



  # Create in the current meshed object the best deltas for the alternate geoms for the list of morph targets.
  # @param poserRootDir    To find the .OBJ files
  # @param refMeshedObj    Figure that contains initial deltas
  # @param ropt            Report options
  # @param setTargetMorph  List of morphs to create
  # @param otherRefObjs     A list of PoserMeshedObject where to find the morphs.
  #                        Useful when the alternate geometry has been created with some fusions
  # @return    C_OK when result is correct. C_ERROR when parameters are not correct.
  def createAlternateDeltas(self, poserRootDir, setTargetMorph, ropt, otherRefObjs=None):
    ret = C_OK
    
    if not setTargetMorph:
      return C_ERROR

    curPoserObject = self.getPoserFile()
    refMeshedObj = self

    # Find the actor      
    srcActor = curPoserObject.findActor(self.getName())

    # Extract and load alternate geoms
    lstAltG = self.getAltGeomList()
    if len(lstAltG) > 0:
      lstCurGeom = [ ]
      # Table of alternate geometry usage valueParm indicators

      # Find the geomChan Channel (should always exists if the list of alt geom is not empty)
      geomChan = self.getAltGeomChannel() # channelsAttr.findAttribut(PoserToken.E_geomChan)
      
      altno = 1
      for altg in lstAltG:
        rfn = altg.getGeomFileName()
        gc = GeomCustom(getRealPath(poserRootDir, rfn))
        lstCurGeom.append(gc)

      lstRefGeom = [ refMeshedObj.getBaseGeomCustom(poserRootDir), ]
      if otherRefObjs:        
        lstRefGeom += [ ro.getBaseGeomCustom(poserRootDir) for ro in otherRefObjs ]

      # Check File error
      if not min( [ not gc or gc.isValid() for gc in lstCurGeom+lstRefGeom ] ):
        return C_FILE_NOT_FOUND

      altno = 1
      for srcGC in lstCurGeom:
        srcWG = srcGC.getWaveGeom()

        # tabMapping = PtMapping.calcMapping(srcWG, lstRefGeom, ropt.translation, ropt.maxDist)
        tabMapping = calcMapping_KDTree(srcWG, lstRefGeom, ropt.translation, ropt.maxDist)

        # Foreach morph target ==> Exploit tabMapping for srcGC
        for channelName in setTargetMorph:
          altChannelName = channelName + "_Alt" + str(altno)
          logging.info("Creating deltas for " + srcGC.getName() + "." + channelName + " into:" + altChannelName)
          setFoundDeltas = findNewDelta(tabMapping, refMeshedObj, channelName)
          
          # Search accros other Reference actors
          if otherRefObjs:
            for ro in otherRefObjs:
              sfd = findNewDelta(tabMapping, ro, channelName)
              setFoundDeltas.update(sfd)
            
          setNewDeltas = { }

          # Local Enhancement
          Deltas.enhancement(srcWG, setFoundDeltas, setNewDeltas, ropt.enhance, ropt.boundingType, ropt.useVicinityLoop, ropt.alpha)
          if len(setNewDeltas) > 0:
            # Filter the result list to remove too short vectors
            setFinalDeltas = filterLength(setNewDeltas, ropt.minVectLen)

            # Create or update the channel list
            destGT = self.updateOrCreate(altChannelName, self.getName(), srcWG, setFinalDeltas, srcActor.getFigure().getBodyIndex(), False)
            
            vod = ValueOpDelta(PoserToken.E_valueOpKey, srcActor.getFigure().getRefName(), srcActor.getName(), geomChan.getName(), 0.0)

            for ia in range(1, len(lstAltG)+1):
              vod.addValueKey(ia, 1.0 if (ia == altno) else 0.0)
                       
            destGT.addVOD(vod)

            # Multiply by the value of the copied channel
            vodMul = ValueOpDelta(PoserToken.E_valueOpTimes, srcActor.getFigure().getRefName(), srcActor.getName(), channelName, 0.0)
            destGT.addVOD(vodMul)

            destGT.setHidden(True)
            logging.info("Deltas created for %s.%s : %d", srcGC.getName(), channelName, len(setFinalDeltas))
        altno += 1

    return ret

  # TODO: Add logging info
  def createMorph(self, poserRootDir, morphGeomGroup, targetMorphName, masterMorphName=None, altGeomNo=0, minVectLen=0.0):
    '''Create a morph for the current PoserMeshedObject, based on an alternate geom.
    The morph applies to the base geometry or to an alternate one.
    Geometries shall have the same number of vertex (indexes matters)
    
    Parameters
    ----------
      poserRootDir : str
        Path to the poser data installation. (Usually c:\...\Poser9) 
      morphGeomGroup : GeomGroup
        GeomGroup containing the morphed (translated) vertex
      targetMorphName : str
        Name of the local Dial (channel) to activate the morph at actor/prop level
      masterMorphName : str, optional, default None
        When set, defines the name of a master dial (channel) to drive the local one.
        if it does not exist at Root (BODY) level, it will be created
      altGeomNo : int, optional, default0
        Index of the alternate geometry for the morph. If null (0), the default
        geometry of the actor/prop is chosen
      minVectLen : float, optional, default 0.0
        Minimal length of morph vectors. None if null (0.0)
    Returns
    -------
    int
      C_OK : Success
      C_FAIL : Bad index for the alternate geometry
      C_BAD_DELTAINDEX : Number of vertex differ between actor/prop and geomgroup
      C_FILE_NOTFOUND : Some Wavefront file not found
    '''
    ret = C_OK
    curPoserObject = self.getPoserFile()
    
    # Find the actor      
    srcActor = curPoserObject.findActor(self.getName())

    # Extract and load alternate geoms
    if altGeomNo>0:
      lstAltG = self.getAltGeomList()
      if altGeomNo>len(lstAltG):
        return C_FAIL
      
      # Find the geomChan Channel (should always exists if the list of alt geom is not empty)
      geomChan = self.getAltGeomChannel() # channelsAttr.findAttribut(PoserToken.E_geomChan)
      
      rfn = lstAltG[altGeomNo-1].getGeomFileName()
      realpath = getRealPath(poserRootDir, rfn)
      refGeom = GeomCustom(realpath)
      if not refGeom or not refGeom.isValid():
        logging.warning('Alternate Geometry file not found:%s for %s', realpath, self.getName())
        return C_FILE_NOT_FOUND
      
      refWG = refGeom.getWaveGeom()
      refGeomGrp = refWG.getGroups()[0]
    else: # Use base geom
      geomChan = None
      refGeom = self.getBaseGeomCustom(poserRootDir)
      if not refGeom or not refGeom.isValid():
        logging.warning('Geometry not found for:%s', self.getName())
        return C_FILE_NOT_FOUND
      refWG = refGeom.getWaveGeom()

      # Need an extract and sort to get the rigth indexes
      refGeomGrp = refWG.extractSortGeom(refWG.groups[0].getName())
      
    if len(refGeomGrp.coordList)!=len(morphGeomGroup.coordList):
      return C_BAD_DELTAINDEX

    logging.info("Creating morph for %s.%s", self.getName(), targetMorphName)

    # Create the dictionnary of non null deltas
    minsq = minVectLen*minVectLen
    setNewDeltas={}
    for nopt,vx in enumerate(refGeomGrp.coordList):
      movedVx = morphGeomGroup.coordList[nopt]
      dp = DeltaPoint(nopt, movedVx.x - vx.x, movedVx.y - vx.y, movedVx.z - vx.z)
      if dp.norme2()>minsq:
        setNewDeltas[dp.noPt] = dp

    # Create or Update the TargetGeom
    
    # Link to selected alternate geom if any
    if geomChan:      
      destGT = self.updateOrCreateVP(targetMorphName, minVal=0.0, maxVal=1.0, applyLimits=False)

      targetGT = self.updateOrCreate(targetMorphName + "_Alt" + str(altGeomNo), self.getName(), refGeomGrp, setNewDeltas, srcActor.getFigure().getBodyIndex(), False)
      
      vod = ValueOpDelta(PoserToken.E_valueOpKey, srcActor.getFigure().getRefName(), srcActor.getName(), geomChan.getName(), 0.0)

      for ia in range(1, len(lstAltG)+1):
        vod.addValueKey(ia, 1.0 if (ia == altGeomNo) else 0.0)
                       
      targetGT.addVOD(vod)
      
      # Multiply by the value of the master channel
      vodMul = ValueOpDelta(PoserToken.E_valueOpTimes, srcActor.getFigure().getRefName(), srcActor.getName(), targetMorphName, 0.0)
      targetGT.addVOD(vodMul)

      targetGT.setHidden(True)  
    else:
      destGT = self.updateOrCreate(targetMorphName, self.getName(), refGeomGrp, setNewDeltas, srcActor.getFigure().getBodyIndex(), False)    
    
    # If a masterMorphName is given: Create it at BODY level then link the destGT to it
    if masterMorphName:
      bodyAct = self.getFigure().getRootActor()
      bodyAct.updateOrCreateVP(masterMorphName, minVal=0.0, maxVal=1.0, applyLimits=False)
      vod = ValueOpDelta(PoserToken.E_valueOpDeltaAdd, srcActor.getFigure().getRefName(), bodyAct.getName(), masterMorphName, 1.0)
      destGT.addVOD(vod)
    
    logging.info("Morph created for %s.%s : %d", refGeomGrp.getName(), targetMorphName, len(setNewDeltas))

    return ret
    
  # 
  # Return the delta for a given channel and a given vertex no.
  # @param channelName
  #          Channel Name (targetGeom name in fact)
  # @param refNo
  #          Index of the vertex in the geometry of the meshed object (Actor or
  #         Prop)
  # @return Delta Object (Aka 3D vector)
  def findDelta(self, channelName, refNo):
    gt = self.getTargetGeom(channelName)
    return gt.getDeltas().deltaSet.get(refNo) if gt and gt.getDeltas() else None
          

  def deleteGTReference(self, grp, gt):
    #  FIX 2019-05-05 : Some (old) character may have not group
    if grp!=None:
      # grp._lstAttr[:] = [ po for po in grp.getLstAttr() if (po.getPoserType()!=PoserToken.E_parmNode) or (gt.getName()==po.getValue()) ]
      # grp.getLstAttr().remove(po)
      for po in grp.getLstAttr():
        if po.getPoserType()==PoserToken.E_parmNode:
          if gt.getName()==po.getValue():
            grp.getLstAttr().remove(po)
            
        elif po.getPoserType()==PoserToken.E_groupNode:
          #  Recursive, because a group may contain another group
          self.deleteGTReference(po, gt)

  def deleteChannel(self, gt):
    '''Delete the given channel.
    
    Parameter:
    ----------
    gt : str or PoserGenericTransform
      The channel to delete.    
    Returns
    -------
    int : C_OK when work done, C_FAIL if string input not found

    '''
    if isinstance(gt, str):
      # Find the channel
      gt = self._channels.get(gt.lower())
      if not gt:
        return C_FAIL
      
    del self._channels[gt.getName().lower()]
    self.deleteGTReference(self._groups, gt)
    return C_OK

  # 
  # Compute the first level list of channels that point to the given channel argument.
  # @param channel Reference channel
  # @param setIn  Set to be extended and returned. Created if null. 
  #               Does not contain duplicate channel.
  def getChannelDescendant(self, channel, setIn):
    implst = setIn if setIn else set()
    cn = channel.getName()
    gn = channel.getPoserMeshedObject().getName()
    for gt in self.getChannels():
      for vop in gt.getVOD():
        if (gn==vop.getGroupName()) and (cn==vop.getChannelName()) and (not gt in implst):
          implst.add(gt)
          break

    return implst
  
  def getWeldParent(self):
    return self.getFigure().getWeldParent(self.getName())


  # Test if the deltas are consistent with the geometry.
  # @param gt
  # @return    C_OK : No problem
  #            C_NODELTA : No Deltas
  #            C_ERROR : Geometry in read error
  def checkChannelDelta(self, gt, poserRootDir):
    res = C_OK
    if gt.ishasDeltas():
      gc = self.getBaseGeomCustom(poserRootDir)
      if gc and (gc.isValid()):
        dlt = gt.getDeltas()
        vertexSize = gc.getWaveGeom().getCoordListLength()
        if vertexSize == gt.getNumbDeltas():
          for dp in dlt.deltaSet.values():
            if dp.noPt >= vertexSize:
              return C_BAD_DELTAINDEX
        else:
          res = C_BAD_DELTACOUNT
      else:
        res = C_ERROR
    else:
      res = C_NODELTA
    return res

  # Change the name of referenced part (actor, prop, hairProp, controlProp)  
  # @param oldPartName
  # @param newPartName
  def changeReference(self, oldPartName, newPartName, changeRefToBODY=True):
    self._parent = TAS(self._parent, oldPartName, newPartName)
    self._conformingTarget = TAS(self._conformingTarget, oldPartName, newPartName)
    for gt in self.getChannels():
      gt.changeReference(oldPartName, newPartName, changeRefToBODY=changeRefToBODY)

  def setDirect(self, tokenID, val):
    if tokenID==PoserToken.E_name:
      self._pmName = val
    elif tokenID==PoserToken.E_on:
      self._visible = True
    elif tokenID==PoserToken.E_off:
      self._visible = False
    elif tokenID==PoserToken.E_hidden:
      self._hidden = val.startswith("1")
    elif tokenID==PoserToken.E_bend:
      self._bend = val.startswith("1")
    elif tokenID==PoserToken.E_animatableOrigin:
      self._animatableOrigin = val.startswith("1")
    elif tokenID==PoserToken.E_dynamicsLock:
      self._dynamicsLock = val.startswith("1")
    elif tokenID==PoserToken.E_collisionDetection:
      self._collisionDetection = val.startswith("1")
    elif tokenID==PoserToken.E_addToMenu:
      self._addToMenu = val.startswith("1")
    elif tokenID==PoserToken.E_castsShadow:
      self._castsShadow = val.startswith("1")
    elif tokenID==PoserToken.E_includeInDepthCue:
      self._includeInDepthCue = val.startswith("1")
    elif tokenID==PoserToken.E_useZBuffer:
      self._useZBuffer = val.startswith("1")
    elif tokenID==PoserToken.E_parent:
      self._parent = val
    elif tokenID==PoserToken.E_conformingTarget:
      self._conformingTarget = val
    elif tokenID==PoserToken.E_creaseAngle:
      self._creaseAngle = float(val)

    elif tokenID==PoserToken.E_geomHandlerGeom:
      self._geomType = PoserConst.GT_GLOBAL_OBJFILE
      tmps = val.strip()
      bci = tmps.rfind(' ');
      self._geomGroupName = tmps[(bci + 1):]

    elif tokenID==PoserToken.E_objFileGeom:
      self._geomType = PoserConst.GT_LOCAL_OBJFILE

      bci1 = 0

      if val.startswith(PoserConst.S_LOCAL_OBJFILE_PFX):
        bci1 = len(PoserConst.S_LOCAL_OBJFILE_PFX) -1
      else:
        bci1 = val.rfind(' ')

      self._geomFileName = val[(bci1 + 1):]

    elif tokenID==PoserToken.E_endPoint:
      self._endPoint = Vector3d.parseVector3d(val)

    elif tokenID==PoserToken.E_origin:
      self._origin = Vector3d.parseVector3d(val)

    elif tokenID==PoserToken.E_orientation:
      self._orientation = Vector3d.parseVector3d(val)

    elif tokenID==PoserToken.E_displayOrigin:
      self._displayOrigin = val.startswith("1")

    elif tokenID==PoserToken.E_locked:
      self._locked = val.startswith("1")

    elif tokenID==PoserToken.E_customMaterial:
      self._customMaterial = int(val)

    elif tokenID==PoserToken.E_displayMode:
      self._displayMode = val

    else:
      logging.warning("Unexpected Direct: (%s) %s", tokenID.token, val)

  
  # Overload add Attribut
  def addAttribut(self, po):
    if isinstance(po, GenericTransform):
      try:
        self._channels[po.getName().lower()]
        logging.warning("Duplicate Channel Definition [%s] in [%s] (overloaded)", po.getName(), self.getName())
      except KeyError:
        pass

      self._channels[po.getName().lower()] = po
      po.setPoserMeshedObject(self)
      
    elif po.getPoserType()==PoserToken.E_geomCustom:
      self._geomCustom = po
      self._geomType = PoserConst.GT_INTERNAL

    elif po.getPoserType()==PoserToken.E_storageOffset:
      # FIX20090607 : Storage Offset seen : shall not be kept in attribute list.
      return

    elif po.getPoserType()==PoserToken.E_alternateGeom:
      self._lstAltGeom.append(po)
      po.setNo(len(self._lstAltGeom))

    elif po.getPoserType()==PoserToken.E_weightMap:
      self._lstWMap.append(po)

    elif po.getPoserType()==PoserToken.E_groups:
      self._groups = po
      
    elif po.getPoserType()==PoserToken.E_readScript:
      #  TODO : Read Channel Definition Script
      logging.error("No Management rule for %s [%s]", po.getName(), po.getPoserType().token)
      
    elif po.getPoserType()==PoserToken.E_customData:
      self._customData = po

    else:
      super(PoserMeshedObject, self).addAttribut(po)

  # Specific reader to take into account Channels class removal
  #
  def read(self, st):
    inchannels = False

    while True:
      code,cn,rw = st.getLine()
      if code==PoserFileParser.TT_WORD: # Other keyword found
        try:
          vc = Lang[cn]
          #  Known word
          if vc.isStructured:
            if vc==PoserToken.E_channels:
              # Read the Openning bracket and jump to next line
              ncode,lw,rw = st.getLine()
              if ncode==PoserFileParser.TT_LEFTBACKET:
                inchannels = True
                continue
              else: # Syntax error
                logging.warning("Line[%s] - read %s instead of '{'", st.lineno(), lw)
                raise ParsingErrorException()

            sta = create(vc, rw)
            self.addAttribut(sta)
            #  Read the opening bracket
            code,cn,rw = st.getLine()
            if code==PoserFileParser.TT_LEFTBACKET:
              sta.read(st)
            else:
              if sta.isAmbi():
                st.pushBack()
              else:
                logging.warning("Line[%s]:  '{' is missing for %s", st.lineno(), cn)
                raise ParsingErrorException()
          else:
            if vc.isDirect:
              self.setDirect(vc, rw)
            else:
              sa = create(vc, cn)
              #  Read before add
              sa.read(st, rw)
              self.addAttribut(sa)
        except KeyError:  #  Mot inconnu
          logging.info("Line[%s] - Unknown word:%s", st.lineno(), cn)

      elif code==PoserFileParser.TT_RIGHTBRACKET:
        if inchannels:
          inchannels = False
        else:
          break
      elif code==PoserFileParser.TT_EOF:
        break
      else:
        logging.warning("Line[%s] - Not Accepted :%s", st.lineno(), cn)
        raise ParsingErrorException()

    # End of read

  # Write the definition part of the meshed object.
  def writeDef(self, fw, pfx):
    nextPfx = pfx + "\t"
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n{nextPfx}{{\n")
    if self._geomType==PoserConst.GT_NONE:
      fw.write('\n')
    elif self._geomType==PoserConst.GT_GLOBAL_OBJFILE:
      fw.write(f"{nextPfx}storageOffset 0 0 0\n")
      fw.write(f"{nextPfx}geomHandlerGeom 13 {self._geomGroupName}\n")
    elif self._geomType==PoserConst.GT_LOCAL_OBJFILE:
      fw.write(f"{nextPfx}storageOffset 0 0.3487 0\n")
      fw.write(f"{nextPfx}objFileGeom 0 0 {self._geomFileName}\n")
    elif self._geomType==PoserConst.GT_INTERNAL:
      self._geomCustom.write(fw, nextPfx)
    else:
      logging.warning("Unknown GeomType at write")
    fw.write(f"{nextPfx}}}\n")

  # Write the Data part of the meshed object.
  def writeData(self, fw, pfx):
    nextPfx = pfx + "\t"
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n{nextPfx}{{\n")
    fw.write(f"{nextPfx}name {self._pmName}\n")
    fw.write(f"{nextPfx}{'on' if self._visible else 'off'}\n")
    WBoolLine(fw, nextPfx, "bend", self._bend)
    
    if self.getPoserFile().isVersion(PoserConst.POSER_V9):
      WBoolLine(fw, nextPfx, "animatableOrigin", self._animatableOrigin)

    WBoolLine(fw, nextPfx, "dynamicsLock", self._dynamicsLock)

    if self.getPoserFile().isVersion(PoserConst.POSER_V9):
      WBoolLine(fw, nextPfx, "collisionDetection", self._collisionDetection )

    WBoolLine(fw, nextPfx, "hidden", self._hidden )
    WBoolLine(fw, nextPfx, "addToMenu", self._addToMenu )
    WBoolLine(fw, nextPfx, "castsShadow", self._castsShadow )
    WBoolLine(fw, nextPfx, "includeInDepthCue", self._includeInDepthCue )
    WBoolLine(fw, nextPfx, "useZBuffer", self._useZBuffer )

    if self._parent:
      fw.write(f"{nextPfx}parent {self._parent}\n")
    if self._conformingTarget:
      fw.write(f"{nextPfx}conformingTarget {self._conformingTarget}\n")
    if self._lstAltGeom:
      for ag in self._lstAltGeom:
        ag.write(fw, nextPfx)

    fw.write(f"{nextPfx}creaseAngle {self._creaseAngle}\n")
    
    # Print WeightMap before channels
    for po in self._lstWMap:
      po.write(fw, nextPfx)
    
    # Channels { } part
    chanPfx = nextPfx + "\t"
    fw.write(f"{nextPfx}channels\n{chanPfx}{{\n")
    if self._groups:
      self._groups.write(fw, chanPfx)
    for po in self.getChannels():
      po.write(fw, chanPfx)
    fw.write(f"{chanPfx}}}\n")

    if self._endPoint:
        fw.write(f"{nextPfx}endPoint {self._endPoint.poserPrint()}\n")
    if self._origin:
        fw.write(f"{nextPfx}origin {self._origin.poserPrint()}\n")
    if self._orientation:
        fw.write(f"{nextPfx}orientation {self._orientation.poserPrint()}\n")

    WBoolLine(fw, nextPfx, "displayOrigin", self._displayOrigin )

    if self._displayMode:
        fw.write(f"{nextPfx}displayMode {self._displayMode}\n")
    fw.write(f"{nextPfx}customMaterial {self._customMaterial}\n")
    WBoolLine(fw, nextPfx, "locked", self._locked )
    
    # Print other found attributes
    for po in self._lstAttr:
      po.write(fw, nextPfx)
    if not self._lstAttr:
      fw.write('\n')
      
    # Write Customer Data
    if self._customData:
      self._customData.write(fw, nextPfx)

    fw.write(f"{nextPfx}}}\n")

  def write(self, fw, pfx):
    raise Exception(PoserConst.C_EX_NOTCALL)




# -----------------------------------------------------------------------------
# Descendant classes of PoserMeshedObject
# -----------------------------------------------------------------------------

# 
# Just to avoid interactions with actors or props that have geoms
#  
class Camera(PoserMeshedObject):
  def __init__(self):
    super(Camera, self).__init__()

# 
# Just to avoid interactions with actors or props that have geoms
#  
class Light(PoserMeshedObject):
  def __init__(self):
    super(Light, self).__init__()

  def getLightType(self):
    sa = self.findAttribut(PoserToken.E_lightType)
    return sa.getIntegerValue()
  
  def addAttribut(self, po):
    if po.getPoserType()==PoserToken.E_depthMapSize:
      prev = self.getGenericTransform(PoserToken.E_depthMapSize)
      if prev:
        # The second defintion should be the Simple attribut
        self.getLstAttr().append(po)
        return         
      
    PoserMeshedObject.addAttribut(self, po)

# 
#  Describes a Poser "actor" object.
#  
class PoserActor(PoserMeshedObject):

  def __init__(self, Name = None):
    super(PoserActor, self).__init__(Name)
    self.idx = 0
    self.setPoserType(PoserToken.E_actor)

  #    * @see pftk.poser.kern.PoserObject#setName(java.lang.String)
  def setName(self, n):
    super(PoserActor, self).setName(n)
    self.idx = index(n)

  def getIndex(self): return self.idx

  def isBody(self):
    c = self.getName().rfind(':')
    return (c == 4) and self.getName().startswith("BODY")

  # Hide an actor.
  #   @param hidden
  #   @param menuHidden  Hide in Poser Menu
  def setHidden(self, hidden, menuHidden=None):
    self._hidden = hidden
    self._visible = False
    self._bend = False
    self._dynamicsLock = False
    self._addToMenu = menuHidden if menuHidden else not hidden
    self._castsShadow = False
    self._includeInDepthCue = False

# 
# Represents a Poser "prop" object
#  
class PoserProp(PoserMeshedObject):
  def __init__(self):
    super(PoserProp, self).__init__()

  # Props may have a figure index
  def setName(self, n):
    super(PoserProp, self).setName(n)
    self.idx = index(n)

  def getIndex(self):
    ''' Return the figure index or 0 if the prop is outside any figure ''' 
    return self.idx

  def createChannelMorphList(self, stm):
    lstCS = ChannelMorphStatusList()

    #  Calculate the list of channels with regards to the known one
    for attr in self.getChannels():
      if attr.getPoserType() == PoserToken.E_targetGeom:
        lstCS.append(ChannelMorphStatus(attr, stm))

    return lstCS


class BaseProp(PoserProp):
  def __init__(self):
    super(BaseProp, self).__init__()
    self.ambiguious = True

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    if not self._lstAttr:
      fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    else:
      super(BaseProp, self).write(fw, pfx)

# 
# Represents the Magnet object of a Magner deformer.
# Just to avoid interactions with actors or props that have geoms
#  
class MagnetDeformerProp(PoserProp):
  def __init__(self):
    super(MagnetDeformerProp, self).__init__()

# Represents the Spehirc zone of a Magner deformer.
# Just to avoid interactions with actors or props that have geoms
class SphereZoneProp(PoserProp):
  def __init__(self):
    super(SphereZoneProp, self).__init__()

# 
# Represents a Poser "path" object
#  
class CurveProp(PoserProp):
  def __init__(self):
    super(CurveProp, self).__init__()

# 
# 
# Represents a Poser "Wave" object
#  
class WaveDeformerProp(PoserProp):
  def __init__(self):
    super(WaveDeformerProp, self).__init__()


# 
# 
# Represents a Poser "Wind Field" object
#  
class ConeForceFieldProp(PoserProp):
  def __init__(self):
    super(ConeForceFieldProp, self).__init__()



# Just to avoid interactions with actors or props that have geoms
#  
class ControlProp(PoserProp):
  def __init__(self):
    super(ControlProp, self).__init__()



# 
# This class represents the hairProp attribut of a Poser File.
#  
class HairProp(PoserProp):
  def __init__(self):
    super(HairProp, self).__init__()
    self._isSimple = True
    self.ambiguious = True

    def __init__(self):
        super(HairProp, self).__init__()

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    if self._isSimple:    
      fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")

  def addAttribut(self, po):
    super(HairProp, self).addAttribut(po)
    self._isSimple = False




