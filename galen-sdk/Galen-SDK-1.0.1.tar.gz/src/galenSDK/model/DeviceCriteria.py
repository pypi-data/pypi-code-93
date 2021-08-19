"""
DeviceCriteria Class
"""

from galenSDK.enumeration.DataOperator import DataOperator


class DeviceCriteria:
    # private String key;
    key = None
    # private DataOperator operator;
    operator = None
    # private Object value;
    value = None
    # valueFrom object
    valueFrom = None
    # valueTo object
    valueTo = None

    def __init__(self, key: str = None, operator: DataOperator = None, value: object = None, valueFrom: object = None,
                 valueTo: object = None):
        """
        Initializer for the DeviceCriteria Class
        :param key: key to set
        :param operator: operator to set
        :param value: value to set
        :param valueFrom: valueFrom to set
        :param valueTo: valueTo to set
        """
        self.key = key
        self.operator = operator
        self.value = value
        self.valueFrom = valueFrom
        self.valueTo = valueTo

    def get_key(self) -> str:
        """
        :return: key
        """
        return self.key

    def set_key(self, key: str):
        """
        :param key: the key to return
        """
        self.key = key

    def get_operator(self) -> DataOperator:
        """
        :return: dataOperator
        """
        return self.operator

    def set_operator(self, operator: DataOperator):
        """
        :param operator: the operator to set
        """
        self.operator = operator

    def get_value(self) -> object:  # return object
        """
        :return: value
        """
        return self.value

    def set_value(self, value: object):
        """
        :param value: the value to set
        """
        self.value = value

    def get_value_from(self) -> object:  # return object
        """
        :return: valueFrom
        """
        return self.value

    def set_value_from(self, valueFrom: object):
        """
        :param valueFrom: the valueFrom to set
        """
        self.valueFrom = valueFrom

    def get_value_to(self) -> object:  # return object
        """
        :return: valueTo
        """
        return self.value

    def set_value_to(self, valueTo: object):
        """
        :param valueTo: the valueTo to set
        """
        self.valueTo = valueTo

    def __hash__(self):
        """
        __hash__ overloaded function
        Hash Function for the DeviceCriteria Class
        :returns: An int representing the hash value of the object
        """
        hash_result = 1
        prime = 1
        hash_result = prime * hash_result + (0 if self.key is None else self.key.__hash__())
        hash_result = prime * hash_result + (0 if self.operator is None else self.operator.__hash__())
        hash_result = prime * hash_result + (0 if self.value is None else self.value.__hash__())
        hash_result = prime * hash_result + (0 if self.valueFrom is None else self.valueFrom.__hash__())
        hash_result = prime * hash_result + (0 if self.valueTo is None else self.valueTo.__hash__())
        return hash_result

    def __eq__(self, other):
        """
        __eq__ overloaded function
        :param other: the object to compare this DeviceCriteria to
        :returns: True if both objects are equivalent, otherwise false
        """
        if not isinstance(other, DeviceCriteria):
            return False
        if self.key is None:
            if other.key is not None:
                return False
        if self.key != other.key:
            return False
        if self.operator != other.operator:
            return False
        if self.value is None:
            if other.value is not None:
                return False
        if self.value != other.value:
            return False
        if self.valueFrom is None:
            if other.valueFrom is not None:
                return False
        if self.valueFrom != other.valueFrom:
            return False
        if self.valueTo is None:
            if other.valueTo is not None:
                return False
        if self.valueTo != other.valueTo:
            return False
        return True

    def __str__(self):
        """
        __str__ overloaded function
        Turns the DeviceCriteria object into a string
        :return: string representing the DeviceCriteria object
        """
        holder = ""
        holder += "DeviceCriteria [key=" + (self.key.__str__() if self.key else "") + \
                  ", operator=" + (DataOperator.to_string(self.operator) if self.operator else "") + \
                  ", value=" + (self.value.__str__() if self.value else "") + \
                  ", valueFrom=" + (self.valueFrom.__str__() if self.valueFrom else "") + \
                  ", valueTo=" + (self.valueTo.__str__() if self.valueTo else "") + "]"
        return holder

    def __dict__(self):
        """
        __dict__ overloaded function
        :return: a dictionary of the DeviceCriteria variables.
        """
        x = {
            "key": self.key,
            "operator": DataOperator.to_string(self.operator),
            "value": self.value,
            "valueFrom": self.valueFrom,
            "valueTo": self.valueTo
        }
        return x
