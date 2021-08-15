"""
Translation support
"""
import collections
import os
from logging import Logger
from typing import Dict, Optional, Union, List, Tuple

from ruamel import yaml

from mcdreforged.constants import core_constant
from mcdreforged.minecraft.rtext import RTextBase, RTextList
from mcdreforged.utils import file_util
from mcdreforged.utils.logger import DebugOption

LANGUAGE_RESOURCE_DIRECTORY = os.path.join('resources', 'lang')
HERE = os.path.abspath(os.path.dirname(__file__))


class TranslationManager:
	DEFAULT_LANGUAGE = 'en_us'

	def __init__(self, logger: Logger):
		self.logger = logger
		self.language = self.DEFAULT_LANGUAGE
		self.translations = collections.defaultdict(dict)  # type: Dict[str, Dict[str, str]]

	def load_translations(self):
		language_directory = os.path.join(HERE, LANGUAGE_RESOURCE_DIRECTORY)
		for file_path in file_util.list_file_with_suffix(language_directory, core_constant.LANGUAGE_FILE_SUFFIX):
			language, _ = os.path.basename(file_path).rsplit('.', 1)
			try:
				with open(os.path.join(language_directory, file_path), encoding='utf8') as file_handler:
					translations = dict(yaml.load(file_handler, Loader=yaml.Loader))
				self.translations[language] = translations
				self.logger.debug('Loaded translation for {} with {} entries'.format(language, len(translations)), option=DebugOption.MCDR)
			except:
				self.logger.exception('Failed to load language {} from "{}"'.format(language, file_path))

	def set_language(self, language):
		self.language = language
		if len(self.translations.get(language, {})) == 0:
			self.logger.warning('Setting language to {} with 0 available translation'.format(language))

	def translate(self, key: str, args: tuple, kwargs: dict, *, allow_failure: bool, language: Optional[str] = None, fallback_language: Optional[str] = None, plugin_translations: Optional[Dict[str, Dict[str, str]]] = None) -> Union[str, RTextBase]:
		if language is None:
			language = self.language

		# Translating
		translated_text = self.translations[language].get(key)
		if translated_text is None and plugin_translations is not None:
			translated_text = plugin_translations.get(language, {}).get(key)

		# Check if there's any rtext inside args
		use_rtext = False
		for arg in args:
			if isinstance(arg, RTextBase):
				use_rtext = True

		# Processing
		if translated_text is not None:
			if use_rtext:
				return self.__apply_args(translated_text, args, kwargs)
			else:
				if len(args) > 0:
					translated_text = translated_text.format(*args, **kwargs)
				return translated_text.strip('\n\r')
		else:
			if fallback_language is not None and language != fallback_language:
				try:
					return self.translate(key, args, allow_failure=False, language=fallback_language, fallback_language=None, plugin_translations=plugin_translations)
				except KeyError:
					pass
			if not allow_failure:
				raise KeyError('Translation key "{}" not found'.format(key))
			self.logger.error('Error translate text "{}" to language {}'.format(key, language))
			return key if not use_rtext else RTextBase.from_any(key)

	@classmethod
	def __apply_args(cls, translated_text: str, args: tuple, kwargs: dict) -> RTextBase:
		args = list(args)
		kwargs = kwargs.copy()
		counter = 0
		rtext_elements = []  # type: List[Tuple[str, RTextBase]]

		def get():
			nonlocal counter
			rv = '@@MCDR#Translation#Placeholder#{}@@'.format(counter)
			counter += 1
			return rv

		for i, arg in enumerate(args):
			if isinstance(arg, RTextBase):
				placeholder = get()
				rtext_elements.append((placeholder, arg))
				args[i] = placeholder
		for key, value in kwargs.items():
			if isinstance(value, RTextBase):
				placeholder = get()
				rtext_elements.append((placeholder, value))
				kwargs[key] = placeholder

		texts = [translated_text.format(*args, **kwargs)]
		for placeholder, rtext in rtext_elements:
			new_texts = []
			for text in texts:
				processed_text = []
				if isinstance(text, str):
					for j, ele in enumerate(text.split(placeholder)):
						if j > 0:
							processed_text.append(rtext)
						processed_text.append(ele)
				else:
					processed_text.append(text)
				new_texts.extend(processed_text)
			texts = new_texts
		return RTextList(*texts)
