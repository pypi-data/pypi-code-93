import pyrql
from pyrql.query import And, Or, Filter
import uuid
from enum import Enum
from s3i import EventMessage
import time, copy
import json


class EventFilterType(Enum):
    """
    Class for creating enumerations of event filter's type, which contains only RQL_FILTER used in S³I EventSystem
    """
    RQL_FILTER = 1


class EventManager:
    """
    Class for creating an event manager that manages an event system built in an edge based thing
    """

    def __init__(self, event_filter_type, ml40_model):
        """
        Constructor

        :param event_filter_type: type of event filter, by default (EventFilterType.RQL_FILTER)
        :param ml40_model: data model of monitored ml40 Thing
        :type ml40_model: dict
        """
        self.__sub_id_list = []
        self.__map_attr_sub = dict()
        self.__map_sub_attr = dict()
        # self.__fml40_model = benedict(fml40_model, keypath_separator=" ")
        self.__ml40_model = ml40_model
        self.__events = []
        self.__event_filter_type = event_filter_type

        if self.__event_filter_type == EventFilterType.RQL_FILTER:
            self.__rql = RQL(fml40=self.__ml40_model)

    def query_sub_id_list(self):
        """
        Function to query all subscription ids

        :return: subscription ids
        :rtype: list
        """
        return self.__sub_id_list

    def query_subscribed_event(self, sub_id):
        """
        Function to query a event via its subscription id

        :param sub_id: subscription id
        :type sub_id: str
        :return: event

        """
        for event in self.__events:
            if event.__dict__.get("sub_id") == sub_id:
                return event.__dict__

    @staticmethod
    def __generate_sub_id():
        """
        generate a S³I subscription id
        :return: subscription id
        :rtype: str

        """
        return "s3i:" + str(uuid.uuid4())

    def add_event(self, filter_expression: str, subscriber: str, subscriber_endpoint: str):
        """
        add event into event manager

        :param filter_expression: RQL expression
        :type filter_expression: str
        :param subscriber: id of event subscriber
        :type subscriber: str
        :param subscriber_endpoint: endpoint of event subscriber
        :type subscriber_endpoint: str

        :return: is event added or not, a generated event subscription id
        :rtype: bool, str

        """
        event = self.__add_event(filter_expression, subscriber, subscriber_endpoint)
        if event is None:
            return False, None
        for exist_event in self.__events:
            if str(exist_event.event_filter) == str(event.event_filter):
                if not set(event.subscribers) < set(exist_event.subscribers):
                    exist_event.subscribers += event.subscribers
                    exist_event.subscriber_endpoints += event.subscriber_endpoints
                return True, exist_event.sub_id
        self.__events.append(event)
        return True, event.sub_id

    def __add_event(self, filter_expression, subscriber, subscriber_endpoint):
        __attributes = []
        __event_filter = None
        if self.__event_filter_type == EventFilterType.RQL_FILTER:
            if not self.__rql.is_rql_valid(filter_expression):
                return None
            __event_filter = self.__rql.make_filter(rql_expr=filter_expression)
            __parsed_rql = self.__rql.parse(rql_expr=filter_expression)
            __attributes = self.__rql.get_attributes(__parsed_rql)
        __sub_id = self.__generate_sub_id()
        self.__sub_id_list.append(__sub_id)

        self.__map_sub_attr[__sub_id] = __attributes

        for __attr in __attributes:
            if self.__map_attr_sub.get(__attr) is None:
                self.__map_attr_sub[__attr] = list()
            self.__map_attr_sub[__attr].append(__sub_id)

        _event = Event(__sub_id, __attributes, __event_filter, [subscriber], [subscriber_endpoint],
                       ml40_model=self.__ml40_model)
        return _event

    def delete_event(self, subscription_id: str) -> bool:
        """
        delete event from event manager

        :param subscription_id: subscription id of event
        :type subscription_id: str
        :return: is event deleted
        :rtype: bool

        """
        for event in self.__events:
            if event.__dict__.get("sub_id") == subscription_id:
                self.__events.remove(event)
                return True
        return False

    def emit_event(self, publisher, sender_id):
        """
        emit events

        :param publisher: event publisher e.g. instantiated S³I Broker object that has a sending function
        :param sender_id: id of sender
        :type sender_id: str
        """
        while True:
            for event in self.__events:
                #if event.is_filter_true:
                if event.is_filter_true and event.is_attributes_changed:
                    event_message = event.generate_event_message(sender_id=sender_id)
                    publisher.send(receiver_endpoints=event.subscriber_endpoints, msg=json.dumps(event_message))

    def subject_updated(self, cur_ml40):
        """
        This function will be called if the subject's data model is changed

        :param path: has a changed value
        :type path: str
        """
        for event in self.__events:
            event.check_attribute_change(cur_ml40)
            event.check_filter(cur_ml40)
        """
        path = path.replace("/", " ")
        sub_ids = self.__map_attr_sub.get(path)
        if sub_ids is None:
            return None

        for sub_id in sub_ids:
            for event in self.__events:
                if event.__dict__.get("sub_id") == sub_id:
                    event(cur_ml40)
        """

