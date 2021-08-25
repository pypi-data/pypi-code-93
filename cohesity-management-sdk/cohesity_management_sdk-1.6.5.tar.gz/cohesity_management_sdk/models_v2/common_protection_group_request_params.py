# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_of_day
import cohesity_management_sdk.models_v2.protection_group_alerting_policy
import cohesity_management_sdk.models_v2.sla_rule

class CommonProtectionGroupRequestParams(object):

    """Implementation of the 'CommonProtectionGroupRequestParams' model.

    Specifies the parameters which are common between all Protection Group
    requests.

    Attributes:
        name (string): Specifies the name of the Protection Group.
        policy_id (string): Specifies the unique id of the Protection Policy
            associated with the Protection Group. The Policy provides retry
            settings Protection Schedules, Priority, SLA, etc.
        priority (PriorityEnum): Specifies the priority of the Protection
            Group.
        storage_domain_id (long|int): Specifies the Storage Domain (View Box)
            ID where this Protection Group writes data.
        description (string): Specifies a description of the Protection
            Group.
        start_time (TimeOfDay): Specifies the time of day. Used for scheduling
            purposes.
        end_time_usecs (long|int): Specifies the end time in micro seconds for
            this Protection Group. If this is not specified, the Protection
            Group won't be ended.
        alert_policy (ProtectionGroupAlertingPolicy): Specifies a policy for
            alerting users of the status of a Protection Group.
        sla (list of SlaRule): Specifies the SLA parameters for this
            Protection Group.
        qos_policy (QosPolicy1Enum): Specifies whether the Protection Group
            will be written to HDD or SSD.
        abort_in_blackouts (bool): Specifies whether currently executing jobs
            should abort if a blackout period specified by a policy starts.
            Available only if the selected policy has at least one blackout
            period. Default value is false.
        environment (Environment6Enum): Specifies the environment type of the
            Protection Group.
        is_paused (bool): Specifies if the the Protection Group is paused. New
            runs are not scheduled for the paused Protection Groups. Active
            run if any is not impacted.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "name":'name',
        "policy_id":'policyId',
        "environment":'environment',
        "priority":'priority',
        "storage_domain_id":'storageDomainId',
        "description":'description',
        "start_time":'startTime',
        "end_time_usecs":'endTimeUsecs',
        "alert_policy":'alertPolicy',
        "sla":'sla',
        "qos_policy":'qosPolicy',
        "abort_in_blackouts":'abortInBlackouts',
        "is_paused":'isPaused'
    }

    def __init__(self,
                 name=None,
                 policy_id=None,
                 environment=None,
                 priority=None,
                 storage_domain_id=None,
                 description=None,
                 start_time=None,
                 end_time_usecs=None,
                 alert_policy=None,
                 sla=None,
                 qos_policy=None,
                 abort_in_blackouts=None,
                 is_paused=None):
        """Constructor for the CommonProtectionGroupRequestParams class"""

        # Initialize members of the class
        self.name = name
        self.policy_id = policy_id
        self.priority = priority
        self.storage_domain_id = storage_domain_id
        self.description = description
        self.start_time = start_time
        self.end_time_usecs = end_time_usecs
        self.alert_policy = alert_policy
        self.sla = sla
        self.qos_policy = qos_policy
        self.abort_in_blackouts = abort_in_blackouts
        self.environment = environment
        self.is_paused = is_paused


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
        name = dictionary.get('name')
        policy_id = dictionary.get('policyId')
        environment = dictionary.get('environment')
        priority = dictionary.get('priority')
        storage_domain_id = dictionary.get('storageDomainId')
        description = dictionary.get('description')
        start_time = cohesity_management_sdk.models_v2.time_of_day.TimeOfDay.from_dictionary(dictionary.get('startTime')) if dictionary.get('startTime') else None
        end_time_usecs = dictionary.get('endTimeUsecs')
        alert_policy = cohesity_management_sdk.models_v2.protection_group_alerting_policy.ProtectionGroupAlertingPolicy.from_dictionary(dictionary.get('alertPolicy')) if dictionary.get('alertPolicy') else None
        sla = None
        if dictionary.get('sla') != None:
            sla = list()
            for structure in dictionary.get('sla'):
                sla.append(cohesity_management_sdk.models_v2.sla_rule.SlaRule.from_dictionary(structure))
        qos_policy = dictionary.get('qosPolicy')
        abort_in_blackouts = dictionary.get('abortInBlackouts')
        is_paused = dictionary.get('isPaused')

        # Return an object of this model
        return cls(name,
                   policy_id,
                   environment,
                   priority,
                   storage_domain_id,
                   description,
                   start_time,
                   end_time_usecs,
                   alert_policy,
                   sla,
                   qos_policy,
                   abort_in_blackouts,
                   is_paused)


