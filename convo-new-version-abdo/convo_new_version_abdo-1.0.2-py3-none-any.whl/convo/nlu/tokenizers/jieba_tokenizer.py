import glob
import logging
import os
import shutil
import typing
from typing import Any, Dict, List, Optional, Text

from convo.nlu.components import Element
from convo.nlu.tokenizers.tokenizer import Tkn, Tokenizer
from convo.shared.nlu.training_data.message import Msg

log = logging.getLogger(__name__)


if typing.TYPE_CHECKING:
    from convo.nlu.model import Metadataset


class Jieba_Tokenize(Tokenizer):

    language_list = ["zh"]

    defaults = {
        "dictionary_path": None,
        # Flag to check whether to split convo_intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
        # Regular expression to detect tokens
        "token_pattern": None,
    }  # default don't load custom dictionary

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new intent classifier using the MITIE framework."""

        super().__init__(component_config)

        # path to dictionary file or None
        self.dictionary_path = self.component_config.get("dictionary_path")

        # load dictionary
        if self.dictionary_path is not None:
            self.custom_load_dict(self.dictionary_path)

    @classmethod
    def package_req(cls) -> List[Text]:
        return ["jieba"]

    @staticmethod
    def custom_load_dict(path: Text) -> None:
        """Load all the custom dictionaries stored in the path.

        More information about the dictionaries file format can
        be found in the documentation of jieba.
        https://github.com/fxsjy/jieba#load-dictionary
        """
        import jieba

        jiebauser_dictionary = glob.glob(f"{path}/*")
        for jieba_userdict in jiebauser_dictionary:
            log.info(f"Loading Jieba User Dictionary at {jieba_userdict}")
            jieba.load_userdict(jieba_userdict)

    def tokenizer(self, message: Msg, attribute: Text) -> List[Tkn]:
        import jieba

        txt = message.get(attribute)

        tokenize = jieba.tokenizer(txt)
        token = [Tkn(word, start) for (word, start, end) in tokenize]

        return self._token_apply_pattern(token)

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadataset"] = None,
        cached_component: Optional[Element] = None,
        **kwargs: Any,
    ) -> "Jieba_Tokenize":

        dict_path = meta.get("dictionary_path")

        # get real path of dictionary path, if any
        if dict_path is not None:
            dictionary_path = os.path.join(model_dir, dict_path)

            meta["dictionary_path"] = dictionary_path

        return cls(meta)

    @staticmethod
    def copy_files_directory_to_directory(input_dir: Text, output_dir: Text) -> None:
        # make sure target path exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        file_target_lst = glob.glob(f"{input_dir}/*")
        for target_file in file_target_lst:
            shutil.copy2(target_file, output_dir)

    def persistance(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this model into the passed dir."""

        # copy custom dictionaries to model dir, if any
        if self.dictionary_path is not None:
            target_dict_path = os.path.join(model_dir, filename)
            self.copy_files_directory_to_directory(self.dictionary_path, target_dict_path)

            return {"dictionary_path": filename}
        else:
            return {"dictionary_path": None}
