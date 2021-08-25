# -*- coding: utf-8 -*-

import json

from flask import Flask, request
from jinja2 import Environment


SUPPORTED_PERSON_NAME = u"Amélie Bisset"

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


@app.route("/name_of_person_to_invite", methods=['POST'])
def name_of_person_to_invite():
    try:
        return person_name_response(value=SUPPORTED_PERSON_NAME, grammar_entry=None)
    except BaseException as exception:
        return error_response(message=str(exception))


def person_name_response(value, grammar_entry):
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


@app.route("/send_invitation", methods=['POST'])
def send_invitation():
    try:
        payload = request.get_json()
        name_of_person_to_invite = payload["request"]["parameters"]["name_of_person_to_invite"]["value"]
        if name_of_person_to_invite == SUPPORTED_PERSON_NAME:
            return successful_action_response()
        else:
            return error_response(message="Expected the person name '{}' but got '{}'".format(
                SUPPORTED_PERSON_NAME, name_of_person_to_invite))
    except BaseException as exception:
        return error_response(message=str(exception))


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
