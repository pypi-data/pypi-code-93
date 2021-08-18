"""This is a somewhat delicate package. It contains all registered components
and preconfigured templates.

Hence, it imports all of the components. To avoid cycles, no component should
import this in module scope."""

import logging
import traceback
import typing
from typing import Any, Dict, Optional, Text, Type

from convo.nlu.classifiers.diet_classifier import DIETClassifier
from convo.nlu.classifiers.fallback_classifier import FallbackClassifier
from convo.nlu.classifiers.keyword_intent_classifier import KeywordIntentClassifier
from convo.nlu.classifiers.mitie_intent_classifier import MitieIntentClassifier
from convo.nlu.classifiers.sklearn_intent_classifier import SklearnIntentClassifier
from convo.nlu.extractors.crf_entity_extractor import CRFEntityExtractor
from convo.nlu.extractors.duckling_entity_extractor import DucklingEntityExtractor
from convo.nlu.extractors.entity_synonyms import EntitySynonymMapper
from convo.nlu.extractors.mitie_entity_extractor import MitieEntityExtractor
from convo.nlu.extractors.spacy_entity_extractor import SpacyEntityExtractor
from convo.nlu.extractors.regex_entity_extractor import ExtractRegexEntity
from convo.nlu.featurizers.sparse_featurizer.lexical_syntactic_featurizer import (
    LexicalSyntacticFeaturizer,
)
from convo.nlu.featurizers.dense_featurizer.convert_featurizer import ConveRTFeaturizer
from convo.nlu.featurizers.dense_featurizer.mitie_featurizer import MitieFeaturizer
from convo.nlu.featurizers.dense_featurizer.spacy_featurizer import SpacyFeaturizer
from convo.nlu.featurizers.sparse_featurizer.count_vectors_featurizer import (
    CountVectorsFeaturizer,
)
from convo.nlu.featurizers.dense_featurizer.lm_featurizer import LangModelFeaturizer
from convo.nlu.featurizers.sparse_featurizer.regex_featurizer import RegexFeaturizer
from convo.nlu.model import Metadataset
from convo.nlu.selectors.response_selector import ResponseSelector
from convo.nlu.tokenizers.convert_tokenizer import ConveRTTokenizer
from convo.nlu.tokenizers.jieba_tokenizer import Jieba_Tokenize
from convo.nlu.tokenizers.mitie_tokenizer import Mitie_Tokenized
from convo.nlu.tokenizers.spacy_tokenizer import SpacyTokenizer
from convo.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from convo.nlu.tokenizers.lm_tokenizer import Lang_Model_Tokenizer
from convo.nlu.utils.mitie_utils import NLP_Mitie
from convo.nlu.utils.spacy_utils import SpacyNLP
from convo.nlu.utils.hugging_face.hf_transformers import HF_Transformers_NLP
from convo.shared.exceptions import ConvoExceptions 
import convo.shared.utils.common
import convo.shared.utils.io
import convo.utils.io
from convo.shared.constants import COMPONENTS_DOCUMENTS_URL

if typing.TYPE_CHECKING:
    from convo.nlu.components import Element
    from convo.nlu.config import ConvoNLUModelConfiguration

log = logging.getLogger(__name__)


# Classes of all known components. If a new component should be added,
# its class name should be listed here.
comp_classes = [
    # utils
    SpacyNLP,
    NLP_Mitie,
    HF_Transformers_NLP,
    # tokenizers
    Mitie_Tokenized,
    SpacyTokenizer,
    WhitespaceTokenizer,
    ConveRTTokenizer,
    Jieba_Tokenize,
    Lang_Model_Tokenizer,
    # extractors
    SpacyEntityExtractor,
    MitieEntityExtractor,
    CRFEntityExtractor,
    DucklingEntityExtractor,
    EntitySynonymMapper,
    ExtractRegexEntity,
    # featurizers
    SpacyFeaturizer,
    MitieFeaturizer,
    RegexFeaturizer,
    LexicalSyntacticFeaturizer,
    CountVectorsFeaturizer,
    ConveRTFeaturizer,
    LangModelFeaturizer,
    # classifiers
    SklearnIntentClassifier,
    MitieIntentClassifier,
    KeywordIntentClassifier,
    DIETClassifier,
    FallbackClassifier,
    # selectors
    ResponseSelector,
]

# Mapping from a components name to its class to allow name based lookup.
reg_comps = {c.name: c for c in comp_classes}


class ElementNotFoundException(ModuleNotFoundError, ConvoExceptions ):
    """Raised if a module referenced by name can not be imported."""

    pass


def fetch_comp_class(comp_name: Text) -> Type["Element"]:
    """Resolve component name to a registered components class."""

    if comp_name == "DucklingHTTPExtractor":
        convo.shared.utils.io.rasing_deprecate_warning(
            "The component 'DucklingHTTPExtractor' has been renamed to "
            "'DucklingEntityExtractor'. Update your pipeline to use "
            "'DucklingEntityExtractor'.",
            docs=COMPONENTS_DOCUMENTS_URL,
        )
        comp_name = "DucklingEntityExtractor"

    if comp_name not in reg_comps:
        try:
            return convo.shared.utils.common.class_name_from_module_path(comp_name)

        except (ImportError, AttributeError) as e:
            # when component_name is a path to a class but that path is invalid or
            # when component_name is a class name and not part of old_style_names

            path_check = "." in comp_name

            if path_check:
                mod_name, _, fetch_class_name = comp_name.rpartition(".")
                if isinstance(e, ImportError):
                    exception_msg = f"Failed to find module '{mod_name}'."
                else:
                    # when component_name is a path to a class but the path does
                    # not contain that class
                    exception_msg = (
                        f"The class '{fetch_class_name}' could not be "
                        f"found in module '{mod_name}'."
                    )
            else:
                exception_msg = (
                    f"Cannot find class '{comp_name}' in global namespace. "
                    f"Please check that there is no typo in the class "
                    f"name and that you have imported the class into the global "
                    f"namespace."
                )

            raise ElementNotFoundException(
                f"Failed to load the component "
                f"'{comp_name}'. "
                f"{exception_msg} Either your "
                f"pipeline configuration contains an error "
                f"or the module you are trying to import "
                f"is broken (e.g. the module is trying "
                f"to import a package that is not "
                f"installed). {traceback.format_exc()}"
            )

    return reg_comps[comp_name]


def load_comp_by_meta(
    component_meta: Dict[Text, Any],
    model_dir: Text,
    metadata: Metadataset,
    cached_component: Optional["Element"],
    **kwargs: Any,
) -> Optional["Element"]:
    """Resolves a component and calls its load method.

    Inits it based on a previously persisted model.
    """

    # try to get class name first, else create by name
    comp_name = component_meta.get("class", component_meta["name"])
    comp_class = fetch_comp_class(comp_name)
    return comp_class.load(
        component_meta, model_dir, metadata, cached_component, **kwargs
    )


def create_comp_by_configuration(
    component_config: Dict[Text, Any], config: "ConvoNLUModelConfiguration"
) -> Optional["Element"]:
    """Resolves a component and calls it's create method.

    Inits it based on a previously persisted model.
    """

    # try to get class name first, else create by name
    component_name = component_config.get("class", component_config["name"])
    component_class = fetch_comp_class(component_name)
    return component_class.create(component_config, config)
