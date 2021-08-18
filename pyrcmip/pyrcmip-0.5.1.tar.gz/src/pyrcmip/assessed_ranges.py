"""
Handling of assessed ranges
"""
import warnings
from collections import defaultdict

import matplotlib.cbook as cbook
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tqdm.autonotebook as tqdman
from matplotlib.gridspec import GridSpec
from scmdata import run_append

from .metric_calculations.utils import _regression_slope, _time_mean
from .plotting import CLIMATE_MODEL_PALETTE
from .stats import get_skewed_normal


class AssessedRanges:
    """
    Class for handling assessed ranges and performing operations with them.

    For example, getting values for specific metrics and plotting results against
    assessed ranges.
    """

    metric_column = "RCMIP name"
    """str: Name of the column which holds the names of the metrics being assessed"""

    assessed_range_label = "assessed range"
    """str: String used for labelling assessed ranges (in plots, dataframes etc.)"""

    def __init__(self, db):
        """
        Initialise

        Parameters
        ----------
        db : :obj:`pd.DataFrame`
            Assessed ranges data
        """
        metric_names = db[self.metric_column]
        if metric_names.duplicated().any():
            duplicates = metric_names[metric_names.duplicated()].tolist()
            raise ValueError(
                "Your assessed ranges do not have unique values for `RCMIP "
                "name`. Duplicates: {}".format(duplicates)
            )

        self.db = db.copy()

    def head(self, n=5):
        """
        Get head of ``self.db``

        Parameters
        ----------
        n : int
            Number of rows to return

        Returns
        -------
        :obj:`pd.DataFrame`
            Head of ``self.db``
        """
        return self.db.head(n)

    def tail(self, n=5):
        """
        Get tail of ``self.db``

        Parameters
        ----------
        n : int
            Number of rows to return

        Returns
        -------
        :obj:`pd.DataFrame`
            Tail of ``self.db``
        """
        return self.db.tail(n)

    def get_col_for_metric(self, metric, col):
        """
        Get value of column for a given metric (i.e. RCMIP name)

        Parameters
        ----------
        metric : str
            Metric whose values we want to look up

        col : str
            Column whose values we want (e.g. "RCMIP scenario")

        Returns
        -------
        str
            The value in the column

        Raises
        ------
        ValueError
            The metric could not be found in ``self.db``

        KeyError
            The column could not be found in ``self.db``
        """
        metric_row = self.db[self.metric_column] == metric
        if not metric_row.any():
            raise ValueError("Metric `{}` not found".format(metric))

        try:
            out = self.db.loc[metric_row, col].tolist()
        except KeyError:
            raise KeyError("Column `{}` not found".format(col))

        return out[0]

    def get_col_for_metric_list(self, metric, col, delimeter=","):
        """
        Get value of column for a given metric (i.e. RCMIP name), split using a delimeter

        Parameters
        ----------
        metric : str
            Metric whose values we want to look up

        col : str
            Column whose values we want (e.g. "RCMIP scenario")

        delimeter : str
            Delimeter used to split ``col``'s values

        Returns
        -------
        list
            List of values, derived by splitting

        Raises
        ------
        TypeError
            The found values are not a string (i.e. cannot be split by a
            delimiter)
        """
        out = self.get_col_for_metric(metric, col)

        try:
            return [v.strip() for v in out.split(delimeter)]
        except (TypeError, AttributeError):
            raise TypeError("Cannot split `{}` of type `{}`".format(out, type(out)))

    def get_variables_regions_scenarios_for_metric(self, metric, single_value=True):
        """
        Get variables, regions and scenarios required to calculate a given metric

        Parameters
        ----------
        metric : str
            Metric for which to get values

        Returns
        -------
        dict
            Dictionary containing required variables, regions and scenarios
        """
        return {
            id_str: self.get_col_for_metric_list(metric, "RCMIP {}".format(id_str))
            for id_str in ("variable", "region", "scenario")
        }

    def get_norm_period_evaluation_period(self, metric):
        """
        Get normalisation and evaluation period for a given metric

        Parameters
        ----------
        metric : str
            Metric for which to get normalisation and evaluation periods

        Returns
        -------
        norm_period, evaluation_period
            Normalisation period and evaluation period. Each return value is a
            range of years which define the relevant period. If there is no
            period supplied, ``None`` is returned. For example, if the
            evaluation period is 1961-1990 and there is no reference period,
            then ``None, range(1961, 1990 + 1)`` is returned.

        Raises
        ------
        ValueError
            A period could not be resolved because it is ambiguous i.e. it has
            nan for the start/end of the period while the other value is not
            nan.
        """
        norm_period = self._check_period_values(
            self.get_col_for_metric(metric, "norm_period_start"),
            self.get_col_for_metric(metric, "norm_period_end"),
            "norm_period",
        )

        evaluation_period = self._check_period_values(
            self.get_col_for_metric(metric, "evaluation_period_start"),
            self.get_col_for_metric(metric, "evaluation_period_end"),
            "evaluation_period",
        )

        return norm_period, evaluation_period

    @staticmethod
    def _check_period_values(start, end, period_name):
        start_is_nan = np.isnan(start)
        end_is_nan = np.isnan(end)

        if start_is_nan and end_is_nan:
            return None

        if not (start_is_nan or end_is_nan):
            return range(int(start), int(end) + 1)

        if start_is_nan:
            raise ValueError(
                "Ambiguous {}, start is nan and end is {}".format(period_name, end)
            )

        raise ValueError(
            "Ambiguous {}, start is {} and end is nan".format(period_name, start)
        )

    def check_norm_period_evaluation_period_against_data(
        self, norm_period, evaluation_period, data
    ):
        """
        Check the normalisation and evaluation periods against the data

        Parameters
        ----------
        norm_period : None or range(int, int)
            Normalisation period to check. If ``None``, no check is performed.

        evaluation_period : None or range(int, int)
            Evaluation period to check. If ``None``, no check is performed.

        data : :obj:`scmdata.ScmRun`
            Data to check

        Raises
        ------
        ValueError
            The data is incompatible with the periods (e.g. the normalisation
            period begins before the data begins).
        """
        res_min_year = data["year"].min()
        res_max_year = data["year"].max()

        self._check_period_against_data(
            norm_period, "normalisation period", res_min_year, res_max_year
        )
        self._check_period_against_data(
            evaluation_period, "evaluation period", res_min_year, res_max_year
        )

    @staticmethod
    def _check_period_against_data(period, period_id, res_min_year, res_max_year):
        if period is not None:
            if res_min_year > min(period):
                raise ValueError(
                    "Res min. year: {} is greater than {} min.: {}".format(
                        res_min_year, period_id, min(period)
                    )
                )

            if res_max_year < max(period):
                raise ValueError(
                    "Res max. year: {} is less than {} max.: {}".format(
                        res_max_year, period_id, max(period)
                    )
                )

    def get_assessed_range_for_boxplot(self, metric, n_to_draw=2 * 10 ** 4):
        """
        Get assessed range for a box plot

        This converts the assessed range from IPCC language (very likely,
        likely, central) into a distribution of values, based on
        :func:`pyrcmip.stats.get_skewed_normal`.

        Parameters
        ----------
        metric : str
            Metric for which to get assessed range distribution

        n_to_draw : int
            Number of points to include in the returned distribution

        Returns
        -------
        :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` with ``n_to_draw`` rows, each of which
            contains a drawn value for ``metric``. The returned values are put
            in a column whose name is equal to the value of ``metric``. We
            also return a ``"unit"`` column and a ``"Source"`` column. The
            ``"Source"`` column is filled with ``self.assessed_range_label``.
            Note that if the central value is nan, the entire distribution
            will simply be filled with nan.
        """
        values = self._get_assessed_range_values_for_metric(metric)

        if np.isnan(values["very_likely__lower"]):
            lower = values["likely__lower"]
            upper = values["likely__upper"]
            conf = 0.66
        else:
            lower = values["very_likely__lower"]
            upper = values["very_likely__upper"]
            conf = 0.9

        if np.isnan(values["central"]):
            out = np.zeros(n_to_draw) * np.nan
        else:
            # generate array which will plot as desired
            out = get_skewed_normal(
                median=values["central"],
                lower=lower,
                upper=upper,
                conf=conf,
                input_data=np.random.random(n_to_draw),
            )

        ar_for_boxplot = pd.DataFrame(out, columns=[metric])
        ar_for_boxplot["Source"] = self.assessed_range_label
        ar_for_boxplot["unit"] = self.get_col_for_metric(metric, "unit")

        return ar_for_boxplot

    def _get_assessed_range_values_for_metric(self, metric):
        value_cols = [
            "very_likely__lower",
            "likely__lower",
            "central",
            "likely__upper",
            "very_likely__upper",
        ]
        values = {k: float(self.get_col_for_metric(metric, k)) for k in value_cols}

        return values

    def get_results_summary_table_for_metric(self, metric, model_results):
        """
        Get results summary table for a given metric

        Parameters
        ----------
        metric : str
            Metric for which to get the summary table

        model_results : :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` containing the model results. It must have at
            least the following columns: ``"climate_model", "value"``.

        Returns
        -------
        :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` containing a summary of the results. The
            percentage difference is calculated as
            ``(model_value - assessed_value) / np.abs(assessed_value) * 100``.
        """
        model_results_metric_row = model_results[self.metric_column] == metric
        if not model_results_metric_row.any():
            raise KeyError("No model results for metric: {}".format(metric))

        model_results_metric = model_results.loc[model_results_metric_row, :]

        assessed_ranges_unit = self.get_col_for_metric(metric, "unit")
        model_results_metric_unit = model_results_metric["unit"].unique().tolist()
        if (
            len(model_results_metric_unit) > 1
            or model_results_metric_unit[0] != assessed_ranges_unit
        ):
            error_msg = "Units mismatch. Assessed range units: {}, model results unit(s): {}".format(
                assessed_ranges_unit, model_results_metric_unit
            )
            raise AssertionError(error_msg)

        summary_table = defaultdict(list)
        assessed_range_quantiles = {
            "very_likely__lower": 0.05,
            "likely__lower": 0.17,
            "central": 0.5,
            "likely__upper": 0.83,
            "very_likely__upper": 0.95,
        }
        for label, quantile in tqdman.tqdm(
            assessed_range_quantiles.items(), leave=False
        ):
            assessed_value = self.get_col_for_metric(metric, label)
            if np.isnan(assessed_value):
                continue

            for climate_model, df in model_results_metric.groupby("climate_model"):
                model_quantile = df["value"].quantile(quantile)

                summary_table["climate_model"].append(climate_model)
                summary_table["assessed_range_label"].append(label)
                summary_table["assessed_range_value"].append(assessed_value)
                summary_table["climate_model_value"].append(model_quantile)
                summary_table["percentage_difference"].append(
                    (model_quantile - assessed_value) / np.abs(assessed_value) * 100
                )

        summary_table = pd.DataFrame(summary_table)
        summary_table[self.metric_column] = metric
        summary_table["unit"] = assessed_ranges_unit

        return summary_table

    def plot_metric_and_results(self, metric, model_results, axes=None, palette=None):
        """
        Plot our parameterisation of the metric's distribution and the model results

        This produces a two-panel plot, the top panel has the distributions,
        the bottom panel has box and whisker plots (with the boxes and
        whiskers adjusted to match the IPCC calibrated likelihood language).

        Parameters
        ----------
        metric : str
            Metric to plot

        model_results : :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` with the model results. Should be of the form
            returned by :meth:`calculate_metric_from_results`.

        axes : (:obj:`matplotlib.axes.SubplotBase`, :obj:`matplotlib.axes.SubplotBase`)
            Axes on which to make the plots. Must be two-panels.

        palette : dict[str, str]
            Colours to use for the different climate models and assessed ranges

        Returns
        -------
        (:obj:`matplotlib.axes.SubplotBase`, :obj:`matplotlib.axes.SubplotBase`)
            Axes on which the plot was made

        Raises
        ------
        AssertionError
            ``axes`` doesn't have a length equal to two
        """
        if axes is None:
            axes = self._get_evaluation_axes()
        else:
            assert len(axes) == 2, "Must pass two axes, received {}".format(len(axes))

        return self._plot(
            metric, model_results, axs=axes, box_only=False, palette=palette
        )

    @staticmethod
    def _get_evaluation_axes():
        fig = plt.figure(figsize=(12, 7))
        gs = GridSpec(2, 1, width_ratios=[1], height_ratios=[3, 2])
        ax0 = fig.add_subplot(gs[0])
        ax1 = fig.add_subplot(gs[1], sharex=ax0)
        axes = [ax0, ax1]

        return axes

    def plot_metric_and_results_box_only(
        self, metric, model_results, ax=None, palette=None
    ):
        """
        Plot box and whisker plots of the metric's distribution and the model results

        The box and whisker plots have the boxes and whiskers adjusted to
        match the IPCC calibrated likelihood language).

        Parameters
        ----------
        metric : str
            Metric to plot

        model_results : :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` with the model results. Should be of the form
            returned by :meth:`calculate_metric_from_results`.

        axes : :obj:`matplotlib.axes.SubplotBase`
            Axis on which to make the plot

        palette : dict[str, str]
            Colours to use for the different climate models and assessed ranges

        Returns
        -------
        :obj:`matplotlib.axes.SubplotBase`
            Axes on which the plot was made
        """
        if ax is None:
            ax = plt.figure().add_subplot(111)

        return self._plot(metric, model_results, axs=ax, box_only=True, palette=palette)

    def _plot(self, metric, model_results, axs, box_only, palette=None):
        if palette is None:
            palette = CLIMATE_MODEL_PALETTE

        box_plot_df = self._get_box_plot_df(metric, model_results)
        unit = box_plot_df["unit"].unique().tolist()
        assert len(unit) == 1, unit
        unit = unit[0]

        if box_only:
            box_ax = axs
        else:
            box_ax = axs[1]

        box_plot_stats = self._get_box_whisker_stats_custom_quantiles(
            box_plot_df, metric, box_quantiles=(17, 83), whisker_quantiles=(5, 95)
        )
        box_ax.bxp(
            box_plot_stats, showfliers=False, vert=box_only,
        )

        xlim = box_ax.get_xlim()

        if box_only:
            box_ax.set_ylabel(unit)
            box_ax.set_title(metric)
            box_ax.grid(axis="y")
        else:
            box_ax.set_xlabel(unit)
            box_ax.set_title("")
            box_ax.grid(axis="x")

            pdf_ax = axs[0]
            sns.histplot(
                data=box_plot_df,
                x=metric,
                bins=50,
                stat="probability",
                common_norm=False,
                kde=True,
                hue="Source",
                palette=palette,
                ax=pdf_ax,
                legend=True,
            )

            pdf_ax.set_title(metric)
            pdf_ax.set_xlim(xlim)
            pdf_ax.set_xlabel("")

        plt.suptitle("")

        return axs

    def _get_box_plot_df(self, metric, model_results):
        model_results_metric = model_results.loc[
            model_results[self.metric_column] == metric, :
        ]
        res = model_results_metric.pivot_table(
            values="value",
            columns=self.metric_column,
            index=list(set(model_results.columns) - {"value", self.metric_column}),
        ).reset_index()

        res["Source"] = res["climate_model"]

        assessed_ranges = self.get_assessed_range_for_boxplot(metric)

        box_plot_df = pd.concat([assessed_ranges, res])[[metric, "Source", "unit"]]

        unit = box_plot_df["unit"].unique().tolist()
        if len(unit) != 1:
            raise AssertionError("Not a single unit, found: {}".format(unit))

        return box_plot_df

    def _get_box_whisker_stats_custom_quantiles(
        self, model_df, metric, box_quantiles=(17, 83), whisker_quantiles=(5, 95)
    ):
        """
        Note that using box_quantiles or whisker_quantiles other than the default
        would imply changing the IPCC likelihood language. As a result, we do not
        currently expose these keyword arguments via any "public" APIs.
        """
        self._check_box_quantiles(box_quantiles, "box")
        self._check_box_quantiles(whisker_quantiles, "whisker")

        assessment = self._get_assessed_range_values_for_metric(metric)

        stats = {}
        for source, df in model_df.groupby("Source"):
            data = df[metric].values.squeeze()

            stats[source] = cbook.boxplot_stats(data, labels=[source])[0]

            if source == self.assessed_range_label:
                _assessment = assessment
            else:
                # Make a dictionary with all nan so all calculations are triggered.
                # This is slightly more expensive but ensures consistency.
                _assessment = {k: np.nan for k in assessment.keys()}

            stats[source] = self._fill_for_matplotlib_based_on_assessment(
                stats[source],
                assessed_vals=_assessment,
                assessed_keys=("central",),
                assessed_implied_quantiles=(50,),
                matplotlib_keys=("med",),
                values=data,
            )

            stats[source] = self._fill_for_matplotlib_based_on_assessment(
                stats[source],
                assessed_vals=_assessment,
                assessed_keys=("likely__lower", "likely__upper"),
                assessed_implied_quantiles=box_quantiles,
                matplotlib_keys=("q1", "q3"),
                values=data,
            )

            stats[source] = self._fill_for_matplotlib_based_on_assessment(
                stats[source],
                assessed_vals=_assessment,
                assessed_keys=("very_likely__lower", "very_likely__upper"),
                assessed_implied_quantiles=whisker_quantiles,
                matplotlib_keys=("whislo", "whishi"),
                values=data,
            )

        return list(stats.values())

    @staticmethod
    def _check_box_quantiles(quantiles, label_str):
        if quantiles[0] >= quantiles[1]:
            raise AssertionError(
                "{} quantiles must be ordered from lower to higher, input: {}".format(
                    label_str, quantiles
                )
            )

    @staticmethod
    def _fill_for_matplotlib_based_on_assessment(
        holder,
        assessed_vals,
        assessed_keys,
        assessed_implied_quantiles,
        matplotlib_keys,
        values,
    ):
        assessed_vals_of_interest = {
            k: v for k, v in assessed_vals.items() if k in assessed_keys
        }

        nan_assessed_values = np.isnan(list(assessed_vals_of_interest.values()))

        if not nan_assessed_values.any():
            for matplotlib_key, assessed_key in zip(matplotlib_keys, assessed_keys):
                holder[matplotlib_key] = assessed_vals[assessed_key]

        elif nan_assessed_values.all():
            for matplotlib_key, quantile in zip(
                matplotlib_keys, assessed_implied_quantiles
            ):
                holder[matplotlib_key] = np.percentile(values, quantile)

        else:  # pragma: no cover
            raise NotImplementedError(
                "One half of the assessed range is nan and the other is not? ({})".format(
                    assessed_vals
                )
            )

        return holder

    def calculate_metric_from_results(self, metric, res_calc, custom_calculators=None):
        """
        Calculate metric values from results

        Parameters
        ----------
        metric : str
            Metric for which to calculate results

        res_calc : :obj:`scmdata.ScmRun`
            Results to use for the calculation

        custom_calculators : tuple(:obj:`pyrcmip.metric_calculations.base.Calculator`)
            Custom calculators to use for calculating metrics which require a
            custom calculation

        Returns
        -------
        :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` containing the calculated metric values
            alongside other relevant metadata

        Raises
        ------
        ValueError
            Data required to calculate the metric is not available
        """
        filters = self.get_variables_regions_scenarios_for_metric(metric)
        res_calc = res_calc.filter(**filters, log_if_empty=False)
        if res_calc.empty:
            raise ValueError(
                "{} requires {} but it is not in the results".format(metric, filters)
            )

        eval_method = self.get_col_for_metric(metric, "RCMIP evaluation method")

        (norm_period, evaluation_period) = self.get_norm_period_evaluation_period(
            metric
        )
        self.check_norm_period_evaluation_period_against_data(
            norm_period, evaluation_period, res_calc
        )

        unit = self.get_col_for_metric(metric, "unit")

        if eval_method == "mean":
            res_calc_normed = self._get_normed_res_calc(res_calc, norm_period)
            res_calc_normed = res_calc_normed.convert_unit(unit)

            derived = _time_mean(res_calc_normed.filter(year=evaluation_period))

        elif eval_method == "regression-slope":
            res_calc_normed = self._get_normed_res_calc(res_calc, norm_period)

            derived = _regression_slope(
                res_calc_normed.filter(year=evaluation_period), unit
            )

        elif eval_method == "custom":
            if custom_calculators is None:
                custom_calculators = []

            calculator = [
                c for c in custom_calculators if c.can_calculate_metric(metric)
            ]
            if not calculator:
                raise ValueError("No custom calculator for {}".format(metric))

            if len(calculator) > 1:
                raise ValueError(
                    "More than one available calculator for metric {}, matched: {}".format(
                        metric, calculator
                    )
                )

            derived = calculator[0].calculate_metric(
                self, res_calc, norm_period, evaluation_period, unit
            )

        else:
            raise NotImplementedError(eval_method)

        derived = derived.to_frame().reset_index()
        derived[self.metric_column] = metric

        return derived

    @staticmethod
    def _get_normed_res_calc(res_calc, norm_period):
        if norm_period is not None:
            res_calc_normed = res_calc.relative_to_ref_period_mean(year=norm_period)
        else:
            res_calc_normed = res_calc.copy()

        return res_calc_normed

    def plot_against_results(
        self,
        results_database,
        climate_models=["*"],
        custom_calculators=None,
        palette=None,
    ):
        """
        Calculate metric values from results, compare and plot against assessed ranges

        Parameters
        ----------
        metric : str
            Metric for which to calculate results

        results_database : :obj:`pyrcmip.database.DataBase`
            Database from which to load results

        climate_models : list[str]
            Climate models to calculate results for

        custom_calculators : tuple(:obj:`pyrcmip.metric_calculations.base.Calculator`)
            Custom calculators to use for calculating metrics which require a
            custom calculation

        palette : dict[str, str]
            Colours to use for the different climate models and assessed
            ranges when plotting

        Returns
        -------
        :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` containing a dataframe based on concatenating
            the results from calling
            :meth:`get_results_summary_table_for_metric` for each metric.
        """
        summary_table = []
        for metric in tqdman.tqdm(self.db[self.metric_column].tolist()):
            eval_method = self.get_col_for_metric(metric, "RCMIP evaluation method")
            if isinstance(eval_method, float) and np.isnan(eval_method):
                warnings.warn("No evaluation method for {}".format(metric))
                continue

            var_region_scen = self.get_variables_regions_scenarios_for_metric(metric)
            variables = var_region_scen["variable"]
            regions = var_region_scen["region"]
            scenarios = var_region_scen["scenario"]

            try:
                # TODO: upgrade the database so we can specify the climate models to load too
                res_calc = run_append(
                    [
                        results_database.load_data(
                            climate_model=cm, variable=v, region=r, scenario=s
                        )
                        for cm in climate_models
                        for v in variables
                        for r in regions
                        for s in scenarios
                    ]
                ).time_mean("AC")
            except IndexError:
                print("No data for: {}".format(metric))
                continue

            # if we need better control, use a meta argument with this docstring:
            """
            meta : list[str]
                Meta columns to use when performing calculations (all other meta
                columns are dropped)
            """
            # and the code below
            """
            if meta is not None:
                meta_to_drop = set(res_calc.meta.columns) - set(meta)
                res_calc = res_calc.drop_meta(meta_to_drop, inplace=False)
            """

            derived = self.calculate_metric_from_results(
                metric, res_calc, custom_calculators=custom_calculators
            )

            summary_table_metric = self._plot_pdf_and_box_and_get_summary_table(
                metric, derived, palette=palette
            )

            summary_table.append(summary_table_metric)

        summary_table = pd.concat(summary_table).reset_index(drop=True)

        return summary_table

    def plot_model_reported_against_assessed_ranges(self, model_reported, palette=None):
        """
        Compare and plot model reported results against assessed ranges

        Parameters
        ----------
        model_reported : :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` of the same format as the result of
            :meth:`calculate_metric_from_results`

        palette : dict[str, str]
            Colours to use for the different climate models and assessed
            ranges when plotting

        Returns
        -------
        :obj:`pd.DataFrame`
            :obj:`pd.DataFrame` containing a dataframe based on concatenating
            the results from calling
            :meth:`get_results_summary_table_for_metric` for each metric
        """
        summary_table = []

        for label, df in model_reported.groupby(self.metric_column):
            summary_table_metric = self._plot_pdf_and_box_and_get_summary_table(
                label, df, palette=palette
            )

            summary_table.append(summary_table_metric)

        summary_table = pd.concat(summary_table).reset_index(drop=True)

        return summary_table

    def _plot_pdf_and_box_and_get_summary_table(
        self, metric, derived, show=True, palette=None
    ):
        axes = self._get_evaluation_axes()

        axes = self.plot_metric_and_results(metric, derived, axes=axes, palette=palette)
        plt.tight_layout()

        ax = plt.figure(figsize=(6, 4)).add_subplot(111)
        self.plot_metric_and_results_box_only(metric, derived, ax=ax, palette=palette)

        plt.tight_layout()
        if show:
            plt.show()

        summary_table_metric = self.get_results_summary_table_for_metric(
            metric, derived
        )

        return summary_table_metric
