# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.cdp_object_last_run_info

class CdpObjectInfo(object):

    """Implementation of the 'CdpObjectInfo' model.

    Specifies the CDP related information for a given object. This field will
    only be populated when protection group is configured with policy having
    CDP retention settings.

    Attributes:
        cdp_enabled (bool): Specifies whether CDP is currently active or not.
            CDP might have been active on this object before, but it might not
            be anymore.
        io_filter_status (IoFilterStatusEnum): Specifies the state of CDP IO
            filter. CDP IO filter is an agent which will be installed on the
            object for performing continious backup. <br> 1. 'kNotInstalled'
            specifies that CDP is enabled on this object but filter is not
            installed. <br> 2. 'kInstallFilterInProgress' specifies that IO
            filter installation is triggered and in progress. <br> 3.
            'kFilterInstalledIOInactive' specifies that IO filter is installed
            but IO streaming is disabled due to missing backup or explicitly
            disabled by the user. <br> 4. 'kIOActivationInProgress' specifies
            that IO filter is activated to start streaming. <br> 5.
            'kIOActive' specifies that filter is attached to theeee object and
            started streaming. <br> 6. 'kIODeactivationInProgress' specifies
            that deactivattion has been initiated to stop the IO streaming.
            <br> 7. 'kUninstallFilterInProgress' specifies that uninstallation
            of IO filter is in progress.
        last_run_info (CdpObjectLastRunInfo): Specifies the last backup
            information for a given CDP object.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "cdp_enabled":'cdpEnabled',
        "io_filter_status":'ioFilterStatus',
        "last_run_info":'lastRunInfo'
    }

    def __init__(self,
                 cdp_enabled=None,
                 io_filter_status=None,
                 last_run_info=None):
        """Constructor for the CdpObjectInfo class"""

        # Initialize members of the class
        self.cdp_enabled = cdp_enabled
        self.io_filter_status = io_filter_status
        self.last_run_info = last_run_info


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
        cdp_enabled = dictionary.get('cdpEnabled')
        io_filter_status = dictionary.get('ioFilterStatus')
        last_run_info = cohesity_management_sdk.models_v2.cdp_object_last_run_info.CdpObjectLastRunInfo.from_dictionary(dictionary.get('lastRunInfo')) if dictionary.get('lastRunInfo') else None

        # Return an object of this model
        return cls(cdp_enabled,
                   io_filter_status,
                   last_run_info)


