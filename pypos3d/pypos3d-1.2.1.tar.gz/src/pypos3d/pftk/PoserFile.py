# -*- coding: utf-8 -*-
import logging
import os, gzip

from langutil import C_OK, C_FAIL, C_ERROR
from pypos3d.wftk.PoserFileParser import PoserFileParser, PZ3_FNAT

from pypos3d.pftk.PoserBasic import getRealPath, index, PoserConst, PoserToken , isCompressed, Lang, getPoserFileType, create
from pypos3d.pftk.StructuredAttribut import GenericTransform, NodeInput, PoserMaterial
from pypos3d.pftk.GeomCustom import GeomCustom
from pypos3d.pftk.PoserMeshed import PoserProp, Camera, Light
from pypos3d.pftk.Figure import Figure

# 
#  Path Match between a referenced path of Poser and a real path.
#  
class PathMatch(object):

    def __init__(self, o, r):
        self._originalPath = o
        self._realPath = r
        self._exist = False

    def getOriginalPath(self):
        return self._originalPath

    def setOriginalPath(self, _originalPath):
        self._originalPath = _originalPath

    def getRealPath(self):
        return self._realPath

    def setRealPath(self, _realPath):
        self._realPath = _realPath

    def isExist(self):
        return self._exist

    def setExist(self, _exist):
        self._exist = _exist


class GTLink():
  ''' Thid class holds the links (parent, descendant) between channels. '''
  def __init__(self, qualifiedName : str, gt=None):
    self.qname = qualifiedName
    self.gt = gt
    self.parents = {}
    self.desc = {}
    #print('Adding GTLink({:s} as {:s})'.format(qualifiedName, 'direct' if gt else 'fwd'))
    
  def getParents(self):
    locset = set(self.parents.values())
    for p in self.parents.values():
      subset = set(p.getParents())
      locset |= subset
      
    return list(locset)
      
  def getDesc(self):
    locset = set(self.desc.values())
    for p in self.desc.values():
      subset = set(p.getDesc())
      locset |= subset
      
    return list(locset)

# 
class PoserFile(object):
  ''' Poser File internal representation.
  The aim of this class is to represent all kind of Poser files.
  But it works fine with : Characters (.cr2), Scenes (.pz3) and Props (.pp2)
  '''
  
  # Set of channel types that can be computed
  __COMPUTABLETRANSF = { PoserToken.E_targetGeom,  PoserToken.E_valueParm, PoserToken.E_deformerPropChan, PoserToken.E_geomChan, \
                         PoserToken.E_rotateX, PoserToken.E_rotateY, PoserToken.E_rotateZ,
                         PoserToken.E_propagatingScale, PoserToken.E_propagatingScaleX, PoserToken.E_propagatingScaleY, PoserToken.E_propagatingScaleZ,
                         PoserToken.E_translateX, PoserToken.E_translateY, PoserToken.E_translateZ,
                         PoserToken.E_scale, PoserToken.E_scaleX, PoserToken.E_scaleY, PoserToken.E_scaleZ,
                         PoserToken.E_visibility
                         }
  

  def __init__(self, fn, createLinks=False):
    ''' Create a PoserFile from a file.
    
    Parameters
    ----------
    fn : str
      Filename to read
    createLinks : Boolean, optional, default False
      Create the internal mapping between channels and operators
      Check referenced parts in each figure (parent, weld, figure Root)
      
    Raises
    ------
    OSError : File Not found
    
    '''
    super(PoserFile, self).__init__()

    #  File name 
    self._name = ''
  
    #  PoserFile type 
    self._fileType = PoserConst.FFT_UNKNOWN
  
    #  Poser File Version   
    self._version = None
    self._versionStr = None
  
    #  Poser File PZ3 movieinfo   
    self._movieinfo = None
  
    #  Poser File PZ3 GROUND prop   
    self._ground = None
  
    #  Poser File PZ3 FocusDistanceControl prop   
    self._focusDistanceControl = None
  
    #  First actor of a PZ3 file 
    self._universe = None
  
    #  List of "Free" props (Prop, hairProp, controlProp)  = Not Attached to any character 
    self._lstProp = [ ]
  
    #  List of managed Camera 
    self._lstCamera = [ ]
  
    #  List of managed Lights 
    self._lstLight = [ ]
  
    #  List of managed Hair growth groups 
    self._lstGrowtGroup = [ ]
  
    #  List of Figure 
    self._lstFigure = [ ]
  
    #  Poser File PZ3 doc   
    self._doc = None
    self._illustrationParms = None
    self._renderDefaults = None
    self._faceRoom = None

    # Channels link Dictionnary
    self._gtlnk = {}
  
    #  Temporary Attributes 
    self._lastBodyIdx = 0
  
    #  Last read (or discovered) figure at read time 
    self._lastFigure = None
    self._lastFRF = None

    self.setName(fn)
    ft = getPoserFileType(fn)
    self._fileType = ft & PoserConst.PFT_MASK
    isZipped = isCompressed(ft)

    logging.info("File[%s] : opening", fn)
    rin =  gzip.open(fn, 'rt', errors='replace') if isZipped else open(fn, 'rt', errors='replace')
    pfr = PoserFileParser(rin, PZ3_FNAT)
    code,*_ = pfr.getLine()
    if code==PoserFileParser.TT_LEFTBACKET:
      self.read(pfr)