class Event(object):
    """
    class for creating an event object
    """
    subscription_count = 0

    def __init__(self, sub_id, attributes, event_filter, subscribers, subscriber_endpoints,
                 ml40_model):
        """
        Constructor

        :param sub_id: subscription id
        :type sub_id: str
        :param attributes: in the event filter related attributes
        :type attributes: str
        :param event_filter: event filter, e.g. RQL filter
        :param subscribers: subscribers
        :type subscribers: list
        :param subscriber_endpoints: endpoints of subscribers
        :type subscriber_endpoints: list

        """
        self.sub_id = sub_id
        self.attributes = attributes
        self.event_filter = event_filter

        self.subscribers = subscribers
        self.subscriber_endpoints = subscriber_endpoints
        self.__class__.subscription_count += 1
        self._cur_dict = dict()
        self.__ml40_model = ml40_model
        #self.__ml40_old_model = ml40_model
        self._is_filter_true = False
        self._is_attribute_changed = False

        self.__resGetValue = list()

    @property
    def is_filter_true(self):
        return self._is_filter_true

    @property
    def is_attributes_changed(self):
        return self._is_attribute_changed

    def __del__(self):
        self.__class__.subscription_count -= 1

    def check_filter(self, cur_ml40):
        """
        Function to check if filter is set to true which means an event is triggered

        :param cur_ml40: current fml40 Json data model
        :type cur_ml40: dict
        :return: the status of filter
        :rtype: bool

        """

        self.__ml40_model = cur_ml40
        for attr in self.attributes:
            value = _uriToData(attr.replace(" ", "/"), self.__ml40_model)
            self._cur_dict.update({attr: value})
        if self.event_filter(self._cur_dict):
            self._is_filter_true = True

        else:
            self._is_filter_true = False

    def check_attribute_change(self, cur_ml40):
        for attr in self.attributes:
            new_value = _uriToData(attr.replace(" ", "/"), cur_ml40)
            old_value = _uriToData(attr.replace(" ", "/"), self.__ml40_model)
            #print(new_value)
            #print(old_value)
            if new_value != old_value:
                print("attribute changed!")
                self._is_attribute_changed = True
                break
            else:
                self._is_attribute_changed = False

    def generate_event_message(self, sender_id):
        """
        Function to generate a S³I-B event message

        :param sender_id: id of sender
        :type sender_id: str
        :return: event message
        :rtype: dict

        """
        if not self._is_filter_true:
            return None

        event_message = EventMessage()
        content_dict = dict()
        for key in self._cur_dict.keys():
            content_dict[key.replace(" ", "/")] = self._cur_dict[key]

        event_message.fillEventMessage(sender=sender_id, receivers=self.subscribers,
                                       msg_id=str(uuid.uuid4()), sub_id=self.sub_id,
                                       timestamp=time.time(), content=content_dict)
        self._is_filter_true = False
        return event_message.msg


class RQL:
    """
    class for parsing, creating and checking rql filter
    """

    def __init__(self, fml40=dict):
        """
        Constructor

        :param fml40: fml40 data model
        :type fml40: dict


        """
        self._fml40 = fml40
        self._rql_logic_operator = ["and", "or"]
        self._rql_math_operator = ["eq", "ne", "gt", "ge", "lt", "ge", "in", "like", "exists"]

    @staticmethod
    def parse(rql_expr):
        """
        Function to parse rql expression

        :param rql_expr: rql expression
        :type rql_expr: str

        :return: parsed rql expression
        :rtype: str

        """
        try:
            rql_expr = rql_expr.replace("/", " ")
            parsed_rql = pyrql.parse(rql_expr)
            return parsed_rql
        except pyrql.RQLSyntaxError:
            return None

    def make_filter(self, rql_expr):
        """
        Function to create a RQL filter

        :param rql_expr: RQL expression
        :type rql_expr: str
        :return: RQL filter

        Returns:

        """
        parsed_rql = self.parse(rql_expr)
        if parsed_rql.get("name") in self._rql_math_operator:
            rql_filter = Filter(parsed_rql.get("name"), parsed_rql.get("args")[0], parsed_rql.get("args")[1])

        else:
            args = parsed_rql.get("args")
            rql_filter = self.__create_single_filter(args)
            for i in range(len(rql_filter) - 1):
                if parsed_rql.get("name") == "and":
                    rql_filter = And(rql_filter[i], rql_filter[i + 1])
                if parsed_rql.get("name") == "or":
                    rql_filter = Or(rql_filter[i], rql_filter[i + 1])
        return rql_filter

    def __create_single_filter(self, args, filters=list()):
        """
        Function to create a single filter which only contains one related variable in filter expression

        Args:
            args:
            filters:

        Returns:

        """
        for i in range(len(args)):
            if args[i].get("name") not in self._rql_logic_operator:
                filters.append(
                    Filter(args[i].get("name"), args[i].get("args")[0], args[i].get("args")[1]))
            else:
                filters.append(list())
                self._create_single_filter(args=args[i].get("args"), filters=filters[i])

                if args[i].get("name") == "and":

                    for j in range(len(filters[i]) - 1):
                        filters[i] = And(filters[i][j], filters[i][j + 1])

                if args[i].get("name") == "or":

                    for j in range(len(filters[i]) - 1):
                        filters[i] = Or(filters[i][j], filters[i][j + 1])

        return filters

    def get_attributes(self, parsed_rql):
        """
        Function to get all attributes listed in RQL expression

        :param parsed_rql: parsed rql expression
        :type parsed_rql: str
        :return: attributes
        :rtype: list

        """
        _attributes = list()
        if parsed_rql.get("name") in self._rql_math_operator:
            _attributes.append(parsed_rql.get("args")[0])

        else:
            args = parsed_rql.get("args")
            _attributes = self._get_attributes(args)
        return _attributes

    def _get_attributes(self, args):
        _attributes = list()
        for i in range(len(args)):
            if args[i].get("name") not in self._rql_logic_operator:
                _attributes.append(args[i].get("args")[0])
            else:
                _temp_attributes = self._get_attributes(args=args[i].get("args"))
                for temp in _temp_attributes:
                    _attributes.append(temp)
        return _attributes

    def is_rql_valid(self, rql_expr):
        """
        Function to check if a RQL expression is valid

        :param rql_expr: RQL expression
        :type rql_expr: str

        :return: status of rql validation
        :rtype: bool

        """
        parsed_rql = self.parse(rql_expr)
        if parsed_rql is None:
            return False

        attributes_list = self.get_attributes(parsed_rql)
        for attr in attributes_list:
            attr = attr.replace(" ", "/")
            try:
                var = _uriToData(uri=attr, ml40_model=self._fml40)
                if var == "Invalid attribute path":
                    return False
            except KeyError:
                return False
        return True

