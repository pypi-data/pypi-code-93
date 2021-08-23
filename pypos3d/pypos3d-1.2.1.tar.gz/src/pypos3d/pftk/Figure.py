# -*- coding: utf-8 -*-
# package: pypos3d.pftk
import os
import sys, traceback
import logging
from collections import namedtuple, UserDict
from bisect import bisect_left

from langutil import C_OK, C_FAIL, C_ERROR, C_UNKNOWN, C_FILE_NOT_FOUND, UsageError

from pypos3d.wftk.PoserFileParser import PoserFileParser

from pypos3d.pftk.PoserBasic import cleanName, getRealPath, index, PoserConst, PoserToken, Lang, create, WBoolLine
from pypos3d.pftk.SimpleAttribut import LinkParmsSA, SimpleAttribut
from pypos3d.pftk.StructuredAttribut import GenericTransform, ValueOpDelta, ChannelMorphStatus, ChannelMorphStatusList, PoserMaterial, Keys, calcMapping_KDTree, CustomData
from pypos3d.pftk.GeomCustom import GeomCustom, FigureResFile
from pypos3d.pftk.PoserMeshed import PoserProp, PoserActor, BaseProp, PoserMeshedObject
from pypos3d.pftk.ChannelImportAnalysis import FigurePart, ChannelImportAnalysis
from pypos3d.wftk.WaveGeom import WaveGeom, readGeom


# Internal tuple used to store addChild and weld links between figure's parts
PMOLink = namedtuple('PMOLink', ['son', 'parent', 'sonPMO', 'parentPMO'])

class LinkDir(UserDict):
  ''' Internal dictionary of links.
  if hierarchical is True, parent is a single string
  else parent contains a list of strings (for multiple welded parents)
    and parentPMO is the reflecting list of PoserMeshed objects
  '''
  
  C_LNK_CHILD, C_LNK_WELD = 'parented', 'welded'
  
  def __init__(self, initialdata=None, hierarchical=True):
    super(LinkDir, self).__init__( { } if not initialdata else initialdata )
    self.hierarchical = hierarchical
    
  def lnkAdd(self, sonName:str, parentName:str, sonobj, parentobj):
    prev = self.get(sonName)
    if self.hierarchical:
      if prev:
        # Child-Parent found --> Update for childs
        logging.warning('Part[%s] already %s to [%s]', sonName, LinkDir.C_LNK_CHILD, parentName)

      self[sonName] = PMOLink(sonName, parentName, sonobj, parentobj)
    else: # weld
      if prev:
        prev.parent.append(parentName)
        prev.parentPMO.append(parentobj)
      else:
        self[sonName] = PMOLink(sonName, [parentName,], sonobj, [parentobj, ])

  def changeReference(self, oldPartName, newPartName):
    sonName, parentName, pPMO = '', '', None
    
    # FIX: Python 3.8 does not support dictionnary change during iteration
    # for k,v in dico.items():
    for (k,v) in [ (k,v) for k,v in self.items() ]:
      if oldPartName==v.son:
        del self[k]
        sonName = newPartName
        replace = True
      else:
        sonName = v.son
        replace = False
        
      pPMO = v.parentPMO
      parentName = v.parent
      
      if self.hierarchical:
        if oldPartName==v.parent:
          parentName = newPartName
          pPMO = None # Lost Link
          replace = True
      else:
        for i,p in enumerate(v.parent):
          if oldPartName==p:
            v.parent[i] = newPartName
            pPMO[i] = None # lost link
            break

      if replace:
        self[sonName] = PMOLink(sonName, parentName, v.sonPMO, pPMO)
        
  def checkActorDico(self, fig):
    msg = LinkDir.C_LNK_CHILD if self.hierarchical else LinkDir.C_LNK_WELD
    nberrors = 0
    rebuild = False
    for k,(son, parent, sonPMO, parentPMO) in self.items():
      if not sonPMO:
        sonPMO = fig.findActor(son)
        if sonPMO:
          # Create a new link
          rebuild = True
        else:
          nberrors+=1
          logging.warn('Missing %s Child Actor [%s] for [%s]', msg, son, parent)

      if self.hierarchical:
        if not parentPMO:
          parentPMO = fig.findActor(parent)
          if parentPMO:
            rebuild = True
          else:
            nberrors+=1
            logging.warn('Missing %s Parent Actor [%s] for [%s]', msg, son, parent)
      else:
        for i,p in enumerate(parent):
          if not parentPMO[i]:
            parentPMO[i] = fig.findActor(p)
        
      if rebuild:
        self[k] = PMOLink(son, parent, sonPMO, parentPMO)
  
    return nberrors


  def writeData(self, fw, nextPfx):
    if self.hierarchical:
      for lnk in self.values():
        fw.write(nextPfx+"addChild "+lnk.son+'\n\t\t\t' + lnk.parent+ '\n')
    else: 
      for lnk in self.values():
        for otherName in lnk.parent:
          fw.write(nextPfx+"weld "+lnk.son+'\n\t\t\t'+otherName+'\n')



# 
class Figure():
  ''' This class represents a Poser Figure.  '''

  #    
  def __init__(self, pf, idx=0, frf=None):
    ''' Create an empty Figure.
    Suppose that the BODY:Idx exists.
    Parameters
    ----------
    pf : PoserFile
      Parent PoserFile
    idx : int, optional, default 0
      Figure index in the PoserFile (>0)
    frf : FigureResFile
      Create a new empty figure when "figureResFile" line is read.
    '''
    super(Figure, self).__init__()

    self._pf = pf
    #self._bodyIdx = idx

    #  figureResFile of the figure (single and shared with the PoserFile)
    self._bodyIdx = PoserConst.C_BAD_INDEX if idx==0 else idx
    self._lstActor = [ ] # Contain all parts of a Figure, including props and deformers
    #self._lstProp = [ ] # Attribut removed in V0.2
    #self._figDesc = None# Attribut removed in V0.2, replaced by a set of Figure class attributes

    self._printName = ''
    self._root = None # Root Actor Name
    self._childs = LinkDir() # Map (child's tree) sonName:PMOLink(son, parent, PoserMeshedObject)
    self._inkyChains = [ ] # List of inkyChain
    self._defaultPick = None
    self._displayOn = True
    self._linkParms = [ ]
    self._welds  = LinkDir(hierarchical=False) # Map (welding dependencies - not a tree -) sonName:PMOLink(son, parent, PoserMeshedObject)
    self._allowsBending = 1
    self._figureType = 1318
    self._origFigureType = 1318
    self._canonType = 8
    self._conforming = False
    self._lstMat = [ ] # Material list
    self._displayMode = None
    self._locked = False
    self._skinType = 0
    self._attribute = None    

    self._figureResFile = frf
    
    self._customData = None # Contain a Dictionnary of 'key' : custData()

    # Channels for computing actions
    self._lstCS = None

  def getBodyIndex(self):
    return self._bodyIdx

  def setBodyIndex(self, idx):
    self._bodyIdx = idx

  def getActors(self):
    ''' Return the list of all actors of the figure, including props, deformers '''
    return self._lstActor

  def getProps(self):
    ''' Return a filter list of actors on 'Prop' descendant '''
    return [ p for p in self.getActors() if isinstance(p, PoserProp) ]

  def getRoot(self): return self._root
  
  def setRoot(self, r):
    self._root = r

  def getRootActor(self):
    return self.findActor(self._root)
    
  #    
  def findActor(self, actorName, withIndex=True):
    ''' Return the actor of the given name (full name with :index) 
    Parameters
    ----------
    actorName : str
      Actor name with index (by default)
    withIndex : bool, optional, default True
      Indicates if name shall be searched with index (:1) or not
    Returns
    -------
    PoserActor
      The PoserActor, else None
    '''
    if withIndex:
      for a in self.getActors():
        if actorName == a.getName():
          return a
    else:
      for a in self.getActors():
        if actorName == a.getName()[:-2]:
          return a
      
    return None

  def findProp(self, propName):
    ''' Return the property of the given name (full name with :index) 
    Parameters
    ----------
    actorName : str
      Prop's name with index (by default)
    Returns
    -------
    PoserProp
      The PoserProp, else None
    '''
    for a in self.getProps():
      if propName == a.getName():
        return a
    return None

