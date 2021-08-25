# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.time_of_day
import cohesity_management_sdk.models_v2.protection_group_alerting_policy
import cohesity_management_sdk.models_v2.sla_rule
import cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters
import cohesity_management_sdk.models_v2.tenant
import cohesity_management_sdk.models_v2.missing_entity_params

class CommonProtectionGroupResponseParams(object):

    """Implementation of the 'CommonProtectionGroupResponseParams' model.

    Specifies the parameters which are common between all Protection Group
    responses.

    Attributes:
        id (string): Specifies the ID of the Protection Group.
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
        is_active (bool): Specifies if the Protection Group is active or not.
        is_deleted (bool): Specifies if the Protection Group has been
            deleted.
        is_paused (bool): Specifies if the the Protection Group is paused. New
            runs are not scheduled for the paused Protection Groups. Active
            run if any is not impacted.
        environment (Environment7Enum): Specifies the environment of the
            Protection Group.
        last_run (CommonProtectionGroupRunResponseParameters): Protection
            run.
        permissions (list of Tenant): Specifies the list of tenants that have
            permissions for this protection group.
        is_protect_once (bool): Specifies if the the Protection Group is using
            a protect once type of policy. This field is helpful to identify
            run happen for this group.
        missing_entities (list of MissingEntityParams): Specifies the
            Information about missing entities.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "id":'id',
        "name":'name',
        "policy_id":'policyId',
        "priority":'priority',
        "storage_domain_id":'storageDomainId',
        "description":'description',
        "start_time":'startTime',
        "end_time_usecs":'endTimeUsecs',
        "alert_policy":'alertPolicy',
        "sla":'sla',
        "qos_policy":'qosPolicy',
        "abort_in_blackouts":'abortInBlackouts',
        "is_active":'isActive',
        "is_deleted":'isDeleted',
        "is_paused":'isPaused',
        "environment":'environment',
        "last_run":'lastRun',
        "permissions":'permissions',
        "is_protect_once":'isProtectOnce',
        "missing_entities":'missingEntities'
    }

    def __init__(self,
                 id=None,
                 name=None,
                 policy_id=None,
                 priority=None,
                 storage_domain_id=None,
                 description=None,
                 start_time=None,
                 end_time_usecs=None,
                 alert_policy=None,
                 sla=None,
                 qos_policy=None,
                 abort_in_blackouts=None,
                 is_active=None,
                 is_deleted=None,
                 is_paused=None,
                 environment=None,
                 last_run=None,
                 permissions=None,
                 is_protect_once=None,
                 missing_entities=None):
        """Constructor for the CommonProtectionGroupResponseParams class"""

        # Initialize members of the class
        self.id = id
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
        self.is_active = is_active
        self.is_deleted = is_deleted
        self.is_paused = is_paused
        self.environment = environment
        self.last_run = last_run
        self.permissions = permissions
        self.is_protect_once = is_protect_once
        self.missing_entities = missing_entities


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
        name = dictionary.get('name')
        policy_id = dictionary.get('policyId')
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
        is_active = dictionary.get('isActive')
        is_deleted = dictionary.get('isDeleted')
        is_paused = dictionary.get('isPaused')
        environment = dictionary.get('environment')
        last_run = cohesity_management_sdk.models_v2.common_protection_group_run_response_parameters.CommonProtectionGroupRunResponseParameters.from_dictionary(dictionary.get('lastRun')) if dictionary.get('lastRun') else None
        permissions = None
        if dictionary.get('permissions') != None:
            permissions = list()
            for structure in dictionary.get('permissions'):
                permissions.append(cohesity_management_sdk.models_v2.tenant.Tenant.from_dictionary(structure))
        is_protect_once = dictionary.get('isProtectOnce')
        missing_entities = None
        if dictionary.get('missingEntities') != None:
            missing_entities = list()
            for structure in dictionary.get('missingEntities'):
                missing_entities.append(cohesity_management_sdk.models_v2.missing_entity_params.MissingEntityParams.from_dictionary(structure))

        # Return an object of this model
        return cls(id,
                   name,
                   policy_id,
                   priority,
                   storage_domain_id,
                   description,
                   start_time,
                   end_time_usecs,
                   alert_policy,
                   sla,
                   qos_policy,
                   abort_in_blackouts,
                   is_active,
                   is_deleted,
                   is_paused,
                   environment,
                   last_run,
                   permissions,
                   is_protect_once,
                   missing_entities)


