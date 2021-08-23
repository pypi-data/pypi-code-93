# -*- coding: utf-8 -*-

import logging
from collections import namedtuple
import numpy as np
from scipy import interpolate

from pypos3d.wftk.PoserFileParser import PoserFileParser, ParsingErrorException
from pypos3d.pftk.PoserBasic import PoserConst, PoserObject, PoserToken, Lang, index, WBoolLine 

# package: pypos3d.pftk
#  
class SimpleAttribut(PoserObject):
  ''' Base class for single value entry of a Poser file :  NAME VALUE '''

  def __init__(self, n=None, value=None):
    super(SimpleAttribut, self).__init__()
    if n:
      self.setName(n.token)
      self.setPoserType(n)
    else:
      self.setPoserType(PoserToken.BADTOKEN)
        
    self._value = value

  #  (non-Javadoc)
  #    * @see deyme.v3d.poser.PoserObject#read(deyme.v3d.poser.PoserFileParser)
  #    
  def read(self, st, val):
    self._value = val if val else None

  def getValue(self):
    return self._value

  def setValue(self, v):
    self._value = v

  def TAS(self, oldValue, newValue):
    if oldValue == self.getValue():
      self.setValue(newValue)

  def getIntegerValue(self):
    return int(self._value)

  def getDoubleValue(self):
    return float(self._value)

  def getBooleanValue(self):
    return (self._value != "0")

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  #    
  def write(self, fw, pfx):
    v = self.getValue()
    if v:
      fw.write(f"{pfx}{self.getName()} {v}\n")
    else:
      fw.write(f"{pfx}{self.getName()}\n")


# addchild and weld attributs
# class AddChildSA(SimpleAttribut): --> Replaced by PMOLink in Figure

# 
#  * Attribute alone on its line : "ON", "OFF" and flipped
#  
class OffSA(SimpleAttribut):

  def __init__(self, n = None):
    if n:
      super(OffSA, self).__init__(Lang[n], "")
    else:
      super(OffSA, self).__init__()
      
    self.setName(n)

  def read(self, st, val):
    self._value = val if (self.getPoserType()==PoserToken.E_flipped) and (val!=None) else ''


# 
#  Color attribut
#  class ColorSA(SimpleAttribut):
# 
# Orientation Attribut
#  class OrientationSA(SimpleAttribut):
# 
# Origin Attribut
#  class OriginSA(SimpleAttribut):
# 
# StorageOffseSA  Attribut
# class StorageOffsetSA(SimpleAttribut):

# 
# Just read the entire line
#  
class TextureMapSA(SimpleAttribut):
  def __init__(self, t=None, initPath=None):
    super(TextureMapSA, self).__init__(n=t)
    if initPath:
      if isinstance(initPath, TextureMapSA):        
        self.setPoserType(initPath.getPoserType())    
        self._name = initPath.getName()    
        self.setPath(initPath.getPath())
      else:
        self.setPath("" if initPath==PoserConst.C_NO_MAP else initPath)
    else:
      self._path = ''
      self._value = PoserConst.C_NO_MAP
      
  def read(self, st, val):
    self._path = val
    if self._path==PoserConst.C_NO_MAP:
      self._value = self._path
    else:
      _, val = st.getFullLine()
      self._value = self._path + "\n\t" + val

  def getPath(self): return self._path
  
  def setPath(self, p):
    self._path = p
    self._value = self._path + ('\n\t 0 0' if p else '')
    

#  
# Dimension attribut.
#  class DimensionSA(SimpleAttribut):
# endPoint attribut
#  class EndPointSA(SimpleAttribut):

# 
# This class represents the following attributs :
#  * widthRange       0.400000 0.700000
#  * lengthRange     0.040000 0.040000
#  * 
#  * Found in Poser 6 hair Prop.
#  
# class HairRange(SimpleAttribut):


class SphereMathsRaw(SimpleAttribut):
  
  def __init__(self):
    super(SphereMathsRaw, self).__init__()
    self.m = [ '', '' ]

  # Read two 4x4 matrix of double
  def read(self, st, val):
    for i in range(0, 2):
      self.m[i] = ''
      for j in range(0,4):
        code, val = st.getFullLine()
        self.m[i] += val + '\n'
       
    self._value = "\n\t" + self.m[0] + "\n" + self.m[1]