#     except:
#       exc_type, exc_value, exc_tb = sys.exc_info()
#       traceback.print_exception(exc_type, exc_value, exc_tb)
#       print('Exception in PoserFile.__init__:'+str(pfr.lineno()))
           
    rin.close()
    logging.info("File[%s] : %d lines read", fn,  pfr.lineno())
    
    if createLinks:
      self.__createLinks(True)
      self.checkActorLinks()
      
    #  if WFBasic.PYPOS3D_TRACE: print ('File({0:s} - Read Error {1:s}'.format(fn, str(e.args)))
      

  # 
  def getName(self): 
    ''' Return the name of the object, for a Poser file the name is the filename. '''
    return self._name

  # 
  # * Set the name.
  # @param string
  #    
  def setName(self, s):
    self._name = s

  # 
  # Return the Poser Language Version as an PoserObject
  #    
  def getVersion(self): return self._version

  def isVersion(self, cmpVers):
    if not self._versionStr:
      sa = self._version.findAttribut(PoserToken.E_number)
      self._versionStr = sa.getValue() if sa else ''

    return False if self._versionStr==None else (self._versionStr==cmpVers)

  # 
  # Read a structured attribute data from the file. This class name, the name
  # and the opening bracket are supposed to be consumed by the caller.
  # Because it is the mean it uses to recognize a structured attribute.
  #    
  def read(self, st):
    code,cn,rw = st.getLine()
    
    while (code!=PoserFileParser.TT_EOF) and (code!=PoserFileParser.TT_RIGHTBRACKET):

      if code== PoserFileParser.TT_WORD:
        try:
          vc = Lang[cn]
          #  Known word
          if vc==PoserToken.E_figure:
            if self._lastFigure:
              self._lastFigure.read(st)
              # Should finish the current figure definition
              logging.info("Line[%d]: figure [%s] defined", st.lineno(), self._lastFigure.getPrintName())
            else:
              # Figure part outside any delcared figure
              #  We're not reading a CR2 or PP2 or PZ3 file, but
              #  probably a Pose file ... nothing to do
              logging.warning("Line[%d]: Figure block found without figure", st.lineno())
              
          elif vc.isStructured:
            nom = rw # "" if st.ttype == PoserFileParser.TT_EOL else st.sval
            sta = create(vc, nom)

            #  Overload of object if definition part exists
            sta = self.addAttribut(sta)

            #  Read the opening bracket
            code,cn,rw = st.getLine()
            if code==PoserFileParser.TT_LEFTBACKET:
              sta.read(st)
            else:
              logging.error("Line[%d]:  '{' is missing for %s", st.lineno(), cn)
          else:
            if vc.isDirect:
              #st.getToNextLine()
              logging.error("Line[%d]: setDirect() illegal at PoserFile level %s", st.lineno(), cn)
            else:
              # Read before add
              sa = create(vc, cn)
              sa.read(st, rw)
              self.addAttribut(sa)

            #nextLine = False
        except KeyError: # if vc == None: --> Unknow word
          logging.info("Line[%d] - Unknown word:%s", st.lineno() , cn)

      #  Get next token
      code,cn,rw = st.getLine()
      # Wend
  # 
  # Add an object at highest level of the Poser File.
  #    
  def addAttribut(self, po):
    pot = po.getPoserType()

    if pot==PoserToken.E_version:
      self._version = po
      return self._version

    elif pot==PoserToken.E_movieInfo:
      self._movieinfo = po
      return self._movieinfo

    elif pot==PoserToken.E_keyLayer:
      logging.error("Ignored " + po.getName() + "[" + po.getPoserType() + "]")
      return po

    elif pot==PoserToken.E_figureResFile:
      #  Beginning of a figure
      self._lastFRF = po
      fig = self.findFigure(self._lastFRF)
      if fig == None:
        fig = Figure(self, frf=self._lastFRF)
        self._lstFigure.append(fig)
        self._lastFRF = None
      #  else  keep the lastFRF, because could be used for another figure with same geometry      
      self._lastFigure = fig
      return None

    elif pot==PoserToken.E_actor:
      pa = po
      pa.setPoserFile(self)
      if pa.getName() == PoserConst.C_UNIVERSE:
        if self._universe == None:
          self._universe = pa
        return self._universe

      idx = pa.getIndex()

      if self._lastFigure == None:
        self._lastFigure = Figure(self, idx)
        self._lstFigure.append(self._lastFigure)
        if (self._fileType==PoserConst.PFT_CR2) or (self._fileType==PoserConst.PFT_PZ3):
          logging.warning("Actor " + pa.getName() + " without figure in " + self.getName())

      else:
        if self._lastFigure.getBodyIndex()==PoserConst.C_BAD_INDEX:
          #  The figure has just been discovered, so the first actor gives the body index
          self._lastFigure.setBodyIndex(idx)

        else:
          #  Check index coherence
          if self._lastFigure.getBodyIndex() != idx:
            #  Means that several figures have the same target OBJ file 
            nf = self.getFigure(idx)
            if nf:
              self._lastFigure = nf
            else:
              #  log.warning("Figure index [" + idx + "] does not exists for actor " + pa.getName());              
              self._lastFigure = Figure(self, frf=self._lastFRF)
              self._lstFigure.append(self._lastFigure)
              self._lastFigure.setBodyIndex(idx)
              self._lastFRF = None

      pa = self._lastFigure.addReadActor(pa)
      if pa.isBody():
        self._lastBodyIdx = idx
      return pa

    elif pot==PoserToken.E_prop:
      pp = po
      pp.setPoserFile(self)
      if pp.getName() == "GROUND":
        if self._ground == None:
          self._ground = pp
        return self._ground

      for epp in self._lstProp:
        if pp.getName() == epp.getName():
          return epp

      if self._lastFigure == None:
        #  We are in the declarative part of "free" props
        self._lstProp.append(pp)
      else:
        pp = self._lastFigure.addReadActor(pp)
      return pp

    elif pot==PoserToken.E_light:
      li = po
      li.setPoserFile(self)
      for ell in self._lstLight:
        if li.getName() == ell.getName():
          return ell
      self._lstLight.append(li)
      return li

    elif pot==PoserToken.E_camera:
      cam = po
      cam.setPoserFile(self)
      for ec in self._lstCamera:
        if cam.getName() == ec.getName():
          return ec
      self._lstCamera.append(cam)
      return cam

    # elif pot==PoserToken.E_figure: Managed in read() as of V0.2
    # Manage other Props : hairProp, controlProp, Magnets
    elif pot==PoserToken.E_controlProp or \
         pot==PoserToken.E_baseProp or \
         pot==PoserToken.E_hairProp or \
         pot==PoserToken.E_magnetDeformerProp or \
         pot==PoserToken.E_sphereZoneProp or \
         pot==PoserToken.E_curveProp or \
         pot==PoserToken.E_waveDeformerProp or\
         pot==PoserToken.E_coneForceFieldProp:
      pp = po
      pp.setPoserFile(self)
      if pp.getName() == "FocusDistanceControl":
        if self._focusDistanceControl == None:
          self._focusDistanceControl = pp
        return self._focusDistanceControl

      for epp in self._lstProp:
        if pp.getName() == epp.getName():
          return epp
      if self._lastFigure == None:
        #  We are in the declarative part of "free" props
        self._lstProp.append(pp)
      else:
        pp = self._lastFigure.addReadActor(pp)

      return pp

    elif pot==PoserToken.E_hairGrowthGroup:
      self._lstGrowtGroup.append(po)
      return po
    elif pot==PoserToken.E_faceRoom:
      self._faceRoom = po
      return self._faceRoom
    elif pot==PoserToken.E_illustrationParms:
      self._illustrationParms = po
      return self._illustrationParms
    elif pot==PoserToken.E_renderDefaults:
      self._renderDefaults = po
      return self._renderDefaults
    elif pot==PoserToken.E_doc:
      self._doc = po
      return self._doc
    elif pot==PoserToken.E_setGeomHandlerOffset:
      return None
    #elif pot==PoserToken.E_readScript: #  TODO : Read Other Definition Script
      #logging.error("No Management rule for %s [%s]", po.getName() , po.getPoserType().token)
    else:
      logging.error("No Management rule for %s [%s]", po.getName() , po.getPoserType().token)

    return None

  # 
  # Return the figure associated to the BODY index
  # * @param idx
  # *          The BODY index
  # * @return
  #    
  def getFigure(self, idx):
    for fig in self._lstFigure:
      if fig.getBodyIndex() == idx:
        return fig
    return None

  # 
  # Returns the list of figures contained in the Poser File
  # @return the list of Figure objects (not a copy)
  #    
  def getLstFigure(self): return self._lstFigure

  # 
  # Returns the list of Cameras contained in the Poser File
  # @return the list of Camera objects (not a copy)
  #    
  def getLstCamera(self): return self._lstCamera

  # 
  # Returns the list of Lights contained in the Poser File
  # @return the list of Light objects (not a copy)
  #    
  def getLstLight(self): return self._lstLight

  # 
  # Returns the list of Props contained in the Poser File
  # @return the list of PoserProp objects (not a copy)
  #    
  def getLstProp(self): return self._lstProp

  # 
  # Return the list of all objects names that can be referenced.
  # @return
  #    
  def getLstFigProp(self):
    return [ pp for pp in self.getLstProp() ] +\
           [ n for f in self.getLstFigure() for n in f.getActors() ] 
   
   
  def findFigure(self, frf):
    for fig in self._lstFigure:
      if frf.getValue() == fig.getFigResFile().getValue():
        return fig
    return None

  def findActor(self, actorName):
    for fig in self._lstFigure:
      for act in fig.getActors():
        if act.getName() == actorName:
          return act
    return None

  def findMeshedObject(self, actorPropName):
    for fig in self._lstFigure:
      for a in fig.getActors():
        if actorPropName == a.getName():
          return a

    for pp in self._lstProp + self._lstLight + self._lstCamera:
      if actorPropName == pp.getName():
        return pp

    return None

  # 
  # Return the list of PoserMeshedObject (actor, prop, hairprop) 
  # Return a list of PoserMeshedObject (actor, prop, hairprop) that match the
  #  given nameif any
  # @return a list of PoserMeshedObject
  #    
  def findAllMeshedObject(self, actorPropName=None):
    if actorPropName:
      return [ pp for pp in self._lstProp + self._lstLight+self._lstCamera if actorPropName == pp.getName() ] + \
            [ part for fig in self._lstFigure for part in fig.getActors() if actorPropName == part.getName() ]
    else:
      return self._lstProp + self._lstLight + self._lstCamera + \
        [ a for fig in self._lstFigure for a in fig.getActors() ] 

  # 
  def writeFile(self, fn):
    ''' Write PoserFile in text format (without compression)
    # RENAMED Java write --> Python writeFile
     
    Parameters
    ----------
    fn : str
      Full path name
      
    Returns
    -------
    int
      C_OK write without error, C_ERROR a write error has occurred
    '''
    ret = C_OK
    try:
      logging.info("File[" + fn + "] : writing")
      prn = open(fn, 'w')
      self.write(prn)
      prn.close()
      logging.info("File[" + fn + "] : " + str(os.path.getsize(fn)) + " bytes")
    except OSError:
      ret = C_ERROR
    return ret

  # 
  def writeZ(self, fn):
    ''' Write PoserFile in Zlib format (text stream compressed)
     
    Parameters
    ----------
    fn : str
      Full path name

    Returns
    -------
    int
      C_OK write without error, C_ERROR a write error has occurred
    '''
    ret = C_OK
    try:
      logging.info("File[" + fn + "] : writing/zipping")
      out = gzip.open(fn, 'wt') 
      self.write(out)
      out.close()
      logging.info("File[" + fn + "] : " + str(os.path.getsize(fn)) + " bytes")
    except OSError:
      ret = C_ERROR
    return ret


  def save(self, fn):
    ''' Write a PoserFile in text mode or in compressed mode.
    Use the extension to find the right mode.

    Parameters
    ----------
    fn : str
      Full path name

    Returns
    -------
    int
      C_OK write without error, C_ERROR a write error has occurred
    '''
    if isCompressed(fn):
      ret = self.writeZ(fn)
    else:
      ret = self.writeFile(fn)

    return ret



  # 
  # @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  #    
  def write(self, fw):
    isPZ3 = (self._fileType & PoserConst.PFT_MASK) == PoserConst.PFT_PZ3

    fw.write("{\n")
    if self._version:
      self._version.write(fw, "")

    if isPZ3 and self._movieinfo:
      self._movieinfo.write(fw, "")

    #  Write Definition of "Free" Props
    #  Write Definition of Lights
    #  Write Definition of Cameras
    #  Write Definition of Figures
    allParts = [ x for x in [ self._ground, self._universe, self._focusDistanceControl ] if isPZ3  and x ]
    allParts += self._lstProp + self._lstLight + self._lstCamera + self._lstFigure 
    for part in allParts:
      part.writeDef(fw, "")

    #  -- DATA WRITING --
    #  Write Data of "Free" Props
    #  Write Data of Lights
    #  Write Data of Cameras
    #  Write Data of Figures
    for part in allParts:
      part.writeData(fw, "")

    for hgg in self._lstGrowtGroup:
      hgg.write(fw, "")

    if self._doc:
      self._doc.write(fw, "")

    if isPZ3:
      for attr in [ self._illustrationParms, self._renderDefaults, self._faceRoom ]:
        if attr:
          attr.write(fw, "")

    if isPZ3 or (self._fileType & PoserConst.PFT_MASK) == PoserConst.PFT_CR2:
      fw.write("setGeomHandlerOffset 0 0.3487 0\n")

    fw.write("}\n")

  def getChannel(self, groupName, channelName):
    po = self.findMeshedObject(groupName)
    return po.getGenericTransform(channelName) if po else None
  
  # Return the ancestors channel list of the channel given by channelName in
  # groupName actor.
  # 
  # @param figureName
  #          Unused because of welknown CrossWalk problems
  # @param groupName
  # @param channelName
  # @return The list of GenericTransform
  def getChannelAncestor(self, figureName, groupName, channelName):
    lstact = self.findAllMeshedObject(groupName)   
    if lstact and (len(lstact)==1):
      po = lstact[0]
      
      channel = po.getChannel(channelName) # next(attr for attr in po.getChannels() if attr.getName()==channelName)
      
      if not self._gtlnk:
        self.__createLinks(True)

      qn = channel.getPoserMeshedObject().getName() + '.' + channel.getName()
      try:
        gtl = self._gtlnk[qn]
        return [ channel, ] + [ descgtl.gt for descgtl in gtl.getParents() ]
      except KeyError:
        logging.warning("Channel[%d] not found", qn)
        return []


    logging.warning(figureName + "." + groupName + " Not Found")
    return []

  # 
  # Return the k factor of the first frame of the channel given by groupName of
  # the group given by groupName.
  # 
  # * @param figureName
  # *          Unused because of well known CrossWalk problems
  # * @param groupName
  # * @param channelName
  # * @return The float factor.
  #    
  def getFactor(self, figureName, groupName, channelName):
    po = self.findActor(groupName)
    if po:
      for attr in po.getChannels():
        if (attr.getName()==channelName) and \
           (attr.getPoserType() in PoserFile.__COMPUTABLETRANSF):
          finalFactor = attr.getKeysFactor(0)

          #  Get Recursively controling channels
          for vod in attr.getVOD():
            #  FIX: 20100906 Avoid simple deadly recursion
            if (groupName != vod.getGroupName()) or (channelName != vod.getChannelName()):
              # Get the real factor of the master
              f = self.getFactor(vod.getFigureName(), vod.getGroupName(), vod.getChannelName())
              finalFactor = vod.calc(finalFactor, f)
                    
          return finalFactor
        
      logging.warning("No Channel [%s] for [%s.%s]", channelName, figureName, groupName)

    logging.warning(figureName + "." + groupName + " Not Found")
    return 0.0

