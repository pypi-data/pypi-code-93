from pydicom.dataelem import BINARY_VR_VALUES, BaseTag, UID
from pydicom.sequence import Sequence
from pydicom.valuerep import PersonName


def uid_to_string(uid):
    """ Convert PyDicom uid to a string """
    return repr(uid).strip("'")


def dataset_to_dict(dicom_dataset):
    """ Convert the supplied PyDicom object into a
        json-serializable dict
    """
    dicom_dataset.decode()
    metadata_dict = dict(
        (dicom_dataset[key].keyword, __jsonify(dicom_dataset[key], [], []))
        for key in dicom_dataset.keys())

    return metadata_dict


def __jsonify(element, binary_elements, tagstack):
    """ Convert key, value to json-serializable types
    Recursive, so if value is key/value pairs then
    all children will get converted
    """
    value = element.value
    if element.VR in BINARY_VR_VALUES:
        binary_elements.append((tagstack[:], element))
        return ''
    elif type(value) == list:
        new_list = [__typemap(listvalue) for listvalue in value]
        return new_list
    elif type(value) == Sequence:
        tagstack.append(element.tag)
        nested_data = []
        for i in range(0, len(value)):
            tagstack.append(i)
            nested_data.append(
                dict((value[i][subkey].keyword, __jsonify(value[i][subkey],
                                                          binary_elements,
                                                          tagstack))
                     for subkey in value[i].keys()))
            tagstack.pop()
        tagstack.pop()
        return nested_data
    else:
        return __typemap(value)


def __typemap(value):
    """ Map PyDicom types that won't serialize
        to JSON types """
    if type(value) == UID:
        return uid_to_string(value)
    elif isinstance(value, BaseTag):
        return int(value)
    elif isinstance(value, PersonName):
        return value.original_string
    else:
        return value
