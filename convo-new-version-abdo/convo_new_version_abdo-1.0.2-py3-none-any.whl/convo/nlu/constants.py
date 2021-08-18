import convo.shared.nlu.constants


ENTITIES_BILOU = "bilou_entities"
ENTITIES_ROLE_BILOU = "bilou_entities_role"
ENTITIES_GROUP_BILOU = "bilou_entities_group"

ENTITY_ATTR_TXT_STR = "text"
ENTITY_ATTR_CONFIDENCE_VAL = "confidence"
ENTITY_ATTR_CONFIDENCE_TYPE_VAL = (
    f"{ENTITY_ATTR_CONFIDENCE_VAL}_{convo.shared.nlu.constants.ATTRIBUTE_TYPE_ENTITY}"
)
ENTITY_ATTR_CONFIDENCE_GRP = (
    f"{ENTITY_ATTR_CONFIDENCE_VAL}_{convo.shared.nlu.constants.ATTRIBUTE_GROUP_ENTITY}"
)
ENTITY_ATTR_CONFIDENCE_ROLE = (
    f"{ENTITY_ATTR_CONFIDENCE_VAL}_{convo.shared.nlu.constants.ATTRIBUTE_ROLE_ENTITY}"
)

EXTRACTOR = "extractor"

PRE_TRAINED_EXTRACTORS = {
    "DucklingEntityExtractor",
    "DucklingHTTPExtractor",  # for backwards compatibility when dumping Markdown
    "SpacyEntityExtractor",
}
EXTRACTORS_TRAINABLE = {"MitieEntityExtractor", "CRFEntityExtractor", "DIETClassifier"}

SUB_TOKENS_NUM = "number_of_sub_tokens"

MSG_ATTRS = [
    convo.shared.nlu.constants.TXT,
    convo.shared.nlu.constants.INTENTION,
    convo.shared.nlu.constants.RETURN_RESPONSE,
    convo.shared.nlu.constants.ACT_NAME,
    convo.shared.nlu.constants.ACT_TEXT,
    convo.shared.nlu.constants.KEY_INTENT_RESPONSE,
]
# the dense featurizable attributes are essentially text attributes
DENSE_FEATURE_ATTRS = [
    convo.shared.nlu.constants.TXT,
    convo.shared.nlu.constants.RETURN_RESPONSE,
    convo.shared.nlu.constants.ACT_TEXT,
]

LANG_MODEL_DOCUMENTS = {
    convo.shared.nlu.constants.TXT: "text_language_model_doc",
    convo.shared.nlu.constants.RETURN_RESPONSE: "response_language_model_doc",
    convo.shared.nlu.constants.ACT_TEXT: "action_text_model_doc",
}
SPACY_DOCUMENTS = {
    convo.shared.nlu.constants.TXT: "text_spacy_doc",
    convo.shared.nlu.constants.RETURN_RESPONSE: "response_spacy_doc",
    convo.shared.nlu.constants.ACT_TEXT: "action_text_spacy_doc",
}

NAMES_OF_TOKENS = {
    convo.shared.nlu.constants.TXT: "text_tokens",
    convo.shared.nlu.constants.INTENTION: "intent_tokens",
    convo.shared.nlu.constants.RETURN_RESPONSE: "response_tokens",
    convo.shared.nlu.constants.ACT_NAME: "action_name_tokens",
    convo.shared.nlu.constants.ACT_TEXT: "action_text_tokens",
    convo.shared.nlu.constants.KEY_INTENT_RESPONSE: "intent_response_key_tokens",
}

TKNS = "tokens"
TKN_IDS = "token_ids"

SEQUENTIAL_FEATURES = "sequence_features"
SENTENCE_FTRS = "sentence_features"

PROP_NAME_RESPONSE_PICKER = "response_selector"
RETRIEVE_INTENTS_RESPONSE_PICKER = "all_convo_intents_retrieval"
DFAULT_INTENT_RESPONSE_PICKER = "default"
PREDICTION_KEY_RESPONSE_PICKER = "response"
RANK_KEY_RESPONSE_PICKER = "ranking"
RESP_KEY_RESPONSE_PICKER = "response_templates"
TEMPLATE_NAME_KEY_RESPONSE_PICKER = "template_name"
RESP_IDENTIFIER_DELIMITER = "/"

FEATURE_CLASS_AS = "alias"

NO_LEN_RESTRICT = -1