resGetValue = list()


def _uriToData(uri, ml40_model):
    """Returns a copy of the value found at uri.

    :param uri: Path to value
    :rtype: Feature

    """
    global resGetValue
    if uri == "":
        return ml40_model
    else:
        uri_list = uri.split("/")
        if uri_list[0] == "features":
            try:
                return ml40_model[uri]
            except KeyError:
                return "Invalid attribute path"

        try:
            _getValue(ml40_model, uri_list, ml40_model)
        except:
            return "Invalid attribute path"
        if resGetValue.__len__() == 0:
            return "Invalid attribute path"
        response = copy.deepcopy(resGetValue)
        resGetValue.clear()
        if response.__len__() == 1:
            return response[0]
        else:
            return response


def _getValue(source, uri_list, ml40_model):
    """Searches for the value specified by uri_list in source and stores
    the result in __resGetValue.

    :param source: Object that is scanned
    :param uri_list: List containing path

    """
    global resGetValue
    value = source[uri_list[0]]
    if uri_list.__len__() == 1:
        # if is ditto-feature
        if isinstance(value, str):
            try:
                stringValue_split = value.split(":")
                if stringValue_split[0] == "ditto-feature":
                    value = ml40_model["features"][stringValue_split[1]][
                        "properties"
                    ][uri_list[0]]
            except:
                pass
        resGetValue.append(value)
        return
    if isinstance(value, dict):
        # ??? uri_list.pop(0) better?!
        del uri_list[0]
        _getValue(value, uri_list, ml40_model)
    if isinstance(value, list):
        if isinstance(value[0], (str, int, float, bool, list)):
            return value
        if isinstance(value[0], dict):
            for item in value:
                if item["class"] == "ml40::Thing":
                    for i in item["roles"]:
                        if _findValue(i, uri_list[1]):
                            uri_list_1 = copy.deepcopy(uri_list)
                            del uri_list_1[:2]
                            _getValue(item, uri_list_1, ml40_model)
                    _f = _findValue({"identifier": item.get("identifier")}, uri_list[1]) or \
                         _findValue({"name": item.get("name")}, uri_list[1])
                    if _f:
                        uri_list_1 = copy.deepcopy(uri_list)
                        del uri_list_1[:2]
                        _getValue(item, uri_list_1, ml40_model)
                else:
                    if _findValue(item, uri_list[1]):
                        uri_list_1 = copy.deepcopy(uri_list)
                        del uri_list_1[:2]
                        if not uri_list_1:
                            resGetValue.append(item)
                            return
                        else:
                            _getValue(item, uri_list_1, ml40_model)
    if isinstance(value, (str, int, float, bool)):
        # if is ditto-feature
        if isinstance(value, str):
            try:
                stringValue_split = value.split(":")
                if stringValue_split[0] == "ditto-feature":
                    value = ml40_model["features"][stringValue_split[1]][
                        "properties"
                    ][uri_list[0]]
            except:
                pass
        resGetValue.append(value)


def _findValue(json, value):
    """Returns true if value has been found in json, otherwise returns false.

    :param json: dictionary
    :param value:
    :returns:
    :rtype:

    """

    # TODO: Simplify: value in json.values()
    for item in json:
        if json[item] == value:
            # print("Parameter: ", json[item])
            return True
    return False
