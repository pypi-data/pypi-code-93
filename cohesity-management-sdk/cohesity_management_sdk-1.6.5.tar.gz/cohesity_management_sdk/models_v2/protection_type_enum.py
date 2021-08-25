# -*- coding: utf-8 -*-

class ProtectionTypeEnum(object):

    """Implementation of the 'ProtectionType' enum.

    Specifies the AWS Protection Group type.

    Attributes:
        KAGENT: TODO: type description here.
        KNATIVE: TODO: type description here.
        KSNAPSHOTMANAGER: TODO: type description here.
        KRDSSNAPSHOTMANAGER: TODO: type description here.

    """

    KAGENT = 'kAgent'

    KNATIVE = 'kNative'

    KSNAPSHOTMANAGER = 'kSnapshotManager'

    KRDSSNAPSHOTMANAGER = 'kRDSSnapshotManager'

