import pandas as pd

from .. import Interpreter as VanillaInterpreter, Time
from ..errors import CraftAiNullDecisionError
from .utils import is_valid_property_value, create_timezone_df, format_input


class Interpreter(VanillaInterpreter):
    @staticmethod
    def decide_from_contexts_df(tree, contexts_df):
        bare_tree, configuration, tree_version = VanillaInterpreter._parse_tree(tree)
        interpreter = VanillaInterpreter._get_interpreter(tree_version)

        df = contexts_df.copy(deep=True)
        tz_col = [
            key
            for key, value in configuration["context"].items()
            if value["type"] == "timezone"
        ]
        # If a timezone is needed create a timezone dataframe which will
        # store the timezone to use. It can either be the DatetimeIndex
        # timezone or the timezone column if provided.
        if tz_col:
            tz_col = tz_col[0]
            df[tz_col] = create_timezone_df(contexts_df, tz_col).iloc[:, 0]

        predictions_iter = (
            Interpreter.decide_from_row(
                {
                    "bare_tree": bare_tree,
                    "context_ops": row,
                    "tz_col": tz_col,
                    "configuration": configuration,
                    "feature_names": df.columns.values,
                    "interpreter": interpreter,
                }
            )
            for row in df.itertuples(name="column_names")
        )
        return pd.DataFrame(predictions_iter, index=df.index)

    @staticmethod
    def decide_from_row(params):
        """
    Compute a decision from a valid context operation

    params : dict {
      "bare_tree": a valid craft ai tree,
      "context_row": a valid tuple representing a context operation,
      "tz_col": the time zone column,
      "configuration": a valid craft-ai configuration,
      "feature_names": the feature names,
      "interpreter": craft_ai interpreter
    }
    """

        context = {
            feature_name: format_input(value)
            for feature_name, value in zip(
                params["feature_names"], params["context_ops"][1:]
            )
            if is_valid_property_value(feature_name, value)
        }
        time = Time(
            t=params["context_ops"][0].value
            // 1000000000,  # Timestamp.value returns nanoseconds
            timezone=context[params["tz_col"]]
            if params["tz_col"]
            else params["context_ops"][0].tz,
        )
        try:
            decision = VanillaInterpreter._decide(
                params["configuration"],
                params["bare_tree"],
                (context, time),
                params["interpreter"],
            )

            return {
                "{}_{}".format(output, key): value
                for output, output_decision in decision["output"].items()
                for key, value in output_decision.items()
            }
        except CraftAiNullDecisionError as e:
            return {"error": e.message}
