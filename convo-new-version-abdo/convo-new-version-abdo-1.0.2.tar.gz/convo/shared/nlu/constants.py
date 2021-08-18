TXT = "text"
INTENTION = "intent"
RETURN_RESPONSE = "response"
KEY_INTENT_RESPONSE = "intent_response_key"
ACT_TEXT = "action_text"
ACT_NAME = "action_name"
KEY_INTENT_NAME = "name"
META_DATA = "metadata"
META_DATA_INTENT = "intent"
META_DATA_EXAMPLE = "example"
KEY_INTENT_RANKING = "intent_ranking"
KEY_PREDICTED_CONFIDENCE = "confidence"

RESP_IDENTIFIER_DELIMITER = "/"

FEATURED_TYPE_SENTENCE = "sentence"
FEATURED_TYPE_SEQUENCE = "sequence"
VALIDATED_FEATURE_TYPES = [FEATURED_TYPE_SEQUENCE, FEATURED_TYPE_SENTENCE]

EXTRACTOR = "extractor"
PRE_TRAINED_EXTRACTORS = {
    "DucklingEntityExtractor",
    "SpacyEntityExtractor",
    "DucklingHTTPExtractor",  # for backwards compatibility when dumping Markdown
}
EXTRACTORS_TRAINABLE = {"MitieEntityExtractor", "CRFEntityExtractor", "DIETClassifier"}

ENTITIES_NAME = "entities"
ATTRIBUTE_TYPE_ENTITY = "entity"
ATTRIBUTE_GROUP_ENTITY = "group"
ATTRIBUTE_ROLE_ENTITY = "role"
ATTRIBUTE_VALUE_ENTITY = "value"
ATTRIBUTE_START_ENTITY = "start"
ATTRIBUTE_END_ENTITY = "end"
ENTITY_TAG_ABSENT = "O"
