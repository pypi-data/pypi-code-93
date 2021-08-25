# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.throttling_params
import cohesity_management_sdk.models_v2.datastore_params

class RegisterVmwareVCenterRequestParameters(object):

    """Implementation of the 'Register VMware vCenter request parameters.' model.

    Specifies parameters to register VMware vCenter.

    Attributes:
        username (string): Specifies the username to access target entity.
        password (string): Specifies the password to access target entity.
        endpoint (string): Specifies the endpoint IPaddress, URL or hostname
            of the host.
        description (string): Specifies the description of the source being
            registered.
        ca_cert (string): Specifies the CA certificate to enable SSL
            communication between host and cluster.
        use_vm_bios_uuid (bool): Specifies to use VM BIOS UUID to track
            virtual machines in the host.
        min_free_datastore_space_for_backup_gb (long|int): Specifies the
            minimum free space (in GB) expected to be available in the
            datastore where the virtual disks of the VM being backed up
            reside. If the space available is lower than the specified value,
            backup will be aborted.
        throttling_params (ThrottlingParams): Specifies throttling params.
        data_store_params (list of DatastoreParams): Specifies datastore
            specific parameters.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "username":'username',
        "password":'password',
        "endpoint":'endpoint',
        "description":'description',
        "ca_cert":'caCert',
        "use_vm_bios_uuid":'useVmBiosUuid',
        "min_free_datastore_space_for_backup_gb":'minFreeDatastoreSpaceForBackupGb',
        "throttling_params":'throttlingParams',
        "data_store_params":'dataStoreParams'
    }

    def __init__(self,
                 username=None,
                 password=None,
                 endpoint=None,
                 description=None,
                 ca_cert=None,
                 use_vm_bios_uuid=None,
                 min_free_datastore_space_for_backup_gb=None,
                 throttling_params=None,
                 data_store_params=None):
        """Constructor for the RegisterVmwareVCenterRequestParameters class"""

        # Initialize members of the class
        self.username = username
        self.password = password
        self.endpoint = endpoint
        self.description = description
        self.ca_cert = ca_cert
        self.use_vm_bios_uuid = use_vm_bios_uuid
        self.min_free_datastore_space_for_backup_gb = min_free_datastore_space_for_backup_gb
        self.throttling_params = throttling_params
        self.data_store_params = data_store_params


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
        username = dictionary.get('username')
        password = dictionary.get('password')
        endpoint = dictionary.get('endpoint')
        description = dictionary.get('description')
        ca_cert = dictionary.get('caCert')
        use_vm_bios_uuid = dictionary.get('useVmBiosUuid')
        min_free_datastore_space_for_backup_gb = dictionary.get('minFreeDatastoreSpaceForBackupGb')
        throttling_params = cohesity_management_sdk.models_v2.throttling_params.ThrottlingParams.from_dictionary(dictionary.get('throttlingParams')) if dictionary.get('throttlingParams') else None
        data_store_params = None
        if dictionary.get('dataStoreParams') != None:
            data_store_params = list()
            for structure in dictionary.get('dataStoreParams'):
                data_store_params.append(cohesity_management_sdk.models_v2.datastore_params.DatastoreParams.from_dictionary(structure))

        # Return an object of this model
        return cls(username,
                   password,
                   endpoint,
                   description,
                   ca_cert,
                   use_vm_bios_uuid,
                   min_free_datastore_space_for_backup_gb,
                   throttling_params,
                   data_store_params)


