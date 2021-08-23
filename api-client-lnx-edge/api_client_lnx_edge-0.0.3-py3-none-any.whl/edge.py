from .components import AdjustmentsAPI, EntityAPI, ReportingAPI


class EdgeAPI(AdjustmentsAPI, EntityAPI, ReportingAPI):
    staging = False


class StagingAPI(AdjustmentsAPI, EntityAPI, ReportingAPI):
    staging = True
