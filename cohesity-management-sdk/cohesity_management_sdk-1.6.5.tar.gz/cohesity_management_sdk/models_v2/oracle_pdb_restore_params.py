# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.oracle_pdb_object_info

class OraclePdbRestoreParams(object):

    """Implementation of the 'OraclePdbRestoreParams' model.

    Specifies information about the list of pdbs to be restored.

    Attributes:
        drop_duplicate_pdb (bool): Specifies if the PDB should be ignored if a
            PDB already exists with same name.
        pdb_objects (list of OraclePdbObjectInfo): Specifies list of PDB
            objects to restore.
        restore_to_existing_cdb (bool): Specifies if pdbs should be restored
            to an existing CDB.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "drop_duplicate_pdb":'dropDuplicatePDB',
        "pdb_objects":'pdbObjects',
        "restore_to_existing_cdb":'restoreToExistingCdb'
    }

    def __init__(self,
                 drop_duplicate_pdb=None,
                 pdb_objects=None,
                 restore_to_existing_cdb=None):
        """Constructor for the OraclePdbRestoreParams class"""

        # Initialize members of the class
        self.drop_duplicate_pdb = drop_duplicate_pdb
        self.pdb_objects = pdb_objects
        self.restore_to_existing_cdb = restore_to_existing_cdb


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
        drop_duplicate_pdb = dictionary.get('dropDuplicatePDB')
        pdb_objects = None
        if dictionary.get('pdbObjects') != None:
            pdb_objects = list()
            for structure in dictionary.get('pdbObjects'):
                pdb_objects.append(cohesity_management_sdk.models_v2.oracle_pdb_object_info.OraclePdbObjectInfo.from_dictionary(structure))
        restore_to_existing_cdb = dictionary.get('restoreToExistingCdb')

        # Return an object of this model
        return cls(drop_duplicate_pdb,
                   pdb_objects,
                   restore_to_existing_cdb)


