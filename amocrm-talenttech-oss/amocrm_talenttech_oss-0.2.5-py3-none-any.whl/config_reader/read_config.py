"""class to read config from the file"""
import json
from operator import itemgetter

"""
 "projects": [
    {
      "config_name": "net",
      "entities": {
            "leads": {
                "extract": {
                    "amocrm_api_url": "https://netologyoutgoing.amocrm.ru/api/v4/leads?page={page}&limit={limit}",
                    "if_modified_since": "0",
                    "with_offset": "0"
                },
                "load": {
                    "vertiaca": {
                        "table_name": "amocrm_leads_v4"
                    },
                    "ch": {
                        "table_name": "amocrm_leads_v4",
                        "parser": [
                            {
                              "from_table": "amocrm_leads_v4",
                              "insert_table": "amocrm_leads_v4_custom_fields_values",
                              "script": ""
                            }
                          ]
                    }
                }
            }
      }      
"""


def get_config_list(config_dir):
    """
    Decompose config json to list of tuple (extract_params, [db_param1, db_param2])
    :param config_dir: path to config file
    :return: list of configs
    """
    result_list = []
    with open(config_dir) as file:
        config = json.load(file)
    projects = sorted(config["projects"], key=itemgetter("config_name"))
    for project in projects:
        entities = project["entities"]
        config_name = project["config_name"]

        for entity in entities:
            api_params = entities[entity]["extract"]
            api_params['config_name'] = config_name
            api_params['entity'] = entity
            api_params["action"] = "extract"
            db_type_params_list = []
            for db_type in entities[entity]["load"]:
                db_type_params = entities[entity]["load"][db_type]
                db_type_params['config_name'] = config_name
                db_type_params['entity'] = entity
                if 'parser' in db_type_params:
                    db_type_params['parser'] = json.dumps(db_type_params['parser'])
                db_type_params["action"] = "load"
                db_type_params["db"] = db_type
                db_type_params["if_modified_since"] = api_params["if_modified_since"]
                db_type_params_list.append(db_type_params)

            result_list.append((api_params, db_type_params_list))
    return result_list
