import json
from argparse import Namespace
from copy import deepcopy


RULE_TEMPLATE = {
  "__MAIN__": {
    "type": "scraping/custom_scraper",
    "params": {
      "script": "$script",
      "script_params": {},
    }
  }
}


def generate_rule(namespace: Namespace):
    rule = deepcopy(RULE_TEMPLATE)
    rule['__MAIN__']['params']['script'] = namespace.input.read()
    for item in namespace.params:
        rule['__MAIN__']['params']['script_params'].update(item)
    json.dump(rule, namespace.output, indent=2)
