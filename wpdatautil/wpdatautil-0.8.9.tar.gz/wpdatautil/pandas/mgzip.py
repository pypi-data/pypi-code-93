"""pandas mgzip utilities."""
import logging
import pickle
from typing import List

import pandas as pd

from wpdatautil.humanfriendly import format_size
from wpdatautil.mgzip import compress, decompress
from wpdatautil.timeit import Timer

log = logging.getLogger(__name__)

_PICKLE_PROTOCOL = 5


def encode_df(df: pd.DataFrame, description: str = "dataframe") -> List[bytes]:
    """Encode a large Pandas dataframe into a pickle-friendly list of bytes.

    Each column is pickled and compressed in sequence. This approach also works for a large dataframe for which pickle otherwise fails.
    """
    num_rows = len(df)
    num_columns = len(df.columns)

    cols_pkl_z = []
    for col_num, col in enumerate(df.columns, start=1):
        col_description = f"{df[col].dtype} column {col} ({col_num}/{num_columns}) of {description} with {num_rows:,} rows"

        # Pickle column
        col_pickle_timer = Timer()
        log.debug(f"Pickling {col_description}.")
        col_pkl = pickle.dumps(df[col], protocol=_PICKLE_PROTOCOL)
        len_col_pkl = len(col_pkl)
        log.debug(f"Pickled {col_description} to {format_size(len_col_pkl)} in {col_pickle_timer}.")

        col_pkl_z = compress(col_pkl, description=f"pickled {col_description}")
        cols_pkl_z.append(col_pkl_z)

    return cols_pkl_z


def decode_df(encoded_df: List[bytes]) -> pd.DataFrame:
    """Decode a large Pandas dataframe which was previously encoded using the `encode_df` function."""
    return pd.concat([pickle.loads(decompress(col)) for col in encoded_df], axis=1)
