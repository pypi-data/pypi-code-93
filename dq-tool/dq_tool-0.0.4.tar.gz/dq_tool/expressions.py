"""Classes related to expectations with expressions"""
from functools import partial
import copy

from great_expectations.dataset.sparkdf_dataset import SparkDFDataset, MetaSparkDFDataset


class Expressions:
    """Classmethods for working with expectation types"""
    _COLUMN_EXPRESSION = 'column_expression'
    _COLUMN = 'column'

    @classmethod
    def is_expression(cls, expectation_type: str) -> bool:
        """Is the expectation_type an expression expectation?"""
        return cls._COLUMN_EXPRESSION in expectation_type

    @classmethod
    def basic_to_expression(cls, expectation_type: str) -> str:
        """Convert basic expectation type to expression expectation type"""
        return expectation_type.replace(cls._COLUMN, cls._COLUMN_EXPRESSION)

    @classmethod
    def expression_to_basic(cls, expectation_type: str) -> str:
        """Convert expression expectation type to basic expectation_type"""
        return expectation_type.replace(cls._COLUMN_EXPRESSION, cls._COLUMN)


class DQToolSparkDFDataset(SparkDFDataset):
    """The GE SparkDFDataset with some additional functions needed for DQTool"""

    @classmethod
    def class_list_available_expectation_types(cls):
        """classmethod version of GE list_available_expectation_types()"""
        return [
            k for k in dir(cls)
            if k.startswith("expect_") and callable(getattr(cls, k))
        ]

    # BTW if you put some custom expectations here, you'll get expression version too - but this is not tested
    # and might not work at all


def _augment_custom_expectation_class(cls):
    """
    This is where magic happens, if you don't know Python internals, tread carefully...

    Class decorator that takes expectations from SparkDFDataset, creates wrapper for
    each of them that handles column transformations, and inserts this wrapper into the
    class.
    """

    def change_function_name(name):
        """GE uses function name under the hood, we need to change it so that it propagates correctly"""
        def wrapper(func):
            func.__name__ = copy.deepcopy(name)
            return func
        return wrapper

    def closure_fix(func):
        """
        without this decorator the function would be bound to nonlocal variable `exp_name` which would
        change value between the function definition and function call

        this way we create a copy of the `exp_name` at the time of function definition and use partial
        so that it is used under the hood on function call
        """
        # force new object creation, copy.deepcopy doesn't work for some reason...
        _exp_name = "".join(x for x in exp_name)  # pylint: disable=W0631
        return partial(func, _exp_name)

    for exp_name in cls.class_list_available_expectation_types():
        if exp_name.startswith("expect_multicolumn"):
            func_name = Expressions.basic_to_expression(exp_name)

            @MetaSparkDFDataset.expectation(["column_expression_list"])
            @change_function_name(func_name)
            @closure_fix
            def _f(exp_name, self, column_expression_list, *args, **kwargs):
                df_with_expr = self.spark_df.selectExpr(
                    *[col + f" AS column_{idx}" for idx, col in enumerate(column_expression_list)]
                )
                exp_class_instance = self.__class__(spark_df=df_with_expr)
                expectation = getattr(exp_class_instance, exp_name)
                return expectation([f"column_{idx}" for idx, _ in enumerate(column_expression_list)], *args, **kwargs)

            setattr(cls, func_name, _f)

        elif exp_name.startswith("expect_column_pair"):
            func_name = Expressions.basic_to_expression(exp_name)

            @MetaSparkDFDataset.expectation(["column_expression_A", "column_expression_A"])
            @change_function_name(func_name)
            @closure_fix
            def _f(exp_name, self, column_expression_A, column_expression_B, *args, **kwargs):  # pylint: disable=C0103
                df_with_expr = self.spark_df.selectExpr(
                    column_expression_A + " AS column_expression_A",
                    column_expression_B + " AS column_expression_B"
                )
                exp_class_instance = self.__class__(spark_df=df_with_expr)
                expectation = getattr(exp_class_instance, exp_name)
                return expectation("column_expression_A", "column_expression_B", *args, **kwargs)

            setattr(cls, func_name, _f)

        elif exp_name.startswith("expect_column"):
            func_name = Expressions.basic_to_expression(exp_name)

            @MetaSparkDFDataset.expectation(["column_expression"])
            @change_function_name(func_name)
            @closure_fix
            def _f(exp_name, self, column_expression, *args, **kwargs):
                df_with_expr = self.spark_df.selectExpr(column_expression + " AS column_expression")
                exp_class_instance = self.__class__(spark_df=df_with_expr)
                expectation = getattr(exp_class_instance, exp_name)
                return expectation("column_expression", *args, **kwargs)

            setattr(cls, func_name, _f)

        else:
            # None of recognized expectation categories, just leave it...
            pass

    return cls


@_augment_custom_expectation_class
class SparkDFDatasetExpectations(DQToolSparkDFDataset):
    """The class that contains all expectations with expressions"""
    def list_available_expectation_with_expersion_types(self):
        """Available expectations with expressions"""
        return [
            ex
            for ex in self.list_available_expectation_types()
            if 'column_expression' in ex
        ]
