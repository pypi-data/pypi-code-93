# -*- coding: utf-8 -*-


class ArchivalDataStatistics(object):

    """Implementation of the 'Archival data statistics.' model.

    Specifies statistics about archival data.

    Attributes:
        logical_size_bytes (long|int): Specifies the logicalSizeBytes.
        logical_bytes_transferred (long|int): Specifies the logical bytes
            transferred.
        physical_bytes_transferred (long|int): Specifies the physical bytes
            transferred.
        avg_logical_transfer_rate_bps (long|int): Specifies the average rate
            of transfer in bytes per second.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "logical_size_bytes":'logicalSizeBytes',
        "logical_bytes_transferred":'logicalBytesTransferred',
        "physical_bytes_transferred":'physicalBytesTransferred',
        "avg_logical_transfer_rate_bps":'avgLogicalTransferRateBps'
    }

    def __init__(self,
                 logical_size_bytes=None,
                 logical_bytes_transferred=None,
                 physical_bytes_transferred=None,
                 avg_logical_transfer_rate_bps=None):
        """Constructor for the ArchivalDataStatistics class"""

        # Initialize members of the class
        self.logical_size_bytes = logical_size_bytes
        self.logical_bytes_transferred = logical_bytes_transferred
        self.physical_bytes_transferred = physical_bytes_transferred
        self.avg_logical_transfer_rate_bps = avg_logical_transfer_rate_bps


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
        logical_size_bytes = dictionary.get('logicalSizeBytes')
        logical_bytes_transferred = dictionary.get('logicalBytesTransferred')
        physical_bytes_transferred = dictionary.get('physicalBytesTransferred')
        avg_logical_transfer_rate_bps = dictionary.get('avgLogicalTransferRateBps')

        # Return an object of this model
        return cls(logical_size_bytes,
                   logical_bytes_transferred,
                   physical_bytes_transferred,
                   avg_logical_transfer_rate_bps)


