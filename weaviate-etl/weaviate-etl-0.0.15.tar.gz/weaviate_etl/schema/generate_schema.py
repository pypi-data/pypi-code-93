""" This module creates a Weaviate schema from a data configuration file """

from weaviate_etl.utilities import get_reference_property_name_from_field
from weaviate_etl.utilities import get_reference_class_name_from_field
from weaviate_etl.utilities import get_field_name_from_reference_property
from weaviate_etl.utilities import DEFAULT_MODULE
from weaviate_etl.exceptions import DuplicateClassInSchema
from weaviate_etl.exceptions import UnsupportedModelType
from weaviate_etl.exceptions import UnknownModelType


###################################################################################################
## These functions are used for generating a schema from excel
###################################################################################################


def _create_prop(name: str, datatype: str, description: str, modulename: str, index: bool=True) -> dict:
    """
    Create the default property basedon the arguments

    Parameters
    ----------
    name: str
        A string that indicates the name of the prop
    datatype: str
        A string that indicates the datatype
    description: str
        A string that indicates the description
    modulename: str
        A string that specifies the modulename

    Returns
    ------
    dict
        The dict describing the property
    """

    prop = {}
    prop['name'] = name
    prop['dataType'] = [datatype]
    prop['description'] = description
    prop['indexInverted'] = index
    prop['moduleConfig'] = {}
    prop['moduleConfig'][modulename] = {}
    prop['moduleConfig'][modulename]['skip'] = not index
    prop['moduleConfig'][modulename]['vectorizePropertyName'] = False
    return prop


def _create_property_from_column(col: dict, modulename: str) -> dict:
    """
    Create a property from a column in the module excel file

    Parameters
    ----------
    col: dict
        A dict that contains the property
    modulename: str
        A string that specifies the modulename

    Returns
    ------
    dict
        The dict describing the class
    """

    prop = None

    if col is not None:
        prop = {}
        prop['name'] = col['name']
        prop['dataType'] = [col['type']]
        prop['description'] = col['name']
        prop['indexInverted'] = col['indexInverted']
        prop['moduleConfig'] = {}
        prop['moduleConfig'][modulename] = {}
        prop['moduleConfig'][modulename]['skip'] = not prop['indexInverted']
        prop['moduleConfig'][modulename]['vectorizePropertyName'] = False

    return prop


def _create_reference_property_from_column(col: dict, modulename: str) -> dict:
    """
    Create a reference property from a column in the module excel file

    Parameters
    ----------
    col: dict
        A dict that contains the property
    modulename: str
        A string that specifies the modulename

    Returns
    ------
    dict
        The dict describing the class
    """
    prop = None

    if col is not None:
        name = get_reference_property_name_from_field(col['name'])
        datatype = get_reference_class_name_from_field(col['name'])
        prop = _create_prop(name, datatype, datatype, modulename)

    return prop


def _create_class_from_column(col: dict, modulename: str) -> dict:
    """
    Create a class from a column in the module excel file

    Parameters
    ----------
    col: dict
        A dict that contains the class
    modulename: str
        A string that specifies the modulename

    Returns
    ------
    dict
        The dict describing the class
    """

    newclass = None

    if col is not None:
        newclass = {}
        newclass['class'] = get_reference_class_name_from_field(col['name'])
        newclass['description'] = newclass['class']
        newclass['moduleConfig'] = {}
        newclass['moduleConfig'][modulename] = {}
        newclass['moduleConfig'][modulename]['vectorizeClassName'] = True
        newclass['properties'] = []
        prop = _create_prop('name', "string", "name of instance", modulename)
        newclass['properties'].append(prop)

    return newclass


def _create_class(classname: str, modulename: str) -> dict:
    """
    Create a class

    Parameters
    ----------
    model: dict
        A dict that contains the class

    Returns
    ------
    dict
        The dict describing the class
    """

    newclass = {}
    newclass['class'] = classname
    newclass['moduleConfig'] = {}
    newclass['moduleConfig'][modulename] = {}
    newclass['moduleConfig'][modulename]['vectorizeClassName'] = True
    newclass['description'] = "A " + classname + "class in this schema"
    newclass['properties'] = []

    # the row proporty indicates the row number from the excel file that the data point was on
    prop = _create_prop('row', "int", "row number of datapoint", modulename)
    newclass['properties'].append(prop)

    # the batchnumber property is used if the number of items to be classified exceeds the max
    prop = _create_prop('batchNumber', "int", "batch number of datapoint", modulename)
    newclass['properties'].append(prop)

    return newclass


