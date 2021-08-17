# import requests
# import json
# import pprint
# import pandas as pd
# from treelib import Node, Tree
# import uuid
#
# __url__ = ""
#
# __cookies__ = ""
#
# __xplain_session__ = {}
#
# __headers__ = ""
#
# __last_error__ = {}
#
# __pp__ = pprint.PrettyPrinter(indent=4)
#
# def store_xsession(response):
#     global __xplain_session__
#     responseJson = __parseResponse__(response)
#     try:
#         if responseJson.get('session') is not None:
#             __xplain_session__ = responseJson["session"][0]["element"]
#     except:
#         print("no session json found")
#
#
# def get_xsession():
#     global __xplain_session__
#     return __xplain_session__
#
#
# def store_cookies(cookies):
#     global __cookies__
#     __cookies__ = cookies
#
#
# def get_cookies():
#     global __cookies__
#     return __cookies__
#
#
# def store_header(header):
#     global __headers__
#     __headers__ = header
#
#
# def get_headers():
#     global __headers__
#     return __headers__
#
#
# def store_url(url):
#     global __url__
#     __url__ = url
#
#
# def get_url():
#     global __url__
#     return __url__
#
#
# def connect(url='http://localhost:8080', user='user', password='xplainData'):
#     global __url__, __cookies__, __headers__
#     __url__ = url
#     response = requests.get(url + "/basiclogin/basic", auth=(user, password))
#     if (response.status_code == 200):
#         __cookies__ = response.cookies
#         print("Authentication successful")
#     else:
#         print("authetication failed")
#
#
# def terminate():
#     '''
#     Terminate the current xplain session.
#     :return:
#     '''
#     requests.get(get_url() + '/logout', cookies=get_cookies(), headers=get_headers())
#     print("logged out")
#
#
# def post(payload):
#     global __url__, __cookies__, __headers__
#     response = requests.post(__url__ + "/xplainsession", data=payload, cookies=__cookies__,
#                              headers=__headers__)
#     return response
#
#
# def post_and_broadcast(payload):
#     response = post(payload)
#     responseJson = __parseResponse__(response)
#     if (response.status_code == 200):
#         store_xsession(response)
#         _broadcast_update()
#         print("perfom xplain method success")
#         return True
#     else:
#         print("perfom xplain method failed")
#         _store_rrror_and_show_message(response)
#         return False
#
#
# def get(params):
#     response = requests.get(__url__ + '/xplainsession', params=params, cookies=__cookies__)
#     return response
#
#
# def __parseResponse__(response):
#     return json.loads(response.text)
#
#
# def list_startups():
#     """
#     list all startup configuration files in the config directory
#     """
#     global __url__
#     response = requests.get(__url__ + '/startupconfig?&fileType=CONFIG_FILE&fileExtension=xstartup&caseSensitive=true')
#     return __parseResponse__(response)['result']
#
#
# def get_session_id():
#     '''
#     get the xplain session id
#     :return:
#     '''
#     global __xplain_session__
#     return __xplain_session__['sessionName']
#
#
# def _broadcast_update():
#     '''
#     use websocket to broadcast session update
#     '''
#     payload = json.dumps({"sessionId": get_session_id()})
#     post(payload)
#
#
# def run(method):
#     '''
#     perform xplain web api method and broadcast the change
#
#     Parameters
#     ----------
#         method: json
#             xplain web api method in json format
#     Returns
#     --------
#          1 (fail) or 0 (success)
#     '''
#     payload = json.dumps(method)
#     return post_and_broadcast(payload)
#
#
# def _store_rrror_and_show_message(response):
#     global __last_error__
#     responseJson = __parseResponse__(response)
#     __last_error__ = responseJson
#     show_error()
#
#
# def last_stack_trace():
#     global __last_error__, __pp__
#     __pp__.pprint(__last_error__['stacktrace'])
#
#
#
#
# def show_error():
#     global __last_error__, __pp__
#     pprint(__last_error__['localized_error_messages'])
#
#
# def get_result(request_name):
#     '''
#     return the result of a ceartain request id
#
#     Parameters
#     ------------
#         request_name:string
#             the request name or id
#     Return
#     --------------
#         result as JSON
#     '''
#     global __xplain_session__
#     if __xplain_session__.get('requests') != None:
#         for xrequest in __xplain_session__["requests"]:
#             if xrequest["requestName"] == request_name:
#                 return xrequest["results"][0]
#
#
# def convert_to_dataframe(data):
#     '''
#     convert result JSON to DataFrame format
#
#     Parameters
#     -----------
#         data:JSON
#             data in JSON format
#     Returns:
#         dataFrame
#     '''
#
#     data_fields = data['fields']
#     children = data['children']
#     dataSet = {}
#     for field in data_fields:
#         dataSet[field] = []
#
#     for child in children:
#         for field in data_fields:
#             for rec in child['data']:
#                 if isinstance(rec[field], str):
#                     dataSet[field].append(rec[field])
#                 else:
#                     if rec[field].get('value') != None:
#                         dataSet[field].append(rec[field]['value'])
#                     else:
#                         dataSet[field].append(None)
#
#     df = pd.DataFrame(dataSet)
#     return df
#
#
# def __buildTree__(new_tree, jsonObject, parent_id):
#     objectRoot = jsonObject['objectName']
#     rootid = uuid.uuid4()
#     if parent_id == None:
#         new_tree.create_node('(( ' + objectRoot + ' ))', rootid)
#     else:
#         new_tree.create_node('(( ' + objectRoot + ' ))', rootid, parent=parent_id)
#
#     for dimension in jsonObject['dimensions']:
#         dimension_id = uuid.uuid4()
#         new_tree.create_node(dimension['dimensionName'], dimension_id, parent=rootid)
#         if dimension.get('attributes') != None:
#             for attribute in dimension['attributes']:
#                 attribute_id = uuid.uuid4()
#                 new_tree.create_node(attribute['attributeName'], attribute_id, parent=dimension_id)
#     if jsonObject.get('childObjects') != None:
#         for childObject in jsonObject['childObjects']:
#             __buildTree__(new_tree, childObject, rootid)
#
#     return new_tree
#
#
# def show_tree():
#     '''
#     show object tree
#     Return
#     -------
#         render the object hierarchy in a tree
#     '''
#     new_tree = Tree()
#     tree = __buildTree__(new_tree, get_xsession()['focusObject'], parent_id=None)
#     tree.show()
#
#
# def get_object_info(objectName, root=None):
#     if root == None:
#         root = get_xsession()['focusObject']
#     if root['objectName'] == objectName:
#         return root
#     else:
#         if root.get('childObjects') != None:
#             for obj in root['childObjects']:
#                 obj_found = get_object_info(objectName, obj)
#                 if obj_found != None:
#                     return obj_found
#         else:
#             return None
#
#
# def get_dimension_info(objectName, dimensionName):
#     object = get_object_info(objectName)
#     for dimension_obj in object['dimensions']:
#         if dimension_obj['dimensionName'] == dimensionName:
#             return dimension_obj
#
#
# def get_attribute_info(objectName, dimensionName, attributeName):
#     dimension = get_dimension_info(objectName, dimensionName)
#     for attribute_obj in dimension['attributes']:
#         if attribute_obj['attributeName'] == attributeName:
#             return attribute_obj
#
#
# def get_tree_details(objectName=None, dimensionName=None, attributeName=None):
#     '''
#     get the meta data details of certain xplain object, dimension or attribute as json
#
#     Parameters
#     -----------
#         objectName:string
#             the name of object optional , if empty, show the whole object tree from root,  if only objectName is specified, this funtion will return the meta data of
#              this object
#         dimensionName:string
#            the name of dimension, optional, it objectName and dimensionName are specified, it will return the dimesion meta data
#         attributeName:string
#            the name of attribute, optional, it objectName, dimensionName and attributeName is specified, it will return the attribute meta data
#     Returns
#     --------
#          JSON object
#
#     '''
#     if objectName == None and dimensionName is None and attributeName is None:
#         return get_xsession()['focusObject']
#     if objectName != None and dimensionName is None and attributeName is None:
#         return get_object_info(objectName)
#     if objectName != None and dimensionName is not None and attributeName is None:
#         return get_dimension_info(objectName, dimensionName)
#     if objectName != None and dimensionName is not None and attributeName is not None:
#         return get_attribute_info(objectName, dimensionName, attributeName)
#
#
# def pprint( content):
#     '''
#     pretty printing
#
#     Parameters
#     -----------
#         content: any
#             the content
#     '''
#     global __pp__
#     __pp__.pprint(content)
#
#
# def get_state_hierarchy(object_name, dimension_name, attribute_name):
#     """
#     returns the state hierarchy of the given attribute
#     :param object_name: object name
#     :param dimension_name: dimension name
#     :param attribute_name: attribute name
#     :return: JSON presentation of the state hierarchy of the attribute
#     """
#     methodCall = {
#         "method": "getStateHierarchy",
#         "object": object_name,
#         "dimension": dimension_name,
#         "attribute": attribute_name
#     }
#     response = post(json.dumps(methodCall))
#     if response.status_code is 200:
#         responseJson = __parseResponse__(response)
#         return   json.loads(responseJson["stateHierarchy"])
#     else:
#         _store_rrror_and_show_message()
#
#
# def build_groupby(object_name=None, dimension_name=None, attribute_name = None, groupby_level=None, groupby_level_number=None):
#     groupby = {
#         "attribute": {
#             "object": object_name,
#             "dimension": dimension_name,
#             "attribute": attribute_name
#         }
#     }
#     if groupby_level is not None:
#         groupby["groupByLevel"] = groupby_level
#
#     if groupby_level_number is not None:
#         groupby["groupByLevelNumber"] = groupby_level_number
#     return groupby
#
# def build_selection(attribute_name, object_name=None, dimension_name=None, selected_states=None):
#     selection = {
#         "attribute": {
#             "object": object_name,
#             "dimension": dimension_name,
#             "attribute": attribute_name
#         },
#         "selectedStates": selected_states
#     }
#     return selection