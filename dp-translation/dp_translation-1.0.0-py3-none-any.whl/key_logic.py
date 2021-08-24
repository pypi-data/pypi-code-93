import re
from sqlalchemy.orm import Session
from typing import List

TranslationKey_SEPERATOR =  "_%_"

class TranslationKeyBuilder:
    NULL_VALUE = "null"
    SEPERATOR = "_%_"
    REGEX = re.compile(f"^\\w+({TranslationKey_SEPERATOR}\\w+){{3}}$")
    KW_NAMES = ["context", "concept", "instance_id", "attr"]
    

    @classmethod
    def construct_translation_key(cls,
        context: str=None,
        concept: str=None,
        instance_id: str=None,
        attr: str=None
        ):
        """Construct a translation key

        Args:
            context (str): The context in which the translation is required, e.g. a specific database
            concept (str): The concept for which the translation is required, e.g. a specific table
            instance_id (str): A key that uniquely identifies an instance of the specific concept
            attr (str): The name of the attribute that should be translated for the specific instance

        Returns:
            [str]: A translation_key that is unique within the whole translation database and can be used to find
                   translations for several target_languages
        """
        return cls.SEPERATOR.join([context, concept, instance_id, attr])
    
    @classmethod
    def destruct_translation_key(cls, tranlsation_key: str):
        match_result_str = cls.REGEX.match(tranlsation_key).group(0)
        assert  match_result_str == tranlsation_key
        return dict(zip(cls.KW_NAMES, match_result_str.split(cls.SEPERATOR)))


class TranslationKeyRetriever:

    @classmethod
    def get_all_translation_keys_of_translateable_model(cls, session: Session, model: type) -> List[str]:
        translation_keys = []
        translation_keys.append(model.get_logical_key_for_concept())

        for attr in model.get_translateable_attrs():
            translation_keys.append(model.get_logical_key_for_attr(attr))

        for instance in session.query(model).all():
            for attr in model.get_translateable_attrs():
                translation_keys.append(instance.get_logical_key_for_attr_value(attr))
        return translation_keys