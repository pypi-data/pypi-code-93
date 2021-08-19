"""pandas utilities."""
import contextlib
import functools
import io
import logging
import textwrap
from typing import Any, Dict, Tuple, cast

import pandas as pd

from wpdatautil.timeit import Timer

log = logging.getLogger(__name__)


def csv_text_to_df(text: str) -> pd.DataFrame:
    """Return the dataframe constructed from the given CSV table text."""
    return pd.read_csv(io.StringIO(textwrap.dedent(text)))


def dedup_df(df: pd.DataFrame, *, df_description: str = "dataframe", log_if_rate_kept_le: float = 0, **kwargs: Any) -> float:
    """Return the rate kept after deduplicating the dataframe in-place.

    The reason for using this function is that it meaningfully logs the outcome.

    `kwargs` are forwarded to `df.drop_duplicates`.
    """
    len_pre_drop = len(df)
    log.debug(f"Dropping duplicate rows from {len_pre_drop:,} rows of the {df_description} using: {kwargs}.")
    timer = Timer()
    assert "inplace" not in kwargs
    df.drop_duplicates(**kwargs, inplace=True)
    len_post_drop = len(df)
    len_dropped = len_pre_drop - len_post_drop
    rate_dropped = (len_dropped / len_pre_drop) if len_pre_drop else float("nan")
    rate_kept = (len_post_drop / len_pre_drop) if len_pre_drop else float("nan")
    logger = log.info if (rate_kept <= log_if_rate_kept_le) else log.debug
    logger(f"Dropped {len_dropped:,} ({rate_dropped:.2%}) duplicate rows in {timer} from the {df_description}, resulting in {len_post_drop:,} ({rate_kept:.2%}) rows.")
    return rate_kept


def deindex_df(df: pd.DataFrame, *, index: Any, df_description: str = "dataframe", log_if_rate_kept_le: float = 0) -> float:
    """Return the rate kept after dropping index labels from the dataframe in-place.

    The reason for using this function is that it meaningfully logs the outcome.
    """
    len_pre_drop = len(df)
    log.debug(f"Dropping rows matching index labels from {len_pre_drop:,} rows of the {df_description}.")
    timer = Timer()
    df.drop(index=index, inplace=True)
    len_post_drop = len(df)
    len_dropped = len_pre_drop - len_post_drop
    rate_dropped = (len_dropped / len_pre_drop) if len_pre_drop else float("nan")
    rate_kept = (len_post_drop / len_pre_drop) if len_pre_drop else float("nan")
    logger = log.info if (rate_kept <= log_if_rate_kept_le) else log.debug
    logger(f"Dropped {len_dropped:,} ({rate_dropped:.2%}) rows matching index labels in {timer} from the {df_description}, resulting in {len_post_drop:,} ({rate_kept:.2%}) rows.")
    return rate_kept


def denull_df(df: pd.DataFrame, *, df_description: str = "dataframe", criteria_description: str = "criteria", log_if_rate_kept_le: float = 0, **kwargs: Any) -> float:
    """Return the rate kept after dropping rows having null values from the dataframe in-place.

    The reason for using this function is that it meaningfully logs the outcome.

    `kwargs` are forwarded to `df.dropna`.
    """
    len_pre_drop = len(df)
    log.debug(f"Dropping rows having {criteria_description} from {len_pre_drop:,} rows of the {df_description} using: {kwargs}")
    timer = Timer()
    assert "inplace" not in kwargs
    df.dropna(**kwargs, inplace=True)
    len_post_drop = len(df)
    len_dropped = len_pre_drop - len_post_drop
    rate_dropped = (len_dropped / len_pre_drop) if len_pre_drop else float("nan")
    rate_kept = (len_post_drop / len_pre_drop) if len_pre_drop else float("nan")
    logger = log.info if (rate_kept <= log_if_rate_kept_le) else log.debug
    logger(
        f"Dropped {len_dropped:,} ({rate_dropped:.2%}) rows in {timer} having {criteria_description} from the {df_description}, "
        f"resulting in {len_post_drop:,} ({rate_kept:.2%}) rows."
    )
    return rate_kept


def set_pandas_display_options() -> None:
    """Set pandas display options."""
    # Ref: https://stackoverflow.com/a/52432757/
    display = pd.options.display

    display.max_columns = 1000
    display.max_rows = 1000
    display.max_colwidth = 199
    display.width = None
    # display.precision = 2  # set as needed


@functools.lru_cache(1)
def versions() -> Dict[str, str]:
    """Return various software versions in use by Pandas."""
    redirect = io.StringIO()
    with contextlib.redirect_stdout(redirect):
        pd.show_versions()
        # Note: pd.show_versions(json=True) doesn't return valid JSON as of pandas 1.2.2.
    pd_versions = redirect.getvalue()
    pd_versions: Dict[str, str] = dict(cast(Tuple[str, str], tuple(map(str.rstrip, v.split(" : ")))) for v in pd_versions.rstrip().split("\n") if " : " in v)
    return pd_versions
