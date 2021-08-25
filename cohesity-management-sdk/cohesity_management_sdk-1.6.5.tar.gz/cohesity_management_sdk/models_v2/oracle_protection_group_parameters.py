# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_protection_group_object_identifier
import cohesity_management_sdk.models_v2.vlan_params_for_backup_restore_operation

class OracleProtectionGroupParameters(object):

    """Implementation of the 'Oracle Protection Group Parameters.' model.

    Specifies the parameters to create Oracle Protection Group.

    Attributes:
        objects (list of OracleProtectionGroupObjectIdentifier): Specifies the
            list of object ids to be protected.
        persist_mountpoints (bool): Specifies whether the mountpoints created
            while backing up Oracle DBs should be persisted.
        vlan_params (VlanParamsForBackupRestoreOperation): Specifies VLAN
            params associated with the backup/restore operation.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "persist_mountpoints":'persistMountpoints',
        "vlan_params":'vlanParams'
    }

    def __init__(self,
                 objects=None,
                 persist_mountpoints=None,
                 vlan_params=None):
        """Constructor for the OracleProtectionGroupParameters class"""

        # Initialize members of the class
        self.objects = objects
        self.persist_mountpoints = persist_mountpoints
        self.vlan_params = vlan_params


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
        objects = None
        if dictionary.get('objects') != None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.oracle_protection_group_object_identifier.OracleProtectionGroupObjectIdentifier.from_dictionary(structure))
        persist_mountpoints = dictionary.get('persistMountpoints')
        vlan_params = cohesity_management_sdk.models_v2.vlan_params_for_backup_restore_operation.VlanParamsForBackupRestoreOperation.from_dictionary(dictionary.get('vlanParams')) if dictionary.get('vlanParams') else None

        # Return an object of this model
        return cls(objects,
                   persist_mountpoints,
                   vlan_params)


