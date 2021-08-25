# -*- coding: utf-8 -*-


class ChassisSpecificResponse(object):

    """Implementation of the 'Chassis specific response.' model.

    Specifies information about hardware chassis.

    Attributes:
        id (long|int): Specifies the id of the chassis used to uniquely
            identify a chassis.
        hardware_model (string): Specifies the hardware model of the chassis.
        name (string): Specifies the name of the chassis.
        serial_number (string): Specifies the serial number of the chassis.
        node_ids (list of long|int): Specifies list of ids of all the nodes in
            chassis.
        rack_id (long|int): Rack Id that this chassis belong to

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "hardware_model":'hardwareModel',
        "name":'name',
        "serial_number":'serialNumber',
        "node_ids":'nodeIds',
        "rack_id":'rackId'
    }

    def __init__(self,
                 id=None,
                 hardware_model=None,
                 name=None,
                 serial_number=None,
                 node_ids=None,
                 rack_id=None):
        """Constructor for the ChassisSpecificResponse class"""

        # Initialize members of the class
        self.id = id
        self.hardware_model = hardware_model
        self.name = name
        self.serial_number = serial_number
        self.node_ids = node_ids
        self.rack_id = rack_id


    @classmethod
    def from_dictionary(cls,
                        dictionary):
        """Creates an instance of this model from a dictionary

        Args:
            dictionary (dictionary): A dictionary representation of the object as
            obtained from the deserialization of the server's response. The keys
            MUST match property names in the API description.

        Returns:
            object: An instance of this structure class.

        """
        if dictionary is None:
            return None

        # Extract variables from the dictionary
        id = dictionary.get('id')
        hardware_model = dictionary.get('hardwareModel')
        name = dictionary.get('name')
        serial_number = dictionary.get('serialNumber')
        node_ids = dictionary.get('nodeIds')
        rack_id = dictionary.get('rackId')

        # Return an object of this model
        return cls(id,
                   hardware_model,
                   name,
                   serial_number,
                   node_ids,
                   rack_id)