# 2020-11-06 Unused?
#   def calcChannelAncestors(self, gt, lstgt, lstMissing):
#     vodTab = gt.getVOD()
#     for op in vodTab:
#       found = False
#       for gl in lstgt:
#         if gl.getPoserMeshedObject().getName()==op.getGroupName() and gl.getName()==op.getChannelName():
#           # Found : Already in the list
#           found = True
#           break
# 
#       if not found:
#         newgt = self.getChannel(op.getGroupName(), op.getChannelName())
#         if newgt:
#           lstgt.append(newgt)
#           self.calcChannelAncestors(newgt, lstgt, lstMissing)
#         else:
#           lstMissing.append(op.getGroupName() + '.' + op.getChannelName())
# 2020-11-06 Unused?
#   def getChannelAncestors(self, gt, lstMissing):
#     lstgt = [ ]
#     self.calcChannelAncestors(gt, lstgt, lstMissing)
#     return lstgt

  def getDescendant(self, bodyIdx, firstName=None):
    f = self.getFigure(bodyIdx)
    return f.getDescendant(firstName) if f else None 

  def getWelded(self, bodyIdx, firstName):
    fig = self.getFigure(bodyIdx)
    return None if (fig == None) else fig.getWelded(firstName)

  def getFigResFileGeom(self, bodyIdx, PoserRootDir):
    gc = None
    f = self.getFigure(bodyIdx)
    if f:
      frf = f.getActors()[0].getFigureResFile()
      if frf:
        # Extract File path from the Poser File
        objFn = frf.getPath(PoserRootDir)

        # Read OBJ filename of the object
        gc = GeomCustom(objFn)
      else:
        gc = GeomCustom()

    return gc

  def addToSet(self, poserRootDir, hshres, ficpath):
    if (ficpath==None) or (ficpath=="") or (ficpath=='""') or (ficpath=="NO_MAP"):
      return

    try: # pm = 
      hshres[ficpath]
    except KeyError:
      # Clean the ficpath
      # Build a full path
      realpath = getRealPath(poserRootDir, ficpath)
      logging.info("Add:" + realpath)
      hshres.update( { ficpath : PathMatch(ficpath, realpath) } )

  def refPoserMaterial(self, poserRootDir, hshres, mat):
    self.addToSet(poserRootDir, hshres, mat.getTextureMap())
    self.addToSet(poserRootDir, hshres, mat.getBumpMap())
    self.addToSet(poserRootDir, hshres, mat.getReflectionMap())
    self.addToSet(poserRootDir, hshres, mat.getTransparencyMap())
    for nd in mat.getLstNodes():
      for po in nd.getLstAttr():
        if isinstance(po, (NodeInput, )):
          self.addToSet(poserRootDir, hshres, po.getFile())

  def refPoserMesh(self, poserRootDir, hshres, po):
    if (po.getPoserType() == PoserToken.E_prop) or (po.getPoserType() == PoserToken.E_hairProp) or (po.getPoserType() == PoserToken.E_actor):
      if po.getGeomType() == PoserConst.GT_LOCAL_OBJFILE:
        self.addToSet(poserRootDir, hshres, po.getGeomFileName())

      la = po.getAltGeomList()
      if la:
        for altg in la:
          self.addToSet(poserRootDir, hshres, altg.getGeomFileName())

      if po.getCustomMaterial() == 1:
        for mo in po.getLstAttr():
          if isinstance(mo, (PoserMaterial, )):
            self.refPoserMaterial(poserRootDir, hshres, mo)

  #  Compute the list of referenced files.
  #  @return    a list of Matched files
  def getReferencedFiles(self, poserRootDir):
    lstres = { }
    for fig in self.getLstFigure():
      # Get figure main file
      frf = fig.getFigResFile()

      ficpath = frf.getPath(poserRootDir)
      self.addToSet(poserRootDir, lstres, ficpath)

      for pa in fig.getActors():
        self.refPoserMesh(poserRootDir, lstres, pa)

      for mat in fig.getLstMaterial():
        self.refPoserMaterial(poserRootDir, lstres, mat)

    # Look up in alone props
    for pp in self.getLstProp():
      self.refPoserMesh(poserRootDir, lstres, pp)

    #logging.info("List size:" + str(len(lstres)))
    return lstres

  # TODO: Ugly interface to change
  # TODO: Duplicate code to clean
  def cleanNonNullDelta(self, bodyIdx:int=-1, pp=None, setTargetMorph=None):
    ''' Remove deltas from targetGeom in a Figure or a PoserProp or a PoserActor.
    Parameters
    ----------
    bodyIdx : int, optional, default -1
      Index of the figure in the PoserFile
    pp : PoserProp or PoserActor, optional, default None
      Used when bodyIdx not set
    setTargetMorph : iterable, optional, default None
      List or Set or channel names to clean. If None targetGeom starting by 'PBM' are cleaned
    Returns
    -------
    int
      Return Code
    '''
    ret = C_OK
    if bodyIdx>=0:
      logging.info("------------------------ Cleaning Deltas ------------------------")
      # Remove unused attributes of the PoserObject
      # Get all part of the character
      lstActor = self.getDescendant(bodyIdx)
      if lstActor:
        # Channels where not found when Figure index was higher than 9 (2 digits)
        #idxRelPos = 3 if (bodyIdx > 9) else 2

        for po in lstActor:
          for attr in po.getChannels():
            if attr.getPoserType()==PoserToken.E_targetGeom and GenericTransform.concerned(attr.getName(), setTargetMorph):
              finalFactor = 0.0
              for vod in attr.getVOD():
                # Get the real factor of the master
                f = self.getFactor(vod.getFigureName(), vod.getGroupName(), vod.getChannelName())
                # Take into account the operator kind
                finalFactor = vod.calc(finalFactor, f)

              # Deltas dltAttr = attr.getDeltas();
              finalFactor += attr.getKeysFactor(0)
              logging.info("Cleaning[%s] in %s f=%g", attr.getName(), po.getName(), finalFactor)
              attr.removeDeltas()
      else:
        ret = C_ERROR

    else: # pp should be a PoserProp
      if not pp: return C_ERROR
      
      for attr in pp.getChannels():
        if attr.getPoserType()==PoserToken.E_targetGeom and GenericTransform.concerned(attr.getName(), setTargetMorph):
          finalFactor = 0.0
          for vod in attr.getVOD():
            # Get the real factor of the master
            f = self.getFactor(vod.getFigureName(), vod.getGroupName(), vod.getChannelName())
            # Take into account the operator kind
            finalFactor = vod.calc(finalFactor, f)

          finalFactor += attr.getKeysFactor(0)

          # Remove the deltas but not the targetGeom
          logging.info("Cleaning[%s] in %s f=%g", pp.getName(), pp.getName(), finalFactor)
          attr.removeDeltas()

    return ret


  # Extract the geometries of a Figure, with or without taking into account the
  # applied morph.
  # 
  # @param poserRootDir
  #          Path to Poser install
  # @param bodyIdx
  #          Index of the figure
  # @param channelSet
  #          Channels to take into account. If null, no delta are applied.
  # @return The list of geometries that compose the figure.
  def extractAll(self, poserRootDir, bodyIdx, channelSet):
    lstgeom = [ ]
    eg = None

    # Read OBJ filename
    body = self.getFigResFileGeom(bodyIdx, poserRootDir)
    if body and body.isValid():
      if channelSet:
        body.findApplyDelta(bodyIdx, self, channelSet)

      for pa in self.getDescendant(bodyIdx):
        # Check if the name of the actor vs the name of the meshed part
        if pa.getGeomType()==PoserConst.GT_GLOBAL_OBJFILE:
          # geomHandlerGeom 13 hip
          eg = body.extractSortGeom(pa.getGeomGroupName(), pa.getGeomType())

        elif pa.getGeomType()==PoserConst.GT_LOCAL_OBJFILE:
          # objFileGeom 0 0 :Runtime:Geometries:Marforno:Elaya:Lamp.obj          
          eg = GeomCustom(getRealPath(poserRootDir, pa.getGeomFileName()))

        #elif pa.getGeomType()==PoserConst.GT_NONE:
        #elif pa.getGeomType()==PoserConst.GT_INTERNAL: 
        else:
          eg = None

        if eg:
          eg.setName(pa.getName())
          lstgeom.append(eg)

    return lstgeom

  # Calculate the impact of a channel deletion. (Not recursive search)
  # The "first" item is the concerned channel.
  # @param channel
  def deleteChannelImpact(self, channel):
    impset = { channel, }
    
    if self._gtlnk:
      qn = channel.getPoserMeshedObject().getName() + '.' + channel.getName()
      gtl = self._gtlnk[qn]
      impset.update( descgtl.gt for descgtl in gtl.desc.values() )
    else:  
      for f in self.getLstFigure():
        for pa in f.getActors():
          pa.getChannelDescendant(channel, impset)