def _create_schema_from_excel(model: dict, modulename:str=None) -> dict:
    """
    Create a schema from the argument model

    Parameters
    ----------
    model: dict
        A dict that contains the data model

    Raises
    ------
    DuplicateClassesInSchema
        If there are duplicate class names in the model

    Returns
    ------
    dict
        The dict describing the Weaviate schema
    """

    # Initialize the return value
    schema = {}
    schema['classes'] = []

    # keep track of which classes for entities have been created
    entities = []

    # determine the module name. Default is 'text2vec-contextionary'
    if modulename is None:
        modulename = DEFAULT_MODULE

    for dataclass in model['classes']:
        # Add the main class to the schema
        if dataclass['classname'] not in entities:
            mainclass = _create_class(dataclass['classname'], modulename)
            schema['classes'].append(mainclass)
            entities.append(dataclass['classname'])
        else:
            raise DuplicateClassInSchema(dataclass['classname'])

        for col in dataclass['columns']:

            # Create the property and add it to the schema
            prop = _create_property_from_column(col, modulename)
            if prop is not None:
                mainclass['properties'].append(prop)

            # If the column represents an entity we need to create a reference property and a new class
            if col['entity']:
                prop = _create_reference_property_from_column(col, modulename)
                if prop is not None:
                    mainclass['properties'].append(prop)

                if col['name'] not in entities:
                    entities.append(col['name'])
                    newclass = _create_class_from_column(col, modulename)
                    if newclass is not None:
                        schema['classes'].append(newclass)
                else:
                    raise DuplicateClassInSchema(col['name'])

    return schema


###################################################################################################
## These functions are used for generating a schema from json
###################################################################################################


def _create_class_from_json_entity(name, entity, modulename):

    # initialize the return value
    newclass = None
    if entity is not None:
        newclass = {}
        newclass['class'] = name
        newclass['description'] = newclass['class']
        newclass['moduleConfig'] = {}
        newclass['moduleConfig'][modulename] = {}
        newclass['moduleConfig'][modulename]['vectorizeClassName'] = True
        newclass['properties'] = []
        for key in entity:
            prop = _create_prop(key, entity[key], prop['dataType'][0], modulename)
            newclass['properties'].append(prop)
    return newclass


def _create_schema_from_json(model: dict, modulename:str=None) -> dict:
    """
    Create a schema from the argument model

    Parameters
    ----------
    model: dict
        A dict that contains the data model

    Raises
    ------
    DuplicateClassesInSchema
        If there are duplicate class names in the model

    Returns
    ------
    dict
        The dict describing the Weaviate schema
    """

    # Initialize the return value
    schema = {}
    schema['classes'] = []

    # determine the module name. Default is 'text2vec-contextionary'
    if modulename is None:
        modulename = DEFAULT_MODULE

    # for all entities create a class in the schema
    for name in model:
        newclass = _create_class_from_json_entity(name, model[name], modulename)
        if newclass is not None:
            schema['classes'].append(newclass)

    return schema



###################################################################################################
## These functions are generic functions
###################################################################################################


def create_schema_from_model(model: dict, modeltype: str, modulename:str=None) -> dict:
    """
    Create a schema from the argument model - based on the type of model

    Parameters
    ----------
    model: dict
        A dict that contains the data model

    Raises
    ------
    UnknownModelType
        If the modeltype is unknown
    UnsupportedModelType
        If the modeltype is not supported yet

    Returns
    ------
    dict
        The dict describing the Weaviate schema
    """

    # Initialze the return value
    schema = None

    # depending on the type of the model, generate the schema
    if modeltype == "excel":
        schema = _create_schema_from_excel(model, modulename)

    elif modeltype == "json":
        schema = _create_schema_from_json(model, modulename)

    elif modeltype == "csv":
        raise UnsupportedModelType("csv")

    elif modeltype == "yaml":
        raise UnsupportedModelType("yaml")

    else:
        raise UnknownModelType()

    return schema


def merge_schemas(schema1: dict, schema2: dict) -> dict:
    """
    Merges two schemas

    Parameters
    ----------
    schema1: dict
        A dict that contains the schema that needs to be merged with schema2
    schema2: dict
        A dict that contains the schema that needs to be merged with schema1

    Raises
    ------
    DuplicateClassInSchema
        If there are duplicate classes in the schemas

    Returns
    ------
    dict
        The dict describing the combined Weaviate schema
    """

    classlist = []
    duplicate = False
    duplicateclass = ""

    if schema1 is None or 'classes' not in schema1:
        return schema2

    if schema2 is None or 'classes' not in schema2:
        return schema1

    # initialize the return value
    schema = {}
    schema['classes'] = []

    # add the names of all classes in schema1 to the classlist
    for temp in schema1['classes']:
        if temp['class'] not in classlist:
            classlist.append(temp['class'])
        else:
            duplicate = True
            duplicateclass = temp['class']

    # add the names of all classes in schema2 to the classlist
    for temp in schema2['classes']:
        if temp['class'] not in classlist:
            classlist.append(temp['class'])
        else:
            duplicate = True
            duplicateclass = temp['class']

    # Check if there are duplicates - if so, raise the exception. Otherwise combine the two schema
    if duplicate:
        # Raise the exception
        raise DuplicateClassInSchema(duplicateclass)

    for temp in schema1['classes']:
        schema['classes'].append(temp)

    for temp in schema2['classes']:
        schema['classes'].append(temp)

    return schema


