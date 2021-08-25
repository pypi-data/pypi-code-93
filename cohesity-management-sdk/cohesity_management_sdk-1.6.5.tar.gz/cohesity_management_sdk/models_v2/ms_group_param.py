# -*- coding: utf-8 -*-

import cohesity_management_sdk.models_v2.recover_object_1

class MsGroupParam(object):

    """Implementation of the 'MsGroupParam' model.

    Specifies parameters to recover MS group.

    Attributes:
        recover_object (RecoverObject1): Specifies the MS group recover Object
            info.
        recover_entire_group (bool): Specifies if the entire Group (mailbox +
            site) is to be restored.
        mailbox_restore_type (MailboxRestoreTypeEnum): Specifies whether
            mailbox restore is full or granular.
        site_restore_type (SiteRestoreTypeEnum): Specifies whether site
            restore is full or granular.

    """

    # Create a mapping from Model property names to API property names
    _names = {
        "recover_object":'recoverObject',
        "recover_entire_group":'recoverEntireGroup',
        "mailbox_restore_type":'mailboxRestoreType',
        "site_restore_type":'siteRestoreType'
    }

    def __init__(self,
                 recover_object=None,
                 recover_entire_group=None,
                 mailbox_restore_type=None,
                 site_restore_type=None):
        """Constructor for the MsGroupParam class"""

        # Initialize members of the class
        self.recover_object = recover_object
        self.recover_entire_group = recover_entire_group
        self.mailbox_restore_type = mailbox_restore_type
        self.site_restore_type = site_restore_type


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
        recover_object = cohesity_management_sdk.models_v2.recover_object_1.RecoverObject1.from_dictionary(dictionary.get('recoverObject')) if dictionary.get('recoverObject') else None
        recover_entire_group = dictionary.get('recoverEntireGroup')
        mailbox_restore_type = dictionary.get('mailboxRestoreType')
        site_restore_type = dictionary.get('siteRestoreType')

        # Return an object of this model
        return cls(recover_object,
                   recover_entire_group,
                   mailbox_restore_type,
                   site_restore_type)


