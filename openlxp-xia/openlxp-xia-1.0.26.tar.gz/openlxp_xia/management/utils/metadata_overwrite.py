import logging

logger = logging.getLogger('dict_config_logger')


def get_metadata_fields_to_fill(mapping, target):
    required_target_list = []

    for section in mapping:
        required_target_list.extend([(section + "." + key) for key, val in
                                     target[section].items() if
                                     val == 'Required'])
    required_source_list = []
    for item in required_target_list:
        if item in mapping:
            required_source_list.append(mapping[item])
        else:
            logger.error("Mapping for required value " + item +
                         " not found in schema mapping")
    return required_source_list
