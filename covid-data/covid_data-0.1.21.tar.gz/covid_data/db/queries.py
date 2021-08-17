from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from psycopg2 import sql
from psycopg2._psycopg import connection  # pylint: disable=no-name-in-module
from psycopg2._psycopg import cursor  # pylint: disable=no-name-in-module

from covid_data.types import (
    Aggregations,
    CaseType,
    OnConflictStrategy,
    OrderBy,
    PlaceProperty,
    PlaceTable,
    PlaceType,
)


def place_exists(
    place: str, engine: connection, table: PlaceTable = PlaceTable.COUNTRY
) -> Union[str, None]:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL("SELECT id FROM {0} WHERE name=%s").format(
                sql.Identifier(table.value)
            ),
            (place,),
        )

        result: dict = cur.fetchone() or {}  # type: ignore

        return result.get("id", None)


def get_place_by_property(
    value: str, property: PlaceProperty, engine: connection, place_type: PlaceType
) -> Optional[dict]:
    from_table = None

    if place_type == PlaceType.COUNTRY:
        from_table = "countries"
    elif place_type == PlaceType.PROVINCE:
        from_table = "provinces"
    elif place_type == PlaceType.COUNTY:
        from_table = "counties"
    else:
        raise ValueError(f"Place type {place_type} not supported")

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL("SELECT * FROM {0} WHERE {1}=%s").format(
                sql.Identifier(from_table), sql.Identifier(property.value)
            ),
            (value,),
        )

        res: dict = cur.fetchone()  # type: ignore

        return res


def get_countries_id_by_alpha2(
    alpha2_codes: List[str], engine: connection
) -> List[int]:
    with engine.cursor() as cur:
        cur: cursor

        query = sql.SQL("SELECT id FROM countries WHERE alpha2 IN %s")

        cur.execute(query, (tuple(alpha2_codes),))

        return [int(t["id"]) for t in cur.fetchall()]  # type: ignore


def get_country_by_alpha2(country: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        country, PlaceProperty.ALPHA_2_CODE, engine, PlaceType.COUNTRY
    )


def get_country_by_alpha3(country: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        country, PlaceProperty.ALPHA_3_CODE, engine, PlaceType.COUNTRY
    )


def get_province_by_alpha2(province: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        province, PlaceProperty.ALPHA_2_CODE, engine, PlaceType.PROVINCE
    )


def get_county_by_alpha2(county: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        county, PlaceProperty.ALPHA_2_CODE, engine, PlaceType.COUNTY
    )


def get_country_by_id(country_id: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        country_id, PlaceProperty.ID, engine, PlaceType.COUNTRY
    )


def get_province_by_id(province_id: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        province_id, PlaceProperty.ID, engine, PlaceType.PROVINCE
    )


def get_province_by_name(province: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(
        province, PlaceProperty.NAME, engine, PlaceType.PROVINCE
    )


def get_county_by_id(county_id: str, engine: connection) -> Optional[dict]:
    return get_place_by_property(county_id, PlaceProperty.ID, engine, PlaceType.COUNTY)


def create_country(country: dict, engine: connection) -> str:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            (
                "INSERT INTO countries "
                "VALUES ("
                "DEFAULT, "
                "%(name)s, "
                "%(alpha2)s, "
                "%(alpha3)s, "
                "ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326), "
                "NULL"
                ") "
                "RETURNING id"
            ),
            country,
        )

        result: dict = cur.fetchone()  # type: ignore

        engine.commit()

        return result["id"]


def create_province(province: dict, engine: connection) -> str:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            (
                "INSERT INTO provinces VALUES ("
                "DEFAULT, "
                "%(name)s, "
                "ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326), "
                "NULL, "
                "%(code)s, "
                "%(country_id)s"
                ") RETURNING id"
            ),
            province,
        )

        result: dict = cur.fetchone()  # type: ignore

        engine.commit()

        return result["id"]


def create_county(county: dict, engine: connection) -> str:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            (
                "INSERT INTO provinces VALUES ("
                "DEFAULT, "
                "%(name)s, "
                "ST_SetSRID(ST_MakePoint(%(lng)s, %(lat)s), 4326), "
                "NULL, "
                "%(code)s, "
                "%(province_id)s"
                ") RETURNING id"
            ),
            county,
        )

        result: dict = cur.fetchone()  # type: ignore

        engine.commit()

        return result["id"]


