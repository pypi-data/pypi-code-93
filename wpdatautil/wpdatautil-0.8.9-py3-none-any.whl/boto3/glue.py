"""boto3 glue client utilities."""
import json
import logging
import time
import timeit
from typing import Any, Dict, List, Optional

import boto3
import s3path

from wpdatautil.pathlib import path_to_uri

log = logging.getLogger(__name__)

# Ref: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/glue.html


def create_database(**kwargs: Any) -> None:
    """Safely create the specified AWS Glue database.

    At minimum the `Name` keyword argument is required.

    :param kwargs: These are forwarded to `create_database` as its `CatalogId` and `DatabaseInput` parameters.
    """
    name = kwargs["Name"]
    call_kwargs = {"DatabaseInput": {k: v for k, v in kwargs.items() if k != "CatalogId"}}
    assert call_kwargs
    if catalog_id := kwargs.get("CatalogId"):
        call_kwargs["CatalogId"] = catalog_id
    client = boto3.client("glue")

    try:
        response = client.create_database(**call_kwargs)
    except client.exceptions.AlreadyExistsException:
        log.info(f"AWS Glue has a database named {name}.")
    else:
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        log.info(f"Created AWS Glue database {name}.")


def delete_database(**kwargs: Any) -> None:
    """Safely delete the specified AWS Glue database.

    At minimum the `Name` keyword argument is required.

    :param kwargs: These are forwarded to `delete_database`.
    """
    name = kwargs["Name"]
    call_kwargs = kwargs.copy()
    if not call_kwargs.get("CatalogId"):
        call_kwargs.pop("CatalogId", None)  # Removes key if having None value.
    client = boto3.client("glue")

    try:
        response = client.delete_database(**call_kwargs)
    except client.exceptions.EntityNotFoundException:
        log.info(f"AWS Glue does not have a database named {name}.")
    else:
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
        log.info(f"Deleted AWS Glue database {name}.")


def ensure_and_run_crawler(**kwargs: Any) -> List[dict]:
    """Return the list of database tables after ensuring and running the specified AWS Glue crawler with the given configuration.

    :param kwargs: These are indirectly forwarded to `create_crawler`.
    """
    crawler_name = kwargs["Name"]
    ensure_crawler(**kwargs)
    run_crawler(crawler_name)

    db_name = kwargs.get("DatabaseName") or crawler_name
    tables = get_tables(DatabaseName=db_name)
    table_names = [t["Name"] for t in tables]
    log.info(f"After crawling {crawler_name}, {len(tables)} tables exist: {', '.join(table_names)}")
    return tables


def ensure_and_run_s3_tables_crawler(crawler: str, s3_path: s3path.S3Path, s3_exclusions: Optional[List[str]] = None, **kwargs: Any) -> List[dict]:
    """Return the list of database tables after ensuring and running the specified AWS Glue crawler to crawl the top-level tables in the given S3 path.

    :param s3_exclusions: These are forwarded for each S3 path.
    :param kwargs: These are indirectly forwarded to `create_crawler`.
    """
    # Ref: https://stackoverflow.com/a/67185483/
    assert all(k not in kwargs for k in ("Name", "Targets"))

    s3_crawl_extra_kwargs = {"Exclusions": s3_exclusions} if s3_exclusions else {}
    s3_crawl_targets: List[Dict[str, Any]] = [
        {"Path": path_to_uri(p), **s3_crawl_extra_kwargs} for p in s3_path.glob("*")
    ]  # For correct crawling, each table's path is independently included.
    assert s3_crawl_targets
    log.info(f"{len(s3_crawl_targets)} S3 paths are to be crawled, the first of which is {s3_crawl_targets[0]['Path']}.")

    tables = ensure_and_run_crawler(
        Name=crawler, Targets={"S3Targets": s3_crawl_targets}, Configuration=json.dumps({"Version": 1.0, "Grouping": {"TableGroupingPolicy": "CombineCompatibleSchemas"}}), **kwargs
    )
    return tables


