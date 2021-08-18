
class TokenAttribute(object):
	"""Token Attribute Info."""
	
	def __init__(self):
		self.termAtt = [] # CharTermAttribute 
		self.offsetAtt = [] # OffsetAttribute 
		#self.posIncAtt = [] # PositionIncrementAttribute 
		self.posLengthAtt = [] # PositionLengthAttribute 
		#self.posAtt = [] # PartOfSpeechAttribute 
		#self.readingAtt = [] # ReadingAttribute 
		self.posTypeAtt = []
		self.posTagAtt = []
		self.dictTypeAtt = []
