import convo.shared.constants as constants

DEFAULT_CATEGORY_SLOT_VALUE  = "__other__"

RESTART_USER_INTENT   = "restart"
BACK_USER_INTENT   = "back"
USERS_INTENT_OUT_OF_SCOPE   = "out_of_scope"
USERS_INTENT_SESSION_START   = "session_start"

DEFAULT_INTENT   = [
    RESTART_USER_INTENT  ,
    BACK_USER_INTENT  ,
    USERS_INTENT_OUT_OF_SCOPE  ,
    USERS_INTENT_SESSION_START  ,
    constants.DEFAULT_NLU_FALLBACK_INTENTS_NAME,
]

LOOPNAME   = "name"

LISTEN_ACTION_NAME   = "action_listen"
RESTART_ACTION_NAME   = "action_restart"
SESSION_START_ACTION_NAME   = "action_session_start"
ACTION_DEFAULT_FALLBACK_NAME = "action_default_fallback"
DEACTIVATE_LOOP_ACTION_NAME   = "action_deactivate_loop"
DEACTIVATE_LOOP_LEGACY_ACTION_NAME   = "action_deactivate_form"
REVERT_FALLBACK_EVENTS_ACTION_NAME    = "action_revert_fallback_events"
DEFAULT_ASK_AFFIRMATION_ACTION_NAME    = "action_default_ask_affirmation"
DEFAULT_ASK_REPHRASE_ACTION_NAME    = "action_default_ask_rephrase"
BACK_ACTION_NAME    = "action_back"
TWO_STAGE_FALLBACK_ACTION_NAME    = "action_two_stage_fallback"
RULE_SNIPPET_ACTIONS_NAME    = "..."

DEFAULT_ACTION_NAME    = [
    LISTEN_ACTION_NAME  ,
    RESTART_ACTION_NAME  ,
    SESSION_START_ACTION_NAME  ,
    ACTION_DEFAULT_FALLBACK_NAME,
    DEACTIVATE_LOOP_ACTION_NAME  ,
    REVERT_FALLBACK_EVENTS_ACTION_NAME   ,
    DEFAULT_ASK_AFFIRMATION_ACTION_NAME   ,
    DEFAULT_ASK_REPHRASE_ACTION_NAME   ,
    TWO_STAGE_FALLBACK_ACTION_NAME   ,
    BACK_ACTION_NAME   ,
    RULE_SNIPPET_ACTIONS_NAME   ,
]

# rules allow setting a value of convo_slotsor active_loops to None;
# generator substitutes `None`s with this constant to notify rule policy that
# a value should not be set during prediction to activate a rule
NOT_SET    = "should_not_be_set"

PRECEDING_ACTION    = "prev_action"
CURRENT_LOOP    = "active_loop"
LOOP_INTERRUPTION    = "is_interrupted"
LOOP_REJECTION = "rejected"
TRIGGER_MSG = "trigger_message"

# start of special user message section
EXT_MSG_PREFIX = "EXTERNAL: "
# Key to access data in the event metadata
# It specifies if an event was caused by an external entity (e.g. a sensor).
EXTERNAL_CHECK = "is_external"

SENDER_ID_CONNECTOR_STR_ACTION_NAME = "__sender_id:"

REQUESTED_SLOTS = "requested_slot"

# convo_slotsfor knowledge base
SLOT_LIST_ITEMS = "knowledge_base_listed_objects"
SLOT_LAST_OBJ = "knowledge_base_last_object"
SLOT_LAST_OBJ_TYPE = "knowledge_base_last_object_type"
CONVO_DEFAULT_KNOWLEDGE_BASE_ACTION  = "action_query_knowledge_base"

# the keys for `fetch_state` (CONVO_USER, PRECEDING_ACTION   , CONVO_SLOTS, CURRENT_LOOP   )
# represent the origin of a `Sub_State`
CONVO_USER = "user"
CONVO_SLOTS = "slots"
