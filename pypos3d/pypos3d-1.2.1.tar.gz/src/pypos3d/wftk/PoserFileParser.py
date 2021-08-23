# -*- coding: utf-8 -*-

from .WFBasic import Point3d, Vector3d, TexCoord2f

class ParsingErrorException(RuntimeError):
  def __init__(self, s=''):
    super(ParsingErrorException, self).__init__(s)


# File types
OBJ_FNAT, PZ3_FNAT, CR2_FNAT = 0,1,2

class PoserFileParser(object):
  ''' Generic OBJ and Poser file parser.
  New full Python3 implementation (about 10 times faster thanks to readline())
  '''
  TRACER = False
  #  A constant indicating that the end of the stream has been read.
  TT_EOF = -1

  #  A constant indicating that the end of the line has been read.
  TT_EOL = ord('\n')
  TT_CR  = ord('\r')
  TT_QUOTE = '"'

  #  A constant indicating that a number token has been read.
  TT_NUMBER = -2

  #  A constant indicating that a word token has been read.
  TT_WORD = -3

  #  A constant indicating that no token has been read, used for
  #  initializing ttype.  
  TT_NOTHING = -4

  TT_LEFTBACKET, TT_RIGHTBRACKET = -100,-101

  def __init__(self, reader, ftype = PZ3_FNAT):
    ''' PoserFileParser constructor
    Parameters
    ----------
    r : input file reader
    ftype : int
      Real File Nature [PZ3, CR2, OBJ]
    '''
    if not reader:
      raise Exception()
    
    self.pushedBack = False

    # The line number of the last token read
    self.LINENO = 1

    self.sval = None
    self.rval = None
    self.ttype = PoserFileParser.TT_NOTHING
    self.reader = reader

    self._FileNature = ftype
    # Just to store customer version
    self._FileVersion = None


  # returns code, leftWord, rightPart
  # Returned strings are stripped
  def getFullLine(self):
    if self.pushedBack:
      self.pushedBack = False
      return self.ttype, self.sval
      
    rline = self.reader.readline()
    line = rline.strip()    
    self.LINENO+=1
    
    while rline and (line=='' or (line[0]=='#')) :
      rline = self.reader.readline()
      line = rline.strip()    
      self.LINENO+=1
    
    if not line: 
      self.ttype = PoserFileParser.TT_EOF
      self.sval = None
      return PoserFileParser.TT_EOF, ''
    
    self.ttype = PoserFileParser.TT_NOTHING
    return self.ttype, line

  # returns code, leftWord, rightPart
  # Returned strings are stripped
  def getLine(self):
    if self.pushedBack:
      self.pushedBack = False
      return self.ttype, self.sval, self.rval

    rline = self.reader.readline()
    line = rline.strip()    
    self.LINENO+=1
    
    while rline and (line=='' or (line[0]=='#')) :
      rline = self.reader.readline()
      line = rline.strip()    
      self.LINENO+=1
    
    if not line: 
      self.ttype = PoserFileParser.TT_EOF
      self.sval = None
      return PoserFileParser.TT_EOF, '', ''
    
    pos=0
    l = len(line)

    #while (pos<l) and not (self.ctype[line[pos]] if line[pos]<256 else PoserFileParser.CT_ALPHA) & PoserFileParser.CT_WHITESPACE : pos+=1
    while (pos<l) and not line[pos].isspace(): pos+=1
    
    leftWord = line[0:pos]
    lw = pos
    
    #    while (pos<l) and (self.ctype[line[pos]] if line[pos]<256 else PoserFileParser.CT_ALPHA) & PoserFileParser.CT_WHITESPACE: pos+=1
    while (pos<l) and line[pos].isspace(): pos+=1
    
    # Check if Line contains Only one word
    rightPart=line[pos:] if pos<l else ''
    if lw==1: # Check for backets
      code =  PoserFileParser.TT_LEFTBACKET if leftWord=='{' else (PoserFileParser.TT_RIGHTBRACKET if leftWord=='}' else PoserFileParser.TT_WORD)
    else:
      code = PoserFileParser.TT_WORD

    self.ttype = code
    self.sval = leftWord
    self.rval = rightPart

    return code, leftWord, rightPart          
    
 
  def pushBack(self):
    ''' Causes the next call to the self.nextToken method of this
    tokenizer to return the current value in the self.ttype
    field, and not to modify the read values
    '''
    self.pushedBack = True

  def lineno(self):
    '''  Return the current line number. '''
    return self.LINENO

  def readVertex(self): # throws ParsingErrorException
    ''' Read a Vertex : three consecutive floats '''
    try:
      vals = self.rval.split()
      if len(vals)==3:
        v = map(float, vals)
        p = Point3d(*v)
      else:
        raise Exception("Parsing Error in line:"+str(self.LINENO)+" Not a Vertex")

    except ValueError as pex:
      # Raise added on 20201013 (TBC)
      raise Exception("Parsing Error in line:"+str(self.LINENO)+" Not a Vertex")

    #self.skipToNextLine()
    return p

  def readTexture(self): # throws ParsingErrorException
    ''' Read a Texture : two consecutive float'''
    try:
      vals = self.rval.split()
      if len(vals)==2:
        v = map(float, vals)
        p = TexCoord2f(*v)
      else:
        raise Exception("Parsing Error in line:"+str(self.LINENO)+" Not a Texture")

    except ValueError as pex:
      raise Exception("Parsing Error in line:"+str(self.LINENO)+" Not a Texture")

    #self.skipToNextLine()
    return p

  def readNormal(self): # throws ParsingErrorException
    ''' Read a Normal : three consecutive floats '''
    try:
      vals = self.rval.split()
      if len(vals)==3:
        v = map(float, vals)
        p = Vector3d(*v)
      else:
        raise Exception("Parsing Error in line:"+str(self.LINENO)+" Not a Vector3d")

    except ValueError as pex:
      raise Exception("Parsing Error in line:"+str(self.LINENO)+" Not a Vector3d")

    #self.skipToNextLine()
    return p

  def getFileNature(self):
    return self._FileNature

  def getFileVersion(self):
    return self._FileVersion

  def setFileVersion(self, v):
    self._FileVersion = v