#   def setName(self, n): USe PrintName instead
#   def getName(self):

  # 
  # Return the name of the figure used by channel references
  #    
  def getRefName(self):
    return "Figure " + str(self._bodyIdx)

  # 
  # @return the printName
  #    
  def getPrintName(self):
    return self._printName

  # 
  # @param printName the printName to set
  #    
  def setPrintName(self, printName):
    self._printName = printName





  #    * Change the name of referenced part (actor, prop, hairProp, controlProp)  
  # 
  #    * @param oldPartName
  #    * @param newPartName
  def changeReference(self, oldPartName, newPartName, changeRefToBODY=True):
    ''' Change the name of a referenced part (actor, prop, hairProp, controlProp)  
    Parameters
    ----------
    oldPartName : str
      Previously Referenced part
    newPartName : str
      New reference part
    changeRefToBODY : bool, optional, default True
      Indicates if references to 'BODY:n' in Channels' operations shall be changed.
      Needed when an actor (that references BODY's channels) is reparented
    '''
    for actor in self.getActors():
      actor.changeReference(oldPartName, newPartName, changeRefToBODY=changeRefToBODY)

    # if (po.getPoserType() == PoserToken.E_root) or (po.getPoserType() == PoserToken.E_defaultPick):
    self._root = newPartName if self._root==oldPartName else self._root
    self._defaultPick = newPartName if self._defaultPick==oldPartName else self._defaultPick
    
    #  Change at figure definition level
    #  Change Attributes : addChild and weld
    self._childs.changeReference(oldPartName, newPartName)
    self._welds.changeReference(oldPartName, newPartName)

    for po in self._inkyChains:        
      for po2 in po.getLstAttr():
        if (po2.getPoserType() == PoserToken.E_goal) or (po2.getPoserType() == PoserToken.E_addLink):
          po2.TAS(oldPartName, newPartName)

  # 
  def rename(self, actor, nInternalName, nPrintName):
    ''' Change the names of an Actor in a Figure.
    Propagates the changes.

    Parameters
    ----------
    actor : PoserActor
      Actor to rename
    nInternalName : str
      new internal name without leading ":n"
    nPrintName : str
      new print name
  
    Returns
    -------
    int
      Ret Code
    '''
    oldIntName = actor.getName()
    if nInternalName != cleanName(oldIntName):
      posc = oldIntName.find(':')
      if posc > 0:
        nInternalName = nInternalName + oldIntName[posc:]

    #  Change the name in both definition and Data parts of the actor
    actor.setName(nInternalName)
    pf = self.getPoserFile()
    pf.changeReference(oldIntName, nInternalName)

    actor.setPrintName(nPrintName)
    return C_OK

  def addReadActor(self, pa):
    if self._figureResFile:
      pa.setFigureResFile(self._figureResFile)

    pa.setFigure(self)
    for lpa in self._lstActor:
      if pa.getName() == lpa.getName():
        return lpa

    self._lstActor.append(pa)
    return pa

  #  def addReadProp(self, pp): --> Use addReadActor as of V0.2

  #
  def addActor(self, parent, pa, changeRefToBODY=True):
    ''' Add actor pa as child of actor parent.
    if changeRetFoBODY is true, all reference including references to 'BODY'
    are replaced by the new parent.
    else only reference to other actors are changed

    Parameters
    ----------
    parent : PoserMeshedObject
      parent PoserMeshedObject (Prop or Actor)
    pa : PoserActor or PoserProp
      Actor to attach
    '''
    ldesc = pa.getFigure().getDescendant(pa)
    ldesc.insert(0, pa)
    idxSuffix = ":{0:d}".format(self.getBodyIndex())

    #  Figure indexes shall be changed in all moved actors    
    for act in ldesc:
      on = act.getName()
      nn = cleanName(on) + idxSuffix
      act.setName(nn)
      pa.getFigure().changeReference(on, nn)

    #  Other references like BODY:n shall be renamed too!
    ms = { vod.getGroupName() for act in ldesc for po in act.getChannels() for vod in po.getVOD() }

    for otherRefName in ms:
      nn = cleanName(otherRefName) + idxSuffix
      pa.getFigure().changeReference(otherRefName, nn)

    self._lstActor += ldesc

    #  Update child and weld trees
    pa.getFigure().changeReference(pa.getParent(), parent.getName(), changeRefToBODY=changeRefToBODY)
    self.createActorLinks(ldesc)

    #  Set the new parent figure
    pa.setFigure(self)
    if self._figureResFile:
      pa.setFigureResFile(self._figureResFile)


  #
  #
  def addMagnet(self, baseProp, deformerProp, sphereZone, masterChannelName=None, ctrlRatio=1.0, keys:'list of Tuple (key,value)'=None):
    ''' Add a Magnet to a Figure.
    Create the deformer channels in the pointed actors and optionaly bind them to a master Value Param.
    The controling channel is created either with a valueOpDeltaAdd or a valueOpKey.

    Parameters
    ----------
    baseProp : BaseProp
      Base Prop of the Magnet
    deformerProp : DeformerProp
      Deformer Prop of the Magnet
    sphereZone : SphereZoneProp
      Spheric Zone Prop of the Magnet
    masterChannelName : str, optional, default None
      Optional Master channel to control the magnet usage from the BODY

    ctrlRatio : float, optional, default 1.0
      Control Ratio of the valueOpDeltaAdd

    keys : list of Tuple (key,value), optional, default None
      List of tuples to use when a valueopKey is created. if None, a valueOpDeltaAdd is created.

    Returns
    -------
    int : Return Code
      C_OK
      C_UNKNOWN : When the smartParent (actor) of the magnet does not exists
      C_FAIL : When a deformer points to a missing actor
    '''
    ret = C_OK
    
    smartParent = baseProp.getAttribut(PoserToken.E_smarParent).getValue()

    actorDest = self.findActor(smartParent)
    if not actorDest:
      logging.warning("Figure[%s] has not Actor[%s] required by Magnet[%s]", self.getName(), smartParent, baseProp.getName())
      return C_UNKNOWN

    # Remove SmartParent attributs
    baseProp.deleteAttribut(PoserToken.E_smarParent.token)
    deformerProp.deleteAttribut(PoserToken.E_smarParent.token)
    sphereZone.deleteAttribut(PoserToken.E_smarParent.token)

    baseProp.setParent(actorDest.getName())
    deformerProp.setParent(baseProp.getName())
    sphereZone.setParent(actorDest.getName())

    ldesc = [baseProp, deformerProp, sphereZone]
    self._lstActor += ldesc
    self.createActorLinks(ldesc, weldActors=False)

    # Create Deformer Channels
    bodyName = self.getRoot() # PoserConst.C_BODY + ":" + str(self._bodyIdx)
    for targetName in [ po.getValue() for po in deformerProp.getLstAttr() if po.getPoserType()==PoserToken.E_deformTarget ]:
      targetActor = self.findActor(targetName)

      if targetActor: 
        dparm = targetActor.CreateDeformerP(deformerProp.getName(), sphereZone.getName(), deformerProp.getName(), isHidden=True)

        if masterChannelName:
          if keys:
            vop = ValueOpDelta(PoserToken.E_valueOpKey, self.getRefName(), bodyName, masterChannelName, keys=keys)
          else:
            vop = ValueOpDelta(PoserToken.E_valueOpDeltaAdd, self.getRefName(), bodyName, masterChannelName, ctrlRatio)
          
          dparm.addVOD(vop)
      else:
        logging.warning("Figure[%s] has no Actor[%s] for Magnet[%s]", self.getName(), targetName, deformerProp.getName())
        ret = min(ret, C_FAIL)

    return ret

  # def getFigureDesc(self):

  # Set the figureResFile.
  def setFigResFile(self, sa):
    self._figureResFile = sa

  # 
  # Get the figureResFile.
  #    
  def getFigResFile(self):
    return self._figureResFile

  def setFigResFileGeom(self, objFileName:str):
    '''
    Set the path to the OBJ file in the figureResFile.
    '''
    fn = objFileName.replace(os.sep, ':')
    self._figureResFile.setValue(fn)

  def getPoserFile(self):
    return self._pf

  def createPropagation(self, upperActor:str or PoserActor, parmName:str, destChannelType:PoserToken, ctrlRatio:float):
    ''' Create a valueParm in upperActor and propage it to all descendants at destChannelType level.
    Parameters
    ----------
    upperActor : str or PoserActor
      Actor or upper actor's name (without :index)

    parmName : str
      Name of new channel

    destChannelType : PoserToken
      Type of channel to control

    ctrlRatio : float
      Control Ratio of the valueOpDelatAdd created operation

    Returns
    -------
    int
      C_OK : Success
      C_FAIL : Actor not found or Missing target channel in some descendant
    '''
    res = C_OK
    vparm = GenericTransform(PoserToken.E_valueParm, parmName)
    vparm.setPrintName(parmName)
    upAct = self.findActor(upperActor, withIndex=False) if isinstance(upperActor, str) else upperActor
    if not upAct:
      logging.warning("Upper Actor[" + str(upperActor) + "] not found ")
      return C_FAIL
    
    upAct.addAttribut(vparm)
    ldesc = self.getDescendant(upAct)
    for pa in ldesc:
      gt = pa.getGenericTransform(destChannelType)
      if gt:
        vop = ValueOpDelta(PoserToken.E_valueOpDeltaAdd, self.getRefName(), upperActor.getName(), parmName, ctrlRatio)
        gt.addVOD(vop)
      else:
        logging.warning("Actor[" + pa.getName() + "] has no channel " + destChannelType.token)
        res = C_FAIL

    return res

  #TODO: Cleaning required
  def createChannelMorphList(self, InitSetTargetMorph):
    pa = self.getActors()[0]

    lstCS = ChannelMorphStatusList()
    if pa.getName().startswith(self.getRoot()[:-2]): # BODY"):
      # bodyIdx = pa.getIndex()

      lstdesc = self.getDescendant()

      #  Calculate the list of channels with regards to the known one
      pareel = self._pf.findActor(pa.getName())
      #channelsAttr = pareel.getChannels()

      for attr in pareel.getChannels():
        if attr.getPoserType() == PoserToken.E_valueParm:
          cs = ChannelMorphStatus(attr, InitSetTargetMorph)

          #  Channels where not found when Figure index was higher than 9 (2 digits)
          # idxRelPos = 3 if (bodyIdx > 9) else 2
          #  Since we are at "BODY" level, we should check if descendants have non null factors for this channel.
          for po in lstdesc:
            #channelsAttrDesc = po.getChannels()
            for attrDesc in po.getChannels():
              if attrDesc.getPoserType() == PoserToken.E_targetGeom and attrDesc.getName() == attr.getName():
                finalFactor = attrDesc.getKeysFactor(0)
                cs.hasNonNullDesc = (finalFactor != 0.0)
                cs.updateDelta(attrDesc)
                break

          lstCS.append(cs)

      #  FIX 20100704 : Channels where not found when Figure index was higher than 9 (2 digits)
      #idxRelPos = 3 if (bodyIdx > 9) else 2
      #  Now check for channels unknown at BODY level (head morph for example)
      for po in lstdesc:
        for attrDesc in po.getChannels():
          if attrDesc.getPoserType() == PoserToken.E_targetGeom:
            cs = lstCS.find(attrDesc.getName())
            if cs == None:
              cs = ChannelMorphStatus(attrDesc, InitSetTargetMorph)
              lstCS.append(cs)
            else:
              cs.updateDelta(attrDesc)

    self._lstCS = lstCS
    return lstCS

  def getChannelMorphList(self):
    return self._lstCS

  def getLstMaterial(self):
    return self._lstMat

  #
  # Return a PoserMaterial by name
  #
  def getMaterial(self, materialName:str):
    return next( (m for m in self._lstMat if m.getName()==materialName), None)    


  def addMaterial(self, mat:'PoserMaterial', replace=False):
    # Check if it does not already exists and find the last material position
    if not mat:
      return C_ERROR
    
    previous = next( (m for m in self._lstMat if m.getName()==mat.getName()), None)
    if previous:
      if replace:
        self._lstMat.remove(previous)
      else:
        return C_FAIL
      
    # The material was not in the Figure list or has been removed, Add it
    self._lstMat.append(mat)            
    
    return C_OK
  
  
  
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
  
  #
  # Options of the report algorithm
  # class ReportOption(object): Named Tuple from PoserMeshed
  #   translation     Translation between original MeshedObject and its localisation in this.
  #   maxDist         Maximal distance to take a point into account.
  #   enhance         Enhancement algorithm in C_NO_ENHANCEMENT, C_AVG_ENHANCEMENT, C_MLS_ENHANCEMENT.
  #   boundingType    Type of bounding in C_NO_BOUNDING, C_BOX_BOUNDING, C_SPHERE_BOUNDING
  #                   A vertex will get a calculated delta if it intersects the bounds.
  #   useVicinityLoop Use a viciniy determination algorithm to find the neighboor vertex of a face
  #                   with missing deltas. The average deplacement will be calculated on neighboor vertex list.
  #   alpha           Influence of distant point (less that one). alpha = 0.6 is usually a good value.
  #   minVectLen       Minimal value for displamcent vectors. Vectors with a norm smaller that minVecttLen will ne ignored
  #   PoserConst.C_OK when result is correct. PoserConst.C_ERROR when parameters are not correct.
  #    
  # @createDeltas.register(object, str, Figure, List, Set, ReportOption)
  # @createDeltas.register(object, str, PoserMeshedObject, Set, ReportOption)
  def createDeltas(self, poserRootDir, refFigObj, lstRefGeom, setTargetMorph, ropt):
    ''' Create in the current Figure the best deltas for the list of morph targets.
    This implementation starts with an extracted refFigure for optimisation purpose.

    Parameters
    ----------
    poserRootDir : str
      Root Dir of the installation (to find the .OBJ files)

    refFigure : str
       name of the figure that contains initial deltas

    setTargetMorph : set or list of str
      Morphs' names to create

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

    if isinstance(refFigObj, Figure):
      refMeshedObj = refFigObj
      if not lstRefGeom:
        pf = refFigObj.getPoserFile()
        lstRefGeom = pf.extractAll(poserRootDir, refFigObj.getBodyIndex(), None)
  
      #  Extract and Sort GeomCustom to get single numbered groups
      curPoserObject = self.getPoserFile()
      lstCurGeom = curPoserObject.extractAll(poserRootDir, self._bodyIdx, None)

    else: # refFigObj should be a PoserMeshedObject
      refMeshedObj = refFigObj

      curPoserObject = self.getPoserFile()
      #  Extract and Sort GeomCustom to get single numbered groups
      lstCurGeom = curPoserObject.extractAll(poserRootDir, self._bodyIdx, None)
      lstRefGeom = [ refMeshedObj.getBaseGeomCustom(poserRootDir), ]

    if not min( [ gc.isValid() for gc in lstCurGeom+lstRefGeom ] ):
      return C_FILE_NOT_FOUND

    for srcGC in lstCurGeom:
      srcWG = srcGC.getWaveGeom()

      tabMapping = calcMapping_KDTree(srcWG, lstRefGeom, ropt.translation, ropt.maxDist)

      #  Find the actor
      srcActor = curPoserObject.findActor(srcGC.getName())

      srcActor.findReportDeltas(refMeshedObj, srcGC, srcWG, tabMapping, setTargetMorph, ropt, checkBODYParm=True)
      
    return ret

  # TODO: Rework!!
  def updateOrCreateValueParm(self, channelName):
    ''' Create or Update a valueParm channel.
    Make it visible (not Hidden)

    Parameters
    ----------
    channelName : str
      Name of the channel to create or modify.

    Returns
    -------
    GenericTransform
      The found or created channel
    '''

    #  Check at BODY level, if valueParm exists
    bodyAct = self.getPoserFile().findActor(self.getRoot()) # "BODY:" + str(self._bodyIdx))
    for rt in bodyAct.getChannels():
      if (rt.getPoserType()==PoserToken.E_valueParm) and (rt.getName()==channelName):
        #  Ensure that it is a visible attribute
        rt.setHidden(False)
        return rt
      
    rt = GenericTransform(PoserToken.E_valueParm, channelName, None, None, None)
    bodyAct.addAttribut(rt)
    return rt


  # 
  def hideAfter(self, pa, hm):
    ''' Hide descendant actors of the given one.
    Parameters
    ----------
    pa : PoserActor
      Start Actor
    hm : bool
      Indicates to Hide the descendant actors in the Poser Menu    
    '''
    lstdesc = self.getDescendant(pa)
    for act in lstdesc:
      act.setHidden(True, hm)

  # 
  def delete(self, pa):
    ''' Delete an actor and its descendant actors or 
    Delete the given PoserProp from the list of props.
    OR
    Delete a material from the figure

    Parameters
    ----------
    pa : PoserActor or PoserProp or PoserMaterial
      object to delete

    Returns
    -------
    int
      C_OK : Success
      C_FAIL : Actor not found
    '''
    res = C_OK

    if isinstance(pa, PoserMeshedObject):
      lstdesc = [pa, ] + self.getDescendant(pa)
      setDelName = set()
      for act in lstdesc:
        try:
          actorName = act.getName()
          self._lstActor.remove(act)
          setDelName.add(actorName)
        except:
          res = C_FAIL
          
      # Finaly clean links (at once for the figure)
      #  Clean Figure Attributs : addChild and weld
      self._childs = LinkDir( { k:v for k,v in self._childs.items() if (v.son not in setDelName) and (v.parent not in setDelName) } )
      prevDict = self._welds        
      self._welds = LinkDir(hierarchical=False)
      for v in [ v for v in prevDict.values() if (v.son not in setDelName)]:
        for i,p in enumerate(v.parent): 
          if p not in setDelName:
            self._welds.lnkAdd(v.son, p, v.sonPMO, v.parentPMO[i])
        
    elif isinstance(pa, PoserMaterial): # pa should be a material
      try:
        self._lstMat.remove(pa)
      except:
        res = C_FAIL
    else:
      res = C_ERROR

    return res

  # 
  def getDescendant(self, paOrFirstName:str or PoserActor=None):
    ''' Return the list of actors which depends on given actor's name or actor object (PoserActor).

    Parameters
    ----------
    paOrFirstName : str or PoserActor, optional, default None
      Actor or actor's name (without :index)
      if None getDescendant returns the descendant of the root actor (usually BODY)

    Returns
    -------
    list of str or list of PoserActor
      A list of actors represented PoserActor or names (according to the call)
    '''
    if paOrFirstName:
      if isinstance(paOrFirstName, PoserMeshedObject):
        fn = paOrFirstName.getName()[0:paOrFirstName.getName().find(':')]
        lst = [ act for act in [ self.findActor(aname) for aname in self.getDescendant(fn) ] if act ]
      else:
        lst = [ paOrFirstName + ":" + str(self._bodyIdx) , ]        
        for lnk in self._childs.values():
          if lnk.parent in lst:
            lst.append(lnk.son)
              
        del lst[0]
    else:
      root = self.findActor(self.getRoot(), withIndex=True)
      lst = [ a for a in self._lstActor if a!=root ]
      
    return lst


  # 
  #    * @param pa
  #    * @param objFileName
  #    * @param adaptJCM
  #    * @param hideAfter
  #    * @param hideMenuAfter
  #    * @return
  def stump(self, pa, poserRootDir, objFileName, adaptJCM, hideAfter, hideMenuAfter):
    ''' Stump an actor of the figure with the given OBJ file.
    No more deleteAfter, because it gives bad results.

    '''
    if not pa in self._lstActor:
      return PoserConst.C_ACTOR_NOTFOUND

    #  Geometry of the limb in the original OBJ file
    bodyg = pa.getBaseGeomCustom(poserRootDir)
    
    #  Change Geometry definition
    pa.setBaseMesh(poserRootDir, objFileName)

    if hideAfter:
      self.hideAfter(pa, hideMenuAfter)

    #  2008AVR14 - AdaptJCM Tested ok
    if adaptJCM:
      #  Get Custom Geometry
      curg = pa.getBaseGeomCustom(poserRootDir)

      tabCur = curg.getWaveGeom().coordList

      for attr in pa.getChannels():
        if attr.getPoserType() == PoserToken.E_targetGeom and attr.getName().startswith("JCM"):
          dlt = attr.getDeltas()
          logging.info("Updating[%s] in %s : %d", attr.getName(), pa.getName(), len(dlt.deltaSet))

          nbIdx = 0
          for dp in dlt.deltaSet.values():
            pcur = bodyg.getWaveGeom().coordList[dp.noPt]

            dmin = sys.float_info.max
            res = -1
            for j,otherPt in enumerate(tabCur):
              d = pcur.distanceL1(otherPt)
              if d < dmin:
                dmin = d
                res = j
                
            if dmin < 1e-3:
              # log.info("Point[" + dp.getPointNo() + "] Found at (" + res + ") : " + dmin);
              dp.setPointNo(res)
              nbIdx += 1
            else:
              # log.info("Point[" + dp.getPointNo() + "] not exactly found " + dmin);
              dp.setPointNo(-1000)
               
          nt = { dp.noPt:dp for dp in dlt.deltaSet.values() if dp.getPointNo()>=0 }
          attr.setDeltaTab(nt)
          attr.setNumbDeltas(curg.getWaveGeom().getCoordListLength())
          logging.info("AdaptJCM[%s] : %d reported", attr.getName(), nbIdx)

    return C_OK

  # 
  def addAlternateGeom(self, pa, poserRootDir, objFileName, altChannelInternalName, altChannelName, pos):
    ''' Add an alternate geometry file to an actor of the figure.

    TODO: NOT IMPLEMENTED

    Parameters
    ----------
    pa : PoserActor
      Actor that receive the alternate geometry
    poserRootDir : str
      Root Dir of the installation (to find the .OBJ files)
   
    objFileName : str
      Path or relative path to the geometry file (.OBJ)

    pos : int
      Position of the geometry in the list of alternate geometries

    Returns
    -------
    int
    '''
    return NotImplemented
#     _res = C_OK
#     if pa in self._lstActor:
#       logging.warning("Not Implemented yet")
#     else:
#       _res = PoserConst.C_ACTOR_NOTFOUND
#     return _res

  #
  def extractGeometry(self, poserRootDir, lstpa=None, lstch=None):
    ''' Extract the geometries of the Figure.

    Parameters
    ----------
    lstpa : list of PoserActor, optional, default None
      List of PoserActor to extract, if none all actors are considered

    lst : ChannelMorphStatusList or set/list of channel names
      List of valueParm or targetGeom names to be used for Apply delta

    Returns
    -------
    list of GeomCustom
      List of Poser representation of a geometry (contains the WaveGeom object)
      Some may be None
    '''
    lstgeom = [ ]
    basegc = None
    resgc = None
    globalgc = None
    stm = lstch.getChannelSet() if isinstance(lstch, ChannelMorphStatusList) else lstch

    if not lstpa:
      lstpa = self.getActors() 

    for pa in lstpa:
      if pa.getGeomType()==PoserConst.GT_GLOBAL_OBJFILE:
        if not globalgc:
          basegc = pa.getFigureResFile().getGeomCustom(poserRootDir)
          if basegc and basegc.isValid():
            globalgc = GeomCustom(basegc)
            globalgc.findApplyDelta(self._bodyIdx, self._pf, stm)
          else:
            #  Probably due to a bad path
            return None

        resgc = globalgc.extractSortGeom(pa.getName(), pa.getGeomType())

      elif (pa.getGeomType()==PoserConst.GT_LOCAL_OBJFILE) or \
           (pa.getGeomType()==PoserConst.GT_INTERNAL):

        basegc = pa.getBaseGeomCustom(poserRootDir)
        localgc =  GeomCustom(basegc)
        localgc.findApplyDelta(self._bodyIdx, self._pf, stm)
        resgc = localgc.extractSortGeom(pa.getName(), pa.getGeomType())

      # elif pa.getGeomType()==PoserMeshedObject.GT_NONE:
      else:
        logging.warning("Unknown GeomType in (%s.%s):%d", self.getPrintName(), pa.getName(), pa.getGeomType())
        resgc = None

      lstgeom.append(resgc)

    return lstgeom

  #
  def getMorphedMesh(self, poserRootDir, lstch):
    ''' Return a morphed GeomCustom of the base geometry of the figure.

    Parameters
    ----------
    poserRootDir : str
      Root Dir of the installation (to find the .OBJ files)

    lst : ChannelMorphStatusList or set/list of channel names
      List of valueParm or targetGeom names to be used for Apply delta

    Returns
    -------
    GeomCustom
      The Poser representation of a geometry (contains the WaveGeom object)
    '''
    localgc = None
    stm = lstch.getChannelSet() if isinstance(lstch, ChannelMorphStatusList) else lstch
    basegc = self.getActors()[0].getFigureResFile().getGeomCustom(poserRootDir)
    if basegc and basegc.isValid():
      localgc = GeomCustom(basegc)
      localgc.findApplyDelta(self._bodyIdx, self._pf, stm)
    return localgc

  # 
  # @param poserRootDir
  # @param pf              the poser file
  # @param lstUsedActor    
  def getActiveGeometry(self, poserRootDir, lstUsedActor):
    ''' Find and load all geometries used by the figure. (including internal and replaced ones)
    Does not extract groups of each Geom, Does not applay any morph
    Main geometry (from figureResFile is stored first).

    Parameters
    ----------
    poserRootDir : str
      Root Dir of the installation (to find the .OBJ files)

    lstUsedActor : list
      Output parameters of actors concerned by a special geometry

    Returns
    -------
    list of GeomCustom
      List of Poser representation of a geometry (contains the WaveGeom object)
    '''
    lstActor = self.getDescendant()
    lstFusion = [ ]
    if not lstUsedActor:
      lstUsedActor = [ ]

    # for gn in lstActor:
    for actor in lstActor:
      if actor!=lstActor[0]:
        lstDesc = self.getWelded(actor.getName())
        #if lstDesc:
        for descGn in lstDesc:
          pa = self.findActor(descGn)
          if (pa.getGeomType()==PoserConst.GT_LOCAL_OBJFILE) or (pa.getGeomType()==PoserConst.GT_INTERNAL):
            locGeom = pa.getBaseGeomCustom(poserRootDir)

            lstUsedActor.append(pa)
            lstFusion.append(locGeom)

            # Modify the storage class of the Actor
            pa.setGeomType(PoserConst.GT_GLOBAL_OBJFILE)
            pa.setGeomGroupName(locGeom.getGroupName())

    return lstFusion

  # 
  def getWelded(self, firstName):
    ''' Return the list of actors which are connected or welded to given actor's name.
    Parameters
    ----------
    firstName : str
      Name of the actor

    Returns
    -------
    list of str
      List of unique names
    '''
    setres = set( lnk.son for lnk in self._welds.values() if firstName in lnk.parent )
    parentName = self.getWeldParent(firstName)
    if parentName:
      for p in parentName: 
        setres.add(p)
    return list(setres)

  # 
  def hasMultipleGeom(self):
    ''' Return a binary maps that indicates if the figure is composed of several geometries.
    
    Returns
    -------
    int
      PoserConst.C_OK : a single geometry is used and defined by FigureResFile attribut
      Bitmask of : C_HAS_INTERNAL, C_HAS_LOCAL_OBJFILE, C_HAS_ALT_GEOM
    '''
    retmask = 0
    lstActor = self.getDescendant()
    for actor in lstActor:
      if actor!=lstActor[0]:
        lstDesc = self.getWelded(actor.getName())
        #if lstDesc:
        for descGn in lstDesc:
          pa = self.findActor(descGn)
          if pa.getGeomType()==PoserConst.GT_LOCAL_OBJFILE:
            retmask |= PoserConst.C_HAS_LOCAL_OBJFILE
          else:
            if pa.getGeomType()==PoserConst.GT_INTERNAL:
              retmask |= PoserConst.C_HAS_INTERNAL
          if pa.getAltGeomList():
            gtalt = pa.getAltGeomChannel()
            valFrame0 = int(gtalt.getKeysFactor(0))

            if valFrame0 != 0:
              retmask |= PoserConst.C_HAS_ALT_GEOM

    return retmask

  # Remap morphs' deltas of actors' channels according to a list of index map.
  # Index map contains the new index of vertex for each geom group.
  # 
  # @param poserRootDir    Should not be used. Main geom supposed to be already loaded
  # @param lstUsedActor    list of actor to remap
  # @param outMapLst       list of index map tables
  #
  # TODO: Remap weightmap(s) also
  #
  def remapMorph(self, poserRootDir, lstUsedActor, outMapLst):
    ret = C_OK
    mainGeom = self.getFigResFile().getGeomCustom(poserRootDir).getWaveGeom()
    i = 0
    for i,pa in enumerate(lstUsedActor):
      tmpmap = outMapLst[i]

      grp = mainGeom.getGroup(pa.getGeomGroupName())

      nVertIdx = mainGeom.calcGroupVertIndex(grp)

      for gt in pa.getChannels():
        if gt.ishasDeltas():
          dlt = gt.getDeltas()
          for dp in dlt.getDeltaTab():
            wholeMapIdx = tmpmap[dp.getPointNo()]
            # pos = Arrays_binarySearch(nVertIdx, wholeMapIdx)
            pi = bisect_left(nVertIdx, wholeMapIdx)
            pos = pi if pi != len(nVertIdx) and nVertIdx[pi] == wholeMapIdx else -1
            if pos < 0:
              logging.warning("Morphs remapping error for " + pa.getGeomGroupName() + "." + gt.getName())
              ret = C_ERROR
            dp.setPointNo(pos)

    return ret

  # Imported table analysis 
  # @param  tabChan
  # @param  baseDir Location of geometries
  # @return a status table, null if check is impossible 
  def checkImportedChannels(self, tabChan, baseDir):
    baseDir = baseDir if baseDir.rfind(os.sep) == len(baseDir)-1 else baseDir + os.sep
    nblgn = len(tabChan)

    if nblgn < 9:
      logging.info("Too few lines in file [%d]",  nblgn)
      return None

    cia = ChannelImportAnalysis(self, baseDir, tabChan)
    cia.checkVocab()
    cia.checkColumns()
    
    for cd in cia.lstChan:
      cia.ts[0][cd.no] = cd.checkLink(self, baseDir)
    
    return cia

  
  #
  def importChannels(self, lstChanDest:list, poserRootDir, hideComputed=False):
    '''Import channel according to specifications contained by a list of ChannelDescriptor(s).
    
    Parameters
    ----------    
    lstChanDest : list
      list of ChannelDescriptor
      
    poserRootDir : str
      Location of Poser files
      
    hideComputed: boolean, optional, default False
      Hide computed parameters
    '''
    ret = C_OK
    for ccd in lstChanDest:
      if ccd.ret == C_OK:
        logging.info("Upgrading : " + ccd.act.getName())
        gt = ccd.gt
        if gt:
          logging.info("Overriding Channel[" + gt.getName() + "]")
        else:
          gt = GenericTransform(ccd.chanType, ccd.chanName)
          gt.setPrintName(ccd.printName)
          ccd.act.addAttribut(gt)
          logging.info("Creating Channel[" + gt.getName() + "]")

        # Set standard values
        
        # Do not override the initValue, if it has not been given
        if ccd.initValue!=None: 
          gt.setInitValue(ccd.initValue)
          gt.addKeyFrame(0, ccd.initValue)
          
        gt.setMin(ccd.min)
        gt.setTrackingScale(ccd.trackingScale)
        gt.setForceLimits(1)
        gt.setInterpStyleLocked(1)
        gt.setHidden( (hideComputed and ccd.lstOps) or ccd.isHidden )
        
        # Create the list of Alternate Geometries
        if ccd.chanType==PoserToken.E_geomChan:
          for fic in ccd.lstAltFiles:
            ccd.act.addAltGeom(altGeomFile=fic, poserRootDir=poserRootDir)
          ccd.max = len(ccd.act.getAltGeomList())
         
        elif ccd.chanType==PoserToken.E_targetGeom: # Perform a Morph import
          wg = readGeom(ccd.lstAltFiles[0].getCanonicalPath())
          grp = wg.getGroup(ccd.groupName) if ccd.groupName else wg.getGroups()[0]
          if not grp:
            logging.warning("  Morph Group not found for Channel[%s] : %s %s", gt.getName(), ccd.lstAltFiles[0], ccd.groupName if ccd.groupName else 'default')
            ret = min(ret, C_FAIL)
            continue
          ret = min(ret, ccd.act.createMorph(poserRootDir, grp, ccd.chanName, altGeomNo=ccd.altGeomNo)) # , minVectLen=minDist)

        elif ccd.chanType==PoserToken.E_shaderNodeParm:
          # Link the Material.Node.NodeInput.parmR to the new channel
          ccd.ni.setParmR(ccd.chanName)

        # The number of alternate geom, could have changed
        gt.setMax(ccd.max)
        for vod in ccd.lstOps:
          logging.info("  Adding Op to Channel[" + gt.getName() + "] : " + vod.getPoserType().token + "(" + vod.l1 + "." + vod.l2 + ")")
          gt.addVOD(vod)

      else:
        logging.info("Skipping channel:%s (%d)", ccd.chanName, ccd.no)
    return ret

  def getChannel(self, pa, expr):
    ''' Find the channel that matches the given expression.

    QualifiedChannelName = [ActorName [':' bodyIndex] '.' ]ChannelName
   
    NB :if the optional body index is different form the body index of the figure, 
    the returned channel could belong to another figure or prop.
    
    Parameters
    ----------
    expr : str
      Expression defining the channel to find
       
    Returns 
    -------
    GenericTransform : 
      The found channel or null if not found
    '''

    channelName = expr
    ptind = expr.find('.')
    if ptind >= 0:
      # Extract the real channel name
      channelName = expr[ptind + 1:]
      actorName = expr[0:ptind]

      # Find the target actor
      actind = index(actorName)
      if actind <= 0:
        # No ':' the actor should belong to the current figure
        actorName = actorName + ':' + str(self._bodyIdx)

      pa = self.findActor(actorName)

    return pa.getChannel(channelName) if pa else None

  # Create a valueParam at Body level to drive the visibility of each Actor
  # @return PoserConst.C_OK
  def addDrivenVisibility(self, vpPrefix = 'HideShow_'):
    ret = C_OK
    lstAct = self.getActors()
    bodyName = self.getRoot() # PoserConst.C_BODY + ":" + str(self._bodyIdx)
    body = self._pf.findActor(bodyName)
    for pa in lstAct:
      if pa != body:
        driverVPName = vpPrefix + cleanName(pa.getName())

        visChan = pa.getGenericTransform("visibility")

        # Create the visibility channel, if it does not exist
        if not visChan:
          visChan = GenericTransform(PoserToken.E_visibility, 'visibility')
          visChan.setInitValue(1.0)
          visChan.setMin(0.0)
          visChan.setMax(1.0)
          visChan.setTrackingScale(1.0)

          keys = Keys() # Default keys are static=0
          keys.addKey(0, 0.0)
          visChan.addAttribut(keys)

          vod = ValueOpDelta(PoserToken.E_valueOpDeltaAdd, self.getRefName(), bodyName, driverVPName, 1.0)
          visChan.addVOD(vod)
          logging.info("Adding Channel[visibility] to " + self.getPrintName() + "." + pa.getName())
          pa.addAttribut(visChan)

        # Check driver channel
        driverChan = body.getGenericTransform(driverVPName)
        if not driverChan:
          driverChan = body.updateOrCreateVP(driverVPName, minVal=0.0, maxVal=1.0, applyLimits=True, isHidden=False)
          keys = Keys() # Default keys are static=0
          keys.addKey(0, 1.0)
          driverChan.addAttribut(keys)
          logging.info("Adding Driver Channel[" + driverVPName + "] to " + self.getPrintName())
          body.addAttribut(driverChan)

        # Remove the object from menu
        pa.setAddToMenu(False)
        pa.setHidden(True)
    return ret

  def appendCheckMat(self, pa, gc, pm, lstUse):
    wg = gc.getWaveGeom()
    lstMat = wg.getMaterialList()
    if (pm.getName() if isinstance(pm, PoserMaterial) else pm) in lstMat:
      lstUse.append([ pa.getName(), PoserConst.GEOMTYPE[pa.getGeomType()], pa.getDisplayName() ] )

  #  Checkif the material is used in any geometry of the figure.
  #  @param pm Material Name or PoserMaterial
  #  @param lstUse
  #  @return    PoserConst.C_OK means used, PoserConst.C_FAIL means not used
  def checkMaterialUsage(self, pm, poserRootDir, lstUse):
    for pa in self.getActors():
      if pa.getGeomType() != PoserConst.GT_NONE:
        self.appendCheckMat(pa, pa.getBaseGeomCustom(poserRootDir), pm, lstUse)

      for ag in pa.getAltGeomList():
        fn = getRealPath(poserRootDir, ag.getGeomFileName())
        gc = GeomCustom(fn)
        if gc.isValid():
          self.appendCheckMat(pa, gc, pm, lstUse)

    return C_OK if len(lstUse) > 0 else C_FAIL


  #
  #  Return the list of actors and deformers that match the pattern
  #
  def findDeformer(self, pattern):
    lstRes = [ (act.getName(), gt.getName()) for act in self.getActors() for gt in act.getChannels() if (gt.getPoserType()==PoserToken.E_deformerPropChan) and gt.getName().startswith(pattern) ]
    return lstRes

  #
  #  Add a master control channel
  #  @param pattern
  #
  def addMasterChannel(self, channelName, pattern):
    res = C_OK
    bodyName = self.getRoot() # "BODY:" + str(self.getBodyIndex())
    body = self.findActor(bodyName)
    masterGT = GenericTransform(PoserToken.E_valueParm, channelName)
    masterGT.setMin(-1.0)
    masterGT.setMax(1.0)
    masterGT.setInterpStyleLocked(0)
    masterGT.setPrintName(channelName)
    body.addAttribut(masterGT)

    for act in self.getActors():
      for gt in act.getChannels():
        if (gt.getPoserType()==PoserToken.E_deformerPropChan) and gt.getName().startswith(pattern):
          vop = ValueOpDelta(PoserToken.E_valueOpDeltaAdd, self.getPrintName(), bodyName, channelName, 1.0)
          gt.addVOD(vop)

    return res


  # 
  def cleanAllChannel(self, pattern):
    ''' Clean (delete) all channels with a name that starts with the pattern and without any descendant. '''

    # Build the map of all targetGeom and valueParm with empty deltas   
    lstgt = [ gt for pa in self.getActors() for gt in pa.getChannels()  \
              if ((gt.getPoserType()==PoserToken.E_targetGeom) or (gt.getPoserType()==PoserToken.E_valueParm)) \
              and (not gt.ishasDeltas()) and gt.getName().startswith(pattern) ]

    logging.info("Candidates Channels:%d for %s", len(lstgt), pattern)

    pf = self.getPoserFile()
    mapgtl = pf.getGTLinks()
    
    lstgtl = [ mapgtl[gt.getQualifiedName()] for gt in lstgt ]
    
    nbdescl1 = sum( [len(gtl.desc)==0 for gtl in lstgtl] )
    
    while(lstgtl and nbdescl1>0):
      ngtl = next( gtl for gtl in lstgtl if len(gtl.desc)==0 )
      gt = ngtl.gt
      logging.info("Channel " + gt.getName() + " can be deleted in " + gt.getPoserMeshedObject().getName())      
      lstgtl.remove(ngtl)
      gt.getPoserMeshedObject().deleteChannel(gt)
      
      # Remove the channel link from the GTLinks Map and update descendant sets
      pf.delGTLink(gt)
      
      nbdescl1 = sum( [len(gtl.desc)==0 for gtl in lstgtl] )
    #Wend
    return C_OK

  # 
  # @param pattern
  def cleanMagnetMaterial(self):
    ''' Clean (delete) all custom materials attached to the magnets of the figure.
    Set Custom Material to False (0)
    '''
    for pp in self.getProps():
      # Check if the Prop is a : BaseProp, SphereZoneProp, MagnetDeformerProp, CurveProp
      if (pp.getCustomMaterial() == 1) and ((isinstance(pp, (BaseProp, ))) or (isinstance(pp, (BaseProp, ))) or (isinstance(pp, (BaseProp, ))) or (isinstance(pp, (BaseProp, )))):
        pp.getLstAttr()[:] = [ m for m in pp.getLstAttr() if pp.getPoserType()!=PoserToken.E_material ]
        # logging.info("Cleaning Material " + pp.getName() + " mat=" + po.getName())
    return C_OK

  # Usage not confirmed anymore
  #   def adaptMagnet(self, poserRootDir, initialGeomFile):
  #     raise(Exception, "not Implemented yet")


  def attachActor(self, parent:'new Parent Actor', srcAct:'Actor to attach from another figure', changeRefToBODY=True,\
                  withProp=True, withDeformer=False):
    ''' Attach an actor from a figure as child of another actor of another figure. (More or less a cut and paste).
    Relink all internal relationships of srcActor.
    Create in the destination figure the root valueParm to satisfy srcActor links
    
    Parameters
    ----------
    parent : PoserActor
      Parent actor to attach a new child
    srcAct : PoserActor
      Actor to attach from another figure
    changeRefToBODY : bool, optional, default True
      Indicates if references to Root (BODY) channels (in srcAct) shall be changed
    Returns
    -------
    int :
      Ret Code
    ''' 
    ret = C_OK

    # Retrieve all srcAct Desc and attached chanels
    srcFig = srcAct.getFigure()
    ldesc = srcFig.getDescendant(srcAct)
    ldesc.insert(0, srcAct)
    idxSuffix = ":{0:d}".format(self.getBodyIndex())

    ldescNames = [ act.getName() for act in ldesc ]

    setExternChannels =  \
     { vod for act in ldesc for po in act.getChannels() for vod in po.getVOD()\
          if vod.getGroupName() not in ldescNames }

    # Recreate channels in the destination figure (may not be only at BODY level)
    for vod in setExternChannels:
      targetActorName = cleanName(vod.getGroupName()) + idxSuffix
      act = self.findActor(targetActorName)
      if act:
        refChan = act.updateOrCreateVP(vod.getChannelName())

        tAct = srcFig.findActor(vod.getGroupName())
        tAct = tAct if tAct else srcFig.findActor(vod.getGroupName(), withIndex=False)
        if tAct:
          srcChannel = tAct.getChannel(vod.getChannelName())
          refChan.copy(srcChannel)
        else:
          logging.warning('Target Actor(%s) pointed by Operator:%s not found', vod.getGroupName(), vod.__class__.__name__)
      else:
        logging.warning('Target Name(%s) pointed by Operator:%s not found', targetActorName, vod.__class__.__name__)

    # Attache (all) Materials of the srcAct actor figure
    for mat in srcFig.getLstMaterial():
      r = self.addMaterial(mat)
      logging.info('Figure[%s]: Material[%s] from Actor[%s] %s', self.getPrintName(), mat.getName(), srcAct.getName(), \
                   'added' if r==C_OK else 'NOT added') 

    # Attach srcAct to parent + Update AddChild + Copy Weld Parts
    self.addActor(parent, srcAct, changeRefToBODY=changeRefToBODY)

    return ret


 
  def getWeldParent(self, partName):
    ''' Return the list of welded parts. Never None '''
    try:
      return self._welds[partName].parent
    except KeyError:
      return [ ]
 
 
 
  # 
  #  Add the list of actors as starting from pa, following pa's figure child and weld trees
  #  * @param parent
  #  * @param pa
  #    
  # def addActor(self, parent, ldesc, weldActors=True):
  def createActorLinks(self, ldesc, weldActors=True):
    self._childs.update( { pfils.getName():PMOLink(pfils.getName(), pfils.getParent(), pfils, self.findActor(pfils.getName())) for pfils in ldesc } )

    if weldActors:
      for pfils in ldesc:
        for gwp in pfils.getWeldParent():
          self._welds.lnkAdd(pfils.getName(), gwp, pfils, self.findActor(gwp))

  
  def checkActorLinks(self):
    ''' Check all actors links in all figure's actors (and props) '''
    # Check the AddChild table
    nberrors =   self._childs.checkActorDico(self)
        
    # Check the Weld table
    nberrors += self._welds.checkActorDico(self)
 
    # Check the Root actor
    root = self.findActor(self._root)
    if not root:
      nberrors+=1
      logging.warn('Missing Actor Root: %s', self._root)
      
    for act in self.getActors():
      parentName = act.getParent()
      
      if parentName=='UNIVERSE':
        if self.getPoserFile()._universe:
          continue
        else:
          nberrors+=1
          logging.warn('Missing Declared Parent Actor: %s for %s', parentName, act.getName())        
      else:
        p = self.findActor(parentName)
        if not p:
          nberrors+=1
          logging.warn('Missing Declared Parent Actor: %s for %s', act.getParent(), act.getName())
        
      
    return nberrors
  
 
  def __copyMat(self, fp, lstMat):
    if not fp.name:
      fp.status(C_FAIL, 'Material Source Undefined is illegal in {:s}', fp.geomGroup.getName())
      return
    
    if fp.name[0]=='{' and fp.name[-1]=='}':
      try:                
        mapMat = eval(fp.name)
        if isinstance(mapMat, dict):                  
          for srcMatName, destMatName in mapMat.items():                    
            srcMat = fp.geomGroup.getMaterial(srcMatName) # , inCustom=True)
            if srcMat:
              # Rename the new material
              nMat = PoserMaterial(src=srcMat)
              nMat.setName(destMatName)
              self.addMaterial(nMat, replace=True)
            else:
              fp.status(C_FAIL, 'Material Source [{:s}] not found in {:s}', srcMatName, fp.geomGroup.getName())
        else:
          fp.status(C_FAIL, 'Material Map [{:s}] Syntax Error:{:s}', fp.geomGroup.getName(), fp.name)
          
      except (SyntaxError, NameError) as se:
        estr = 'Syntax Error in Material Map' + str(type(se)) + ' ==> ' + str(se.args) + '(' + str(se) + ')'      
        fp.status(C_FAIL, 'Material Map [{:s}] {:s}', fp.geomGroup.getName(), estr)
    else:
      for mat in (lstMat if fp.name=='*' else [ fp.geomGroup.getMaterial(fp.name), ]):
        self.addMaterial(PoserMaterial(src=mat), replace=True)


  def __transformGeom(self, grp, fp:'FigurePart'):
    ''' Create a copy of the grp with defined transformations: translation, symetry, rotations
    
    Parameters
    ----------
    fp: FigurePart
      Description of the actor.
      Used fields are: geomGroup, translation, rotation, orientation, center
    
    Return
    ------
    int,GeomGroup : Return Code, The GeomGroup (none if error)
    
    '''
    ret = C_OK
    
    # Avoid Useless job
    if not fp.rotation and not fp.translation:
      return ret, grp
    
    # First do a deep copy of the group into a new optimized WaveGeom
    nwg = grp.geom.copy(groups=grp)    
    grp = nwg.getGroups()[0]
    
    AxisOrder, _ = fp.getOrientation(grp)
      
    try:
      # Compute Actor's center
      bc = fp.getBaryCentre(grp)
  
      # Manage Geomery Rotation first
      if fp.rotation:
        vri = fp.getRotation(grp)
        grp.rotate(*vri, *bc, AxisOrder)
              
      # Manage Translation
      if fp.translation:
        tr = fp.getTranslation(self, bc, grp)
        grp.translate(*tr)  
        
    except UsageError:
      exc_type, exc_value, exc_tb = sys.exc_info()
      traceback.print_exception(exc_type, exc_value, exc_tb)
      # Input Error have already been managed and logged
      ret = fp.ret
      #ret = fp.status(C_FAIL, 'Computation error for [{:s}]:', grp.getName(), str(ve))

    return ret, grp

    
 
  def createMechanical(self, lstParts:'list of FigurePart', optimize=True):
    ''' Create the actors described by a set of FigurePart(s) into the current figure.
    Current figure is mostly empty.
    At the end of the process, the resulting figure's geometry is saved.
    Individual status of FigurePart analysis are stored in their LogStatus fields.
    
    * 1st FigurePart shall be the figure description
    * 2nd FigurePart shall be the BODY (aka Root Actor)
    * Other FigurePart are either actor or just geometry to add to the previous actor
    
    Parameters
    ----------
    lstParts : list of FigurePart
      List of Figure Parts that describe actors, fusioned geometries, materials
      
    lstStatus : Will be filled with a list of ret codes  
    
    optimize : bool, optional, default True
      When True, the figure's main geometry is optimized before saving.
    
    Return
    ------
    int : Status of the creation
    '''
    
    # Compute the max level of the figure
    maxLevel = max( fp.level for fp in lstParts )
    
    figfp = lstParts.pop(0)
    
    frf = FigureResFile()
    frf.setName(PoserToken.E_figureResFile.token)
    self.setFigResFile(frf)
    self.setFigResFileGeom(figfp.geom)
    self.setPrintName(figfp.printName)
    
    curLevelActor = [None]*(maxLevel+1)
    
    # Create the 'Root' of the character, without any geometry
    bodyfp = lstParts.pop(0)
    
    srcWG = bodyfp.geom if bodyfp.geom else WaveGeom()
    
    fullCopy = True
    if bodyfp.oplst and bodyfp.oplst[0]=='add':
      # Add the whole source geometry to the final geometry
      # Create a Deep copy of the input geom
      wg = srcWG.copy()
    else:
      # Create an empty geometry
      wg = WaveGeom()
      fullCopy = False
      
    # Set The geometry
    frf.setGeomCustom(wg)
    
    idxSuffix = ":{0:d}".format(self.getBodyIndex())

    bodyAct = PoserActor(Name=cleanName(bodyfp.name) + idxSuffix)
    bodyAct.setPrintName(bodyfp.printName)
    bodyAct.setPoserFile(self.getPoserFile())
    self._lstActor.append(bodyAct)
    bodyAct.setFigure(self)
    bodyAct.setFigureResFile(self._figureResFile)
    
    # Create the Root actor with an empty FigurePart
    #grp:'GeomGroup', translation=None, rotation=None, orientation=None, center=None):
    bodyAct.createDefaultChannels(FigurePart(center='(0.0,0.0,0.0)')) # None, '', '', '', '(0.0,0.0,0.0)')

    self.setRoot(bodyAct.getName())
    self._defaultPick = bodyAct.getName()
    
    curLevelActor[0] = bodyAct
    prevLevel = 0
      
    for fp in lstParts:
      # logging.info('FigurePart[%d]:%s', partNo, str(fp))
      
      if fp.partType[:3]=='act': # Actor Creation
        # Check level consistency
        if fp.logCond(fp.level<=0 or curLevelActor[fp.level-1] is None, \
                      f'Unconsistent level for part:{fp.name}'):
          continue
        
        act = PoserActor(Name=cleanName(fp.name) + idxSuffix)
        act.setPrintName(fp.printName)
        #  Set the new parent figure
        act.setPoserFile(self.getPoserFile())
        act.setFigure(self)
        act.setFigureResFile(self._figureResFile)
        # Manage Menu/Access to the actor
        act.setParent(curLevelActor[fp.level-1].getName())
        # Add (link) to parent actor in Figure
        self._lstActor.append(act) # += ldesc
        #  Update child and weld trees
        self.createActorLinks([ act, ])
        
        curLevelActor[fp.level] = act
        prevLevel = fp.level

        act.setHidden(fp.hidden)
        act.setAddToMenu(fp.addToMenu)
        act.setCastsShadow(True) # FIX: To have shadows on each parts
        act.setVisible(True)
        act.setDisplayMode('USEPARENT')
        act.addAttribut(SimpleAttribut(PoserToken.E_backfaceCull, '0'))
        act.addAttribut(SimpleAttribut(PoserToken.E_visibleInReflections, '1'))
        act.addAttribut(SimpleAttribut(PoserToken.E_visibleInRender, '1'))
        act.addAttribut(SimpleAttribut(PoserToken.E_visibleInCamera, '1'))
        act.addAttribut(SimpleAttribut(PoserToken.E_visibleInIDL, '1'))
        act.addAttribut(SimpleAttribut(PoserToken.E_displacementBounds, '0'))
        act.addAttribut(SimpleAttribut(PoserToken.E_shadingRate, '0.2'))
        act.addAttribut(SimpleAttribut(PoserToken.E_smoothPolys, '1'))

        # Set the geometry
        if fp.geom==srcWG:
          act.setGeomType(PoserConst.GT_GLOBAL_OBJFILE)
          act.setGeomGroupName(fp.geomGroup.getName())
          
          if not fullCopy: # The final geometry does not contain the GeomGroup
            # The final geometry was empty
            wg.addGroup(fp.geomGroup)
            
        else: # The geometry source for this actor is not the global source
          if fp.oplst and 'add' in fp.oplst:
            act.setGeomType(PoserConst.GT_GLOBAL_OBJFILE)
            act.setGeomGroupName(fp.geomGroup.getName())
            # Copy the GeomGroup into the final geometry
            wg.addGroup(fp.geomGroup)
            
          elif fp.oplst and 'reuse' in fp.oplst: #  Reuse a Previously added/created geometry
            # In such case, geomGroup is a string
            # Check if the Geometry has really been created
            realGrp = wg.getGroup(fp.geomGroup)
            if not realGrp:
              fp.status(C_FAIL, f'Actor [{fp.name}] has no group [{fp.geomGroup}]')
            
            act.setGeomType(PoserConst.GT_GLOBAL_OBJFILE)
            act.setGeomGroupName(fp.geomGroup)
            fp.geomGroup= realGrp
          else:
            # The Geometry will be loaded from another file
            act.setGeomType(PoserConst.GT_LOCAL_OBJFILE)
            act.setGeomFileName(fp.geom.getName())          
            act.initBaseGeomCustom(fp.geom)

        # Create Default Channels
        act.createDefaultChannels(fp)
        
      elif fp.partType[:3]=='geo': # Geometry add to previous actor's GeomGroup
        # Retrieve previous actor GeomGroup in the final geometry
        prevGrp = wg.getGroup(curLevelActor[prevLevel].getGeomGroupName()) # TODO Check LOCAL/GLOBAL if 
        
        # The part comes for the global source and it has been copied
        if fp.geom==srcWG and fullCopy:
          # The part should be in the global copied source
          partGeom = wg.getGroup(fp.geomGroup.getName())
          # prevGrp.fusion(partGeom)
          if 'combine' in fp.oplst:
            # Delete the duplicate (the source geom)
            wg.removeGroup(partGeom)
            
        else: # The part comes from another WaveGeom
          partGeom = fp.geomGroup
          
        # Do some transform(s) before fusion (do not alter the source)
        ret, partGeom = self.__transformGeom(partGeom, fp)
        
        if ret==C_OK:
          # Finaly fusion the result with the previous Group
          prevGrp.fusion(partGeom)

      elif fp.partType[:3]=='mat': # Add a Material to the figure
        if isinstance(fp.geom, dict):
          for wfmat in fp.geom.values():
            self.addMaterial(PoserMaterial(wfmat), replace=True)
          
        elif isinstance(fp.geomGroup, Figure):
          self.__copyMat(fp, fp.geomGroup.getLstMaterial())  
            
        elif isinstance(fp.geomGroup, PoserMeshedObject): # partGeom is supposed to be an Actor/Prop
          if fp.geomGroup.getCustomMaterial():
            self.__copyMat(fp, [ a for a in fp.geomGroup.getLstAttr() \
                          if a.getPoserType()==PoserToken.E_material ] )  
          else:
            fp.status(C_FAIL, f'Actor [{fp.geomGroup.getName()}] has no custom material')
            
        else:
          fp.status(C_FAIL, f'Actor [{fp.geomGroup.getName()}] illegal type')
          
      else:
        fp.status(C_FAIL, f'Unknow part type:{fp.partType}')
    #End of for 'FigurePart'
    
    # Create file of the final geometry
    ret = min(fp.ret for fp in  lstParts)
    if ret==C_OK:
      if optimize:
        wg.optimizeGroups(cleaning=True)
      
      ret = wg.save(figfp.geom)
    
    return ret
    #End of createMechanical
 

  # Read Figure Description Chapter
  def read(self, st):
    code,cn,val = st.getLine()
    while (code!=PoserFileParser.TT_EOF) and (code!=PoserFileParser.TT_RIGHTBRACKET):
      if code==PoserFileParser.TT_WORD:
        try:
          vc = Lang[cn]
          #  Known word
          if vc==PoserToken.E_name:
            self.setPrintName(val)

          elif vc==PoserToken.E_root:
            self._root = val

          elif vc==PoserToken.E_addChild: # Two lines attribute
            _,nw = st.getFullLine()
            self._childs.lnkAdd(val, nw, self.findActor(val), self.findActor(nw))

          elif vc==PoserToken.E_defaultPick:
            self._defaultPick = val

          elif vc==PoserToken.E_linkParms: # 4 lines attribute
            sa = LinkParmsSA()
            sa.setName(cn)
            sa.read(st, val)
            self._linkParms.append(sa)

          elif vc==PoserToken.E_weld: # Two lines attribute
            _,nw = st.getFullLine()
            self._welds.lnkAdd(val, nw, self.findActor(val), self.findActor(nw))

          elif vc==PoserToken.E_allowsBending:
            self._allowsBending = val

          elif vc==PoserToken.E_figureType:
            self._figureType = val

          elif vc==PoserToken.E_canonType:
            self._canonType = val

          elif vc==PoserToken.E_displayMode:
            self._displayMode = val

          elif vc==PoserToken.E_locked:
            self._locked = (val[0] == "1")

          elif vc==PoserToken.E_skinType:
            self._skinType = val
            
          elif vc==PoserToken.E_displayOn:
            self._displayOn = (val[0] == "1")

          elif vc==PoserToken.E_origFigureType:
            self._origFigureType = int(val)

          elif vc==PoserToken.E_conforming:
            self._conforming = (val[0] == "1")
            
          elif vc==PoserToken.E_attribute:
            self._attribute = val

          elif vc.isStructured: # Material or inkyChain
            sta = create(vc, val)

            self.addAttribut(sta)

            #  Read the opening bracket
            code,cn,_ = st.getLine()
            if code==PoserFileParser.TT_LEFTBACKET:
              sta.read(st)
            else:
              if sta.isAmbi():
                st.pushBack()
              else:
                logging.warning( "Line[%s]: '{' is missing for %s", st.lineno, cn)
          else:
            logging.info("Line[%s] - Illegal word:%s in Figure[%s]", st.lineno(), cn, self._printName)

        except KeyError: #  Mot inconnu
          logging.info("Line[%s] - Unknown word:%s", st.lineno(), cn)

      #  Get next line
      code,cn,val = st.getLine()
      # Wend
    #End of read()

  def addAttribut(self, po):
    if po.getPoserType()==PoserToken.E_inkyChain:
      self._inkyChains.append(po)
    elif po.getPoserType()==PoserToken.E_material:
      self._lstMat.append(po)
    elif po.getPoserType()==PoserToken.E_customData:
      self._customData = po
    else:
      logging.info("Figure[%s] - Illegal structured:%s", self._printName, po.getPoserType().token)
      

  # Write the definition part of the meshed object.
  def writeDef(self, fw, pfx):
    self._figureResFile.write(fw, "")

    for pa in self._lstActor:
      pa.writeDef(fw, "")

    #for pp in self._lstProp:
    #  pp.writeDef(fw, "")

  # Write the Data part of the meshed object.
  def writeData(self, fw, pfx):
    self._figureResFile.write(fw, "")

    for pa in self._lstActor:
      pa.writeData(fw, "")

    # Write FigureDescription part
    nextPfx = pfx + "\t"
    fw.write(f"{pfx}figure\n{nextPfx}{{\n")
    fw.write(f"{nextPfx}name {self._printName}\n")
    fw.write(f"{nextPfx}root {self.getRoot()}\n")
    
    self._childs.writeData(fw, nextPfx)

    for po in self._inkyChains:        
      po.write(fw, nextPfx)

    fw.write(f"{nextPfx}defaultPick {self._defaultPick}\n")
    WBoolLine(fw, nextPfx, "displayOn", self._displayOn)

    for po in self._linkParms:
      po.write(fw, nextPfx)

    self._welds.writeData(fw, nextPfx)

    fw.write(f"{nextPfx}allowsBending {self._allowsBending}\n")
    fw.write(f"{nextPfx}figureType {self._figureType}\n")
    fw.write(f"{nextPfx}origFigureType {self._origFigureType}\n")
    fw.write(f"{nextPfx}canonType {self._canonType}\n")
    WBoolLine(fw, nextPfx, "conforming", self._conforming)

    for po in self._lstMat:
      po.write(fw, nextPfx)

    if self._displayMode:
      fw.write(f"{nextPfx}displayMode {self._displayMode}\n")

    WBoolLine(fw, nextPfx, "locked", self._locked )
    fw.write(f"{nextPfx}skinType {self._skinType}\n")
    if self._attribute:
      fw.write(f"{nextPfx}attribute {self._attribute}\n")
      
    # Write Custom Data if any  
    if self._customData:
      self._customData.write(fw, nextPfx)
      
    fw.write(f"{nextPfx}}}\n")


