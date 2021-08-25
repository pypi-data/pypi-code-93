# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.common_recover_object_snapshot_params
import cohesity_management_sdk.models_v2.recover_awsvm_params
import cohesity_management_sdk.models_v2.recover_aws_file_and_folder_params
import cohesity_management_sdk.models_v2.recover_rds_params

class RecoverAWSEnvironmentParams(object):

    """Implementation of the 'Recover AWS environment params.' model.

    Specifies the recovery options specific to AWS environment.

    Attributes:
        objects (list of CommonRecoverObjectSnapshotParams): Specifies the
            list of recover Object parameters. This property is mandatory for
            all recovery action types except recover vms. While recovering
            VMs, a user can specify snapshots of VM's or a Protection Group
            Run details to recover all the VM's that are backed up by that
            Run. For recovering files, specifies the object contains the file
            to recover.
        recovery_action (RecoveryAction2Enum): Specifies the type of recover
            action to be performed.
        recover_vm_params (RecoverAWSVMParams): Specifies the parameters to
            recover AWS VM.
        recover_file_and_folder_params (RecoverAWSFileAndFolderParams):
            Specifies the parameters to recover files and folders.
        recover_rds_params (RecoverRdsParams): Specifies the parameters to AWS
            RDS.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recovery_action":'recoveryAction',
        "objects":'objects',
        "recover_vm_params":'recoverVmParams',
        "recover_file_and_folder_params":'recoverFileAndFolderParams',
        "recover_rds_params":'recoverRdsParams'
    }

    def __init__(self,
                 recovery_action=None,
                 objects=None,
                 recover_vm_params=None,
                 recover_file_and_folder_params=None,
                 recover_rds_params=None):
        """Constructor for the RecoverAWSEnvironmentParams class"""

        # Initialize members of the class
        self.objects = objects
        self.recovery_action = recovery_action
        self.recover_vm_params = recover_vm_params
        self.recover_file_and_folder_params = recover_file_and_folder_params
        self.recover_rds_params = recover_rds_params


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
        recovery_action = dictionary.get('recoveryAction')
        objects = None
        if dictionary.get('objects') != None:
            objects = list()
            for structure in dictionary.get('objects'):
                objects.append(cohesity_management_sdk.models_v2.common_recover_object_snapshot_params.CommonRecoverObjectSnapshotParams.from_dictionary(structure))
        recover_vm_params = cohesity_management_sdk.models_v2.recover_awsvm_params.RecoverAWSVMParams.from_dictionary(dictionary.get('recoverVmParams')) if dictionary.get('recoverVmParams') else None
        recover_file_and_folder_params = cohesity_management_sdk.models_v2.recover_aws_file_and_folder_params.RecoverAWSFileAndFolderParams.from_dictionary(dictionary.get('recoverFileAndFolderParams')) if dictionary.get('recoverFileAndFolderParams') else None
        recover_rds_params = cohesity_management_sdk.models_v2.recover_rds_params.RecoverRdsParams.from_dictionary(dictionary.get('recoverRdsParams')) if dictionary.get('recoverRdsParams') else None

        # Return an object of this model
        return cls(recovery_action,
                   objects,
                   recover_vm_params,
                   recover_file_and_folder_params,
                   recover_rds_params)


