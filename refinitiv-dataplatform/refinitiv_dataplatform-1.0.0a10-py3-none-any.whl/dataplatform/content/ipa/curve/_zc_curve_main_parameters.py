# coding: utf8
# contract_gen 2020-06-15 10:07:47.578318

__all__ = ["ZcCurveMainParameters"]

from ..instrument._definition import ObjectDefinition
from ..enum_types.interpolation_mode import InterpolationMode
from ..enum_types.extrapolation_mode import ExtrapolationMode
from ..enum_types.price_side import PriceSide
from ..enum_types.interest_calculation_method import InterestCalculationMethod
from .step import Step
from .turn import Turn
from .zc import ZcCurveParameters
from .convexity import ConvexityAdjustment


class ZcCurveMainParameters(ObjectDefinition):
    def __init__(
        self,
        interest_calculation_method=None,
        convexity_adjustment=None,
        extrapolation_mode=None,
        interpolation_mode=None,
        pivot_curve_parameters=None,
        price_side=None,
        reference_curve_parameters=None,
        steps=None,
        turns=None,
        reference_tenor=None,
        use_convexity_adjustment=None,
        use_multi_dimensional_solver=None,
        use_steps=None,
        valuation_date=None,
    ):
        super().__init__()
        self.interest_calculation_method = interest_calculation_method
        self.convexity_adjustment = convexity_adjustment
        self.extrapolation_mode = extrapolation_mode
        self.interpolation_mode = interpolation_mode
        self.pivot_curve_parameters = pivot_curve_parameters
        self.price_side = price_side
        self.reference_curve_parameters = reference_curve_parameters
        self.steps = steps
        self.turns = turns
        self.reference_tenor = reference_tenor
        self.use_convexity_adjustment = use_convexity_adjustment
        self.use_multi_dimensional_solver = use_multi_dimensional_solver
        self.use_steps = use_steps
        self.valuation_date = valuation_date

    @property
    def convexity_adjustment(self):
        """
        :return: object ConvexityAdjustment
        """
        return self._get_object_parameter(ConvexityAdjustment, "convexityAdjustment")

    @convexity_adjustment.setter
    def convexity_adjustment(self, value):
        self._set_object_parameter(ConvexityAdjustment, "convexityAdjustment", value)

    @property
    def extrapolation_mode(self):
        """
        None: no extrapolation
        Constant: constant extrapolation
        Linear: linear extrapolation
        :return: enum ExtrapolationMode
        """
        return self._get_enum_parameter(ExtrapolationMode, "extrapolationMode")

    @extrapolation_mode.setter
    def extrapolation_mode(self, value):
        self._set_enum_parameter(ExtrapolationMode, "extrapolationMode", value)

    @property
    def interest_calculation_method(self):
        """
        Day count basis of the calculated zero coupon rates.
        Default value is: Dcb_Actual_Actual
        :return: enum InterestCalculationMethod
        """
        return self._get_enum_parameter(
            InterestCalculationMethod, "interestCalculationMethod"
        )

    @interest_calculation_method.setter
    def interest_calculation_method(self, value):
        self._set_enum_parameter(
            InterestCalculationMethod, "interestCalculationMethod", value
        )

    @property
    def interpolation_mode(self):
        """
        Interpolation method used in swap zero curve bootstrap.
        Default value is: CubicSpline

        CubicDiscount: local cubic interpolation of discount factors
        CubicRate: local cubic interpolation of rates
        CubicSpline: a natural cubic spline
        Linear: linear interpolation
        Log: log linear interpolation
        ForwardMonotoneConvex
        :return: enum InterpolationMode
        """
        return self._get_enum_parameter(InterpolationMode, "interpolationMode")

    @interpolation_mode.setter
    def interpolation_mode(self, value):
        self._set_enum_parameter(InterpolationMode, "interpolationMode", value)

    @property
    def pivot_curve_parameters(self):
        """
        :return: object ZcCurveParameters
        """
        return self._get_object_parameter(ZcCurveParameters, "pivotCurveParameters")

    @pivot_curve_parameters.setter
    def pivot_curve_parameters(self, value):
        self._set_object_parameter(ZcCurveParameters, "pivotCurveParameters", value)

    @property
    def price_side(self):
        """
        Defines which data is used for the rate surface computation.
        Default value is: Mid
        :return: enum PriceSide
        """
        return self._get_enum_parameter(PriceSide, "priceSide")

    @price_side.setter
    def price_side(self, value):
        self._set_enum_parameter(PriceSide, "priceSide", value)

    @property
    def reference_curve_parameters(self):
        """
        referenceCurveParameters notes...
        :return: object ZcCurveParameters
        """
        return self._get_object_parameter(ZcCurveParameters, "referenceCurveParameters")

    @reference_curve_parameters.setter
    def reference_curve_parameters(self, value):
        self._set_object_parameter(ZcCurveParameters, "referenceCurveParameters", value)

    @property
    def steps(self):
        """
        Use to calculate the swap rate surface discount curve, when OIS is selected as discount curve.
        The steps can specify overnight index stepped dates or/and rates.
        :return: list Step
        """
        return self._get_list_parameter(Step, "steps")

    @steps.setter
    def steps(self, value):
        self._set_list_parameter(Step, "steps", value)

    @property
    def turns(self):
        """
        Used to include end period rates/turns when calculating swap rate surfaces
        :return: list Turn
        """
        return self._get_list_parameter(Turn, "turns")

    @turns.setter
    def turns(self, value):
        self._set_list_parameter(Turn, "turns", value)

    @property
    def reference_tenor(self):
        """
        Root tenor(s) for the xIbor dependencies
        :return: str
        """
        return self._get_parameter("referenceTenor")

    @reference_tenor.setter
    def reference_tenor(self, value):
        self._set_parameter("referenceTenor", value)

    @property
    def use_convexity_adjustment(self):
        """
        false / true
        Default value is: true.
        It indicates if the system needs to retrieve the convexity adjustment
        :return: bool
        """
        return self._get_parameter("useConvexityAdjustment")

    @use_convexity_adjustment.setter
    def use_convexity_adjustment(self, value):
        self._set_parameter("useConvexityAdjustment", value)

    @property
    def use_multi_dimensional_solver(self):
        """
        false / true
        Default value is: true.
        Specifies the use of the multi-dimensional solver for yield curve bootstrapping.
        This solving method is required because the bootstrapping method sometimes creates a ZC curve which does not accurately reprice the input instruments used to build it.
        The multi-dimensional solver is recommended when cubic interpolation methods are used in building the curve (in other cases, performance might be inferior to the regular bootstrapping method).
         - true: to use multi-dimensional solver for yield curve bootstrapping
         - false: not to use multi-dimensional solver for yield curve bootstrapping
        :return: bool
        """
        return self._get_parameter("useMultiDimensionalSolver")

    @use_multi_dimensional_solver.setter
    def use_multi_dimensional_solver(self, value):
        self._set_parameter("useMultiDimensionalSolver", value)

    @property
    def use_steps(self):
        """
        false / true
        Default value is: false.
        It indicates if the system needs to retrieve the overnight index stepped dates or/and rates
        :return: bool
        """
        return self._get_parameter("useSteps")

    @use_steps.setter
    def use_steps(self, value):
        self._set_parameter("useSteps", value)

    @property
    def valuation_date(self):
        """
        The valuation date
        Default value is the current date
        :return: str
        """
        return self._get_parameter("valuationDate")

    @valuation_date.setter
    def valuation_date(self, value):
        self._set_parameter("valuationDate", value)
