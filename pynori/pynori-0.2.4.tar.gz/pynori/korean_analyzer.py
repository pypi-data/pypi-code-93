import os
from configparser import ConfigParser

from pynori.korean_tokenizer import KoreanTokenizer
from pynori.korean_posstop_filter import KoreanPOSStopFilter
from pynori.synonym_graph_filter import SynonymGraphFilter
from pynori.pre_processing import PreProcessing
from pynori.post_processing import PostProcessing

from pynori.korean_tokenizer import Type
from pynori.korean_tokenizer import DcpdMode
from pynori.synonym_graph_filter import SynMode


cfg = ConfigParser()
#PATH_CUR = os.getcwd() + '/pynori'
PATH_CUR = os.path.dirname(__file__)
cfg.read(PATH_CUR+'/config.ini')

# OPTION
DECOMPOUND_MODE = cfg['OPTION']['DECOMPOUND_MODE']
INFL_DECOMPOUND_MODE = cfg['OPTION']['INFL_DECOMPOUND_MODE']
VERBOSE = cfg.getboolean('OPTION', 'VERBOSE')
OUTPUT_UNKNOWN_UNIGRAMS = cfg.getboolean('OPTION', 'OUTPUT_UNKNOWN_UNIGRAMS')
DISCARD_PUNCTUATION = cfg.getboolean('OPTION', 'DISCARD_PUNCTUATION')
# FILTER
USE_SYNONYM_FILTER = cfg.getboolean('FILTER', 'USE_SYNONYM_FILTER')
USE_POS_FILTER = cfg.getboolean('FILTER', 'USE_POS_FILTER')
MODE_SYNONYM_FILTER = cfg['FILTER']['MODE_SYNONYM_FILTER']
# PATH
PATH_USER_DICT = cfg['PATH']['USER_DICT']


class KoreanAnalyzer(object):
	"""Analyzer for Korean text, composed of Pre-/Post-processors, Filters, and Tokenizers.

	KoreanAnalyzer - Users only need to initialize this object.
	Basic only use tokenizer.
	Advanced constructs pipeline that consists of Pre-/Post-processors, Filters, and Tokenizers.
	The order of the pipeline is important.
	"""

	def __init__(self, 
				 verbose=VERBOSE,
				 path_userdict=PATH_USER_DICT,
				 decompound_mode=DECOMPOUND_MODE,
				 infl_decompound_mode=INFL_DECOMPOUND_MODE,
				 output_unknown_unigrams=OUTPUT_UNKNOWN_UNIGRAMS,
				 discard_punctuation=DISCARD_PUNCTUATION,
				 pos_filter=USE_POS_FILTER,
				 stop_tags=KoreanPOSStopFilter.DEFAULT_STOP_TAGS,
				 synonym_filter=USE_SYNONYM_FILTER, 
				 mode_synonym=MODE_SYNONYM_FILTER):
		self.pre_processor = PreProcessing()
		self.post_processor = PostProcessing()
		self.kor_tokenizer = KoreanTokenizer(verbose, 
											 path_userdict, 
											 decompound_mode,
											 infl_decompound_mode,
											 output_unknown_unigrams, 
											 discard_punctuation)
		self.pos_filter = pos_filter
		self.kor_pos_filter = KoreanPOSStopFilter(stop_tags=stop_tags)
		self.synonym_filter = synonym_filter
		self.mode_synonym = mode_synonym
		self.syn_graph_filter = None
		if self.synonym_filter: # SynonymGraphFilter 초기화 처리 지연 시간으로 True일 때만 활성.
			self.syn_graph_filter = SynonymGraphFilter(preprocessor=self.pre_processor, 
													   kor_tokenizer=self.kor_tokenizer, 
													   mode_synonym=self.mode_synonym)

	def do_analysis(self, in_string):
		"""Analyze text input string and return tokens
			
			Filtering 순서에 유의. (POS -> SYNONYM)
		"""

		if not isinstance(in_string, str):
			raise ValueError(
					f"the input type must be {type('')}"
				)

		##################
		# Pre-processing #
		##################
		in_string = self.pre_processor.lower(in_string)

		##############
		# Tokenizing #
		##############
		self.kor_tokenizer.set_input(in_string)
		while self.kor_tokenizer.increment_token():
			pass
		tkn_attr_obj = self.kor_tokenizer.tkn_attr_obj

		#################
		# POS Filtering #
		#################
		if self.pos_filter:
			tkn_attr_obj = self.kor_pos_filter.do_filter(tkn_attr_obj)

		#####################
		# Synonym Filtering #
		#####################
		if self.synonym_filter:
			tkn_attr_obj = self.syn_graph_filter.do_filter(tkn_attr_obj)

		# reset token offset
		#tkn_attr_obj = self._reset_token_offset(tkn_attr_obj)

		###################
		# Post-processing #
		###################
		MIN_CHAR_LENGTH = 7
		if len(tkn_attr_obj.termAtt) == 1 and tkn_attr_obj.dictTypeAtt[0] == Type.UNKNOWN and len(tkn_attr_obj.termAtt[0]) >= MIN_CHAR_LENGTH:
			tkn_attr_obj = self.post_processor.relax_long_unk(tkn_attr_obj, self.kor_tokenizer)

		# reset token offset
		#tkn_attr_obj = self._reset_token_offset(tkn_attr_obj)

		return tkn_attr_obj.__dict__

	def _reset_token_offset(self, tkn_attrs):
		# TODO: 필터링 후 포지션 재정렬 필요.
		pass

	def set_option_tokenizer(self,
							 decompound_mode=None, 
							 infl_decompound_mode=None, 
							 output_unknown_unigrams=None, 
							 discard_punctuation=None):
		if decompound_mode is not None: 
			self.kor_tokenizer.mode = decompound_mode
		if infl_decompound_mode is not None: 
			self.kor_tokenizer.infl_mode = infl_decompound_mode
		if output_unknown_unigrams is not None: 
			self.kor_tokenizer.output_unknown_unigrams = output_unknown_unigrams
		if discard_punctuation is not None: 
			self.kor_tokenizer.discard_punctuation = discard_punctuation
		pass

	def set_option_filter(self,
						  pos_filter=None,
						  stop_tags=None,
						  synonym_filter=None,
						  mode_synonym=None):
		if pos_filter is not None:
			self.pos_filter = pos_filter
		if stop_tags is not None:
			self.kor_pos_filter.stop_tags = stop_tags
		if synonym_filter is not None or mode_synonym is not None:
			if self.synonym_filter or synonym_filter:
				# 주의: 현재 상태 모드의 kor_tokneizer가 입력.
				self.syn_graph_filter = SynonymGraphFilter(preprocessor=self.pre_processor,
														   kor_tokenizer=self.kor_tokenizer, 
														   mode_synonym=mode_synonym)
		if mode_synonym is not None:
			self.mode_synonym = mode_synonym
		if synonym_filter is not None:
			self.synonym_filter = synonym_filter
		pass


if __name__ == "__main__":

	nori = KoreanAnalyzer(decompound_mode=DcpdMode.MIXED,
						  infl_decompound_mode=DcpdMode.DISCARD,
						  discard_punctuation=True,
						  output_unknown_unigrams=False,
						  pos_filter=False, stop_tags=['JKS', 'JKB', 'VV', 'EF'])

	print(nori.do_analysis("아빠가 방에 들어가신다."))

