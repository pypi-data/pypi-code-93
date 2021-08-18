import os
from copy import deepcopy

from configparser import ConfigParser
from pynori.dict.trie import Trie
from pynori.token_attribute import TokenAttribute

cfg = ConfigParser()
#PATH_CUR = os.getcwd() + '/pynori'
PATH_CUR = os.path.dirname(__file__)
cfg.read(PATH_CUR+'/config.ini')

# PATH
PATH_SYN_DICT = cfg['PATH']['SYN_DICT']



class SynMode(object):
	""" Synonym mode to select synonyms """
	NORM = 'NORM' # select representative synonym token
	EXT = 'EXTENSION' # select all synonym tokens


class SynonymGraphFilter(object):
	"""Synonym Text Processing

	Add synonym words to token stream / or Norm synonmy words
	keeping token offsets.

	Parameters
	----------
	kor_tokenizer

	mode_synonym : {'EXTENSION', 'NORM'}

	동의어 필터링 특징
	 - Decompound 모드(MIXED, DISCARD, NONE)에 상관없이 동작

	"""

	def __init__(self, preprocessor, kor_tokenizer, mode_synonym):
		self.SEP_CHAR = '_' # separate charcter in token
		self.preprocessor = preprocessor
		self.kor_tokenizer = kor_tokenizer # korean_analyzer.py 에서 decompound mode가 이미 결정
		self.mode_synonym = mode_synonym
		self.syn_trie = None
		self.synonym_build(PATH_CUR+PATH_SYN_DICT)
		pass

	def _simple_tokenizer(self, in_string):
		# Pre-processing
		in_string = self.preprocessor.pipeline(in_string)
		# Tokenizing
		self.kor_tokenizer.set_input(in_string)
		while self.kor_tokenizer.increment_token():
			pass
		return self.kor_tokenizer.tkn_attr_obj

	def synonym_build(self, path_syn_file):
		# File Read
		entries = []
		with open(path_syn_file, 'r', encoding='utf-8') as rf:
			for line in rf:
				line = line.strip()
				if len(line) == 0:
					continue
				if line[:2] == '# ': # 주석 line
					continue
				entries.append(line)
		
		# Save entries to data structure.
		self.syn_trie = Trie()
		for line in entries:
			tkn_attr_obj_list = []
			for i, token in enumerate(line.split(',')): # list
				tkn_attr_obj_list.append(self._simple_tokenizer(token)) # tkn_attr_obj

			if self.mode_synonym == SynMode.EXT:
				trie_result = tkn_attr_obj_list
			elif self.mode_synonym == SynMode.NORM:
				trie_result = [tkn_attr_obj_list[0]] # 첫 번째 토큰을 동의어 대표어

			for tkn_attr_obj in tkn_attr_obj_list: # result
				self.syn_trie.insert(self.SEP_CHAR.join(tkn_attr_obj.termAtt), trie_result)

	def _set_token_attribute(self, source, target, idx):
		for name, _ in target.__dict__.items():
			target.__dict__[name].append(source.__dict__[name][idx])
		return target

	def do_filter(self, tkn_attrs):
		new_tkn_attrs = TokenAttribute()
		token_list = tkn_attrs.termAtt
		step = 0

		for m, _ in enumerate(token_list):
			if m < step:
				# m 이 아닌 n+1 이상에서 [C]가 실행된 경우 step을 맞춰줌
				continue

			token = token_list[step] # 현재 step의 token
			for n in range(m, len(token_list)):
				tkn, node = self.syn_trie.search(token)
				if tkn == False and node is None: # [A]
					# 해당 token의 마지막 음절 기준으로 trie 검색이 안되는 경우 & trie 검색 결과값이 없는 경우
					# 단, token의 마지막이 아닌 음절은 trie 검색이 가능함.

					if len(token.split(self.SEP_CHAR)) == 1:
						new_tkn_attrs = self._set_token_attribute(tkn_attrs, new_tkn_attrs, n)
						step = n+1
						break
					else:
						new_tkn_attrs = self._set_token_attribute(tkn_attrs, new_tkn_attrs, n-1)
						step = n
						break

				if tkn == True and node is None: # [B]
					# 해당 token의 마지막 음절 기준으로 trie 검색이 된 경우 & trie 검색 결과값이 없는 경우
					# ex) 해당 token이 노드가 생성된 token의 부분집합이고 그의 동의어가 없는 경우 (ex. '노리_분석기' 에서 현재 token이 '노리')

					if n == len(token_list)-1:
						new_tkn_attrs = self._set_token_attribute(tkn_attrs, new_tkn_attrs, n)
					else:
						token += self.SEP_CHAR
						token += token_list[n+1]
						continue

				if tkn == True and node is not None: # [C]
					# 동의어 사전 룩업 성공
					# 해당 token의 마지막 음절 기준으로 trie 검색이 된 경우 & trie 검색 결과값이 있는 경우

					# 속도 감소가 우려됨. "노리_분석_기" 케이스 동의어 최장일치 확장 문제.
					# if n < len(token_list)-1:
					# 	# 한 토큰 앞을 먼저 확인. (동의어 최장일치를 위해서)
					# 	while True:
					# 		tkn_f, node_f = self.syn_trie.search(token+self.SEP_CHAR+token_list[n+1])
					# 		if tkn_f == True and node_f is not None:
					# 			break
					# 		else:
					# 			token += self.SEP_CHAR
					# 			token += token_list[n+1]

					for trie_tkn_attrs in node.result[0]:
						for k, _ in enumerate(trie_tkn_attrs.termAtt):
							new_tkn_attrs = self._set_token_attribute(trie_tkn_attrs, new_tkn_attrs, k)
					step = n+1
					break

		return new_tkn_attrs