def ensure_crawler(**kwargs: Any) -> None:
    """Ensure that the specified AWS Glue crawler exists with the given configuration.

    At minimum the `Name` and `Targets` keyword arguments are required. Various default arguments are used.

    :param kwargs: These are forwarded to `create_crawler`.
    """
    # Use defaults
    assert all(kwargs.get(k) for k in ("Name", "Targets"))
    defaults = {
        "Role": "AWSGlueRole",
        "DatabaseName": kwargs["Name"],
        "SchemaChangePolicy": {"UpdateBehavior": "UPDATE_IN_DATABASE", "DeleteBehavior": "DELETE_FROM_DATABASE"},
        "RecrawlPolicy": {"RecrawlBehavior": "CRAWL_EVERYTHING"},
        "LineageConfiguration": {"CrawlerLineageSettings": "DISABLE"},
    }
    kwargs = {**defaults, **kwargs}

    # Ensure crawler
    client = boto3.client("glue")
    name = kwargs["Name"]
    try:
        response = client.create_crawler(**kwargs)
        log.info(f"Created AWS Glue crawler {name}.")
    except client.exceptions.AlreadyExistsException:
        response = client.update_crawler(**kwargs)
        log.info(f"Updated AWS Glue crawler {name}.")
    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200


def get_tables(skip_temp: bool = False, **kwargs: Any) -> List[dict]:
    """Return the list of tables in the specified AWS Glue database.

    At minimum the `DatabaseName` keyword argument is required.

    :param skip_temp: If true, table names starting with "temp_" are skipped.
    :param kwargs: These are forwarded to `get_tables`.
    """
    assert "DatabaseName" in kwargs
    tables = boto3.client("glue").get_paginator("get_tables").paginate(**kwargs).build_full_result()["TableList"]
    if skip_temp:
        # Note: Such tables are sometimes automatically created.
        tables = [t for t in tables if not t["Name"].startswith("temp_")]
    return tables


def recreate_database(**kwargs: Any) -> None:
    """Safely delete and create the specified AWS Glue database.

    At minimum the `Name` keyword argument is required.

    :param kwargs: These are forwarded.
    The `CatalogId` (optional) and `Name` (required) keyword arguments are forwarded to `delete_database`.
    All kwargs are forwarded to `create_database` as its `CatalogId` and `DatabaseInput` parameters.
    """
    delete_database(CatalogId=kwargs.get("CatalogId"), Name=kwargs["Name"])  # Note: Additional kwargs, such as for `create_database`, are not relevant.
    create_database(**kwargs)


def run_crawler(crawler: str, *, timeout_minutes: int = 120, retry_seconds: int = 5) -> None:
    """Run the specified AWS Glue crawler, waiting until completion."""
    # Ref: https://stackoverflow.com/a/66072347/
    timeout_seconds = timeout_minutes * 60
    client = boto3.client("glue")
    start_time = timeit.default_timer()
    abort_time = start_time + timeout_seconds

    def wait_until_ready() -> None:
        state_previous = None
        while True:
            response_get = client.get_crawler(Name=crawler)
            state = response_get["Crawler"]["State"]
            if state != state_previous:
                log.info(f"Crawler {crawler} is {state.lower()}.")
                state_previous = state
            if state == "READY":  # Other known states: RUNNING, STOPPING
                return
            if timeit.default_timer() > abort_time:
                raise TimeoutError(f"Failed to crawl {crawler}. The allocated time of {timeout_minutes:,} minutes has elapsed.")
            time.sleep(retry_seconds)

    wait_until_ready()
    response_start = client.start_crawler(Name=crawler)
    assert response_start["ResponseMetadata"]["HTTPStatusCode"] == 200
    log.info(f"Crawling {crawler}.")
    wait_until_ready()
    log.info(f"Crawled {crawler}.")
