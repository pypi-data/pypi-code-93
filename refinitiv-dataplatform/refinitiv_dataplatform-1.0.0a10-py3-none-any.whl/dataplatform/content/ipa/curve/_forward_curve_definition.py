# coding: utf8
# contract_gen 2020-06-15 10:07:47.565306

__all__ = ["ForwardCurveDefinition"]

from ..instrument._definition import ObjectDefinition


class ForwardCurveDefinition(ObjectDefinition):
    def __init__(
        self,
        index_tenor=None,
        forward_curve_tenors=None,
        forward_curve_tag=None,
        forward_start_date=None,
        forward_start_tenor=None,
    ):
        super().__init__()
        self.index_tenor = index_tenor
        self.forward_curve_tenors = forward_curve_tenors
        self.forward_curve_tag = forward_curve_tag
        self.forward_start_date = forward_start_date
        self.forward_start_tenor = forward_start_tenor

    @property
    def forward_curve_tenors(self):
        """
        Defines expected forward rate surface tenor/slices
        :return: list string
        """
        return self._get_list_parameter(str, "forwardCurveTenors")

    @forward_curve_tenors.setter
    def forward_curve_tenors(self, value):
        self._set_list_parameter(str, "forwardCurveTenors", value)

    @property
    def forward_curve_tag(self):
        """
        :return: str
        """
        return self._get_parameter("forwardCurveTag")

    @forward_curve_tag.setter
    def forward_curve_tag(self, value):
        self._set_parameter("forwardCurveTag", value)

    @property
    def forward_start_date(self):
        """
        Defines the forward start date by date format
        :return: str
        """
        return self._get_parameter("forwardStartDate")

    @forward_start_date.setter
    def forward_start_date(self, value):
        self._set_parameter("forwardStartDate", value)

    @property
    def forward_start_tenor(self):
        """
        Defines the forward start date by tenor format: "Spot" / "1M" / ...
        :return: str
        """
        return self._get_parameter("forwardStartTenor")

    @forward_start_tenor.setter
    def forward_start_tenor(self, value):
        self._set_parameter("forwardStartTenor", value)

    @property
    def index_tenor(self):
        """
        :return: str
        """
        return self._get_parameter("indexTenor")

    @index_tenor.setter
    def index_tenor(self, value):
        self._set_parameter("indexTenor", value)