###################################################################################################
## These functions are to enable classification
###################################################################################################


def _create_classification_config_class(modulename: str) -> dict:
    """
    Creates the schema for the class that holds the classification configuration

    Parameters
    ----------
    modulename: str
        A string that specifies the modulename

    Returns
    -------
    dict
        The dict describing the new class for the classification configuration
    """

    newclass = None

    newclass = {}
    newclass['class'] = "ClassificationConfiguration"
    newclass['description'] = "This class stores the configuration of the classification"
    newclass['moduleConfig'] = {}
    newclass['moduleConfig'][modulename] = {}
    newclass['moduleConfig'][modulename]['vectorizeClassName'] = False
    newclass['properties'] = []

    # Add a property that holds the name of the class that has been classified
    prop = _create_prop('classname', 'string', "Name of this class that has been classified", modulename)
    newclass['properties'].append(prop)

    # Add a property that holds the names of the fields that have been classified
    prop = _create_prop('properties', 'string', "Names of properties that have been classified", modulename)
    newclass['properties'].append(prop)

    # Add a property that holds the number of batches that have been classified
    prop = _create_prop('batchCount', 'int', "Number of batches in the classification", modulename)
    newclass['properties'].append(prop)

    # Add a property that holds the type of classification
    prop = _create_prop('type', 'string', "type of classification", modulename)
    newclass['properties'].append(prop)

    # Add a property that holds the number of neighbors (in case of a knn classification)
    prop = _create_prop('numberOfNeighbors', 'int', "The number of neighbors in a knn classification", modulename)
    newclass['properties'].append(prop)

    # Add a property that holds the number of confidence buckets
    prop = _create_prop('confidenceBuckets', 'int', "Number of conf. buckets in a classification", modulename)
    newclass['properties'].append(prop)

    # Add a property that holds the maximum batch size
    prop = _create_prop('maxBatchSize', 'int', "Maximum batch size", modulename)
    newclass['properties'].append(prop)

    return newclass


def _add_classification_properties(classification, mainclass, modulename):
    """
    Adds the properties to a class that are needed to do a classification

    Parameters
    ----------
    classification: dict
        A dict that contains the parameters of the classification
    mainclass: dict
        A dict that contains the class to which we add properties
    modulename: str
        A string that specifies the modulename
    """

    if mainclass is not None and 'properties' in mainclass:

        # the validated property indicates whether this data point can be used for training
        prop = _create_prop('validated', 'boolean', "Indicates this is training data", modulename)
        mainclass['properties'].append(prop)

        # the preClassified property indicates whether this data point has been pre-classified
        prop = _create_prop('preClassified', 'boolean', "Indicates if point is preclassified", modulename)
        mainclass['properties'].append(prop)

        if 'classify_properties' in classification:
            for propname in classification['classify_properties']:

                # This property stores the confidence score for classification
                field = get_field_name_from_reference_property(propname)
                name = field + 'ConfidenceScore'
                prop = _create_prop(name, 'number', "conf. score", modulename, index=False)
                mainclass['properties'].append(prop)

                # This property stores the confidence bucket for classification
                field = get_field_name_from_reference_property(propname)
                name = field + 'ConfidenceBucket'
                prop = _create_prop(name, 'int', "conf. bucket", modulename, index=False)
                mainclass['properties'].append(prop)


def add_classification_to_schema(schema: dict, classification: dict, modulename: str=None):
    """
    Adds the classes and properties to the schema that are needed to do a classification

    Parameters
    ----------
    schema: dict
        A dict that contains the schema
    classification: dict
        A dict that contains the parameters of the classification
    modulename: str
        A string that specifies the modulename
    """

    if modulename is None:
        modulename = DEFAULT_MODULE

    newclass = _create_classification_config_class(modulename)
    if 'classes' in schema:
        schema['classes'].append(newclass)

    target = None
    if 'classify_class' in classification:
        for temp in schema['classes']:
            if 'class' in temp and temp['class'] == classification['classify_class']:
                target = temp
                break

    if target is not None:
        _add_classification_properties(classification, target, modulename)