#         for pp in f.getProps():
#           pp.getChannelDescendant(channel, impset)
      for pp in self.getLstProp():
        pp.getChannelDescendant(channel, impset)
        
    return impset

  # Calculate the set of channels that are referenced at any level by the given channel. (recursive search)
  # @param channel
  # Raise KeyError when the channel is not known
  def calcChannelParent(self, channel):
    if not self._gtlnk:
      self.__createLinks(True)

    qn = channel.getPoserMeshedObject().getName() + '.' + channel.getName()
    gtl = self._gtlnk[qn]

    lstgtl = gtl.getParents()

    return [ descgtl.gt for descgtl in lstgtl ]

  # Calculate the set of channels that reference at any level the given channel. (recursive search)
  # @param channel
  # Raise KeyError when the channel is not known
  def calcChannelDesc(self, channel):
    if not self._gtlnk:
      self.__createLinks(True)

    qn = channel.getPoserMeshedObject().getName() + '.' + channel.getName()
    gtl = self._gtlnk[qn]

    lstgtl = gtl.getDesc()

    return [ descgtl.gt for descgtl in lstgtl ]
    

  def printChannelLinks(self, channel):
    ''' Return a tuple of printable data for the channel (Qualified Name, nbDescDelta, DescChannelsNames, ParentChannelsNames) '''
    if not self._gtlnk:
      self.__createLinks(True)

    if isinstance(channel, str): # Input as string as a qualified string
      try:
        gt = self._gtlnk[channel].gt
      except KeyError:
        # Channel does not exist
        return (channel, -1, '', '')
    else:
      gt = channel
      
    # Compute channel dependencies
    nbdeltas, labparent, labdesc = 0, '',''
    try:
      lparent = self.calcChannelParent(gt)
      for gtdesc in [ g for g in lparent if g ]:
        if labparent:
          labparent += ', '          
        labparent += gtdesc.getQualifiedName()
      
      ldesc = self.calcChannelDesc(gt)
      for gtdesc in [ g for g in ldesc if g ]:
        nbdeltas += len(gtdesc._dlt.deltaSet) if gtdesc._dlt and gtdesc.getPoserType()==PoserToken.E_targetGeom else 0
        if labdesc:
          labdesc += ', '
        labdesc += gtdesc.getQualifiedName()
      
    except KeyError:
      # Channel does not exist
      return (channel, -1, '', '')
    
    return (channel.getQualifiedName(), nbdeltas, labdesc, labparent)

  def __createLinks(self, printErrors=False):
    ''' Create the link dictionnary of all channels in the file. '''
    logging.info("Linking[%s]:Channels", self.getName())
    self._gtlnk = {}

    nbdeclfwd,nblinks = 0,0

    for pmo in self.getLstFigProp():
      for gt in pmo.getChannels():
        qn = pmo.getName() + '.' + gt.getName()
        # Check if the channel has already been seen else create it
        try:
          gtl = self._gtlnk[qn]

          if gtl.gt==None: # If it was discovered before declaration
            nbdeclfwd-=1
            gtl.gt = gt

        except KeyError:
          gtl = GTLink(qn, gt)
          self._gtlnk[qn] = gtl

        for vop in gt.getVOD():
          # Check valueOp syntax, the figure index seems to be optional
          gn = vop.getGroupName()
          
          # Search for the channel as given by the valueOp
          refqn = gn + '.' +  vop.getChannelName()
          try:
            refgtl = self._gtlnk[refqn]
            
          except KeyError:
            p = gn.rfind(':')
            if p<0:
              refqn = gn + ':' + str(pmo.getIndex()) + '.' +  vop.getChannelName()
              # Make a second search with a qualified name
              try:
                refgtl = self._gtlnk[refqn]
              except KeyError:
                refgtl = GTLink(refqn)
                self._gtlnk[refqn] = refgtl
                nbdeclfwd+=1
            else:
              refgtl = GTLink(refqn)
              self._gtlnk[refqn] = refgtl
              nbdeclfwd+=1

          # The referenced channel is a parent for the current one
          gtl.parents[refqn] = refgtl

          # The current channel is a descendant for the channel named in the valueOp
          refgtl.desc[qn] = gtl
          nblinks+=1

    logging.info("Link.end[%s]: NbChannels=%d, Links=%d, Unlinked=%d", self.getName(), len(self._gtlnk), nblinks, nbdeclfwd)
    if printErrors and nbdeclfwd>0:
      for k,gtl in self._gtlnk.items():
        if not gtl.gt:
          print('Not Declared Channel:{:s}'.format(k))
  
  def getGTLinks(self):
    if not self._gtlnk:
      self.__createLinks(True)
    return self._gtlnk

  def delGTLink(self, gtOrQn):
    if not self._gtlnk: return
    
    qn = gtOrQn.getQualifiedName() if isinstance(gtOrQn, GenericTransform) else gtOrQn
      
    del self._gtlnk[qn]
    for gtl in self._gtlnk.values():
      gtl.desc.pop(qn, None)


  # Delete a channel in a PoserMeshedObject
  # @param fig
  #          Figure where is the channel (if the meshed object is an Actor)
  # @param lstImp
  #          Prepared impact list. If null will be calculated again.
  def deleteChannel(self, channel, lstImp=None):
    if lstImp == None:
      lstImp = self.deleteChannelImpact(channel)
    
    lstImp.remove(channel)
    
    # Remove calculated links
    self.delGTLink(channel)
    
    pmo = channel.getPoserMeshedObject()
    pmo.deleteChannel(channel)
    for ci in lstImp:
      ci.deleteChannelRef(channel)
    




