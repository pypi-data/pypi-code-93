# -*- coding: utf-8 -*-
import logging

from pypos3d.wftk.WFBasic import getOBJFile
from pypos3d.wftk.PoserFileParser import PoserFileParser, OBJ_FNAT
from pypos3d.wftk.WaveGeom import WaveGeom

from pypos3d.pftk.PoserBasic import PoserConst, PoserToken, getRealPath
from pypos3d.pftk.SimpleAttribut import SimpleAttribut
from pypos3d.pftk.StructuredAttribut import StructuredAttribut, GenericTransform

class GeomCustom(StructuredAttribut):
  ''' This class represents the geometry of a Poser Meshed object.
  Either read from an .OBJ (or a compressed .OBZ) file or from the embedded lines 
  between brackets in a Poser file.
  '''

  # Create a new geometry containing the WaveGeom3d from a WaveFront file (src is string).
  # First try to read the compressed file with a .obz if it exists.
  # Set the 'Valid' property to false, in case of a read error. (Bad choice of design).
  # @param fn  full path name of the WaveFront file.
  def __init__(self, src=None):
    super(GeomCustom, self).__init__()
    
    self._isValid = True

    self.numbVerts = 0
    self.numbTVerts = 0 
    self.numbNorms = 0

    self.numbTSets = 0
    self.numbElems = 0
    self.numbSets = 0

    if src:
      if isinstance(src, WaveGeom):
        self.setPoserType(PoserToken.E_geomCustom)
        self._geom = src

      elif isinstance(src, PoserFileParser):
        self.setPoserType(PoserToken.E_geomCustom)
        self._geom = WaveGeom(src)

      elif isinstance(src, GeomCustom):   
        self.setPoserType(PoserToken.E_geomCustom)
        self._geom = src.getWaveGeom().copy()
        self.setName(src.getName())

      else: # src should be a filename
        self._geom = WaveGeom()
  
        # Read full geometry
        try:
          rin = getOBJFile(src)
          pfr = PoserFileParser(rin, OBJ_FNAT)
          self._geom.readInternal(pfr)
          self.setName(src)
          rin.close()
          logging.info("File[%s] : %d lines read", src, pfr.lineno())

        except IOError: # as ioex:
          self._isValid = False
          logging.warning("File[%s] does not exist (.obj/.obz)", src)

    else:  # Default Empty constructor     
      self._geom = WaveGeom()

  # 
  # Return the first group name.
  #    
  def getGroupName(self): return self._geom.getGroupName()

  # 
  # Return the underlying geometry.
  # @return the geometry
  #    
  def getWaveGeom(self): return self._geom

  # 
  # Indicates if the geometry has been correctly read.
  #    
  def isValid(self): return self._isValid

  # 
  # Dummy implementation.
  #    
  def read(self, st):

    (self.numbVerts, self.numbTVerts, self.numbTSets, self.numbElems, self.numbSets) = self._geom.readInternal(st)

    # Control given lengths vs found
    if self.numbVerts != len(self._geom.coordList):
      self.numbVerts = len(self._geom.coordList)

    if self.numbTVerts != len(self._geom.texList):
      self.numbTVerts = len(self._geom.texList)

  def applyDelta(self, dlt, factor, mapPt, comCoord:'set of integer'):
    demifactor = factor / 2.0

    cl = self._geom.coordList
    lcl = len(cl)
    # Performance enhancement (test comCoord) once
    if comCoord:
      for dp in dlt.deltaSet.values():
        noPt = mapPt[dp.noPt] if mapPt else dp.noPt 
        if noPt < lcl:
          cl[noPt].scaleAdd(demifactor if noPt in comCoord else factor, dp, cl[noPt])
        else:
          logging.warning("Pt:%d", noPt)
    else:
      for dp in dlt.deltaSet.values():
        noPt = mapPt[dp.noPt] if mapPt else dp.noPt 
        if noPt < lcl:
          cl[noPt].scaleAdd(factor, dp, cl[noPt])
        else:
          logging.warning("Pt:%d", noPt)


  # @param bodyIdx
  # @param groupName
  # @param refPoserObject
  # @param mapPt
  # @param comCoord
  # @param setTargetMorph    If null consider all "PBM*" else consider the targets contained in this set.
  def findApplyDeltaInternal(self, bodyIdx, groupName, refPoserObject, mapPt, comCoord:'set of integer', setTargetMorph):
    # Position of ':' change when bodyIdx >= 10
    searchName = groupName if (groupName.rfind(':') == len(groupName) - (3 if bodyIdx > 9 else 2)) else groupName + ":" + bodyIdx;

    # 20080406 : Duplicate Channel application in V4 (caused by getChannels())
    po = refPoserObject.findActor(searchName)
 
    for attr in po.getChannels():
      if (attr.getPoserType()==PoserToken.E_targetGeom) and GenericTransform.concerned(attr.getName(), setTargetMorph):
        finalFactor = 0.0

        for vod in attr.getVOD():
          # Get the real factor of the master
          f = refPoserObject.getFactor(vod.getFigureName(), vod.getGroupName(), vod.getChannelName())

          logging.info("Herited Factor[%s" + "] : %s f=%g", attr.getName(), vod.getGroupName(), f)

          # Take into account the Control Ratio (deltaAddDelta)
          finalFactor = vod.calc(finalFactor, f)
          
        dltAttr = attr.getDeltas()
        localFactor = attr.getKeysFactor(0)
        finalFactor += localFactor

        if dltAttr and (finalFactor!=0.0):
          logging.info("Deltas[%s] : %s f=%g", attr.getName(), groupName, finalFactor)
          self.applyDelta(dltAttr, finalFactor, mapPt, comCoord)


  # Unused Variante
  # Apply deltas for a group of the geometry.
  # def findApplyDelta(self, bodyIdx, groupName, refPoserObject, comCoord):
  #        self.findApplyDeltaInternal(bodyIdx, groupName, refPoserObject, None, comCoord, None)

  #
  # Apply deltas for each group of the geometry.
  #   @findApplyDelta.register(object, int, PoserFile, Set)
  #   @findApplyDelta.register(object, PoserMeshedObject, PoserFile, Set)
  # def findApplyDelta_1(self, pp, refPoserObject, setTargetMorph):
  #
  def findApplyDelta(self, PropOrBodyIdx, refPoserObject, setTargetMorph):
    if isinstance(PropOrBodyIdx, int):
      bodyIdx = PropOrBodyIdx

      # Calculate global comCoord set (better for speed)    
      comCoord = set()

      # Get all part of the character
      lstActor = refPoserObject.getDescendant(bodyIdx)

      for gn in [ a.getName() for a in lstActor if a!=lstActor[0] ]:
        lstDesc = refPoserObject.getWelded(bodyIdx, gn)
        gBas = self._geom.getGroup(gn)
        if lstDesc and gBas:
          sBas = set(gBas.vertIdx)
          logging.info("Groupe Bas[%s]: %d faces", gn, gBas.getNbFace())
          # FIX 20210327: bad detection of common points --> New algo based on set()
          for d in lstDesc:
            # Retrieve the GeomGroup of the actor
            gHaut = self._geom.getGroup(d)
            if gHaut:
              logging.info("Groupe Haut[%s]: %d faces", d, gHaut.getNbFace()) 

              # Common points belong to both groups
              tmpComCoord = sBas & set(gHaut.vertIdx)

              # Merge the set of interface points
              comCoord |= tmpComCoord
            else:
              logging.warning("Groupe Bas[%s] NO faces", d )


      logging.info("Applying Deltas with [%d] Common Coordinates", len(comCoord))

      # log.info("------------------------ Applying Deltas ----------------")
      for gn in  [ a.getName() for a in lstActor ]:
        grp = self._geom.getGroup(gn)
        if grp:
          idxMap = self._geom.calcGroupVertIndex(grp)
          self.findApplyDeltaInternal(bodyIdx, gn, refPoserObject, idxMap, comCoord, setTargetMorph)

    else:
      pp = PropOrBodyIdx
      for attr in pp.getChannels():
        if (attr.getPoserType()==PoserToken.E_targetGeom) and GenericTransform.concerned(attr.getName(), setTargetMorph):
          finalFactor = 0.0
          for vod in attr.getVOD():
            # Get the real factor of the master
            f = refPoserObject.getFactor(vod.getFigureName(), vod.getGroupName(), vod.getChannelName())

            logging.info("Herited Factor[%s" + "] : %s f=%g", attr.getName(), vod.getGroupName(), f)
            finalFactor = vod.calc(finalFactor, f)

          dltAttr = attr.getDeltas()
          localFactor = attr.getKeysFactor(0)
          finalFactor += localFactor
          if dltAttr and (finalFactor != 0.0):
            logging.info("Deltas[%s] : %s f=%g", attr.getName(), pp.getName(), finalFactor)
            self.applyDelta(dltAttr, finalFactor, None, None)


  def createGeomGroup(self, name):
    return self._geom.createGeomGroup(name)

  def extractSortJonction(self, pBasName, pHautName):
    return self._geom.extractSortJonction(pBasName, pHautName)

  # @param inLst list of geomcustom to fusion to this
  # @return    the list of mapping vertex table.
  def fusion(self, inLst):
    inWGLst = [ inGC._geom for inGC in inLst if inGC ]
    outMapLst = [ ] # ArrayList<int>(len(inLst))
    self._geom.fusion(inWGLst, outMapLst)
    return outMapLst

  def calcPointMapping(self, newGeom):
    self._geom.calcPointMapping(newGeom._geom)

