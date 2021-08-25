from . import types

class CostExplorerFilter:
    filter: types.CAUFilter=None

    def __init__(self, filter: types.CAUFilter=None) -> None:
        self.filter = filter

    @staticmethod
    def NoCredits(IncSupport=False):
        DimensionValues = types.RECORD_TYPE_DIMENSIONS
        if IncSupport:
            DimensionValues.pop(types.RECORD_TYPE_DIMENSIONS.find('Support'))
            # DimensionValues = ["Credit", "Refund", "Upfront"]
        return {"Not": {"Dimensions": {"Key": "RECORD_TYPE", "Values": DimensionValues}}}

    @staticmethod
    def CreditsOnly():
        return {"Dimensions": {"Key": "RECORD_TYPE","Values": ["Credit"]}}

    @staticmethod
    def RefundOnly():
        return {"Dimensions": {"Key": "RECORD_TYPE","Values": ["Refund"]}}

    @staticmethod
    def UpfrontOnly():
        return {"Dimensions": {"Key": "RECORD_TYPE","Values": ["Upfront"]}}