# Tuple Key/Value for OpKey operation
valueKey = namedtuple('valueKey', ['key', 'val'])

# 
#  * This class represents a Poser Mathematical operation between channels
#  * 
#  
class ValueOpDelta(SimpleAttribut):
  #  Should not be used, because SimpleAttribut stores already the tokenID
  #  PTK deltaType = null;
  # 
  #    *  Default constructor needed by StructuredAttribut.

  # if figure and actor not null
  #   * Create an operation from a text expression
  #   * +QualifiedChannelName
  #   * -QualifiedChannelName
  #   * +VAL*QualifiedChannelName
  #   * 
  #   * QualifiedChannelName = [ActorName [':' bodyIndex] '.' ]ChannelName
  #   * 
  # public ValueOpDelta(PoserToken deltaType, String figureName, String actorName, String channelName, float ctrlRatio)
  # public ValueOpDelta(Figure fig, PoserActor curAct, String expr)
  def __init__(self, deltatype=None, pfigure=None, pactor=None, channelExpr=None, ctrlRatio=None, keys:'list of (key,val)'=None, src=None):
    super(ValueOpDelta, self).__init__(deltatype if deltatype else src.getPoserType() if src else None)
    self.lstValKeys = [ ]

    if pfigure and isinstance(pfigure, str) and pactor and channelExpr:
      self.l0 = pfigure
      self.l1 = pactor # As Name
      self.l2 = channelExpr # As Name
      self.controlRatio = ctrlRatio if ctrlRatio else 0.0
      
      if keys:
        # Force type to OpKey
        self.setPoserType(PoserToken.E_valueOpKey)
        for t in keys:
          self.addValueKey(t[0], t[1])


    elif pfigure and pactor and channelExpr:
      # String Cleaning
      expr = channelExpr.strip()
  
      if (expr[0]=="'") or (expr[0]=="\""):
        expr = expr[1:]
  
      if (expr[-1]=="'") or (expr[-1]=="\""):
        expr = expr[:len(expr) - 1]
  
      if (len(expr) < 2):
        logging.info("Too short string")
        return
  
      expr = expr.strip()
  
      c0 = expr[0]
      c1 = expr[1]
  
      qualifiedName = None
  
      opType = PoserToken.E_valueOpDeltaAdd if (c0.isdigit() or (c1.isdigit() and ((c0 == '+') or (c0 == '-')))) else \
               PoserToken.E_valueOpPlus  if c0=='+' else \
               PoserToken.E_valueOpMinus if c0=='-' else \
               PoserToken.E_valueOpTimes if c0=='*' else \
               PoserToken.E_valueOpDivideBy if c0=='/' else \
               PoserToken.BADTOKEN
  
      self.setPoserType(opType)
      self.setName(opType.token)
  
      if (opType==PoserToken.E_valueOpPlus) or (opType==PoserToken.E_valueOpMinus) or \
         (opType==PoserToken.E_valueOpTimes) or (opType==PoserToken.E_valueOpDivideBy):
        qualifiedName = expr[1:]
      elif opType==PoserToken.E_valueOpDeltaAdd: # case(PoserToken.E_valueOpDeltaAdd):
        posstar = expr.find('*')
        self.controlRatio = float(expr[0:posstar])
        qualifiedName = expr[posstar + 1:]
      else: # Error
        raise ParsingErrorException('Incorrect Expression:'+expr)
  
      ptind = qualifiedName.find('.')
      if ptind < 0:
        self.l0 = "Figure " + str(pfigure.getBodyIndex())
        self.l1 = pactor.getName()
        self.l2 = qualifiedName
      else:
        self.l1 = qualifiedName[0:ptind]
        
        ptdp = qualifiedName.find(':')
        if (ptdp < 0):
          self.l1 += ':' + str(pfigure.getBodyIndex())
  
        self.l0 = "Figure " + str(index(self.l1))
        self.l2 = qualifiedName[ptind + 1:]
  
    elif src: # Copy Constructor
      self.setName(src.getPoserType().token)
      self.l0 = src.l0
      self.l1 = src.l1
      self.l2 = src.l2
      self.controlRatio = src.controlRatio
      
      if src.lstValKeys:
        for t in src.lstValKeys:
          self.addValueKey(t[0], t[1])

    else: # Default Creator called 
      self.l0 = ''
      self.l1 = ''
      self.l2 = ''
      self.controlRatio = 0.0

    self._value = self.l0 + "\n" + self.l1 + "\n" + self.l2


  def calc(self, curv, parentv):
    ''' Compute the result of the operator '''
    opType = self.getPoserType()
    if opType==PoserToken.E_valueOpDeltaAdd:      
      return curv + parentv * self.controlRatio
    
    elif opType==PoserToken.E_valueOpPlus:
      return curv + parentv
    
    elif opType==PoserToken.E_valueOpMinus:
      return curv - parentv
    
    elif opType==PoserToken.E_valueOpTimes:
      return curv * parentv
    
    elif opType==PoserToken.E_valueOpDivideBy:
      return curv / parentv
    
    elif opType==PoserToken.E_valueOpKey:
      # logging.warning("ValueOpKey not implemented for Channel [%s] for [%s.%s]", self.l0, self.l1, self.l2)      
      if not self.lstValKeys: return 0.0
      
      firstp = self.lstValKeys[0]
      lastp = self.lstValKeys[-1]
      
      if parentv<=firstp[0]: return firstp[1]
      
      if parentv>=lastp[0]: return lastp[1]
      
      # if len(self.lstValKeys)==1: Shall fall in two previous cases
      nbkeys = len(self.lstValKeys) 
      if nbkeys==2: # Do a linear interpolation
        if lastp[0]==firstp[0]: return firstp[1]
        m = (lastp[1] - firstp[1]) / (lastp[0] -firstp[0])        
        p = firstp[1] - m*firstp[0]
        return m*parentv+p
        
      else: # Do a Quadratic or a Cubic Spline interpolation
        tabX = np.array( [ vk[0] for vk in self.lstValKeys ])
        tabY = np.array( [ vk[1] for vk in self.lstValKeys ])
        tck = interpolate.splrep(tabX, tabY, k=nbkeys-1 if nbkeys<=3 else 3)
        k = interpolate.splev(parentv, tck, der=0)
        return float(k)
      
    elif opType==PoserToken.E_valueOpDivideInto:
      logging.warning("ValueOpDivideInto not supported for Channel [%s] for [%s.%s]", self.l0, self.l1, self.l2)
      return curv


  # Add a pair {key value} the a OptKey operation
  # @param key
  # @param val
  def addValueKey(self, key, val):
    vk = valueKey(key, val)
    self.lstValKeys.append(vk)

  def read(self, st, val):
    code, self.l0 = st.getFullLine()
    code, self.l1 = st.getFullLine()
    code, self.l2 = st.getFullLine()
    
    if self.getPoserType()==PoserToken.E_valueOpDeltaAdd:
      code,cn,rw = st.getLine() #  Should get 'deltaAddDelta'      
      self.controlRatio = float(rw)
    else:
      if self.getPoserType() == PoserToken.E_valueOpKey:
        code,cn,rw = st.getLine() #  Should get 'beginValueKeys'
        #  While next token != endValueKeys : Store the keys        
        while True:
          code,cn,rw = st.getLine()
          if code==PoserFileParser.TT_WORD:
            try:
              vc = Lang[cn]

              if vc==PoserToken.E_valueKey:  
                tv = rw.split()                    
                self.addValueKey(float(tv[0]), float(tv[1]))
              elif vc==PoserToken.E_endValueKeys:
                break
              else:
                logging.warning("L[" + st.lineno() + "] - Not Accepted :" + st.sval)
                continue 
            except KeyError:
              logging.warning("L[" + st.lineno() + "] - Not Accepted :" + st.sval)
              raise ParsingErrorException()
          elif code==PoserFileParser.TT_EOF: 
            break

    _value = self.l0 + "\n" + self.l1 + "\n" + self.l2

  #    * @see deyme.v3d.poser.PoserObject#write(java.io.FileWriter)
  #    
  def write(self, fw, pfx):
    fw.write(pfx + self.getName() + '\n')
    #  FIX 20140329 - Use indentation to avoid some cross bug in Poser7
    #  fw.write(pfx + "\t" + getValue());
    fw.write(pfx + "\t" + self.l0 + '\n')
    fw.write(pfx + "\t" + self.l1 + '\n')
    fw.write(pfx + "\t" + self.l2 + '\n')
    #  fw.write(pfx + "\t" + getValue().replaceAll("\n", pfx+"\n"));
    if self.getPoserType()==PoserToken.E_valueOpDeltaAdd:
      fw.write(pfx + "\tdeltaAddDelta " + str(self.controlRatio) + '\n')
    elif self.getPoserType()==PoserToken.E_valueOpKey:
      fw.write(pfx + '\tbeginValueKeys\n')
      for vk in self.lstValKeys:
        fw.write(pfx + "\t  valueKey " + str(vk.key) + " " + str(vk.val) + '\n')
      fw.write(pfx + '\tendValueKeys\n')

  def getFigureName(self): return self.l0

  def getGroupName(self): return self.l1

  def setGroupName(self, gn):
    self.l1 = gn
    self._value = self.l0 + "\n" + self.l1 + "\n" + self.l2

  def getChannelName(self): return self.l2

  def getControlRatio(self): return self.controlRatio

  def setControlRatio(self, cr):
    self.controlRatio = cr