#   def deleteFigureImpact(self, fig):
#     logging.error("Not implemented yet")
#     return None

  def delete(self, obj):
    '''  Delete the given PoserProp or Figure from the list of general props '''
    res = C_OK
    if isinstance(obj, PoserProp):
      try:
        self._lstProp.remove(obj)
        propName = obj.getName()

        # Clean Figure Attributs : addChild and weld
        for po in self._doc.getLstAttr():
          if (po.getPoserType() == PoserToken.E_addActor) and (po.getValue()==propName):
            self._doc.getLstAttr().remove(po)

      except:
        res = C_FAIL
    elif isinstance(obj, Camera):
      try:
        self._lstCamera.remove(obj)
        propName = obj.getName()
        for po in self._doc.getLstAttr():
          if (po.getPoserType() == PoserToken.E_addCamera) and (po.getValue()==propName):
            self._doc.getLstAttr().remove(po)

        # Relink Lights, if the parent of the deleted camera was not "UNIVERSE"
        if not obj.getParent() == PoserConst.C_UNIVERSE:
          for li in self._lstLight:
            sa = li.findAttribut(PoserToken.E_depthCamera)
            if sa and (sa.getValue() == propName):
              # What value to set?? instead : Name of the first Camera of the file
              sa.setValue(self._lstCamera[0].getName())
      except:
        res = C_FAIL

    elif isinstance(obj, Light):
      try:
        self._lstLight.remove(obj)
        propName = obj.getName()
        for po in self._doc.getLstAttr():
          if (po.getPoserType() == PoserToken.E_addLight) and (po.getValue()==propName):
            self._doc.getLstAttr().remove(po)

        # Check the 'parent' of each Camera and relikn if needed
        firstLight = self._lstLight[0]
        for cam in self._lstCamera:
          if cam.getParent() == propName:
            if firstLight == None:
              logging.warning("Camera[" + cam.getName() + "] can not be relinked (no more lights)")
            else:
              cam.setParent(firstLight.getName())
              logging.info("Camera[" + cam.getName() + "] relinked to " + firstLight.getName())
      except:
        res = C_FAIL

    elif isinstance(obj, Figure):
      try:
        self._lstFigure.remove(obj)
        fi = obj.getBodyIndex()
        lstprp = self.findAllMeshedObject()

        # Change any references in "ConformingTarget" of actors of other figures.
        # No more "conformingTarget" attributs.
        for pmo in lstprp:
          if index(pmo.getConformingTarget()) == fi:
            pmo.setConformingTarget(None)

          # Delete any references in channels of actors of other figures and Props
          for pgt in pmo.getChannels():
            pgt.deleteFigureRef(obj)

      except:
        res = C_FAIL
        
    # Remove calculated links (anyway, to be consistent)
    self._gtlnk.clear()

    return res

  # Change the name of referenced part (actor, prop, hairProp, controlProp)  
  # @param oldPartName
  # @param newPartName
  def changeReference(self, oldPartName, newPartName):
    for fig in self._lstFigure + self._lstProp:
      fig.changeReference(oldPartName, newPartName)




  def checkActorLinks(self):
    ''' Check all actors links in all figure and props '''

    logging.info("Linking[%s]:Actors", self.getName())
    nberrors=0
    
    for fig in self._lstFigure:
      nberrors += fig.checkActorLinks()

    for act in self._lstProp:
      parentName = act.getParent()
      
      if parentName==PoserConst.C_UNIVERSE:
        if self._universe:
          continue
        else:
          nberrors+=1
          logging.warn('Missing Declared Parent Actor: %s for %s', parentName, act.getName())        
      else:
        p = self.findActor(parentName)
        if not p:
          nberrors+=1
          logging.warn('Missing Declared Parent Actor: %s for %s', act.getParent(), act.getName())

    if nberrors:
      logging.info("Linking[%s]:Actors with %d errors", self.getName(), nberrors)
      
    return C_OK if nberrors==0 else C_FAIL
      
      
  def createFigure(self, name=None):
    ''' Create a new Figure object, initialize the correct index. '''
    bodyIdx = 1 + (max( f.getBodyIndex() for f in self.getLstFigure() ) if self.getLstFigure() else 0)
     
    fig = Figure(self, idx=bodyIdx)
    
    if name:
      fig.setPrintName(name)
    
    self._lstFigure.append(fig)
    
    # At this stage the Figure is not consistent (no geom, no actor, ...)
    
    logging.info("Figure Created: [%s]:%d", name if name else '', bodyIdx)
    return fig
      
      
      