def get_cases_by_country(
    country_id: int, engine: connection, case_type: CaseType = None
) -> List[Dict]:
    return get_cases_by_filters(engine, countries_id=[country_id], case_type=case_type)


def get_cases_by_province(
    provinces_id: List[int], engine: connection, case_type: CaseType = None
) -> List[Dict]:
    return get_cases_by_filters(engine, provinces_id=provinces_id, case_type=case_type)


def get_cases_by_filters_query(
    countries_id: List[int] = None,
    provinces_id: List[int] = None,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    aggregation: List[Aggregations] = [],
    limit: int = None,
    sort: List[str] = [],
) -> Dict[str, Any]:
    params = []
    constraints = []

    select = sql.SQL("SELECT ")

    if len(aggregation):
        select += sql.SQL("sum(c.amount) as amount")
        if Aggregations.DATE in aggregation:
            select += sql.SQL(", c.date")
        if Aggregations.COUNTRY in aggregation:
            select += sql.SQL(", co.name as country")
        if Aggregations.TYPE in aggregation:
            select += sql.SQL(", c.type")
        if Aggregations.PROVINCE in aggregation:
            select += sql.SQL(", p.name as province")
        if Aggregations.PROVINCE_CODE in aggregation:
            select += sql.SQL(", p.code as province_code")
    else:
        select += sql.SQL("c.amount, type, c.date")

    from_ = sql.SQL("FROM cases c")

    query = sql.SQL("")

    if Aggregations.COUNTRY in aggregation:
        query += sql.SQL("INNER JOIN countries co ON c.country_id = co.id ")

    if (
        Aggregations.PROVINCE in aggregation
        or Aggregations.PROVINCE_CODE in aggregation
    ):
        query += sql.SQL("INNER JOIN provinces p ON c.province_id = p.id ")

    if countries_id:
        constraints.append(sql.SQL("c.country_id IN %s"))
        params.append(tuple(countries_id))

    if provinces_id:
        constraints.append(sql.SQL("c.province_id IN %s"))
        params.append(tuple(provinces_id))

    if date:
        constraints.append(sql.SQL("c.date=%s"))
        params.append(date)

    if date_lte:
        constraints.append(sql.SQL("c.date<=%s"))
        params.append(date_lte)

    if date_gte:
        constraints.append(sql.SQL("c.date>=%s"))
        params.append(date_gte)

    if case_type:
        constraints.append(sql.SQL("c.type=%s"))
        params.append(case_type.value)

    constraints.append(sql.SQL("amount > 0"))

    query += sql.SQL(" WHERE ") + sql.SQL(" AND ").join(constraints)

    if len(aggregation):
        query += sql.SQL(" GROUP BY ")

        query += sql.SQL(", ").join(
            sql.SQL("{}").format(sql.Identifier(agg.value)) for agg in aggregation
        )

    if len(sort):
        query += sql.SQL(" ORDER BY")
        for field in sort:
            order = OrderBy.ASC

            if field.startswith("-"):
                order = OrderBy.DESC
                field = field[1:]

            query += sql.SQL(" {} " + f"{order.value}").format(sql.Identifier(field))

    if limit:
        query += sql.SQL(" LIMIT %s")
        params.append(limit)

    return {
        "select": select,
        "from": from_,
        "query": query,
        "params": tuple(params),
    }


def get_cases_by_filters(
    engine: connection,
    countries_id: List[int] = None,
    provinces_id: List[int] = None,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    aggregation: List[Aggregations] = [],
    limit: int = None,
    sort: list = [],
) -> List[Dict]:
    with engine.cursor() as cur:
        cur: cursor

        query = get_cases_by_filters_query(
            countries_id,
            provinces_id,
            date,
            date_lte,
            date_gte,
            case_type,
            aggregation,
            limit,
            sort,
        )

        params = query.pop("params")

        final_query = sql.SQL(" ").join([query[k] for k in query.keys()])
        cur.execute(final_query, params)

        return cur.fetchall()  # type: ignore


