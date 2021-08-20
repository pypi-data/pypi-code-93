import hashlib
import numpy as np
import random

from pandas import DataFrame, concat, to_datetime
from sqlalchemy import Column, func, text, literal
from stakenix import MySQL, PostgreDB, MongoDB
from stakenix.utils.common import merger


def get_traffic_source(df: DataFrame, user_id_column: str = "player_id") -> DataFrame:
    ph = hashlib.md5(b"project").hexdigest()
    projects = [
        "mk5",
        "mk1",
        "mk2",
        "mk3",
        "vipclub",
        "vipclub2",
        "vipclub",
        "lara",
        "vipt",
        "pobeda",
    ]
    regexp = "p[a-z0-9]+p[a-z0-9]+p[a-z0-9]{4}"
    players = concat(
        [
            MySQL(project)
            .query(
                columns=[
                    Column("player_id"),
                    func.regexp_substr(Column("partner_code"), regexp).label(
                        "ref_code"
                    ),
                    Column("partner_subid"),
                ],
                table="players",
                where=Column("player_id").in_(df[user_id_column].unique()),
            )
            .assign(project=project)
            for project in projects
        ]
    )
    unique_projects = players.project.unique()
    campaings = concat(
        [
            MySQL(project).query(
                table="campaigns",
                columns=[
                    Column("id"),
                    Column("name").label("promo_name"),
                    Column("cost_type_label"),
                ],
            )
            for project in projects
        ]
    )

    lp_users = concat(
        [
            MySQL(project)
            .query(table="lp_users", columns=[text("*"), literal(project).label(ph)])
            .rename({"id": "user_id", "login": "Account"}, axis=1)
            for project in projects
        ]
    )
    partners = PostgreDB("customdata").query(
        table="partner_accounts", columns=[text("*")]
    )
    ref_codes = concat(
        [
            MySQL(project).query(
                columns=[
                    func.regexp_substr(Column("ref_code"), regexp).label("ref_code"),
                    Column("campaign_id"),
                    Column("user_id"),
                ],
                table="ref_codes",
            )
            for project in projects
        ]
    )

    merged = merger(
        (df,),
        (players, {"left_on": user_id_column, "right_on": "player_id"}),
        (ref_codes.drop_duplicates(), {"on": "ref_code", "how": "left"}),
        (
            campaings.drop_duplicates(),
            {"left_on": "campaign_id", "right_on": "id", "how": "left"},
        ),
        (lp_users.drop_duplicates(), {"on": "user_id", "how": "left"}),
        (partners.drop_duplicates(), {"on": "Account", "how": "left"}),
    )
    duplicates = merged[merged[user_id_column].duplicated(keep=False)].loc[
        (~merged["ref_code"].isna())
    ]
    to_filter = duplicates.loc[~duplicates[ph].isin(unique_projects)]
    to_filter = to_filter.loc[
        ~(~(to_filter["ref_code"].isna()) & to_filter["Account"].isna())
    ]
    return _set_provider(merged[~merged.index.isin(to_filter.index)]).drop(
        columns=[ph, user_id_column] if user_id_column != "player_id" else [ph]
    )


def _set_provider(df):
    df, col = df.copy(), "source"
    df[col] = df["Provider"].fillna("undefined")
    prv, acc, ref = (df[i] for i in (col, "Account", "ref_code"))
    df[col] = np.where(ref.isnull(), "Direct", prv)
    df[col] = np.where(
        (prv == "undefined") & (acc.isnull() == False), "Partnerka", df[col]
    )
    df[col] = np.where(
        (df[col] == "undefined") & (acc.isnull() == True), "UndefRef", df[col]
    )
    df[col] = np.where(df[col].isin(["Experiments", "Inhouse"]), "Inhouse", df[col])
    df["Provider"] = df["Provider"].fillna(df[col])
    return df


def get_rates(
    df,
    dates_field="date",
    currencies_field="currency",
    values_fields=None,
    via_ssh=True,
):

    if df.empty:
        return DataFrame()
    try:
        unique_dates = df[~df[dates_field].isna()][dates_field].dt.date.unique()
    except AttributeError:
        dates = df[~df[dates_field].isna()]
        dates[dates_field] = to_datetime(dates[dates_field])
        unique_dates = dates[dates_field].dt.date.unique()
    currencies = df[currencies_field].unique()
    projects = ["pobeda", "lara", "mk5", "vipclub"]
    rates = MongoDB(random.choice(projects), via_ssh=via_ssh).query(
        table="currency_rates_history",
    )
    columns = [f"rates_{currency}" for currency in currencies]
    rates = rates[rates["date"].isin(unique_dates)]
    rates = (
        rates.set_index("date")
        .loc[:, columns]
        .stack()
        .reset_index()
        .rename(columns={0: "rate", "date": "rates_date"})
    )
    rates["currency"] = rates["level_1"].str.split("_", expand=True).loc[:, 1]
    rates = rates.drop("level_1", axis=1)
    df["merge_date"] = to_datetime(df[dates_field].dt.date)
    merged_rates = df.merge(
        rates,
        how="left",
        left_on=["merge_date", currencies_field],
        right_on=["rates_date", "currency"],
    ).drop(["merge_date", "rates_date"], axis=1)
    if values_fields is None:
        return merged_rates
    elif isinstance(values_fields, list):
        merged_rates[
            ["{column_name}_usd".format(column_name=column) for column in values_fields]
        ] = merged_rates.loc[:, values_fields].div(merged_rates["rate"], axis=0)
        return merged_rates
    else:
        return merged_rates.assign(usd_sum=lambda x: x[values_fields] / x["rate"])
