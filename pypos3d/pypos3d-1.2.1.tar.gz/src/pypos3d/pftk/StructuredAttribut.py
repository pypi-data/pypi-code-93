# -*- coding: utf-8 -*-
'''  
Created on 3 oct. 2004
Ported in Python in May 2020
'''
import sys
import logging
import copy
from collections import namedtuple

import numpy as np
from scipy import spatial

from langutil import C_OK, C_FAIL, C_ERROR
from pypos3d.wftk.WFBasic import Vector3d, Point3d, BoundingBox, BoundingSphere, calcMLS
from pypos3d.wftk.Repere import Repere
from pypos3d.wftk.PoserFileParser import PoserFileParser, ParsingErrorException
from pypos3d.wftk.WaveGeom import WFMat, WFColor
from pypos3d.pftk.PoserBasic import PoserConst, PoserObject, PToken, PoserToken, Lang, TAS, index, create, WBoolLine, RemoveQuotes, nodeNameNo
from pypos3d.pftk.SimpleAttribut import KSA, ValueOpDelta, OffSA, TextureMapSA, SimpleAttribut

 
PtMapping = namedtuple('PtMapping', ['srcNo', 'refNo', 'refGeom', 'dist' ])
  
#   
class StructuredAttribut(PoserObject):
  ''' Structured attribute of a Poser file : NAME { list of PoserObject } '''
 
  def __init__(self, n=''):
    super(StructuredAttribut, self).__init__()
    self.setName(n)
    self._lstAttr = [ ]

  def getLstAttr(self): return self._lstAttr

  # 
  # Read a structured attribute data from the file. This class name, the name
  # and the opening bracket are supposed to be consumed by the caller.
  # Because it is the mean it uses to recognize a structured attribute.
  #    
  def read(self, st):    
    code,cn,rw = st.getLine()
    
    while (code!=PoserFileParser.TT_EOF) and (code!=PoserFileParser.TT_RIGHTBRACKET):
      if st.ttype == PoserFileParser.TT_WORD:
        try:
          vc = Lang[cn]
          #  Known word
          if vc.isStructured:
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
                logging.warning( "Line[%s]: '{' is missing for %s", st.lineno, cn)
          else:
            if vc.isDirect:
              self.setDirect(vc, rw)
            else:
              sa = create(vc, cn)
              #  Read before add
              sa.read(st, rw)
              self.addAttribut(sa)

        except KeyError: #  Mot inconnu
          logging.info("Line[%s] - Unknown word:%s", st.lineno(), cn)

      #  Get next line
      code,cn,rw = st.getLine()
      # Wend

  def isAmbi(self): return self.ambiguious

  # @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    nextPfx = pfx + "\t"
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n{nextPfx}{{\n")
    for po in self._lstAttr:
      po.write(fw, nextPfx)

    if not self._lstAttr:
      fw.write('\n')

    fw.write(f"{nextPfx}}}\n")

  def getAttribut(self, attrTypeOrName):
    if isinstance(attrTypeOrName, PToken):
      po = next((x for x in self._lstAttr if x.getPoserType() == attrTypeOrName), None)
    else:
      po = next((x for x in self._lstAttr if x.getName() == attrTypeOrName), None)

    return po
    #  20080417 : Fix - Shall return null if not found

# Useless as we always use less 'free' attributs
#   def replaceAttribut(self, attrTypeName, nattr):
#     for i,po in enumerate(self._lstAttr):
#       if po.getPoserType()==attrTypeName:
#         self._lstAttr[i] = nattr
#         return True
# 
#     return False

  def deleteAttribut(self, attrName):
    for po in self._lstAttr:
      if po.getName() == attrName:
        self._lstAttr.remove(po)
        return True

    return False

  def addAttribut(self, po):
    self._lstAttr.append(po)

  def setDirect(self, tokenID, val):
    #  Dummy (debug) implementation
    logging.warning("Unexpected Direct:" + tokenID.token + " (" + (val if val else 'null') + ") in " + str(self.__class__) + " for " + self.getPoserType().token)
    # Workaround: Create a simple atttribut and inster it 'as usual'
    sa = SimpleAttribut(tokenID, val)
    self._lstAttr.append(sa)

  def findAttribut(self, attrTypeName:PoserToken, name=None) -> PoserObject :
    if name:
      try:
        po = next(x for x in self._lstAttr if (x.getPoserType() == attrTypeName) and (x.getName() == name))
        return po
      except:
        #  20080417 : Fix - Shall return null if not found
        return None
    else:
      return self.getAttribut(attrTypeName)

#TODO 
#  * This class represents a set of vertice indexes used by 
#  * Poser to adapt dynamic clothes (I think). 
#  * Moreover it can contain embedded attribute like 'stitchVertsGroupProperties'
#  
class VertsGroup(StructuredAttribut):
  def __init__(self):
    super(VertsGroup, self).__init__()
    self.vertList = None
    self.vertTab = []

  #    * @see deyme.v3d.poser.PoserObject#read(deyme.v3d.poser.PoserFileParser)
  #    
  def read(self, st):
    self.vertTab = [ ]

    fin = False
    while not fin:
      code,cn,rw = st.getLine()
      if code == PoserFileParser.TT_WORD:
        if cn == "v":          
          self.vertTab.append(int(rw))
          continue 

        #  Other keyword found
        try:
          vc = Lang[cn]
          #  Known word
          if vc.isStructured:
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
          else:
            sa = create(vc, cn)
            #  Read before add
            sa.read(st, rw)
            self.addAttribut(sa)

        except:
          #  Mot inconnu
          logging.info("Line[%s] - Unknown word:%s",st.lineno(),  cn)
      elif (code==PoserFileParser.TT_EOF) or (code==PoserFileParser.TT_RIGHTBRACKET): 
        break
      else:
        logging.warning("Line[%s] - Not Accepted :%s", st.lineno(), cn)
        raise ParsingErrorException()

    # End of read

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    #  FIXME: Wrong output - Other attributes (like stitchVertsGroupProperties are forgotten)
    nextPfx = pfx + "\t"
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n{nextPfx}{{\n")
    nextPfx = pfx + "\tv "

    for vi in self.vertTab:
      fw.write(f"{nextPfx}{vi}\n")
 
    fw.write(f"{nextPfx}}}\n")

# 
# This class represents the "textureFile" element of Poser files.
#  
class TextureFile(StructuredAttribut):

  def __init__(self):
    super(TextureFile, self).__init__()
    self._file = '' #  "NO_MAP" 
    self._warped = False

  def setDirect(self, tokenID, val):
    if tokenID==PoserToken.E_file:
      self._file = None if val == PoserConst.C_NO_MAPG or val == PoserConst.C_NO_MAP else val
    elif tokenID==PoserToken.E_warped:
      self._warped = val.startswith("1")
    else:
      logging.warning("Unexpected Direct:%s (%s)",tokenID.token, val)

  #  (non-Javadoc)
  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  #    
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    fw.write(f"{nextPfx}file {PoserConst.C_NO_MAPG if self._file==None else self._file}\n") #  "NO_MAP" 
    WBoolLine(fw, nextPfx, "warped", self._warped )
    for po in self._lstAttr:
      po.write(fw, nextPfx)
    if not self._lstAttr:
      fw.write('\n')
    fw.write(f"{nextPfx}}}\n")

 

# 
# This class represents the "nodeInput" element of Poser files.
#  
class NodeInput(StructuredAttribut):
  def __init__(self, nodeName='', colorStr='1 1 1', src=None):
    super(NodeInput, self).__init__()
    self._poserType = PoserToken.E_nodeInput
    
    if src:
      self._nodeName = src._nodeName
      self._name = nodeName if nodeName else src._name
      self._value    = src._value
      self._parmR    = src._parmR
      self._parmG    = src._parmG
      self._parmB    = src._parmB
      self._node     = src._node
      self._file     = src._file 
    else:
      self._nodeName = nodeName
      if nodeName:
        self._name = nodeName
        
      self._value    = colorStr #  22 0 32768
      self._parmR    = "" #  NO_PARM
      self._parmG    = "" #  NO_PARM
      self._parmB    = "" #  NO_PARM
      self._node     = "" #  NO_NODE
      self._file     = "" #  "NO_MAP" 
    
  # Set the name.
  def setName(self, s):
    self._name = RemoveQuotes(s)
    self._nodeName = self._name

  def read(self, st):
       
    while True:
      code,cn,val = st.getLine()
      if code==PoserFileParser.TT_WORD:
        try:
          tokenID = Lang[cn]        
        
          if tokenID==PoserToken.E_name:
            self._nodeName = RemoveQuotes(val)
          elif tokenID==PoserToken.E_value:
            self._value = val
          elif tokenID==PoserToken.E_parmR:
            self._parmR = None if val==PoserConst.C_NO_PARM else val
          elif tokenID==PoserToken.E_parmG:
            self._parmG = None if val==PoserConst.C_NO_PARM else val
          elif tokenID==PoserToken.E_parmB:
            self._parmB = None if val==PoserConst.C_NO_PARM else val
          elif tokenID==PoserToken.E_node:
            self._node = None if val==PoserConst.C_NO_NODE else RemoveQuotes(val)
          elif tokenID==PoserToken.E_file:
            val = val.strip()
            self._file = None if val==PoserConst.C_NO_MAPG or val==PoserConst.C_NO_MAP else val
          else:
            logging.warning("Unexpected Direct in NodeInput:%s (%s)",tokenID.token, val)
        
        except KeyError: #  Mot inconnu
          logging.info("Line[%s] - Unknown word:%s", st.lineno(), cn)
      elif (code==PoserFileParser.TT_RIGHTBRACKET) or (code==PoserFileParser.TT_EOF): 
        break
      else:
        logging.warning("L[%d] - Not Accepted :%s", st.lineno(), cn)
        raise ParsingErrorException()




  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  #    
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} \"{self.getName()}\"\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    fw.write(f"{nextPfx}name \"{self._nodeName}\"\n")
    fw.write(f"{nextPfx}value {self._value}\n")
    fw.write(f"{nextPfx}parmR {self._parmR if self._parmR else PoserConst.C_NO_PARM}\n")
    fw.write(f"{nextPfx}parmG {self._parmG if self._parmG else PoserConst.C_NO_PARM}\n")
    fw.write(f"{nextPfx}parmB {self._parmB if self._parmB else PoserConst.C_NO_PARM}\n")
    fw.write(f"{nextPfx}node \"{self._node if self._node else PoserConst.C_NO_NODE}\"\n")
    fw.write(f"{nextPfx}file {self._file if self._file else PoserConst.C_NO_MAPG}\n")
    fw.write(f"{nextPfx}}}\n")




  def getFile(self): return self._file

  #
  # Mimic Poser Python interface
  # Set the _file with a filename value
  #
  def setString(self, fn):
    self._file = fn

  #
  # Mimic Poser Python interface
  # Set the _parmR with a float value
  #
  def setFloat(self, f):
    t = self._value.split(' ')
    self._value = str(f) + ' ' + t[1] + ' ' + t[2]

  def setParmR(self, s):
    self._parmR = s

  def getInNode(self, sht):
    if self._node and self._node!=PoserConst.C_NO_NODE:
      return sht.getNodeByInternalName(self._node)
    return None

#
#  Shader Tree Node
#
class Node(StructuredAttribut):
  def __init__(self, src=None):
    super(Node, self).__init__()
    self._poserType = PoserToken.E_node
    self.ambiguious = True
    
    # Copy constructor
    if src:
      self._name      = src._name
      self._nodeName  = src._nodeName
      self._typeName  = src._typeName
      self._pos       = src._pos
      self._collapsed = src._collapsed
      self._showPreview = src._showPreview
      lsrc = src.getLstAttr()
      if lsrc:
        for ni in lsrc:
          nci = NodeInput(src=ni)
          self.addAttribut(nci)
          
    else:
      self._nodeName  = ''
      self._typeName  = ''
      self._pos       = '0 0'
      self._collapsed = False
      self._showPreview = False

  def setDirect(self, tokenID, val):
    if tokenID == PoserToken.E_name:
      self._nodeName = RemoveQuotes(val)
    elif tokenID==PoserToken.E_inputsCollapsed:
      self._collapsed = (val[0] == "1")
    elif tokenID==PoserToken.E_showPreview:
      self._showPreview = (val[0] == "1")
    else:
      logging.warning("Unexpected Direct in Node:%s (%s)",tokenID.token, val)
  
  def addAttribut(self, po):
    if po.getPoserType()==PoserToken.E_pos:
      self._pos = po.getValue()
    else:
      super(Node, self).addAttribut(po)

  # Set the name.
  def setName(self, s):
    if s:
      t = s.split(' ')
      self._name = RemoveQuotes(t[1])
      self._typeName = RemoveQuotes(t[0])
    else:
      self._name = s
      
  def setCollapsed(self, inputsCollapsed):
    self._collapsed = inputsCollapsed
    
  def setShowPreview(self, showPreview):
    self._showPreview = showPreview

  # @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} \"{self._typeName}\" \"{self.getName()}\"\n")
    if self._lstAttr:
      nextPfx = pfx + "\t"
      fw.write(f"{nextPfx}{{\n")
      fw.write(f"{nextPfx}name \"{self._nodeName}\"\n")
      fw.write(f"{nextPfx}pos {self._pos}\n")

      if self._collapsed:
        WBoolLine(fw, nextPfx, "inputsCollapsed", self._collapsed)
      if self._showPreview:
        WBoolLine(fw, nextPfx, "showPreview", self._showPreview)
        
      for po in self._lstAttr:
        po.write(fw, nextPfx)
        
      fw.write(f"{nextPfx}}}\n")

  def getInputByInternalName(self, inpName='Blending'):
    return next( (n for n in self.getLstAttr() if isinstance(n, NodeInput) and n._nodeName==inpName), None)

#   def getInputByName(self, name):
#     return next( (n for n in self.getLstAttr() if isinstance(n, NodeInput) and n.getName()==name), None)


  def setLocation(self, x, y):
    self._pos = str(x)+ ' ' + str(y)

  def getNodeType(self):
    return PoserConst.kNodeTypeCodeBLENDER if self._typeName=='blender' else PoserConst.kNodeTypeCodeIMAGEMAP if self._typeName=='image_map' else C_ERROR

#
# Shader Tree
# 
class ShaderTree(StructuredAttribut):
  def __init__(self):
    super(ShaderTree, self).__init__()
    self.setPoserType(PoserToken.E_shaderTree)

  def getNodeByInternalName(self, intName):
    return next( (n for n in self.getLstAttr() if isinstance(n, Node) and n._nodeName==intName), None)

  def getNodeByName(self, name):
    return next( (n for n in self.getLstAttr() if isinstance(n, Node) and n.getName()==name), None)


  # Create a Node in a shader tree
  # Partial Implementation for 'blender' and 'image_map'
  #
  # Pos as (x,y)
  # Default Blender:
  #			node "blender" "Blender"
  #				{
  #				name "Blender"
  #				pos 396 54
  #       inputsCollapsed 1
  #       showPreview 1
  #				nodeInput "Input_1"
  #					{
  #					name "Input_1"
  #					value 1 1 1
  #					parmR NO_PARM
  #					parmG NO_PARM
  #					parmB NO_PARM
  #					node NO_NODE
  #					file NO_MAP
  #					}
  #				nodeInput "Input_2"
  #					{
  #					name "Input_2"
  #					value 1 1 1
  #					parmR NO_PARM
  #					parmG NO_PARM
  #					parmB NO_PARM
  #					node NO_NODE
  #					file NO_MAP
  #					}
  #				nodeInput "Blending"
  #					{
  #					name "Blending"
  #					value 0.5 0 1
  #					parmR NO_PARM
  #					parmG NO_PARM
  #					parmB NO_PARM
  #					node NO_NODE
  #					file NO_MAP
  #					}  
  def CreateNode(self, poserkNodeTypeCode, pos=None, inputsCollapsed=False, showPreview=False): # kNodeTypeCodeBLENDER or kNodeTypeCodeIMAGEMAP
    n = Node()
    # Generated a name according to the type
    baseName = 'Blender_' if poserkNodeTypeCode==PoserConst.kNodeTypeCodeBLENDER else 'Image_Map_'

    lstno = [ nodeNameNo(no._nodeName) for no in self.getLstAttr() \
      if no.getNodeType()==poserkNodeTypeCode ]

    no = max(lstno) + 1 if lstno else 0

    n._name = baseName+str(no)
    n._nodeName = n._name
    n._typeName = 'blender' if poserkNodeTypeCode==PoserConst.kNodeTypeCodeBLENDER else 'image_map'

    # Add the relevant NodeInput to the new Node
    if poserkNodeTypeCode==PoserConst.kNodeTypeCodeBLENDER:
      lstni = (("Input_1", "1 1 1"), ("Input_2", "1 1 1"), ("Blending", "0 0 1"))
    else:
      lstni = (("Image_Source", "-1 0 0"), ("Auto_Fit", "0 0 0"), ("U_Scale", "1 -1 1"),\
                  ("V_Scale", "1 -1 1"), ( "U_Offset", "0 0 1"), ("V_Offset", "0 0 1"), \
                  ("Texture_Coords", "1 0 0"), ("Image_Mapped", "4 0 0"), ("Background", "1 1 1"),\
		  ("Global_Coordinates", "0 0 1"), ("Mirror_U", "0 0 0"), ("Mirror_V", "0 0 0"), \
                  ("Texture_Strength", "1 0 1"), ("Filtering", "3 0 0"))

    n._lstAttr += [ NodeInput(tni[0], colorStr=tni[1]) for tni in lstni ]
    self._lstAttr.append(n)

    if pos:
      n.setLocation(pos[0], pos[1])
    
    n.setCollapsed(inputsCollapsed)
    n.setShowPreview(showPreview)
    return n
 
  def AttachTreeNodes(self, nodeDest, inputName, nodeRef):
    ni = nodeDest.getInputByInternalName(inpName=inputName)
    ni._node = nodeRef.getName()


#  
# material class.  
#  
class PoserMaterial(StructuredAttribut):
  # 
  # Create the default "skin" material.
  #
  def __init__(self, src=None):
    super(PoserMaterial, self).__init__()
    
    # Create the Minimal Direct attributs
    self._KdColor = WFColor(0.992157, 0.992157, 0.992157, 1.) 
    self._KaColor = WFColor(0., 0., 0., 1.) 
    self._KsColor = WFColor(0.733333, 0.733333, 0.733333, 1.) 
    self._TextureColor = WFColor(1.0, 1.0, 1.0, 1.0) 
    self._NsExponent = 10 
    self._tMin = 0.
    self._tMax  = 0. 
    self._tExpo = 0.6 
    self._bumpStrength = 1.
    self._ksIgnoreTexture = 0 
    self._reflectThruLights = 1 
    self._reflectThruKd = 0. 
    self._textureMap = TextureMapSA(PoserToken.E_textureMap) 
    self._bumpMap = TextureMapSA(PoserToken.E_bumpMap)   # NO_MAP
    self._reflectionMap = TextureMapSA(PoserToken.E_reflectionMap)  # NO_MAP
    self._transparencyMap = TextureMapSA(PoserToken.E_transparencyMap)   # NO_MAP
    self._ReflectionColor = WFColor(0.733333, 0.733333, 0.733333, 1.) 
    self._reflectionStrength = 1. 
    self._shaderTree = None
    self.setPoserType(PoserToken.E_material) # FIX: Shall be set anyway
    
    if src:
      if isinstance(src, WFMat):
        # Create a Material from a simple WaveFront material
        self.setName(src.name)
        self._KdColor = WFColor(src.kd[0], src.kd[1], src.kd[2], src.kd[3])
        self._KaColor = WFColor(src.ka[0], src.ka[1], src.ka[2], src.ka[3])
        self._KsColor = WFColor(src.ks[0], src.ks[1], src.ks[2], src.ks[3])
        
        self._textureMap = TextureMapSA(PoserToken.E_textureMap, initPath=src.map_kd)
        
      elif isinstance(src, PoserMaterial):
        
        self.setName(src.getName())
        self._KdColor =  WFColor(src._KdColor.r, src._KdColor.g, src._KdColor.b, src._KdColor.t)
        self._KaColor =  WFColor(src._KaColor.r, src._KaColor.g, src._KaColor.b, src._KaColor.t)
        self._KsColor =  WFColor(src._KsColor.r, src._KsColor.g, src._KsColor.b, src._KsColor.t)
        self._TextureColor =  WFColor(src._TextureColor.r, src._TextureColor.g, src._TextureColor.b, src._TextureColor.t)
        self._NsExponent =  src._NsExponent 
        self._tMin = src._tMin 
        self._tMax  =  src._tMax  
        self._tExpo =  src._tExpo 
        self._bumpStrength = src._bumpStrength 
        self._ksIgnoreTexture =  src._ksIgnoreTexture 
        self._reflectThruLights =  src._reflectThruLights 
        self._reflectThruKd =  src._reflectThruKd 
        self._textureMap = TextureMapSA(initPath=src._textureMap) 
        self._bumpMap = TextureMapSA(initPath=src._bumpMap)
        self._reflectionMap = TextureMapSA(initPath=src._reflectionMap)
        self._transparencyMap = TextureMapSA(initPath=src._transparencyMap)
        self._ReflectionColor = WFColor(src._ReflectionColor.r, src._ReflectionColor.g, src._ReflectionColor.b, src._ReflectionColor.t)
        self._reflectionStrength = src._reflectionStrength
        if src._shaderTree:
          self._shaderTree = ShaderTree()
          
          for n in src._shaderTree.getLstAttr():
            # It is supposed that ShaderTree only contains Nodes
            nn = Node(src=n)
            self._shaderTree.addAttribut(nn)
          
          
      else: # Illegal source
        raise TypeError() 

  def getTextureMap(self): return self._textureMap.getPath() #if self._textureMap else None 

  def getBumpMap(self): return self._bumpMap.getPath() #if self._bumpMap else None

  def getReflectionMap(self): return self._reflectionMap.getPath() #if self._reflectionMap else None

  def getTransparencyMap(self): return self._transparencyMap.getPath() #if self._transparencyMap else None

  def getShaderTree(self): return self._shaderTree

  def getLstNodes(self):
    st = self._shaderTree
    return [ po for po in st.getLstAttr() if isinstance(po, Node) ] if st else [ ]

  def setDirect(self, tokenID, val):
    if tokenID == PoserToken.E_KdColor:
      tv = val.split()
      self._KdColor = WFColor(float(tv[0]), float(tv[1]), float(tv[2]), float(tv[3]))
      
    elif tokenID == PoserToken.E_KaColor:
      tv = val.split()
      self._KaColor = WFColor(float(tv[0]), float(tv[1]), float(tv[2]), float(tv[3]))
      
    elif tokenID == PoserToken.E_KsColor:
      tv = val.split()
      self._KsColor = WFColor(float(tv[0]), float(tv[1]), float(tv[2]), float(tv[3]))
       
    elif tokenID == PoserToken.E_TextureColor:
      tv = val.split()
      self._TextureColor = WFColor(float(tv[0]), float(tv[1]), float(tv[2]), float(tv[3]))
      
    elif tokenID == PoserToken.E_NsExponent:
      self._NsExponent = float(val)
      
    elif tokenID == PoserToken.E_tMin:
      self._tMin = float(val)
      
    elif tokenID == PoserToken.E_tMax:
      self._tMax  = float(val)
      
    elif tokenID == PoserToken.E_tExpo:
      self._tExpo = float(val)
      
    elif tokenID == PoserToken.E_bumpStrength:
      self._bumpStrength = float(val)
      
    elif tokenID == PoserToken.E_ksIgnoreTexture:
      self._ksIgnoreTexture = int(val)
      
    elif tokenID == PoserToken.E_reflectThruLights:
      self._reflectThruLights = int(val)
      
    elif tokenID == PoserToken.E_reflectThruKd:
      self._reflectThruKd = float(val)
      
    elif tokenID == PoserToken.E_ReflectionColor:
      tv = val.split()
      self._ReflectionColor = WFColor(float(tv[0]), float(tv[1]), float(tv[2]), float(tv[3]))
       
    elif tokenID == PoserToken.E_reflectionStrength:
      self._reflectionStrength = float(val)

    else:
      logging.warning("Unexpected Direct in Material:%s (%s)",tokenID.token, val)
  
  def addAttribut(self, po):
    tokenID = po.getPoserType()
    if tokenID == PoserToken.E_textureMap:
      self._textureMap = po
       
    elif tokenID == PoserToken.E_bumpMap:
      self._bumpMap = po
      
    elif tokenID == PoserToken.E_reflectionMap:
      self._reflectionMap = po
      
    elif tokenID == PoserToken.E_transparencyMap:
      self._transparencyMap = po
    
    elif tokenID==PoserToken.E_shaderTree:
      self._shaderTree = po
    else:
      super(PoserMaterial, self).addAttribut(po)

  # @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    fw.write(f"{nextPfx}KdColor {self._KdColor.r} {self._KdColor.g} {self._KdColor.b} {self._KdColor.t}\n") 
    fw.write(f"{nextPfx}KaColor {self._KaColor.r} {self._KaColor.g} {self._KaColor.b} {self._KaColor.t}\n")
    fw.write(f"{nextPfx}KsColor {self._KsColor.r} {self._KsColor.g} {self._KsColor.b} {self._KsColor.t}\n")
    fw.write(f"{nextPfx}TextureColor {self._TextureColor.r} {self._TextureColor.g} {self._TextureColor.b} {self._TextureColor.t}\n") 

    fw.write(f"{nextPfx}NsExponent {self._NsExponent}\n") 
    fw.write(f"{nextPfx}tMin {self._tMin}\n") 
    fw.write(f"{nextPfx}tMax {self._tMax}\n") 
    fw.write(f"{nextPfx}tExpo {self._tExpo}\n") 
    fw.write(f"{nextPfx}bumpStrength {self._bumpStrength}\n") 
    fw.write(f"{nextPfx}ksIgnoreTexture {self._ksIgnoreTexture}\n") 
    fw.write(f"{nextPfx}reflectThruLights {self._reflectThruLights}\n") 
    fw.write(f"{nextPfx}reflectThruKd {self._reflectThruKd}\n") 
    
    self._textureMap.write(fw, nextPfx)
    self._bumpMap.write(fw, nextPfx)
    self._reflectionMap.write(fw, nextPfx)
    self._transparencyMap.write(fw, nextPfx)

    fw.write(f"{nextPfx}ReflectionColor {self._ReflectionColor.r} {self._ReflectionColor.g} {self._ReflectionColor.b} {self._ReflectionColor.t}\n") 
    fw.write(f"{nextPfx}reflectionStrength {self._reflectionStrength}\n") 

    if self._shaderTree:
      self._shaderTree.write(fw, nextPfx)

    if self._lstAttr:
      for po in self._lstAttr:
        po.write(fw, nextPfx)

    fw.write(f"{nextPfx}}}\n")


# 
# Representation of an Inverse Kynematic Chain
#  
class InkyChain(StructuredAttribut):

  # on
  def __init__(self):
    super(InkyChain, self).__init__()
    self._pmName = None
    self._active = False

  # 
  #    * Return true if the actor or the prop is ON
  #    * @return a boolean
  #    
  def isActive(self): return self._active

  def setDirect(self, tokenID, val):
    if tokenID==PoserToken.E_name:
      self._pmName = val
    elif tokenID==PoserToken.E_on:
      self._active = True
    elif tokenID==PoserToken.E_off:
      self._active = False
    else:
      logging.warning("Unexpected Direct in InkyChain:%s (%s)", tokenID.token, val)

  # 
  #    * @see pftk.poser.kern.StructuredAttribut#write(java.io.PrintWriter,
  #    
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    fw.write(f"{nextPfx}name {self._pmName}\n")
    fw.write(f"{nextPfx}{'on' if self._active else 'off'}\n")
    for po in self._lstAttr:
      po.write(fw, nextPfx)
    if not self._lstAttr:
      fw.write('\n')
    fw.write(f"{nextPfx}}}\n")

# 
#  * This class represents the "keys" entry of every channel definition.
#  * 
#  * keys
#  *  {
#  *  static <0|1>
#  *  k <long> <real>
#  *  [sl <0|1>
#  *  spl|lin|con
#  *  sm|br]
#  *  }
#  * 
#  * static determines whether this channel is animating (=0) or static (=1).
#  * k denotes the key information. The first values is the frame, starting at 0. The second value is the channel value at this frame.
#  * sl determines whether or not to loop animation.
#  * spl|lin|con denote the section interpolation type: spline, linear, constant.
#  * sm|br represent either a smooth transition or break in the transition.
#  
class Keys(StructuredAttribut):

  def __init__(self, src=None):
    super(Keys, self).__init__()
    self.setPoserType(PoserToken.E_keys)
    self._static = src._static if src else False
    self._hshKeys = { frameNo:KSA(src=ksa) for frameNo,ksa in src._hshKeys.items() } if src else { } # Replaced by a dict frameNo:KSA

  def read(self, st):
    curK = None
    while True:
      code,cn,rw = st.getLine()
      if code==PoserFileParser.TT_WORD:
        try:
          vc = Lang[cn]

          if vc==PoserToken.E_k:
            tv = rw.split()
            curK = KSA(int(tv[0]), float(tv[1]))
            self._hshKeys[curK._noFrame] = curK
            # Read 3 lines after (if any)
            c0, _, cval = st.getLine()
            
            if c0==PoserFileParser.TT_RIGHTBRACKET: 
              break
            
            _, cty, *_ = st.getLine()
            _, ccnx, *_ = st.getLine()

            # elif vc==PoserToken.E_sl:
            curK.setSl(cval[0]=='1')
            
            # elif (vc==PoserToken.E_spl) or (vc==PoserToken.E_lin) or (vc==PoserToken.E_con):
            curK.setCurveType(Lang[cty])

            #elif (vc==PoserToken.E_sm) or (vc==PoserToken.E_br):
            curK.setCurveCnx(Lang[ccnx])
            
          elif vc==PoserToken.E_static:
            self._static = (rw[0]=='1')
          else:
            logging.warning("L[%d] - Not Accepted :%s", st.lineno(), cn)
            
        except KeyError:
          pass
      elif (code==PoserFileParser.TT_RIGHTBRACKET) or (code==PoserFileParser.TT_EOF): 
        break
      else:
        logging.warning("L[%d] - Not Accepted :%s", st.lineno(), cn)
        raise ParsingErrorException()


  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    WBoolLine(fw, nextPfx, "static", self._static )
    for ks in sorted(self._hshKeys.values(), key=lambda k:k._noFrame):
      ks.write(fw, nextPfx)
    fw.write(f"{nextPfx}}}\n")

  def setStatic(self, s):
    self._static = s

  def addKey(self, noFrame, factor):
    self._hshKeys[noFrame] = KSA(noFrame, factor)

  # 
  # Return the K factor for a given frameNo.
  # Intermediate values are not yet calculated.
  #  
  # @param frameNo 0 based frame index
  # @return the found key factor. 0.0 if not found.
  #    
  def getKeyFactor(self, frameNo):
    try:
      return self._hshKeys[frameNo]._factor
    except KeyError:
      return 0.0

  # 
  #    * Set the K factor for a given frameNo.
  #    * Intermediate values are not yet calculated.
  #    * 
  #    * @param frameNo 0 based frame index
  #    * @return C_OK when the frame no exists and C_FAIL if not found.
  #    
  def setKeyFactor(self, frameNo, k):
    try:
      self._hshKeys[frameNo].setFactor(k)
      return C_OK
    except KeyError:
      return C_FAIL

  # 
  #  Return the list of declared "k" frames.
  #    
  # def getLstKey(self): return self._lstKeys

  # 
  # Convert a GenericTransform to a static one (i.e. no keys)
  # @return    The number of deleted keys
  #    
  def toStatic(self, staticValue):
    l = len(self._hshKeys)
    self._static = True
    #  Remove all keys
    self._hshKeys.clear()
    cle = KSA(0, staticValue)
    cle.setSl(True)
    cle.setCurveType(PoserToken.E_spl)
    cle.setCurveCnx(PoserToken.E_sm)
    self._hshKeys[0] = cle
    return l - 1

class HairGrowthGroup(StructuredAttribut):
  pass

class DocDescription(StructuredAttribut):
  def __init__(self):
    super(DocDescription, self).__init__()
    self._dimensions = None
    self._screenPlace = None
    self._displayMode = None

  #  USEPARENT
  def setDirect(self, tokenID, val):
    if tokenID==PoserToken.E_dimensions:
      self._dimensions = val
    elif tokenID==PoserToken.E_screenPlace:
      self._screenPlace = val
    elif tokenID==PoserToken.E_displayMode:
      self._displayMode = val
    else:
      logging.warning("Unexpected Direct in DocDescription:%s (%s)", tokenID.token, val)

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    if self._dimensions:
      fw.write(f"{nextPfx}dimensions {self._dimensions}\n")

    if self._screenPlace:
      fw.write(f"{nextPfx}screenPlace {self._screenPlace}\n")

    if self._displayMode:
      fw.write(f"{nextPfx}displayMode {self._displayMode}\n")

    for po in self._lstAttr:
      po.write(fw, nextPfx)

    fw.write(f"{nextPfx}}}\n")

# Description part of a figure.
#  class FigureDescription(StructuredAttribut): --> inlined in Figure
        

class AlternateGeom(StructuredAttribut):
  def __init__(self):
    super(AlternateGeom, self).__init__()
    #  Index of the Alternate geometry in the list (not a real attribut) 
    self._no = 0
    self._printName = None

    #  Geom filename formated like Poser with ':' or ""  
    self._geomFileName = None

  def setDirect(self, tokenID, val):
    if tokenID==PoserToken.E_name:
      self._printName = val
    elif tokenID==PoserToken.E_objFile:      
      bci1 = val.rfind(' ')
      self._geomFileName = val[(bci1 + 1):]
    else:
      logging.warning("Unexpected Direct in AlternateGeom:%s (%s)", tokenID.token, val)

  #  @see pftk.poser.kern.StructuredAttribut#write(java.io.PrintWriter,
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    fw.write(f"{nextPfx}name {self._printName}\n")
    fw.write(f"{nextPfx}objFile 20 {self._geomFileName}\n")
    fw.write(f"{nextPfx}}}\n")


  def setNo(self, n):
    self._no = n

  def getNo(self): return self._no

  # Set the print name 
  #  @param gfn
  def setPrintName(self, gfn):
    self._printName = gfn

  # Set the filename as represented on the "objFile" line.
  #  @param gfn
  def setGeomFileName(self, gfn):
    self._geomFileName = gfn

  def getGeomFileName(self): return self._geomFileName


# Represents a delta for the vertex identified by noPt.
class DeltaPoint(Vector3d):

  def __init__(self, no=0, dx=0.0, dy=0.0, dz=0.0):
    super(DeltaPoint, self).__init__(dx,dy,dz)
    self.noPt = no

  def getPointNo(self): return self.noPt

  def setPointNo(self, n):
    self.noPt = n

  def __str__(self):
    return "d {0:d} {1: 11.8f} {2: 11.8f} {3: 11.8f}".format(self.noPt, self.x, self.y, self.z)

  # Round the value to C_MIN_DELTA
  #@classmethod --> Replaced by the buildin round(f,ndigit)
  #def round(cls, v):

  def getVector(self): return self

  def setVector(self, v):
    self.x = v.x
    self.y = v.y
    self.z = v.z

  def toV3d(self): return Vector3d(self)

# 
# This class represents a Deltas attribute used to morph a meshed object. 
#  
class Deltas(StructuredAttribut):

  def __init__(self, src=None):
    super(Deltas, self).__init__()
    self.setPoserType(PoserToken.E_deltas)

    #In python deltaTab replaced by a dict { noPt:DeltaPoint() }
    self.deltaSet = { no:DeltaPoint(dp.noPt, dp.x, dp.y, dp.z) for no,dp in src.deltaSet.items() } if src else { }

  #    * @see deyme.v3d.poser.PoserObject#read(deyme.v3d.poser.PoserFileParser)
  def read(self, st):
    self.deltaSet = { }

    while True:
      code,cn,rw = st.getLine()
      if (code==PoserFileParser.TT_WORD) and (cn=="d"):
        tv = rw.split()
        p = DeltaPoint(int(tv[0]), float(tv[1]), float(tv[2]), float(tv[3]))
        self.deltaSet[p.noPt] = p
      elif (code==PoserFileParser.TT_RIGHTBRACKET) or (code==PoserFileParser.TT_EOF): 
        break
      else:
        logging.warning("L[%d] - Not Accepted :%s", st.lineno(), cn)
        raise ParsingErrorException()

  # @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    for d in sorted(self.deltaSet.values(), key=lambda p:p.noPt):
      fw.write(f"{nextPfx}{d}\n")
    fw.write(f"{nextPfx}}}\n")

  def clear(self):
    self.deltaSet.clear() # = { }

  @classmethod
  def enhancement(cls, srcWG, setFoundDeltas, setNewDeltas, enhance, boundingType, useVicinityLoop, alpha):
    res = C_OK
    mlsFailed = False

    # Populate result with extact matches
    setNewDeltas.update(setFoundDeltas)

    if enhance != PoserConst.C_NO_ENHANCEMENT:
      # 03FEV2008 : Check For missed/not complete faces 
      for grp in srcWG.getGroups():

        # Create an empty sphere (i.e. negative volume)
        # Or (default C_NO_BOUNDING or BOX) Create an empty box (i.e. negative volume)
        bnd = BoundingSphere(Point3d(), -1.0) if boundingType==PoserConst.C_SPHERE_BOUNDING else \
              BoundingBox(Point3d(1.0, 1.0, 1.0), Point3d(-1.0, -1.0, -1.0))

        for faceno in range(0, grp.getNbFace()):
          startIdx = grp.stripCount[faceno]
          lastIdx = grp.stripCount[faceno + 1]
          
          nbEdgeMoved = 0
          faceEdge = [ ]
          faceEdgeIdx = [ ]
          
          for vi in grp.vertIdx[startIdx:lastIdx]: 
            try:
              dp = setFoundDeltas[vi]
              nbEdgeMoved += 1
              # Keep in bounding box, points that have a move
              bnd.combine(grp.coordList[vi])
            except KeyError: #if not found:
              # Record a copy of the point that has no delta              
              faceEdge.append( Point3d(grp.coordList[vi]) )
              faceEdgeIdx.append(vi)
          
          nbmissing = lastIdx - startIdx - nbEdgeMoved
          if (nbEdgeMoved > 0) and (nbmissing > 0):
            # Some vertex are not moved!
            # Get the vertex that compose the "hole face"
            edgePtIdx = grp.vertIdx[startIdx:lastIdx]

            # Calculate '1' loop Vicinity
            edgeLoopPtIdx =  copy.copy(edgePtIdx)

            # First Loop Vicinity
            if useVicinityLoop:
              grp.extendLoopVicinity(edgePtIdx, edgeLoopPtIdx)

            if enhance==PoserConst.C_MLS_ENHANCEMENT:
              # Keep trace of math. error to apply other type of enhancement
              mlsFailed = False

              # Apply deltas to points designed by edgeLoopPtIdx[]
              nuageVoisin = [ ] 
              nuageIdx = [ ] 
              nbPtNuage = 0

              for vi in edgeLoopPtIdx:
                # Add to the cloud (nuage) only vertex that have a delta
                try:
                  faceEdgeIdx.index(vi)
                except ValueError:  #if not found:
                  nuageVoisin.append( Point3d(srcWG.coordList[vi]) )
                  nuageIdx.append(nbPtNuage)
                  try:
                    dp = setFoundDeltas[vi]
                    nuageVoisin[nbPtNuage].add(dp)
                  except KeyError:
                    pass
                  
                  nbPtNuage += 1
              # End for vi

              try:
                # Compute projection Repere with SVD matrix decomposition
                repUVN = Repere(nbPtNuage, nuageIdx, nuageVoisin)

                tabproj = repUVN.project(0, 0, nbPtNuage, nuageIdx, nuageVoisin, None)
                tabdest = repUVN.project(0, 0, nbmissing, nuageIdx, faceEdge, None)

                # Calculate Point Altitudes in the UVN repere
                calcMLS(tabdest, 0, nbmissing, tabproj, alpha)

                ncl = repUVN.reserveProject(0, 0, nbmissing, tabdest, None)

                # Create some new deltas
                for i,vi in enumerate(faceEdgeIdx):
                  if (boundingType==PoserConst.C_NO_BOUNDING) or bnd.intersect(grp.coordList[vi]):
                    dx = round(ncl[i].x - srcWG.coordList[vi].x, 6)
                    dy = round(ncl[i].y - srcWG.coordList[vi].y, 6)
                    dz = round(ncl[i].z - srcWG.coordList[vi].z, 6)
                    if (dx != 0.0) or (dy != 0.0) or (dz != 0.0):
                      dp = DeltaPoint(vi, dx, dy, dz)
                      setNewDeltas[vi]= dp
                    
              except Exception as e:
                logging.warning("Math. Error in %s[%s face=%d] : %s", srcWG.getName(), grp.getName(), faceno, e)
                mlsFailed = True

            if (enhance==PoserConst.C_AVG_ENHANCEMENT) or ((enhance==PoserConst.C_MLS_ENHANCEMENT) and mlsFailed):
              # Find deltas of points designed by edgeLoopPtIdx[]
              dx = 0.0
              dy = 0.0
              dz = 0.0
              nbdelta = 0
              for vi in edgeLoopPtIdx:
                try:
                  dp = setFoundDeltas[vi]
                  dx += dp.x
                  dy += dp.y
                  dz += dp.z
                  nbdelta += 1
                except KeyError:
                  pass

              # Calculage average displacment
              # Value less than 1e-6 are set to 0 by Poser + Null Delta shall not be kept
              if nbdelta>0:
                dx = round(dx / nbdelta, 6)
                dy = round(dy / nbdelta, 6)
                dz = round(dz / nbdelta, 6)
                if (dx != 0.0) or (dy != 0.0) or (dz != 0.0):
                  setNewDeltas.update( { vi:DeltaPoint(vi, dx, dy, dz) for vi in faceEdgeIdx if (boundingType==PoserConst.C_NO_BOUNDING) or bnd.intersect(grp.coordList[vi]) } )

      # Sort the list according to point index (I'm not sure of Poser behavior if not sorted)
      #lstNewDeltas.sort(key=lambda dp: dp.noPt)

    return res



# 
#  * Generic Transformation dedicated to represent : targetGeom <name> valueParm
#  * <name> geomChan <name> xOffsetA|yOffsetA|zOffsetA <name>
#  * xOffset|yOffsetB|zOffsetB <name> taperX|Y|Z <name> scale|X|Y|Z <name>
#  * propagatingScale|X|Y|Z <name> translateX|Y|Z <name> rotateX|Y|Z <name>
#  * smoothScaleX|Y|Z <name> twistX|Y|Z <name> jointX|Y|Z <name> curveX|Y|Z <name>
#  * handGrasp|thumbGrasp|handSpread <name> pointAtParm <name> hairDynamicsParm 
#  * curve  <name>
#  * <name> ... And others ...
#  
#  This method should actually take a ValueOpDelta[] because a single
#  transform can have many valueOpDelta fields!!!
class GenericTransform(StructuredAttribut):
  # Managed operators
  OPS = (PoserToken.E_valueOpDeltaAdd, PoserToken.E_valueOpPlus, PoserToken.E_valueOpMinus, PoserToken.E_valueOpTimes, PoserToken.E_valueOpDivideBy, PoserToken.E_valueOpDivideInto, PoserToken.E_valueOpKey)

  def __init__(self, poserType=None, channelName=None, vodFigure=None, vodActor=None, vodChannel=None):
    super(GenericTransform, self).__init__()

    #  PoserMeshedObject that contains the channel list 
    self._pmo = None

    #  Optimized attributs
    self._transfName = None
    self._initValue = 0.0
    self._hidden = False
    self._enabled = True

    #  V9 attribut (unknown effect)
    self._forceLimits = 4.0
    self._min = -100000
    self._max = 100000
    self._trackingScale = 0.001
    self._interpStyleLocked = -sys.maxsize
    self._keys = None
    # self._indexes = -sys.maxsize - Replaced by a computed value
    self._numbDeltas = -sys.maxsize
    self._dlt = None
    self._lstVOD = [ ]

    self._hasStaticValue = False
    self._staticValue = 0.0

    if poserType:
      self.setPoserType(poserType)
      self.setName(channelName)

      #  20080821: Do not add a prefix to printable name (old P4 Stuff)
      self._transfName = channelName[3:] if (channelName.startswith("PBM") or channelName.startswith("FBM")) else channelName
      self.addKeyFrame(0, 0.0)
      #  Default keys are static=0
      self._interpStyleLocked = 0

      #  Create the deltas table
      if poserType != PoserToken.E_valueParm:
        self._numbDeltas = 0
        #self._dlt = Deltas()

        if vodActor or vodChannel:
          if vodFigure:
            #  HACK HACK HACK Hardwiring valueOpDeltaAdd for now. This will let the
            #  typical case of
            #  valueOpDeltaAdd work for now but all others (valueOpDeltaPlus,
            #  valueOpDeltaMinus, etc)
            #  will be broken! I'll fix this after Olivier adds his hair stuff.
            vod = ValueOpDelta(PoserToken.E_valueOpDeltaAdd, vodFigure, vodActor, vodChannel, 1.0)
            self.addVOD(vod)



  # Overload setPoserType to create Deltas
  def setPoserType(self, poserType):
    StructuredAttribut.setPoserType(self, poserType)
    if not self._dlt and (poserType==PoserToken.E_targetGeom):
      self._dlt = Deltas()

  #
  # Copy all data from src, except the _pmo if parentPO is set
  #
  def copy(self, src, parentPO=None):
    self.setPoserType(self.getPoserType())
    self.setName(src.getName())

    self._pmo = parentPO if parentPO else src._pmo
    self._transfName = src._transfName
    self._initValue = src._initValue
    self._hidden = src._hidden
    self._enabled = src._enabled
    self._forceLimits = src._forceLimits
    self._min = src._min
    self._max = src._max
    self._trackingScale = src._trackingScale
    self._interpStyleLocked = src._interpStyleLocked
    self._hasStaticValue = src._hasStaticValue
    self._staticValue = src._staticValue
    self._numbDeltas = src._numbDeltas
    self._keys = Keys(src=src._keys)
    self._dlt = Deltas(src=src._dlt)
    self._lstVOD = [ ValueOpDelta(src=v) for v in src.getVOD() ]
    self._transfName = src._transfName


  @classmethod
  def createFrom(cls, gtdef:'list from PoserToken'):
    ''' Create a GenericTransform and initialize it with the data
    of tables PoserToken.MINIMAL_***_CHANNEL
    
    Package Reserved method
    '''
    vp = GenericTransform(gtdef[0], gtdef[0].defaultName)
    
    vp.setPrintName(gtdef[0].token)
    vp.setInterpStyleLocked(0)
    vp.setMin(gtdef[2])
    vp.setMax(gtdef[3])
    vp.setInitValue(gtdef[4])      
    vp.setForceLimits(0)
    vp.setTrackingScale(gtdef[8])
    
    if gtdef[1]: #If Static channel
      vp.setStaticValue(gtdef[4])
      vp.setHidden(True)
      
    if (gtdef[0] in PoserToken.SCALES) or not gtdef[1]:
      # Init Scales at 1.0 (100%) and other with their initvalue
      vp.addKeyFrame(0, gtdef[4])
      
    return vp
    

  def addKeyFrame(self, frameno, v):
    if not self._keys:
      self._keys = Keys() #  Default keys are static=0

    self._keys.addKey(frameno, v)


  def getKeysFactor(self, frameNo):
    return self._keys.getKeyFactor(frameNo) if self._keys else 0.0

  def getDeltas(self):
    return self._dlt

  def ishasDeltas(self): return self._dlt and (len(self._dlt.deltaSet)>0)

  # 
  #    * Remove the deltas of tha current channel
  #    
  def removeDeltas(self):
    #  20090711 : Not sure that should be REALLY cleared?
    #  As of 20100226 do not delete anymore the calculation dependencies : _lstVOD.clear();
    #self._indexes = 0
    self._numbDeltas = 0
    #  20190105 : Fix for robusness
    if self.ishasDeltas():
      self.getDeltas().deltaSet.clear()

  # 
  # Optimize deltas : Delete delta with a too small norme
  #    
  def optimizeDeltas(self, refNorm):
    dl = self.getDeltas()
    oldLength = len(dl.deltaSet)
    optSet = { no:t for no,t in dl.deltaSet.items() if t.norme() > refNorm }

    # optTabFinal = Arrays.copyOf(optTab, nbpt)
    dl.deltaSet = optSet
    indexes = len(optSet)
    logging.info("Channel[%s] reduced from %d to %d", self.getName(), oldLength, indexes )
    return indexes 

  def getVOD(self): return self._lstVOD

  # Add an operator to the GenericChannel
  def addVOD(self, vop):
    self._lstVOD.append(vop)

  def findValueOp(self, vodType:'ValueOpDelta', targetName:'str'=None):
    return next((vop for vop in self._lstVOD \
                if (vop.getPoserType()==vodType) and ((targetName is None) or (vop.getChannelName()==targetName))), None)

  # 
  #    * Delete any reference to the given GenericTransform
  #    * @param gt
  #    
  def deleteChannelRef(self, gt):
    chName = gt.getName()
    grpName = gt.getPoserMeshedObject().getName()
    self._lstVOD[:] = [ vod for vod in self._lstVOD if (grpName!=vod.getGroupName()) or (chName!=vod.getChannelName()) ]


  # 
  #    * Delete any reference to the given GenericTransform
  #    * @param gt
  #    
  def deleteFigureRef(self, fig):
    fi = fig.getBodyIndex()
    self._lstVOD[:] = [ vod for vod in self._lstVOD if index(vod.getGroupName())!=fi ]


  # 
  #    * Change the name of referenced part (actor, prop, hairProp, controlProp)  
  #    * @param oldPartName
  #    * @param newPartName
  #    
  def changeReference(self, oldPartName, newPartName, changeRefToBODY=True):
    for vod in self._lstVOD:
      if not vod.getGroupName().startswith(PoserConst.C_BODY) or changeRefToBODY:
        vod.setGroupName(TAS(vod.getGroupName(), oldPartName, newPartName))
      
    for po in self.getLstAttr():
      if po.getPoserType() == PoserToken.E_otherActor:
        po.TAS(oldPartName, newPartName)


  def addAttribut(self, po):
    if po.getPoserType() in GenericTransform.OPS:
      self._lstVOD.append(po)
    elif po.getPoserType()==PoserToken.E_keys:
      self._keys = po
    elif po.getPoserType()==PoserToken.E_deltas:
      self._dlt = po
    else:
      super(GenericTransform, self).addAttribut(po)

  def setDirect(self, tokenID, val):
    if tokenID==PoserToken.E_name:
      self._transfName = val
    elif tokenID==PoserToken.E_initValue:
      self._initValue = float(val)
    elif tokenID==PoserToken.E_hidden:
      self._hidden = val.startswith("1")
    elif tokenID==PoserToken.E_trackingScale:
      self._trackingScale = float(val)
    elif tokenID==PoserToken.E_min:
      self._min = float(val)
    elif tokenID==PoserToken.E_max:
      self._max = float(val)
    elif tokenID==PoserToken.E_forceLimits:
      self._forceLimits = float(val)
    elif tokenID==PoserToken.E_flipped:
      #  Bad fix ... but for the moment
      self.addAttribut(OffSA("flipped"))
    elif tokenID==PoserToken.E_indexes:
      #self._indexes = int(val)
      pass
    elif tokenID==PoserToken.E_numbDeltas:
      self._numbDeltas = int(val)
    elif tokenID==PoserToken.E_enabled:
      self._enabled = val.startswith("1")
    elif tokenID==PoserToken.E_interpStyleLocked:
      self._interpStyleLocked = int(val)
    elif tokenID==PoserToken.E_staticValue:
      self.setStaticValue(float(val))
    else:
      logging.warning("Unexpected Direct in GenericTranform:%s (%s)", tokenID.token, val)

  #    * @see pftk.poser.kern.StructuredAttribut#write(java.io.PrintWriter,
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    fw.write(f"{nextPfx}name {self._transfName}\n")
    fw.write(f"{nextPfx}initValue {self._initValue}\n")
    WBoolLine(fw, nextPfx, "hidden", self._hidden )
    
    #  Test Poser language version before writing
    if self._pmo and (self._pmo.getPoserFile().isVersion(PoserConst.POSER_V9)):
      WBoolLine(fw, nextPfx, "enabled", self._enabled )
    fw.write(f"{nextPfx}forceLimits {self._forceLimits}\n")
    fw.write(f"{nextPfx}min {self._min}\n")
    fw.write(f"{nextPfx}max {self._max}\n")
    fw.write(f"{nextPfx}trackingScale {self._trackingScale}\n")
    #  Print Keys
    if self._keys != None:
      self._keys.write(fw, nextPfx)
    if self._interpStyleLocked != -sys.maxsize:
      fw.write(f"{nextPfx}interpStyleLocked {self._interpStyleLocked}\n")
    if self._hasStaticValue:
      fw.write(f"{nextPfx}staticValue {self._staticValue}\n")
    for vod in self._lstVOD:
      vod.write(fw, nextPfx)
    for po in self._lstAttr:
      po.write(fw, nextPfx)
    if self._dlt and (len(self._dlt.deltaSet)>0):
      fw.write(f"{nextPfx}indexes {len(self._dlt.deltaSet)}\n")
      fw.write(f"{nextPfx}numbDeltas {self._numbDeltas}\n")
      self._dlt.write(fw, nextPfx)
    fw.write(f"{nextPfx}}}\n")



  def setPoserMeshedObject(self, pmo):
    self._pmo = pmo

  def getPoserMeshedObject(self): return self._pmo

  def getPrintName(self): return self._transfName

  def getQualifiedName(self):
    return (self._pmo.getName() if self._pmo else '?' )+ '.' + self.getName()

  def setPrintName(self, n):
    self._transfName = n

  def isHidden(self): return self._hidden

  def setHidden(self, h):
    self._hidden = h

  def getMin(self): return self._min

  def getMax(self): return self._max

  def setMin(self, m):
    self._min = m

  def setMax(self, m):
    self._max = m

  def setInterpStyleLocked(self, isl):
    self._interpStyleLocked = isl

  def getPrintableDependencies(self):
    return [ vod.getPoserType().token + " " +vod.getGroupName() + " " + vod.getChannelName() for vod in self.getVOD() ]

  def getTrackingScale(self): return self._trackingScale

  def setTrackingScale(self, m):
    self._trackingScale = m

  def setNumbDeltas(self, n):
    self._numbDeltas = n

  def getNumbDeltas(self): return self._numbDeltas

  def getInitValue(self): return self._initValue

  def setInitValue(self, m):
    self._initValue = m

  def getStaticValue(self): return self._staticValue

  def setStaticValue(self, m):
    self._hasStaticValue = True
    self._staticValue = m

  def getForceLimits(self): return self._forceLimits

  def setForceLimits(self, m):
    self._forceLimits = m

  def setDeltaTab(self, tdp):
    self._dlt.deltaSet = tdp
    

  def getKeys(self): return self._keys

  # Convert a GenericTransform to a static one (i.e. no keys)
  def toStatic(self):
    ret = C_OK
    if self._hasStaticValue:
      logging.info("Channel[%s]: keep static=%d", self.getName(), self.getStaticValue())
    else:
      self.setStaticValue(self.getInitValue())
      logging.info("Channel[%s]: set static=%d", self.getName(), self.getStaticValue())

    if self._keys:
      ret = self._keys.toStatic(self.getStaticValue())
    return ret

  # Determine if a target morph shall be taken into account. 
  # @param attrName        Name of the targetGeom or valueParm
  # @param setTargetMorph  Set of names
  # @return    true when the set of target morph is empty AND the attrName starts with "PBM" OR when the set of target contains the given attrName
  @classmethod
  def concerned(cls, attrName, setTargetMorph):
    return attrName.startswith("PBM") if setTargetMorph==None else attrName in setTargetMorph 


class Scale(GenericTransform):

  def __init__(self):
    super(Scale, self).__init__()
    self.ambiguious = True
    self._isSimple = True

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  #    
  def write(self, fw, pfx):
    if self._isSimple:
      fw.write(pfx + self.getPoserType().token + " " + self.getName() + '\n')
    else:
      super(Scale, self).write(fw, pfx)

  def addAttribut(self, po):
    super(Scale, self).addAttribut(po)
    self._isSimple = False

# 
# DepthMapSize attribut.
#  
class DepthMapSize(GenericTransform):
  def __init__(self):
    super(DepthMapSize, self).__init__()
    self.ambiguious = True
    self._isSimple = True

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    if self._isSimple:
      fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    else:
      super(DepthMapSize, self).write(fw, pfx)

  def addAttribut(self, po):
    super(DepthMapSize, self).addAttribut(po)
    self._isSimple = False

# 
# Represents the list of channels of a PoserMeshedObject.
# class Channels(StructuredAttribut):  --> Inlined in PoserMeshedObject

# 
#  * Used to create morph. 
#  
class ChannelMorphStatus(object):
  #    
  PRESENCE_IMG = ("Unused", "in Reference", "in Destination", "Both")
  ATTR = ("Channel", "Presence", "RefFactor", "RefNonNullDesc", "RefHasDelta", "SrcFactor", "SrcNonNullDesc", "SrcHasDelta", "Optimized")

  def __init__(self, cnOrgt, InitSetTargetMorph=None):

    # 
    # * 0x0 = Unused
    # * 0x1 = Used only in Reference figure
    # * 0x2 = Used only in Destination figure
    # * 0x3 = Used by both
    #    
    self.presence = 0
    self.peer = None
    self.hasDelta = False
    
    if isinstance(cnOrgt, GenericTransform):
      self.channelName = cnOrgt.getName()
      self.selected = GenericTransform.concerned(cnOrgt.getName(), InitSetTargetMorph)
      self.finalFactor = cnOrgt.getKeysFactor(0)
      self.updateDelta(cnOrgt)

    else: # cnOrgt is a String
      self.channelName = cnOrgt
      self.finalFactor = 0.0
      self.hasNonNullDesc = False     
      self.selected = False


  def updateDelta(self, attrDesc):
    dlt = attrDesc.getDeltas()
    self.hasDelta = self.hasDelta or dlt

  def getChannelName(self): return self.channelName

  def setChannelName(self, channelName):
    self.channelName = channelName

  def getFinalFactor(self): return self.finalFactor

  def setFinalFactor(self, finalFactor):
    self.finalFactor = finalFactor

  def isHasNonNullDesc(self): return self.hasNonNullDesc

  def setHasNonNullDesc(self, hasNonNullDesc):
    self.hasNonNullDesc = hasNonNullDesc

  def isHasDelta(self): return self.hasDelta

  def setHasDelta(self, hasDelta):
    self.hasDelta = hasDelta

  def isSelected(self): return self.selected

  def setSelected(self, selected):
    self.selected = selected

  def getPeer(self): return self.peer

  def setPeer(self, peer):
    self.peer = peer

  def getPresence(self): return self.presence

  def setPresence(self, presence):
    self.presence = presence


# 
# A list of ChannelMorphStatus
#  
class ChannelMorphStatusList(list):
  FILTER_NONE = 0x0000
  FILTER_NONNULLREFDELTA = 0x0001
  FILTER_REFPRESENCE = 0x0002
  FILTER_NONNULLREFFACTOR = 0x0004


  # 
  # Create an empty list.
  # Create an filtered copy of list lstsrc.
  #    * @param filter
  #    
  # def __init___0(self, filterCode)
  # def __init__(self):
  def __init__(self, filterCode=None, lstsrc=None):
    super(ChannelMorphStatusList, self).__init__()
    self._filter = filterCode if filterCode else ChannelMorphStatusList.FILTER_NONE
    if lstsrc:
      for refCS in lstsrc:
        self.addFiltered(refCS, None)

  def __str__(self):
    return str(len(self))

  def find(self, channelName):
    for c in self:
      if channelName == c.channelName:
        return c
    return None

  def extract(self, channelName):
    for c in self:
      if channelName == c.channelName:
        self.remove(c)
        return c

    return None

  def addFiltered(self, refCS, srcCS):
    refCS.peer = srcCS
    result = True
    if self._filter != self.FILTER_NONE:
      if (self._filter & self.FILTER_NONNULLREFDELTA) == self.FILTER_NONNULLREFDELTA:
        result = result and refCS.hasDelta
      if (self._filter & self.FILTER_REFPRESENCE) == self.FILTER_REFPRESENCE:
        result = result and ((refCS.presence & 0x1) == 0x1)
      if (self._filter & self.FILTER_NONNULLREFFACTOR) == self.FILTER_NONNULLREFFACTOR:
        result = result and (refCS.finalFactor != 0.0)
    if result:
      self.append(refCS)

  def getFilter(self): return self._filter

  # 
  # Return a Set with the selected channels.
  #    
  def getChannelSet(self):
    return { cs.channelName for cs in self if cs.selected }

  # 
  #  Save the list of selected channels.
  #  @param fn  Full path name of the file to create.
  #TODO: Useless and serialization pb due to the link to a Generictransform
#   def saveSelected(self, fn):
#     try:
#       #  Write File Version
#       ois = open(fn, "w")
# 
#       jsonD = { cs.channelName : cs.__dict__ for cs in self if cs.selected }
# 
#       json.dump(jsonD, ois)
# 
#       ois.close()
#       logging.info("List saved in %s (JSON)", fn)
#     except IOError as ioex:
#       ioex.printStackTrace()
# 
#   @classmethod
#   def loadList(cls, fn):
#     l = ChannelMorphStatusList()
#     try:
#       ois = open(fn, "r")
#       data = json.load(ois)
#       for cs in data.values():
#         l.append(cs)
# 
#       ois.close()
#     except IOError as ioex:
#       # ioex.printStackTrace()
#       print(str(ioex))
#       l = None
#     return l


# 
# This class represents the "frontImage" & "sideImage" elements of Poser files.
#  
class FrontImage(StructuredAttribut):
  def __init__(self):
    super(FrontImage, self).__init__()
    self._loaded = False
    self._file = None #  "NO_MAP" 
    self._flipped = False

  def setDirect(self, tokenID, val):
    if tokenID==PoserToken.E_loaded:
      self._loaded = val.startswith("1")
    elif tokenID==PoserToken.E_file:
      self._file = None if val == PoserConst.C_NO_MAPG or val == PoserConst.C_NO_MAP else val
    elif tokenID==PoserToken.E_flipped:
      self._flipped = val.startswith("1")
    else:
      logging.warning("Unexpected Direct in FrontImage:%s (%s)", tokenID.token, val)

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    fw.write(f"{nextPfx}loaded {1 if self._loaded else 0}\n")
    fw.write(f"{nextPfx}file {self._file if self._file else PoserConst.C_NO_MAPG}\n")
    fw.write(f"{nextPfx}flipped {1 if self._flipped else 0}\n")
    for po in self._lstAttr:
      po.write(fw, nextPfx)
    if not self._lstAttr:
      fw.write('\n')
    fw.write(f"{nextPfx}}}\n")

# package: pftk.poser.kern
class SideImage(FrontImage):
  def __init__(self):
    super(SideImage, self).__init__()



class WeightMap(StructuredAttribut):
  def __init__(self, Name=None):
    super(WeightMap, self).__init__(Name)
    self._numbVerts = 0
    self._vertTab = []

  # Overloaded reader    
  def read(self, st):
    self._vertTab = [ ]

    while True:
      code,cn,rw = st.getLine()
      if code== PoserFileParser.TT_WORD:
        if cn=="v":
          tv = rw.split()
          self._vertTab.append( ( int(tv[0]), float(tv[1]) ) )
        elif cn=='numbVerts':
          self._numbVerts = int(rw)
        else: #  Mot illegal
          logging.info("Line[%s] - Not accepted word:%s",st.lineno(), cn)
      elif (code==PoserFileParser.TT_RIGHTBRACKET) or (code==PoserFileParser.TT_EOF): 
        break
      else:
        logging.warning("Line[%s] - Not Accepted :%s", st.lineno(), cn)
        raise ParsingErrorException()

    # End of read

  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")
    fw.write(f"{nextPfx}numbVerts {self._numbVerts}\n")
    for vi in self._vertTab:
      fw.write(f"{pfx}\tv {vi[0]:d} {vi[1]:9.6f}\n")

    fw.write(f"{pfx}\t}}\n")
 


class Zones(StructuredAttribut):
  def __init__(self, Name=None):
    super(Zones, self).__init__(Name)
   
class WeightMapZone(StructuredAttribut):
  def __init__(self, Name=None):
    super(WeightMapZone, self).__init__()
   
class SphereZone(StructuredAttribut):
  def __init__(self, Name=None):
    super(SphereZone, self).__init__()

class CapsuleZone(StructuredAttribut):
  def __init__(self, Name=None):
    super(CapsuleZone, self).__init__(Name)


# E_Data Tuple Key/Value for Customer Data Storage
custData = namedtuple('custData', ['val', 'withPose', 'withMat'])

class CustomData(StructuredAttribut):
  ''' Represents the customData structure that can be found at figure/actor/prop level '''
  def __init__(self, Name=None):
    super(CustomData, self).__init__(Name)
    self._data = {}

  def set(self, key, val, withPose=0, withMat=0):
    self._data[key] = custData(val, withPose, withMat)

  def get(self, key):
    return self._data.get(key, None)

  # Overloaded reader    
  def read(self, st):
    while True:
      code,cn,rw = st.getLine()
      if code== PoserFileParser.TT_WORD:
        if cn=="data":
          tv = rw.split()
          self.set(tv[0], RemoveQuotes(tv[3]), int(tv[1]), int(tv[2]))
        else: #  Mot illegal
          logging.info("Line[%s] - Not accepted word:%s",st.lineno(), cn)
      elif (code==PoserFileParser.TT_RIGHTBRACKET) or (code==PoserFileParser.TT_EOF): 
        break
      else:
        logging.warning("Line[%s] - Not Accepted :%s", st.lineno(), cn)
        raise ParsingErrorException()
    # End of read

  def write(self, fw, pfx):
    fw.write(f"{pfx}{self.getPoserType().token} {self.getName()}\n")
    nextPfx = pfx + "\t"
    fw.write(f"{nextPfx}{{\n")

    nextPfx = pfx + '\tdata {0:s} {1:d} {2:d} "{3:s}"\n'

    for k,d in self._data.items():
      fw.write(nextPfx.format(k, d.withPose, d.withMat, d.val))
 
    fw.write(f"{pfx}\t}}\n")


# 
# Calculate point mapping table :<br>
# For each vertex of srcWG, find the closest vertex in the list of reference WaveGeom 
# If maxDist is not null, some vertex could have <b>no</b> mapping. 
# Should this occur, refGeom attribut of PtMapping is set to null. 
# 
# @param srcWG           Source WaveGeom
# @param lstRefGeom      List of reference WaveGeom
# @param translation     Translation between original MeshedObject and its localisation in this.
# @param maxDist         Maximal distance to take a point into account. If null, no maxDist are applied.
# @return                A Table of non null PtMapping
def calcMapping_KDTree(srcWG, lstRefGeom, translation, maxDist):

    vt = translation if translation else Vector3d()
    tabGeom = [ ]
    tabStart = [ ]

    # Create a numpy table Nx3
    nbsrc=0
    for refGC in lstRefGeom:
      refWG = refGC.getWaveGeom()
      nbsrc += len(refWG.coordList)


    refNo = 0
    npTab = np.zeros( (nbsrc, 3) )
    for refGC in lstRefGeom:
      refWG = refGC.getWaveGeom()
      startNo = refNo
      for p in refWG.coordList:
        npTab[refNo] = [ p.x, p.y, p.z ]
        refNo+=1
        tabGeom.append(refGC)
        tabStart.append(startNo)

    # Create an KDtree with the numpy table
    tree = spatial.KDTree(npTab, leafsize=10 if nbsrc<10000 else 100)

    svect = np.zeros((len(srcWG.coordList),3))
    for i,psrc in enumerate(srcWG.coordList):
      svect[i] = [ psrc.x - vt.x , psrc.y - vt.y , psrc.z - vt.z ]

    rest, resIdx = tree.query( svect, distance_upper_bound=maxDist )

    tabMapping = [ PtMapping(i, int(ri-tabStart[ri]), tabGeom[ri], float(rest[i])) \
                  for i,ri in enumerate(resIdx) if rest[i]<maxDist ]
    
    return tabMapping

# 
# Filter the result list to remove too short vectors.
# Does not modify the source set
#    
def filterLength(setDeltas, minVectLen):
  return { dp.noPt:dp for dp in setDeltas.values() if minVectLen <= dp.norme() }

# 
# @param tabMapping
# @param refFigure
# @param channelName
# @param minVectLen
# @return a set of { noPt:DeltaPoint }
#    
# findNewDelta(PtMapping[] tabMapping, Figure refFigure, String channelName)
# findNewDelta(PtMapping[] tabMapping, PoserMeshedObject refMeshedObj, String channelName)
def findNewDelta(tabMapping, refObj, channelName):
    setNewDeltas = { }
    emptySet = { }

    #if isinstance(refObj, "Figure"):
    if refObj.__class__.__name__ == "Figure":
      lastGeom = None
      for pm in tabMapping:
        if pm.refGeom:
          if pm.refGeom!=lastGeom:
            lastGeom = pm.refGeom
            gt = refObj.getPoserFile().findActor(pm.refGeom.getName()).getTargetGeom(channelName)            
            cachDelta = gt.getDeltas().deltaSet if gt else emptySet
              
          #srcDp = refObj.getPoserFile().findActor(pm.refGeom.getName()).findDelta(channelName, pm.refNo)
          try:
            srcDp = cachDelta[pm.refNo]
            dp = DeltaPoint(pm.srcNo, srcDp.x, srcDp.y, srcDp.z)
            setNewDeltas[dp.noPt] = dp
          except KeyError:
            pass
    else: # refObj is supposed to be a PoserMeshedObject
      gt = refObj.getTargetGeom(channelName)

      # FIX: More robust
      if gt:
        cachDelta = gt.getDeltas().deltaSet if gt.getDeltas() else emptySet
  
        for pm in tabMapping:
          if pm.refGeom:
            try:
              srcDp = cachDelta[pm.refNo]
              dp = DeltaPoint(pm.srcNo, srcDp.x, srcDp.y, srcDp.z)
              setNewDeltas[dp.noPt] = dp
            except KeyError:
              pass

    return setNewDeltas


# Increase recursion limit for very big data sets - For KDTree
sys.setrecursionlimit(20000)
