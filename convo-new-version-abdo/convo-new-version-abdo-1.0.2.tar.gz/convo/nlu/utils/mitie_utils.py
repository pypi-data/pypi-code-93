import os
import typing
from typing import Any, Dict, List, Optional, Text

from convo.nlu.components import Element
from convo.nlu.config import ConvoNLUModelConfiguration, overriding_dfault_values
from convo.nlu.model import Metadataset

if typing.TYPE_CHECKING:
    import mitie


class NLP_Mitie(Element):

    defaults = {
        # name of the language model to load - this contains
        # the MITIE feature extractor
        "model": os.path.join("data", "total_word_feature_extractor.dat")
    }

    def __init__(
        self, component_config: Optional[Dict[Text, Any]] = None, extractor=None
    ) -> None:
        """Construct a new language model from the MITIE framework."""

        super().__init__(component_config)

        self.extractor = extractor

    @classmethod
    def req_packages(cls) -> List[Text]:
        return ["mitie"]

    @classmethod
    def generate(
        cls, component_configuration: Dict[Text, Any], config: ConvoNLUModelConfiguration
    ) -> "NLP_Mitie":
        import mitie

        component_configuration = overriding_dfault_values(cls.defaults, component_configuration)

        model_data_filename = component_configuration.get("model")
        if not model_data_filename:
            raise Exception(
                "The MITIE component 'NLP_Mitie' needs "
                "the configuration value for 'model'."
                "Please take a look at the "
                "documentation in the pipeline section "
                "to get more info about this "
                "parameter."
            )
        extract = mitie.total_word_feature_extractor(model_data_filename)
        cls.ensure_proper_lang_model(extract)

        return cls(component_configuration, extract)

    @classmethod
    def cache_key(
        cls, component_meta: Dict[Text, Any], model_metadata: "Metadataset"
    ) -> Optional[Text]:

        file_mitie = component_meta.get("model", None)
        if file_mitie is not None:
            return cls.name + "-" + str(os.path.abspath(file_mitie))
        else:
            return None

    def context_provide(self) -> Dict[Text, Any]:

        return {
            "mitie_feature_extractor": self.extractor,
            "mitie_file": self.component_config.get("model"),
        }

    @staticmethod
    def ensure_proper_lang_model(
        extractor: Optional["mitie.total_word_feature_extractor"],
    ) -> None:

        if extractor is None:
            raise Exception(
                "Failed to load MITIE feature extractor. "
                "Loading the model returned 'None'."
            )

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional[Metadataset] = None,
        cached_component: Optional["NLP_Mitie"] = None,
        **kwargs: Any,
    ) -> "NLP_Mitie":
        import mitie

        if cached_component:
            return cached_component

        file_mitie = meta.get("model")
        return cls(meta, mitie.total_word_feature_extractor(file_mitie))

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:

        return {
            "mitie_feature_extractor_fingerprint": self.extractor.fingerprint,
            "model": self.component_config.get("model"),
        }
