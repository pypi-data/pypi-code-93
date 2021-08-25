# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.vmware_protection_group_object_params
import cohesity_management_sdk.models_v2.disk_information
import cohesity_management_sdk.models_v2.indexing_policy
import cohesity_management_sdk.models_v2.pre_and_post_script_params

class VmwareProtectionGroupParams(object):

    """Implementation of the 'VmwareProtectionGroupParams' model.

    Specifies the parameters which are specific to VMware related Protection
    Groups.

    Attributes:
        objects (list of VmwareProtectionGroupObjectParams): Specifies the
            objects to include in this Protection Group.
        exclude_object_ids (list of long|int): Specifies the list of IDs of
            the objects to not be protected by this Protection Group. This can
            be used to ignore specific objects under a parent object which has
            been included for protection.
        vm_tag_ids (list of long|int): Array of Array of VM Tag Ids that
            Specify VMs to Protect. Optionally specify a list of VMs to
            protect by listing Protection Source ids of VM Tags in this two
            dimensional array. Using this two dimensional array of Tag ids,
            the Cluster generates a list of VMs to protect which are derived
            from intersections of the inner arrays and union of the outer
            array, as shown by the following example. To protect only 'Eng'
            VMs in the East and all the VMs in the West, specify the following
            tag id array: [ [1101, 2221], [3031] ], where 1101 is the 'Eng' VM
            Tag id, 2221 is the 'East' VM Tag id and 3031 is the 'West' VM Tag
            id. The inner array [1101, 2221] produces a list of VMs that are
            both tagged with 'Eng' and 'East' (an intersection). The outer
            array combines the list from the inner array with list of VMs
            tagged with 'West' (a union). The list of resulting VMs are
            protected by this Protection Group.
        exclude_vm_tag_ids (list of long|int): Array of Arrays of VM Tag Ids
            that Specify VMs to Exclude. Optionally specify a list of VMs to
            exclude from protecting by listing Protection Source ids of VM
            Tags in this two dimensional array. Using this two dimensional
            array of Tag ids, the Cluster generates a list of VMs to exclude
            from protecting, which are derived from intersections of the inner
            arrays and union of the outer array, as shown by the following
            example. For example a Datacenter is selected to be protected but
            you want to exclude all the 'Former Employees' VMs in the East and
            West but keep all the VMs for 'Former Employees' in the South
            which are also stored in this Datacenter, by specifying the
            following tag id array: [ [1000, 2221], [1000, 3031] ], where 1000
            is the 'Former Employee' VM Tag id, 2221 is the 'East' VM Tag id
            and 3031 is the 'West' VM Tag id. The first inner array [1000,
            2221] produces a list of VMs that are both tagged with 'Former
            Employees' and 'East' (an intersection). The second inner array
            [1000, 3031] produces a list of VMs that are both tagged with
            'Former Employees' and 'West' (an intersection). The outer array
            combines the list of VMs from the two inner arrays. The list of
            resulting VMs are excluded from being protected this Job.
        app_consistent_snapshot (bool): Specifies whether or not to quiesce
            apps and the file system in order to take app consistent
            snapshots.
        fallback_to_crash_consistent_snapshot (bool): Specifies whether or not
            to fallback to a crash consistent snapshot in the event that an
            app consistent snapshot fails. This parameter defaults to true and
            only changes the behavior of the operation if
            'appConsistentSnapshot' is set to 'true'.
        skip_physical_rdm_disks (bool): Specifies whether or not to skip
            backing up physical RDM disks. Physical RDM disks cannot be backed
            up, so if you attempt to backup a VM with physical RDM disks and
            this value is set to 'false', then those VM backups will fail.
        global_exclude_disks (list of DiskInformation): Specifies a list of
            disks to exclude from the Protection Group.
        source_id (long|int): Specifies the id of the parent of the objects.
        source_name (string): Specifies the name of the parent of the
            objects.
        leverage_storage_snapshots (bool): Whether to leverage the storage
            array based snapshots for this backup job. To leverage storage
            snapshots, the storage array has to be registered as a source. If
            storage based snapshots can not be taken, job will fallback to the
            default backup method.
        leverage_hyperflex_snapshots (bool): Whether to leverage the hyperflex
            based snapshots for this backup job. To leverage hyperflex
            snapshots, it has to first be registered. If hyperflex based
            snapshots cannot be taken, job will fallback to the default backup
            method.
        cloud_migration (bool): Specifies whether or not to move the workload
            to the cloud.
        indexing_policy (IndexingPolicy): Specifies settings for indexing
            files found in an Object (such as a VM) so these files can be
            searched and recovered. This also specifies inclusion and
            exclusion rules that determine the directories to index.
        pre_post_script (PreAndPostScriptParams): Specifies the params for pre
            and post scripts.
        leverage_san_transport (bool): If this field is set to true, then the
            backup for the objects will be performed using dedicated storage
            area network (SAN) instead of LAN or managment network.
        enable_nbdssl_fallback (bool): If this field is set to true and SAN
            transport backup fails, then backup will fallback to use NBDSSL
            transport. This field only applies if 'leverageSanTransport' is
            set to true.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "objects":'objects',
        "exclude_object_ids":'excludeObjectIds',
        "vm_tag_ids":'vmTagIds',
        "exclude_vm_tag_ids":'excludeVmTagIds',
        "app_consistent_snapshot":'appConsistentSnapshot',
        "fallback_to_crash_consistent_snapshot":'fallbackToCrashConsistentSnapshot',
        "skip_physical_rdm_disks":'skipPhysicalRDMDisks',
        "global_exclude_disks":'globalExcludeDisks',
        "source_id":'sourceId',
        "source_name":'sourceName',
        "leverage_storage_snapshots":'leverageStorageSnapshots',
        "leverage_hyperflex_snapshots":'leverageHyperflexSnapshots',
        "cloud_migration":'cloudMigration',
        "indexing_policy":'indexingPolicy',
        "pre_post_script":'prePostScript',
        "leverage_san_transport":'leverageSanTransport',
        "enable_nbdssl_fallback":'enableNBDSSLFallback'
    }

    def __init__(self,
                 objects=None,
                 exclude_object_ids=None,
                 vm_tag_ids=None,
                 exclude_vm_tag_ids=None,
                 app_consistent_snapshot=None,
                 fallback_to_crash_consistent_snapshot=None,
                 skip_physical_rdm_disks=None,
                 global_exclude_disks=None,
                 source_id=None,
                 source_name=None,
                 leverage_storage_snapshots=None,
                 leverage_hyperflex_snapshots=None,
                 cloud_migration=None,
                 indexing_policy=None,
                 pre_post_script=None,
                 leverage_san_transport=None,
                 enable_nbdssl_fallback=None):
        """Constructor for the VmwareProtectionGroupParams class"""

        # Initialize members of the class
        self.objects = objects
        self.exclude_object_ids = exclude_object_ids
        self.vm_tag_ids = vm_tag_ids
        self.exclude_vm_tag_ids = exclude_vm_tag_ids
        self.app_consistent_snapshot = app_consistent_snapshot
        self.fallback_to_crash_consistent_snapshot = fallback_to_crash_consistent_snapshot
        self.skip_physical_rdm_disks = skip_physical_rdm_disks
        self.global_exclude_disks = global_exclude_disks
        self.source_id = source_id
        self.source_name = source_name
        self.leverage_storage_snapshots = leverage_storage_snapshots
        self.leverage_hyperflex_snapshots = leverage_hyperflex_snapshots
        self.cloud_migration = cloud_migration
        self.indexing_policy = indexing_policy
        self.pre_post_script = pre_post_script
        self.leverage_san_transport = leverage_san_transport
        self.enable_nbdssl_fallback = enable_nbdssl_fallback


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
                objects.append(cohesity_management_sdk.models_v2.vmware_protection_group_object_params.VmwareProtectionGroupObjectParams.from_dictionary(structure))
        exclude_object_ids = dictionary.get('excludeObjectIds')
        vm_tag_ids = dictionary.get('vmTagIds')
        exclude_vm_tag_ids = dictionary.get('excludeVmTagIds')
        app_consistent_snapshot = dictionary.get('appConsistentSnapshot')
        fallback_to_crash_consistent_snapshot = dictionary.get('fallbackToCrashConsistentSnapshot')
        skip_physical_rdm_disks = dictionary.get('skipPhysicalRDMDisks')
        global_exclude_disks = None
        if dictionary.get('globalExcludeDisks') != None:
            global_exclude_disks = list()
            for structure in dictionary.get('globalExcludeDisks'):
                global_exclude_disks.append(cohesity_management_sdk.models_v2.disk_information.DiskInformation.from_dictionary(structure))
        source_id = dictionary.get('sourceId')
        source_name = dictionary.get('sourceName')
        leverage_storage_snapshots = dictionary.get('leverageStorageSnapshots')
        leverage_hyperflex_snapshots = dictionary.get('leverageHyperflexSnapshots')
        cloud_migration = dictionary.get('cloudMigration')
        indexing_policy = cohesity_management_sdk.models_v2.indexing_policy.IndexingPolicy.from_dictionary(dictionary.get('indexingPolicy')) if dictionary.get('indexingPolicy') else None
        pre_post_script = cohesity_management_sdk.models_v2.pre_and_post_script_params.PreAndPostScriptParams.from_dictionary(dictionary.get('prePostScript')) if dictionary.get('prePostScript') else None
        leverage_san_transport = dictionary.get('leverageSanTransport')
        enable_nbdssl_fallback = dictionary.get('enableNBDSSLFallback')

        # Return an object of this model
        return cls(objects,
                   exclude_object_ids,
                   vm_tag_ids,
                   exclude_vm_tag_ids,
                   app_consistent_snapshot,
                   fallback_to_crash_consistent_snapshot,
                   skip_physical_rdm_disks,
                   global_exclude_disks,
                   source_id,
                   source_name,
                   leverage_storage_snapshots,
                   leverage_hyperflex_snapshots,
                   cloud_migration,
                   indexing_policy,
                   pre_post_script,
                   leverage_san_transport,
                   enable_nbdssl_fallback)


