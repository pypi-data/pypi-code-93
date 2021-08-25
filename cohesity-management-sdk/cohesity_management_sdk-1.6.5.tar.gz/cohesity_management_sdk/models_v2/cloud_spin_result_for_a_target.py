# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.aws_parameters
import cohesity_management_sdk.models_v2.azure_parameters
import cohesity_management_sdk.models_v2.cloud_spin_data_statistics
import cohesity_management_sdk.models_v2.data_lock_constraints

class CloudSpinResultForATarget(object):

    """Implementation of the 'Cloud Spin result for a target.' model.

    Cloud Spin result for a target.

    Attributes:
        id (long|int): Specifies the unique id of the cloud spin entity.
        aws_params (AWSParameters): Specifies various resources when
            converting and deploying a VM to AWS.
        azure_params (AzureParameters): Specifies various resources when
            converting and deploying a VM to Azure.
        name (string): Specifies the name of the already added cloud spin
            target.
        start_time_usecs (long|int): Specifies the start time of Cloud Spin in
            Unix epoch Timestamp(in microseconds) for a target.
        end_time_usecs (long|int): Specifies the end time of Cloud Spin in
            Unix epoch Timestamp(in microseconds) for a target.
        status (Status7Enum): Status of the Cloud Spin for a target. 'Running'
            indicates that the run is still running. 'Canceled' indicates that
            the run has been canceled. 'Canceling' indicates that the run is
            in the process of being canceled. 'Failed' indicates that the run
            has failed. 'Missed' indicates that the run was unable to take
            place at the scheduled time because the previous run was still
            happening. 'Succeeded' indicates that the run has finished
            successfully. 'SucceededWithWarning' indicates that the run
            finished successfully, but there were some warning messages.
        message (string): Message about the Cloud Spin run.
        stats (CloudSpinDataStatistics): Specifies statistics about Cloud Spin
            data.
        is_manually_deleted (bool): Specifies whether the snapshot is deleted
            manually.
        expiry_time_usecs (long|int): Specifies the expiry time of attempt in
            Unix epoch Timestamp (in microseconds) for an object.
        cloudspin_task_id (string): Task ID for a CloudSpin protection run.
        progress_task_id (string): Progress monitor task id for Cloud Spin
            run.
        data_lock_constraints (DataLockConstraints): Specifies the dataLock
            constraints for local or target snapshot.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "aws_params":'awsParams',
        "azure_params":'azureParams',
        "name":'name',
        "start_time_usecs":'startTimeUsecs',
        "end_time_usecs":'endTimeUsecs',
        "status":'status',
        "message":'message',
        "stats":'stats',
        "is_manually_deleted":'isManuallyDeleted',
        "expiry_time_usecs":'expiryTimeUsecs',
        "cloudspin_task_id":'cloudspinTaskId',
        "progress_task_id":'progressTaskId',
        "data_lock_constraints":'dataLockConstraints'
    }

    def __init__(self,
                 id=None,
                 aws_params=None,
                 azure_params=None,
                 name=None,
                 start_time_usecs=None,
                 end_time_usecs=None,
                 status=None,
                 message=None,
                 stats=None,
                 is_manually_deleted=None,
                 expiry_time_usecs=None,
                 cloudspin_task_id=None,
                 progress_task_id=None,
                 data_lock_constraints=None):
        """Constructor for the CloudSpinResultForATarget class"""

        # Initialize members of the class
        self.id = id
        self.aws_params = aws_params
        self.azure_params = azure_params
        self.name = name
        self.start_time_usecs = start_time_usecs
        self.end_time_usecs = end_time_usecs
        self.status = status
        self.message = message
        self.stats = stats
        self.is_manually_deleted = is_manually_deleted
        self.expiry_time_usecs = expiry_time_usecs
        self.cloudspin_task_id = cloudspin_task_id
        self.progress_task_id = progress_task_id
        self.data_lock_constraints = data_lock_constraints


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
        aws_params = cohesity_management_sdk.models_v2.aws_parameters.AWSParameters.from_dictionary(dictionary.get('awsParams')) if dictionary.get('awsParams') else None
        azure_params = cohesity_management_sdk.models_v2.azure_parameters.AzureParameters.from_dictionary(dictionary.get('azureParams')) if dictionary.get('azureParams') else None
        name = dictionary.get('name')
        start_time_usecs = dictionary.get('startTimeUsecs')
        end_time_usecs = dictionary.get('endTimeUsecs')
        status = dictionary.get('status')
        message = dictionary.get('message')
        stats = cohesity_management_sdk.models_v2.cloud_spin_data_statistics.CloudSpinDataStatistics.from_dictionary(dictionary.get('stats')) if dictionary.get('stats') else None
        is_manually_deleted = dictionary.get('isManuallyDeleted')
        expiry_time_usecs = dictionary.get('expiryTimeUsecs')
        cloudspin_task_id = dictionary.get('cloudspinTaskId')
        progress_task_id = dictionary.get('progressTaskId')
        data_lock_constraints = cohesity_management_sdk.models_v2.data_lock_constraints.DataLockConstraints.from_dictionary(dictionary.get('dataLockConstraints')) if dictionary.get('dataLockConstraints') else None

        # Return an object of this model
        return cls(id,
                   aws_params,
                   azure_params,
                   name,
                   start_time_usecs,
                   end_time_usecs,
                   status,
                   message,
                   stats,
                   is_manually_deleted,
                   expiry_time_usecs,
                   cloudspin_task_id,
                   progress_task_id,
                   data_lock_constraints)


