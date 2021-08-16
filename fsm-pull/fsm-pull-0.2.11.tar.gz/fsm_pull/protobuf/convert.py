import json
from fsm_pull.protobuf.records_pb2 import (
    Call,
    CallDataFrame,
    Turn,
    Utterance,
    Prediction,
    Intent,
)

turn_type_map = {"UNKNOWN": 0, "ACTION": 1, "INPUT": 2, "RESPONSE": 3, "VALIDATION": 4}


def call_dict2proto(call_dict):
    turns = call_dict.get("turns", {})
    conversations = turns.get("conversations", [])
    turns = [turn_dict2proto({**turns, **turn}) for turn in conversations]
    return Call(
        id=call_dict.get("uuid"),
        created_at=call_dict.get("created_at"),
        virtual_number=call_dict.get("virtual_number"),
        audio_url=call_dict.get("audio_url"),
        duration=call_dict.get("duration"),
        turns=turns,
    )


def turn_dict2proto(conversation_dict):
    utterances = utterance_dict2proto(
        conversation_dict.get("debug_metadata", {})
        .get("plute_request", {})
        .get("alternatives")
    )
    prediction = conversation_dict.get("prediction")
    if prediction:
        prediction = json.loads(prediction)
    prediction = prediction_dict2proto(prediction)
    return Turn(
        id=conversation_dict["uuid"],
        created_at=conversation_dict["created_at"],
        type=turn_type_map.get(conversation_dict.get("type"), 0),
        sub_type=conversation_dict.get("sub_type"),
        text=conversation_dict.get("text"),
        utterances=utterances,
        audio_url=conversation_dict.get("audio_url"),
        state=conversation_dict.get("state"),
        asr_context=conversation_dict.get("asr_context"),
        asr_provider=conversation_dict.get("asr_provider"),
        language=conversation_dict.get("language"),
        prediction=prediction,
    )


def utterance_dict2proto(utterances_dict):
    if not isinstance(utterances_dict, list):
        return None
    elif not utterances_dict:
        return None
    elif isinstance(utterances_dict, list) and isinstance(utterances_dict[0], dict):
        utterances_dict = [utterances_dict]
    elif isinstance(utterances_dict, list) and not isinstance(utterances_dict[0], list):
        raise TypeError(
            f"Expected {utterances_dict=} to be List[List[Dict[str, Any]]]."
        )

    utterances = []
    for utterance in utterances_dict:
        alternatives = []
        for alternative in utterance:
            _alternative = Utterance.Alternative(transcript=alternative["transcript"])
            if "confidence" in alternative:
                _alternative.confidence = alternative["confidence"]
            elif "am_score" in alternative and "lm_score" in alternative:
                _alternative.am_score = alternative["am_score"]
                _alternative.lm_score = alternative["lm_score"]
            alternatives.append(_alternative)
        utterances.append(Utterance(alternatives=alternatives))
    return utterances


def prediction_dict2proto(prediction_dict):
    if not prediction_dict:
        return Prediction()
    # handle plute style predictions
    if "graph" in prediction_dict:
        intents = prediction_dict["graph"]["output"][0]
    # or dialogy style predictions
    else:
        intents = prediction_dict["intents"]
    intents_ = []
    for intent in intents:
        slots = []
        for slot in intent["slots"]:
            if isinstance(slot["type"], str):
                slot_types = [slot["type"]]
            elif isinstance(slot["type"], list):
                slot_types = slot["type"]
            else:
                slot_types = None
            slots.append(
                Intent.Slot(name=slot["name"], type=slot_types, values=slot["values"])
            )
        intents_.append(Intent(name=intent["name"], score=intent["score"], slots=slots))
    return Prediction(intents=intents_)


def build_records_dataframe(calls_dict):
    """
    Builds a dataframe from a list of Call objects.
    """
    calls = []
    for call_dict in calls_dict:
        call_ = call_dict2proto(call_dict)
        if call_:
            calls.append(call_)
    return CallDataFrame(calls=calls)
