# -*- coding: utf-8 -*-

import json

from flask import Flask, request
from jinja2 import Environment


JOHN = "contact_john"
LISA = "contact_lisa"
MARY = "contact_mary"
ANDY = "contact_andy"

PHONE_NUMBERS = {
    JOHN: "0701234567",
    LISA: "0709876543",
    MARY: "0706574839",
    ANDY: None
}

CONTACTS = {
    "46070202122": {
        "John": JOHN,
        "Lisa": LISA,
    },
    "46070404142": {
        "Mary": MARY,
        "Andy": ANDY
    }
}


app = Flask(__name__)
environment = Environment()


def jsonfilter(value):
    return json.dumps(value)


environment.filters["json"] = jsonfilter


def error_response(message):
    response_template = environment.from_string(
        """
    {
      "status": "error",
      "message": {{message|json}},
      "data": {
        "version": "1.0"
      }
    }
    """
    )
    payload = response_template.render(message=message)
    response = app.response_class(response=payload, status=200, mimetype='application/json')
    return response


def query_response(value, grammar_entry):
    response_template = environment.from_string("""
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
          {
            "value": {{value|json}},
            "confidence": 1.0,
            "grammar_entry": {{grammar_entry|json}}
          }
        ]
      }
    }
    """)
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    response = app.response_class(
        response=payload,
        status=200,
        mimetype='application/json'
    )
    return response


@app.route("/successful_action_response", methods=['POST'])
def successful_action_response():
    response_template = environment.from_string(
        """
    {
      "status": "success",
      "data": {
        "version": "1.0"
      }
    }
    """
    )
    payload = response_template.render()
    response = app.response_class(response=payload, status=200, mimetype='application/json')
    return response


@app.route("/failed_action_response", methods=['POST'])
def failed_action_response(reason):
    response_template = environment.from_string(
        """
    {
      "status": "fail",
      "data": {
        "version": "1.0",
        "reason": {{reason|json}}
      }
    }
    """
    )
    payload = response_template.render(reason=reason)
    response = app.response_class(response=payload, status=200, mimetype='application/json')
    return response


@app.route("/start_session_mock_data", methods=['POST'])
def start_session_mock_data():
    try:
        payload = request.get_json()
        session = payload.get("session", {})
        session_data = "There is no session data"
        if "key" in session:
            session_data = session["key"]
        return query_response(value=session_data, grammar_entry=None)
    except BaseException as exception:
        return error_response(message=str(exception))


@app.route("/caller_phone_number", methods=['POST'])
def caller_phone_number():
    try:
        payload = request.get_json()
        session = payload.get("session", {})
        answer = "46079808182"
        if "mock_caller" in session:
            answer = session["mock_caller"]
        return query_response(value=answer, grammar_entry=None)
    except BaseException as exception:
        return error_response(message=str(exception))


@app.route("/mock_perform", methods=['POST'])
def mock_perform():
    try:
        payload = request.get_json()
        session = payload.get("session", {})
        if "key" in session:
            return successful_action_response()
        return failed_action_response(reason="no_mock_data")
    except BaseException as exception:
        return error_response(message=str(exception))


@app.route("/contact_recognizer", methods=['POST'])
def contact_recognizer():
    try:
        payload = request.get_json()
        session = payload.get("session", {})
        called_number = "46070404142"
        if "mock_called" in session:
            called_number = payload["session"]["mock_called"]
        utterance = payload["request"]["utterance"]
        words = utterance.lower().split()
        results = []
        for contact_name, identifier in CONTACTS[called_number].items():
            if contact_name.lower() in words:
                results.append({"value": identifier, "sort": "contact", "grammar_entry": contact_name})
        return contact_recognizer_response(results)
    except BaseException as exception:
        return error_response(message=str(exception))


def contact_recognizer_response(entities):
    response_template = environment.from_string(
        """
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "result": [
        {% for entity in entities %}
          {
            "sort": {{entity.sort|json}},
            "value": {{entity.value|json}},
            "grammar_entry": {{entity.grammar_entry|json}}
          }{{"," if not loop.last}}
        {% endfor %}
        ]
      }
    }
     """
    )
    payload = response_template.render(entities=entities)
    response = app.response_class(response=payload, status=200, mimetype='application/json')
    return response


@app.route("/frontend_session_data_validator", methods=['POST'])
def frontend_session_data_validator():
    try:
        payload = request.get_json()
        session = payload.get("session", {})
        if "mock_called" in session:
            called_number = payload["session"]["mock_called"]
            is_valid = called_number is not None
            return contact_validator_response(is_valid)
        return contact_validator_response(is_valid=False)
    except BaseException as exception:
        return error_response(message=exception)


def contact_validator_response(is_valid):
    response_template = environment.from_string(
        """
    {
      "status": "success",
      "data": {
        "version": "1.0",
        "is_valid": {{is_valid|json}}
      }
    }
    """
    )
    payload = response_template.render(is_valid=is_valid)
    response = app.response_class(response=payload, status=200, mimetype='application/json')
    return response


@app.route("/phone_number_of_contact", methods=['POST'])
def phone_number_of_contact():
    try:
        payload = request.get_json()
        selected_contact = payload["request"]["parameters"]["selected_contact"]["value"]
        number = PHONE_NUMBERS.get(selected_contact)
        return query_response(value=number, grammar_entry=None)
    except BaseException as exception:
        return error_response(message=str(exception))
