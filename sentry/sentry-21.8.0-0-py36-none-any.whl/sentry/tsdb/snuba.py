import collections
import itertools
from copy import deepcopy

from sentry.constants import DataCategory
from sentry.ingest.inbound_filters import FILTER_STAT_KEYS_TO_VALUES
from sentry.tsdb.base import BaseTSDB, TSDBModel
from sentry.utils import outcomes, snuba
from sentry.utils.compat import map, zip
from sentry.utils.dates import to_datetime

SnubaModelQuerySettings = collections.namedtuple(
    # `dataset` - the dataset in Snuba that we want to query
    # `groupby` - the column in Snuba that we want to put in the group by statement
    # `aggregate` - the column in Snuba that we want to run the aggregate function on
    # `conditions` - any additional model specific conditions we want to pass in the query
    "SnubaModelSettings",
    ["dataset", "groupby", "aggregate", "conditions"],
)

# combine DEFAULT, ERROR, and SECURITY as errors. We are now recording outcome by
# category, and these TSDB models and where they're used assume only errors.
# see relay: py/sentry_relay/consts.py and relay-cabi/include/relay.h
OUTCOMES_CATEGORY_CONDITION = [
    "category",
    "IN",
    DataCategory.error_categories(),
]


class SnubaTSDB(BaseTSDB):
    """
    A time series query interface to Snuba

    Write methods are not supported, as the raw data from which we generate our
    time series is assumed to already exist in snuba.

    Read methods are supported only for models based on group/event data and
    will return empty results for unsupported models.
    """

    # Since transactions are currently (and temporarily) written to Snuba's events storage we need to
    # include this condition to ensure they are excluded from the query. Once we switch to the
    # errors storage in Snuba, this can be omitted and transactions will be excluded by default.
    events_type_condition = ["type", "!=", "transaction"]
    # ``non_outcomes_query_settings`` are all the query settings for for non outcomes based TSDB models.
    # Single tenant reads Snuba for these models, and writes to DummyTSDB. It reads and writes to Redis for all the
    # other models.
    non_outcomes_query_settings = {
        TSDBModel.project: SnubaModelQuerySettings(
            snuba.Dataset.Events, "project_id", None, [events_type_condition]
        ),
        TSDBModel.group: SnubaModelQuerySettings(
            snuba.Dataset.Events, "group_id", None, [events_type_condition]
        ),
        TSDBModel.release: SnubaModelQuerySettings(
            snuba.Dataset.Events, "tags[sentry:release]", None, [events_type_condition]
        ),
        TSDBModel.users_affected_by_group: SnubaModelQuerySettings(
            snuba.Dataset.Events, "group_id", "tags[sentry:user]", [events_type_condition]
        ),
        TSDBModel.users_affected_by_project: SnubaModelQuerySettings(
            snuba.Dataset.Events, "project_id", "tags[sentry:user]", [events_type_condition]
        ),
        TSDBModel.frequent_environments_by_group: SnubaModelQuerySettings(
            snuba.Dataset.Events, "group_id", "environment", [events_type_condition]
        ),
        TSDBModel.frequent_releases_by_group: SnubaModelQuerySettings(
            snuba.Dataset.Events, "group_id", "tags[sentry:release]", [events_type_condition]
        ),
        TSDBModel.frequent_issues_by_project: SnubaModelQuerySettings(
            snuba.Dataset.Events, "project_id", "group_id", [events_type_condition]
        ),
    }

    # ``project_filter_model_query_settings`` and ``outcomes_partial_query_settings`` are all the TSDB models for
    # outcomes
    project_filter_model_query_settings = {
        model: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "project_id",
            "times_seen",
            [["reason", "=", reason], OUTCOMES_CATEGORY_CONDITION],
        )
        for reason, model in FILTER_STAT_KEYS_TO_VALUES.items()
    }

    outcomes_partial_query_settings = {
        TSDBModel.organization_total_received: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "org_id",
            "times_seen",
            [["outcome", "!=", outcomes.Outcome.INVALID], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.organization_total_rejected: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "org_id",
            "times_seen",
            [["outcome", "=", outcomes.Outcome.RATE_LIMITED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.organization_total_blacklisted: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "org_id",
            "times_seen",
            [["outcome", "=", outcomes.Outcome.FILTERED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.project_total_received: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "project_id",
            "times_seen",
            [["outcome", "!=", outcomes.Outcome.INVALID], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.project_total_rejected: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "project_id",
            "times_seen",
            [["outcome", "=", outcomes.Outcome.RATE_LIMITED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.project_total_blacklisted: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "project_id",
            "times_seen",
            [["outcome", "=", outcomes.Outcome.FILTERED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.key_total_received: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "key_id",
            "times_seen",
            [["outcome", "!=", outcomes.Outcome.INVALID], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.key_total_rejected: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "key_id",
            "times_seen",
            [["outcome", "=", outcomes.Outcome.RATE_LIMITED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.key_total_blacklisted: SnubaModelQuerySettings(
            snuba.Dataset.Outcomes,
            "key_id",
            "times_seen",
            [["outcome", "=", outcomes.Outcome.FILTERED], OUTCOMES_CATEGORY_CONDITION],
        ),
    }

    # ``model_query_settings`` is a translation of TSDB models into required settings for querying snuba
    model_query_settings = dict(
        itertools.chain(
            project_filter_model_query_settings.items(),
            outcomes_partial_query_settings.items(),
            non_outcomes_query_settings.items(),
        )
    )

    project_filter_model_query_settings_lower_rollup = {
        model: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "project_id",
            None,
            [["reason", "=", reason], OUTCOMES_CATEGORY_CONDITION],
        )
        for reason, model in FILTER_STAT_KEYS_TO_VALUES.items()
    }

    # The Outcomes dataset aggregates outcomes into chunks of an hour. So, for rollups less than an hour, we want to
    # query the raw outcomes dataset, with a few different settings (defined in lower_rollup_query_settings).
    other_lower_rollup_query_settings = {
        TSDBModel.organization_total_received: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "org_id",
            None,
            [["outcome", "!=", outcomes.Outcome.INVALID], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.organization_total_rejected: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "org_id",
            None,
            [["outcome", "=", outcomes.Outcome.RATE_LIMITED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.organization_total_blacklisted: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "org_id",
            None,
            [["outcome", "=", outcomes.Outcome.FILTERED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.project_total_received: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "project_id",
            None,
            [["outcome", "!=", outcomes.Outcome.INVALID], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.project_total_rejected: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "project_id",
            None,
            [["outcome", "=", outcomes.Outcome.RATE_LIMITED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.project_total_blacklisted: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "project_id",
            None,
            [["outcome", "=", outcomes.Outcome.FILTERED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.key_total_received: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "key_id",
            None,
            [["outcome", "!=", outcomes.Outcome.INVALID], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.key_total_rejected: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "key_id",
            None,
            [["outcome", "=", outcomes.Outcome.RATE_LIMITED], OUTCOMES_CATEGORY_CONDITION],
        ),
        TSDBModel.key_total_blacklisted: SnubaModelQuerySettings(
            snuba.Dataset.OutcomesRaw,
            "key_id",
            None,
            [["outcome", "=", outcomes.Outcome.FILTERED], OUTCOMES_CATEGORY_CONDITION],
        ),
    }

    lower_rollup_query_settings = dict(
        itertools.chain(
            project_filter_model_query_settings_lower_rollup.items(),
            other_lower_rollup_query_settings.items(),
        )
    )

    def __init__(self, **options):
        super().__init__(**options)

    def get_data(
        self,
        model,
        keys,
        start,
        end,
        rollup=None,
        environment_ids=None,
        aggregation="count()",
        group_on_model=True,
        group_on_time=False,
        conditions=None,
        use_cache=False,
    ):
        """
        Normalizes all the TSDB parameters and sends a query to snuba.

        `group_on_time`: whether to add a GROUP BY clause on the 'time' field.
        `group_on_model`: whether to add a GROUP BY clause on the primary model.
        """
        # XXX: to counteract the hack in project_key_stats.py
        if model in [
            TSDBModel.key_total_received,
            TSDBModel.key_total_blacklisted,
            TSDBModel.key_total_rejected,
        ]:
            keys = list(set(map(lambda x: int(x), keys)))

        # 10s is the only rollup under an hour that we support
        if rollup and rollup == 10 and model in self.lower_rollup_query_settings:
            model_query_settings = self.lower_rollup_query_settings.get(model)
        else:
            model_query_settings = self.model_query_settings.get(model)

        if model_query_settings is None:
            raise Exception(f"Unsupported TSDBModel: {model.name}")

        model_group = model_query_settings.groupby
        model_aggregate = model_query_settings.aggregate

        groupby = []
        if group_on_model and model_group is not None:
            groupby.append(model_group)
        if group_on_time:
            groupby.append("time")
        if aggregation == "count()" and model_aggregate is not None:
            # Special case, because count has different semantics, we change:
            # `COUNT(model_aggregate)` to `COUNT() GROUP BY model_aggregate`
            groupby.append(model_aggregate)
            model_aggregate = None

        columns = (model_query_settings.groupby, model_query_settings.aggregate)
        keys_map = dict(zip(columns, self.flatten_keys(keys)))
        keys_map = {k: v for k, v in keys_map.items() if k is not None and v is not None}
        if environment_ids is not None:
            keys_map["environment"] = environment_ids

        aggregations = [[aggregation, model_aggregate, "aggregate"]]

        # For historical compatibility with bucket-counted TSDB implementations
        # we grab the original bucketed series and add the rollup time to the
        # timestamp of the last bucket to get the end time.
        rollup, series = self.get_optimal_rollup_series(start, end, rollup)
        start = to_datetime(series[0])
        end = to_datetime(series[-1] + rollup)
        limit = min(10000, int(len(keys) * ((end - start).total_seconds() / rollup)))

        conditions = conditions if conditions is not None else []
        if model_query_settings.conditions is not None:
            conditions += deepcopy(model_query_settings.conditions)
            # copy because we modify the conditions in snuba.query

        orderby = []
        if group_on_time:
            orderby.append("-time")

        if group_on_model and model_group is not None:
            orderby.append(model_group)

        if keys:
            result = snuba.query(
                dataset=model_query_settings.dataset,
                start=start,
                end=end,
                groupby=groupby,
                conditions=conditions,
                filter_keys=keys_map,
                aggregations=aggregations,
                rollup=rollup,
                limit=limit,
                orderby=orderby,
                referrer=f"tsdb-modelid:{model.value}",
                is_grouprelease=(model == TSDBModel.frequent_releases_by_group),
                use_cache=use_cache,
            )
        else:
            result = {}

        if group_on_time:
            keys_map["time"] = series

        self.zerofill(result, groupby, keys_map)
        self.trim(result, groupby, keys)

        return result

    def zerofill(self, result, groups, flat_keys):
        """
        Fills in missing keys in the nested result with zeroes.
        `result` is the nested result
        `groups` is the order in which the result is nested, eg: ['project', 'time']
        `flat_keys` is a map from groups to lists of required keys for that group.
                    eg: {'project': [1,2]}
        """
        if len(groups) > 0:
            group, subgroups = groups[0], groups[1:]
            # Zerofill missing keys
            for k in flat_keys[group]:
                if k not in result:
                    result[k] = 0 if len(groups) == 1 else {}

            if subgroups:
                for v in result.values():
                    self.zerofill(v, subgroups, flat_keys)

    def trim(self, result, groups, keys):
        """
        Similar to zerofill, but removes keys that should not exist.
        Uses the non-flattened version of keys, so that different sets
        of keys can exist in different branches at the same nesting level.
        """
        if len(groups) > 0:
            group, subgroups = groups[0], groups[1:]
            if isinstance(result, dict):
                for rk in list(result.keys()):
                    if group == "time":  # Skip over time group
                        self.trim(result[rk], subgroups, keys)
                    elif rk in keys:
                        if isinstance(keys, dict):
                            self.trim(result[rk], subgroups, keys[rk])
                    else:
                        del result[rk]

    def get_range(
        self,
        model,
        keys,
        start,
        end,
        rollup=None,
        environment_ids=None,
        conditions=None,
        use_cache=False,
    ):
        # 10s is the only rollup under an hour that we support
        if rollup and rollup == 10 and model in self.lower_rollup_query_settings:
            model_query_settings = self.lower_rollup_query_settings.get(model)
        else:
            model_query_settings = self.model_query_settings.get(model)

        assert model_query_settings is not None, f"Unsupported TSDBModel: {model.name}"

        if model_query_settings.dataset == snuba.Dataset.Outcomes:
            aggregate_function = "sum"
        else:
            aggregate_function = "count()"

        result = self.get_data(
            model,
            keys,
            start,
            end,
            rollup,
            environment_ids,
            aggregation=aggregate_function,
            group_on_time=True,
            conditions=conditions,
            use_cache=use_cache,
        )
        # convert
        #    {group:{timestamp:count, ...}}
        # into
        #    {group: [(timestamp, count), ...]}
        return {k: sorted(result[k].items()) for k in result}

    def get_distinct_counts_series(
        self, model, keys, start, end=None, rollup=None, environment_id=None
    ):
        result = self.get_data(
            model,
            keys,
            start,
            end,
            rollup,
            [environment_id] if environment_id is not None else None,
            aggregation="uniq",
            group_on_time=True,
        )
        # convert
        #    {group:{timestamp:count, ...}}
        # into
        #    {group: [(timestamp, count), ...]}
        return {k: sorted(result[k].items()) for k in result}

    def get_distinct_counts_totals(
        self, model, keys, start, end=None, rollup=None, environment_id=None, use_cache=False
    ):
        return self.get_data(
            model,
            keys,
            start,
            end,
            rollup,
            [environment_id] if environment_id is not None else None,
            aggregation="uniq",
            use_cache=use_cache,
        )

    def get_distinct_counts_union(
        self, model, keys, start, end=None, rollup=None, environment_id=None
    ):
        return self.get_data(
            model,
            keys,
            start,
            end,
            rollup,
            [environment_id] if environment_id is not None else None,
            aggregation="uniq",
            group_on_model=False,
        )

    def get_most_frequent(
        self, model, keys, start, end=None, rollup=None, limit=10, environment_id=None
    ):
        aggregation = f"topK({limit})"
        result = self.get_data(
            model,
            keys,
            start,
            end,
            rollup,
            [environment_id] if environment_id is not None else None,
            aggregation=aggregation,
        )
        # convert
        #    {group:[top1, ...]}
        # into
        #    {group: [(top1, score), ...]}
        for k, top in result.items():
            item_scores = [(v, float(i + 1)) for i, v in enumerate(reversed(top or []))]
            result[k] = list(reversed(item_scores))

        return result

    def get_most_frequent_series(
        self, model, keys, start, end=None, rollup=None, limit=10, environment_id=None
    ):
        aggregation = f"topK({limit})"
        result = self.get_data(
            model,
            keys,
            start,
            end,
            rollup,
            [environment_id] if environment_id is not None else None,
            aggregation=aggregation,
            group_on_time=True,
        )
        # convert
        #    {group:{timestamp:[top1, ...]}}
        # into
        #    {group: [(timestamp, {top1: score, ...}), ...]}
        return {
            k: sorted(
                (timestamp, {v: float(i + 1) for i, v in enumerate(reversed(topk or []))})
                for (timestamp, topk) in result[k].items()
            )
            for k in result.keys()
        }

    def get_frequency_series(self, model, items, start, end=None, rollup=None, environment_id=None):
        result = self.get_data(
            model,
            items,
            start,
            end,
            rollup,
            [environment_id] if environment_id is not None else None,
            aggregation="count()",
            group_on_time=True,
        )
        # convert
        #    {group:{timestamp:{agg:count}}}
        # into
        #    {group: [(timestamp, {agg: count, ...}), ...]}
        return {k: sorted(result[k].items()) for k in result}

    def get_frequency_totals(self, model, items, start, end=None, rollup=None, environment_id=None):
        return self.get_data(
            model,
            items,
            start,
            end,
            rollup,
            [environment_id] if environment_id is not None else None,
            aggregation="count()",
        )

    def flatten_keys(self, items):
        """
        Returns a normalized set of keys based on the various formats accepted
        by TSDB methods. The input is either just a plain list of keys for the
        top level or a `{level1_key: [level2_key, ...]}` dictionary->list map.
        The output is a 2-tuple of ([level_1_keys], [all_level_2_keys])
        """
        if isinstance(items, collections.Mapping):
            return (
                list(items.keys()),
                list(set.union(*(set(v) for v in items.values())) if items else []),
            )
        elif isinstance(items, (collections.Sequence, collections.Set)):
            return (items, None)
        else:
            raise ValueError("Unsupported type: %s" % (type(items)))
