import os, json

def open_json(json_file):
    with open(json_file) as data:
        return json.load(data)