# 
#  KS Attribut
#  
class KSA(SimpleAttribut):
  def __init__(self, frameNo = -1, f=0.0, src=None):
    self._noFrame = src._noFrame if src else frameNo
    self._factor = src._factor if src else f

    #    * 0x80 : hasFlag
    #    * 0x40 : sl
    #    * 0x20, 0x10, 0x08 : spl=0x20, lin=0x10, con=0x08
    #    * 0x00=sm 0x01=br
    self._flags = src._flags if src else 0x00

  def getFactor(self): return self._factor

  def setFactor(self, f):
    self._factor = f

  def getFrameNo(self): return self._noFrame

  def setSl(self, sl):
    if sl:
      self._flags |= 0x40
    else:
      self._flags &= 0xBF
    self._flags |= 0x80

  def isSl(self): return (self._flags & 0x40) != 0

  def getCurveType(self):
    if (self._flags & 0x20) != 0: return PoserToken.E_spl
    if (self._flags & 0x10) != 0: return PoserToken.E_lin
    if (self._flags & 0x08) != 0: return PoserToken.E_con
    return None

  def setCurveType(self, ct):
    if ct == PoserToken.E_spl:
      self._flags |= 0x20
    else:
      if ct == PoserToken.E_lin:
        self._flags |= 0x10
      else:
        self._flags |= 0x08
    self._flags |= 0x80

  def setCurveCnx(self, cc):
    if cc == PoserToken.E_br:
      self._flags |= 0x01
    else:
      self._flags &= 0xFE
    self._flags |= 0x80

  def write(self, fw, pfx):
    fw.write(f"{pfx}k {self._noFrame} {self._factor}\n")
    if self._flags & 0x80:
      WBoolLine(fw, pfx, "sl", ((self._flags & 0x40) != 0))
      fw.write(f"{pfx}{'spl' if self._flags & 0x20 else ('lin' if self._flags & 0x10 else 'con')}\n")
      fw.write(f"{pfx}{'br' if self._flags & 0x01 else 'sm'}\n")

#  
# linkParms attribut
#  
class LinkParmsSA(SimpleAttribut):
  def __init__(self, item='', parent=''):
    super(LinkParmsSA, self).__init__()
    self.MasterGroupName = item
    self.MasterChannelName = parent
    self.setValue(self.MasterGroupName + "\n\t" + self.MasterChannelName)
    self.SlaveGroupName = ''
    self.SlaveChannelName = ''
    
  def read(self, st, val):
    self.MasterGroupName = val
    code,self.MasterChannelName = st.getFullLine()
    code,self.SlaveGroupName = st.getFullLine()    
    code,self.SlaveChannelName = st.getFullLine()
    self._value = self.MasterGroupName + "\n\t\t" + self.MasterChannelName + "\n\t\t" + self.SlaveGroupName + "\n\t\t" + self.SlaveChannelName

  def getChildName(self): return self.getName()

  def getParentName(self): return self.MasterChannelName


#  
# LinkWeight attribut.
#   class LinkWeightSA(SimpleAttribut):
#  
# Just read the entire line
#  class NameSA(SimpleAttribut):


# if __name__ == '__main__':
#   print(dir(SimpleAttribut))

