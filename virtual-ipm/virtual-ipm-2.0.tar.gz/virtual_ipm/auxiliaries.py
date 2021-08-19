from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
import shutil
from subprocess import run, DEVNULL
import tempfile
import warnings

import pandas as pd

from virtual_ipm.utils.ui import Spinner


def run_simulation(config: Path, *, stdout: bool | None, only_detected: bool = False) -> pd.DataFrame:
    if stdout:
        run_kwargs = {}
        user_interface = nullcontext()
    elif stdout is not None:
        run_kwargs = dict(stdout=DEVNULL, stderr=DEVNULL)
        user_interface = Spinner(title='Running: ')
    else:
        run_kwargs = dict(stdout=DEVNULL, stderr=DEVNULL)
        user_interface = nullcontext()

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        shutil.copy(config, td.joinpath(config.name))

        with user_interface:
            run(['virtual-ipm', config.name], cwd=td, check=True, **run_kwargs)

        csv_files = list(td.glob('*.csv'))
        if not csv_files:
            raise RuntimeError('The simulation did not produce a .csv output file')
        return read_csv_output_file(csv_files[0], only_detected=only_detected)


def read_csv_output_file(f_name: Path, *, only_detected: bool = False) -> pd.DataFrame:
    df = pd.read_csv(f_name, index_col=0)
    if only_detected:
        detected = df['status'] == 'DETECTED'
        if not detected.all():
            warnings.warn(f'[{f_name}] The output file contains {len(detected) - sum(detected)} undetected particles')
            df = df.loc[detected]
    return df