def get_cum_cases_by_date(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    countries: List[int] = None,
) -> List[Dict]:
    params = []

    inner_query = sql.SQL(
        (
            "SELECT c.type as type, sum(c.amount) as amount, "
            "c.date as date "
            "FROM cases c"
        )
    )

    constraints = []

    if date:
        constraints.append(sql.SQL("date=%s"))
        params.append(date)
    elif date_gte or date_lte:
        if date_gte:
            constraints.append(sql.SQL("date>=%s"))
            params.append(date_gte)

        if date_lte:
            constraints.append(sql.SQL("date<=%s"))
            params.append(date_lte)

    if countries:
        constraints.append(sql.SQL("c.country_id IN %s"))
        params.append(tuple(countries))

    if case_type:
        constraints.append(sql.SQL("type=%s"))
        params.append(case_type.value)

    constraints.append(sql.SQL("amount > 0"))

    inner_query += sql.SQL(" WHERE ") + sql.SQL(" AND ").join(constraints)

    inner_query += sql.SQL((" GROUP BY c.date, c.type"))

    outter_query = (
        sql.SQL(
            (
                "SELECT "
                "type, "
                "sum(amount) OVER (PARTITION BY type ORDER BY date ASC) as amount, "
                "date FROM ( "
            )
        )
        + inner_query
        + sql.SQL((") as _ ORDER BY date ASC"))
    )

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(outter_query, tuple(params))

        return cur.fetchall()  # type: ignore


def get_cum_cases_by_date_country(
    engine: connection,
    country_id: int,
    provinces_id: List[int] = [],
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
) -> List[Dict]:
    params: List[Any] = [country_id]

    inner_query = sql.SQL(
        (
            "SELECT c.type as type, sum(c.amount) as amount, "
            "c.date as date "
            "FROM cases c "
            "WHERE c.country_id=%s "
        )
    )

    constraints = []

    if date:
        constraints.append(sql.SQL("date=%s"))
        params.append(date)
    elif date_gte or date_lte:
        if date_gte:
            constraints.append(sql.SQL("date>=%s"))
            params.append(date_gte)

        if date_lte:
            constraints.append(sql.SQL("date<=%s"))
            params.append(date_lte)

    if case_type:
        constraints.append(sql.SQL("type=%s"))
        params.append(case_type.value)

    if len(provinces_id):
        constraints.append(sql.SQL("province_id IN %s"))
        params.append(tuple(provinces_id))

    constraints.append(sql.SQL("amount > 0"))

    inner_query += sql.SQL("AND ") + sql.SQL(" AND ").join(constraints)

    inner_query += sql.SQL((" GROUP BY c.date, c.type"))

    outter_query = (
        sql.SQL(
            (
                "SELECT "
                "type, "
                "sum(amount) OVER (PARTITION BY type ORDER BY date ASC) as amount, "
                "date FROM ( "
            )
        )
        + inner_query
        + sql.SQL((") as _ ORDER BY date ASC"))
    )

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(outter_query, tuple(params))

        return cur.fetchall()  # type: ignore


def get_cum_cases_by_country(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    countries_id: List[int] = [],
    limit: int = None,
) -> List[Dict]:
    params = []

    query = sql.SQL(
        (
            "SELECT co.name as country, sum(c.amount) as amount "
            "FROM cases c INNER JOIN countries co ON c.country_id = co.id "
        )
    )

    constraints = []

    if date:
        constraints.append(sql.SQL("date=%s"))
        params.append(date)
    elif date_gte or date_lte:
        if date_gte:
            constraints.append(sql.SQL("date>=%s"))
            params.append(date_gte)

        if date_lte:
            constraints.append(sql.SQL("date<=%s"))
            params.append(date_lte)

    if case_type:
        constraints.append(sql.SQL("type=%s"))
        params.append(case_type.value)

    if len(countries_id):
        constraints.append(sql.SQL("c.country_id IN %s"))
        params.append(tuple(countries_id))

    constraints.append(sql.SQL("amount > 0"))

    query += sql.SQL(" WHERE ") + sql.SQL(" AND ").join(constraints)

    query += sql.SQL("GROUP BY co.name ORDER BY amount DESC")

    if limit:
        query += sql.SQL(" LIMIT %s")
        params.append(limit)

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(query, tuple(params))

        return cur.fetchall()  # type: ignore


