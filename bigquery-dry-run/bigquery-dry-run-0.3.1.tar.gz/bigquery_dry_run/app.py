import argparse
import sys
import concurrent.futures
from collections import namedtuple
from pathlib import Path
from typing import List

from google.cloud import bigquery


QueryResult = namedtuple("QueryResult", "filepath, success, error, bytes_processed")


def bq_dry_run(filepath: str) -> QueryResult:
    """
    Perform a dry run in BigQuery for a file. Return True if the query ran
    successfully or False if it did not.

    :param filepath: File path of the file containing the SQL to be run.
    :returns: Named tuple True if the query succeeded or False if it failed.
    """
    with open(filepath, mode="r") as fin:
        sql = fin.read()

    # return a failure for blank files.
    if not sql:
        return QueryResult(
            filepath=filepath, success=False, error=["Empty file"], bytes_processed=0
        )

    client = bigquery.Client()
    query_config = bigquery.QueryJobConfig()
    query_config.dry_run = True

    try:
        query_job = client.query(sql, job_config=query_config)
        result = QueryResult(filepath, True, None, query_job.total_bytes_processed)
    except Exception as ex:
        error = [error["message"] for error in ex.errors]
        result = QueryResult(filepath, False, error, 0)

    return result


def get_files(folder: str) -> List[str]:
    """
    Traverse the folder and subfolders to find all `.sql` files.

    :param folder: Folder to start scanning for `.sql` files.
    :returns: List of POSIX path string for each file found in the folder and
              subfolders.
    """
    p = Path(folder)
    return [path.as_posix() for path in p.glob("**/*.sql")]


def output_results(results: List[QueryResult], verbose: bool) -> None:
    """
    Output the results to the console (stdout).

    :param results: List of QueryResult named tuples.
    :param verbose: If true print the result of all files otherwise just failures.
    :returns: None
    """
    # Get the success, failed and total counts
    success = len([result.success for result in results if result.success == True])
    failed = len([result.success for result in results if result.success == False])
    total = len(results)

    # If the output should not be verbose then only output failures
    if not verbose:
        results = [result for result in results if result.success == False]

    # Sort based on path length and actual path str ensure files in subfolder
    # is shown before files in additional subfolders
    results.sort(key=lambda r: f"{len(r.filepath.split('/'))} - {r.filepath}")

    # Print query by query detail
    print("Dry run results:\n")
    for result in results:
        errors = " | ".join(result.error) if result.error else None
        status = "Passed" if result.success else "Failed"
        print(f"File: {result.filepath}\n  Result: {status}\n  Errors: {errors}\n")

    # Print the final result
    print(f"Total: {total}\nSucceeded: {success}\nFailed: {failed}\n")


def process_args():
    """
    Process the arguments passed to the application and return them.
    """
    parser = argparse.ArgumentParser(
        description="Dry run of all `.sql` files in folder and subfolders."
    )
    parser.add_argument(
        "folder", type=str, help="Top level folder to start scanning for `.sql` files."
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=2,
        help="Number of threads for concurrent running of queries. Defaults to 2.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show all file results, not just failures.",
    )

    return parser.parse_args()


def run():
    """
    Main entry point of the application.
    """
    args = process_args()

    # Run queries in parallel
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as exec:
        futures = []
        for file in get_files(args.folder):
            futures.append(exec.submit(bq_dry_run, file))

        # Wait and get results
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())

    output_results(results, args.verbose)

    # Get the status of the overall execution
    status = all([result.success for result in results])

    # Exit the app with an error status code if not all queries ran succesfully
    if not status:
        sys.exit(1)
