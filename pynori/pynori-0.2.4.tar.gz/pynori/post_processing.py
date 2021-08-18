import os
from configparser import ConfigParser

from pynori.token_attribute import TokenAttribute
from pynori.pos import POS
from pynori.korean_tokenizer import Type

cfg = ConfigParser()
#PATH_CUR = os.getcwd() + '/pynori'
PATH_CUR = os.path.dirname(__file__)
cfg.read(PATH_CUR+'/config.ini')

# PREPROCESSING
ENG_LOWER = cfg.getboolean('POSTPROCESSING', 'RELAX_LONG_UNK')


class PostProcessing(object):
	"""Postprocessing modules
	   
	   It doesn't need to be initialized.
	"""

	def __init__(self):
		pass

	def _init_unk_token_attribute(self, ternAtt, offsetAtt):
		""" 길이가 1이고 첫 번째의 unknown token attribute를 생성
		"""
		unk_x = TokenAttribute()
		unk_x.termAtt = [ternAtt] 
		unk_x.offsetAtt = [offsetAtt]
		unk_x.posLengthAtt = [1]
		unk_x.posTypeAtt = [POS.Type.MORPHEME]
		unk_x.posTagAtt = ['UNKNOWN'] # unk.def 파일 참조. 보통 unk token은 HANGUL이다.
		unk_x.dictTypeAtt = [Type.UNKNOWN]
		return unk_x


	def _merge_token_attribute(self, source, target):
		""" source token attribute를 
			target token attribute에 append한다.
		"""
		for name, _ in target.__dict__.items():
			target.__dict__[name] += (source.__dict__[name]) # 둘 다 list이므로 +=
		return target

	def relax_long_unk(self, 
					   tkn_attr_obj, 
					   kor_tokenizer):

		long_unknown_token = tkn_attr_obj.termAtt[0]

		# 첫 문자가 반복되는 idx 획득
		idx = -1
		for i, ch in enumerate(long_unknown_token):
			if i == 0:
				pch = ch
			if ch != pch:
				idx = i
				break

		if idx == -1: # 아무것도 하지 않고 그대로 출력 (ex. 'ㅠㅠㅠㅠㅠㅠㅠ')
			return tkn_attr_obj 

		# 문자열 분할
		front_string = long_unknown_token[:idx]
		rest_string = long_unknown_token[idx:]

		# front_string 그대로 token attribute 획득
		front_tkn_attr = self._init_unk_token_attribute(ternAtt=front_string, offsetAtt=(0, len(front_string)-1))

		# rest_string 토크나이징 재실시
		kor_tokenizer.set_input(rest_string)
		while kor_tokenizer.increment_token():
			pass
		rest_tkn_attr = kor_tokenizer.tkn_attr_obj

		return self._merge_token_attribute(source=rest_tkn_attr, target=front_tkn_attr)
		






	