def get_cum_cases_by_province(
    engine: connection,
    date: datetime = None,
    date_lte: datetime = None,
    date_gte: datetime = None,
    case_type: CaseType = None,
    country_id: int = None,
    provinces_id: List[str] = None,
) -> List[Dict]:
    params: List[Any] = [country_id]

    query = sql.SQL(
        (
            "SELECT sum(c.amount) as amount, p.name as province "
            "FROM cases c INNER JOIN provinces p ON c.province_id = p.id "
            "WHERE c.country_id=%s "
        )
    )

    constraints = []

    if date:
        constraints.append(sql.SQL("date=%s"))
        params.append(date)
    elif date_gte or date_lte:
        if date_gte:
            constraints.append(sql.SQL("date>=%s"))
            params.append(date_gte)

        if date_lte:
            constraints.append(sql.SQL("date<=%s"))
            params.append(date_lte)

    if case_type:
        constraints.append(sql.SQL("type=%s"))
        params.append(case_type.value)

    constraints.append(sql.SQL("amount > 0"))

    if provinces_id:
        constraints.append(sql.SQL("c.province_id IN %s"))
        params.append(tuple(provinces_id))

    query += sql.SQL("AND ") + sql.SQL(" AND ").join(constraints)

    query += sql.SQL((" GROUP BY province ORDER BY amount DESC"))

    with engine.cursor() as cur:
        cur: cursor

        cur.execute(query, tuple(params))

        return cur.fetchall()  # type: ignore


def create_case(
    case: dict,
    engine: connection,
    conflict_strategy: OnConflictStrategy = OnConflictStrategy.REPLACE,
) -> bool:
    with engine.cursor() as cur:
        cur: cursor

        query = (
            "INSERT INTO cases VALUES (DEFAULT, %(type)s, %(amount)s, %(date)s, %(country_id)s, "
            "%(province_id)s, %(county_id)s) "
            "ON CONFLICT ("
            "type, "
            "date, "
            "country_id, "
            "COALESCE(province_id, -1), COALESCE(county_id, -1)"
            ") DO UPDATE SET "
        )

        if conflict_strategy is OnConflictStrategy.ADD:
            query += "amount=cases.amount + %(amount)s"
        else:
            query += "amount=%(amount)s"

        cur.execute(query, case)

        engine.commit()

        return True


def get_all_countries(
    engine: connection, name: str = None, near: List[float] = []
) -> List[dict]:
    with engine.cursor() as cur:
        cur: cursor

        params = []

        query = sql.SQL("SELECT * FROM countries")

        if name:
            query += sql.SQL(" WHERE name=%s")
            params.append(name)

        if len(near):
            query += sql.SQL(
                " ORDER BY location <-> ST_SetSRID(ST_MakePoint(%s,%s), 4326)"
            )
            params.append(near[1])
            params.append(near[0])

        cur.execute(query, params)

        return cur.fetchall()  # type: ignore


def get_all_provinces(engine: connection) -> List[dict]:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL(
                (
                    "SELECT p.name as province, "
                    "p.id as province_id, "
                    "p.code as province_code, "
                    "c.name as country, "
                    "c.id as country_id "
                    "FROM provinces p INNER JOIN countries c ON p.country_id = c.id"
                )
            )
        )

        return cur.fetchall()  # type: ignore


def get_provinces_by_country(engine: connection, country_id: int) -> List[dict]:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL(
                (
                    "SELECT p.name as province, "
                    "p.id as province_id, "
                    "p.code as province_code, "
                    "c.name as country, "
                    "c.id as country_id "
                    "FROM provinces p INNER JOIN countries c ON p.country_id = c.id "
                    "WHERE p.country_id=%s"
                )
            ),
            (country_id,),
        )

        return cur.fetchall()  # type: ignore


def insert_api_key(engine: connection, hashed_key: str) -> bool:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL("INSERT INTO api_keys VALUES (DEFAULT, %s)"),
            (hashed_key,),
        )

        engine.commit()

        return True


def check_api_key(engine: connection, hashed_key: str) -> bool:
    with engine.cursor() as cur:
        cur: cursor

        cur.execute(
            sql.SQL("SELECT COUNT(*) FROM api_keys WHERE api_key=%s"),
            (hashed_key,),
        )

        res = int(cur.fetchone()[0])

        return res > 0