#   def compareTo(self, gc):
#     return self._geom.compareTo(gc.getWaveGeom())

  # Extract the group of the given name and create a new GeomCustom
  # that contains a <u>deep copy</u> of the original data.
  # 
  # @param     groupName   Name of the group to be extracted
  # @param     storageGeomType Storage Type of the geometrie in the poser file.
  # @return    a new GeomCustom
  def extractSortGeom(self, groupName, storageGeomType):
    wg = self._geom.extractSortGeom(groupName)

    # 20081230 : Bug fix for internal geometrie without specified group name
    if (wg == None) and (storageGeomType == PoserConst.GT_INTERNAL):
      # Extract the group named "default"
      wg = self._geom.extractSortGeom("default")

      # 20120819 : Bug fix when the "default" group name is not named "default", return the first group
      if (wg == None) and (len(self._geom.groups) == 1):
        wg = self._geom.extractSortGeom(self._geom.groups[0].getName())

      if wg:
        wg.getGroups()[0].setName(groupName.replace(':', '-'))

    return GeomCustom(wg)

  # Write the Geomcustom as a WaveFront format (.OBJ)
  def writeOBJ(self, fileName):
    ''' Write the underlying WaveGeom in a WaveFront format file (.obj) 
    Paramters
    ---------
    filename : str
      Path of the file to create.

    Returns
    -------
    int : C_OK, C_ERROR
    '''
    return self._geom.writeOBJ(fileName)

  # public void writeConst(PrintWriter fw, String nPfx, GeomGroup g)
  def writeConst(self, fw, nPfx, g): # PrintWriter fw, String nPfx, GeomGroup g)
    fw.write(f"{nPfx}numbVerts {self.numbVerts}\n")
    fw.write(f"{nPfx}numbTVerts {self.numbTVerts}\n")
    if g:
      fw.write(f"{nPfx}numbTSets {0 if (g.vertIdx == None) else len(g.vertIdx)}\n")
      fw.write(f"{nPfx}numbElems {g.getNbFace()}\n")
      fw.write(f"{nPfx}numbSets {0 if (g.vertIdx == None) else len(g.vertIdx)}\n")


  def write(self, fw, pfx):
    gn = self.getGroupName()
    gg = self._geom.getGroup(gn)
    fw.write(f"{pfx}geomCustom\n{pfx}\t{{\n")
    nPfx = pfx + "\t"
    self.writeConst(fw, nPfx, gg)
    self._geom.writeVertex(fw, nPfx, False)
    self._geom.writeGroups(fw, nPfx, False)
    fw.write(f"{nPfx}}}\n")



class FigureResFile(SimpleAttribut):
  def __init__(self):
    super(FigureResFile, self).__init__()
    self._geomCustom = None # GeomCustom()

  def getGeomCustom(self, poserRootDir):
    if not self._geomCustom:
      gc = GeomCustom(self.getPath(poserRootDir))
      self._geomCustom = gc if gc.isValid() else None

    return self._geomCustom

  def setGeomCustom(self, gc:'GeomCustom or WaveGeom'):
    if isinstance(gc, WaveGeom):
      wg = gc
      gc = GeomCustom(src=wg)
      
    self._geomCustom = gc

  def getPath(self, poserRootDir):
    return getRealPath(poserRootDir, self.getValue())



