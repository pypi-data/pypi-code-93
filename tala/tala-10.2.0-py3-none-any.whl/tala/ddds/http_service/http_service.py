import json

from flask import Flask, request
from jinja2 import Environment

JOHN = "contact_john"
LISA = "contact_lisa"
MARY = "contact_mary"
ANDY = "contact_andy"

PHONE_NUMBERS = {JOHN: "0701234567", LISA: "0709876543", MARY: "0706574839", ANDY: None}

CONTACTS = {"John": JOHN, "Lisa": LISA, "Mary": MARY, "Andy": ANDY}

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


@app.route("/phone_number_of_contact", methods=['POST'])
def phone_number_of_contact():
    try:
        payload = request.get_json()
        selected_contact = payload["request"]["parameters"]["selected_contact"]["value"]
        number = PHONE_NUMBERS.get(selected_contact)
        return phone_number_response(value=None, grammar_entry=number)
    except BaseException as exception:
        return error_response(message=str(exception))


def phone_number_response(value, grammar_entry):
    response_template = environment.from_string(
        """
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
    """
    )
    payload = response_template.render(value=value, grammar_entry=grammar_entry)
    response = app.response_class(response=payload, status=200, mimetype='application/json')
    return response


@app.route("/call", methods=['POST'])
def call():
    try:
        payload = request.get_json()
        selected_contact = payload["request"]["parameters"]["selected_contact"]["value"]
        number = PHONE_NUMBERS.get(selected_contact)  # noqa: F841
        return successful_call_response()
    except BaseException as exception:
        return error_response(message=str(exception))


def successful_call_response():
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


@app.route("/contact_recognizer", methods=['POST'])
def contact_recognizer():
    try:
        payload = request.get_json()
        utterance = payload["request"]["utterance"]
        words = utterance.lower().split()
        results = []
        for contact_name, identifier in list(CONTACTS.items()):
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


@app.route("/validate", methods=['POST'])
def contact_validator():
    try:
        payload = request.get_json()
        selected_contact = payload["request"]["parameters"]["selected_contact"]["value"]
        number = PHONE_NUMBERS.get(selected_contact)
        is_valid = number is not None
        return contact_validator_response(is_valid)
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
