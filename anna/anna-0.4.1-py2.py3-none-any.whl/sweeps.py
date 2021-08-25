from __future__ import annotations

import itertools as it
import math
from pathlib import Path
import re
from typing import Any, Callable, Sequence, Type, Union
import numpy as np
import pandas as pd
from anna.adaptors import XMLAdaptor
from anna.exceptions import InvalidPathError


class Generator:
    count: int
    def generate(self) -> Sequence: raise NotImplementedError


DistributionType = Callable[[float, float, int], Sequence[float]]


class Distribution:
    GRID = np.linspace
    RANDOM = np.random.default_rng().uniform


class Transformation:
    def apply(self, x): raise NotImplementedError
    def inverse(self, x): raise NotImplementedError


class Linear(Transformation):
    def apply(self, x):
        return x

    def inverse(self, x):
        return x


class Log10(Transformation):
    def apply(self, x):
        return np.log10(x)

    def inverse(self, x):
        return 10 ** x


class NumberRange(Generator):
    def __init__(self, lower: float, upper: float, count: int, method: DistributionType, scale: Type[Transformation]):
        self.scale = scale()
        self.lower = lower
        self.upper = upper
        self.count = count
        self.method = method

    def generate(self) -> Sequence[float]:
        return self.scale.inverse(self.method(self.scale.apply(self.lower), self.scale.apply(self.upper), self.count))


class IntegerRange(NumberRange):
    def generate(self) -> Sequence[int]:
        return np.rint(super().generate()).astype(np.int64)


class FilepathRange(Generator):
    def __init__(self, path: Path | str, pattern: str):
        self.path = Path(path)
        self.pattern = pattern

    def generate(self) -> Sequence[Path]:
        if not self.path.is_dir():
            raise ValueError(f'{self.path.resolve()!s} does not point to an existing directory')
        return list(self.path.glob(self.pattern))

    @property
    def count(self) -> int:
        return len(self.generate())


class CombinationMethod:
    def __init__(self, parameters: Sequence[Generator]):
        self.parameters = parameters

    def generate(self) -> Sequence[Sequence]:
        raise NotImplementedError

    @property
    def count(self) -> int:
        raise NotImplementedError


class ProductCombination(CombinationMethod):
    def generate(self) -> list[tuple]:
        return list(it.product(*(p.generate() for p in self.parameters)))

    @property
    def count(self) -> int:
        return math.prod(p.count for p in self.parameters)


class ZipCombination(CombinationMethod):
    def generate(self) -> list[tuple]:
        return list(zip(*(p.generate() for p in self.parameters)))

    @property
    def count(self) -> int:
        return min(p.count for p in self.parameters)


CombinationMethodType = Type[CombinationMethod]


class Combinator(Generator):
    def __init__(self, parameters: Sequence[Generator], method: CombinationMethodType):
        self.parameters = parameters
        self.method = method

    def generate(self) -> np.ndarray:
        return np.asarray(self.method(self.parameters).generate(), dtype=object)


class VectorRange(Combinator):
    def __init__(
            self,
            lowers: Sequence[float],
            uppers: Sequence[float],
            counts: Sequence[int],
            methods: Sequence[DistributionType],
            scales: Sequence[Type[Transformation]],
            *,
            method: CombinationMethodType
    ):
        assert len(lowers) == len(uppers) == len(counts) == len(methods) == len(scales)
        super().__init__(
            [NumberRange(l, u, c, m, s)
             for l, u, c, m, s in zip(lowers, uppers, counts, methods, scales)],
            method=method
        )


class Sweep:
    def __init__(self, names: Sequence[str], combinator: Combinator):
        self.dataframe = pd.DataFrame.from_records(
            data=combinator.generate(),
            columns=names,
        )

    def __len__(self):
        return len(self.dataframe)

    def to_dataframe(self) -> pd.DataFrame:
        return self.dataframe

    def to_json(self, json_path=None) -> Union[str, None]:
        return self.dataframe.to_json(
            path_or_buf=json_path,
            orient='index',
            indent=4,
            default_handler=lambda path: str(path.resolve()),
        )


class Generate:
    CONFIG_DIRECTORY = 'configurations'

    def __init__(
        self,
        sweep_instance: Sweep,
        *,
        seed_path: Path,
        folder_path: Path,
        config_prefix: str,
        meta: dict[str, dict[str, Any]],
        constants: dict[str, Any]
    ):
        self.seed_path = seed_path
        self.folder_path = folder_path
        self.config_prefix = config_prefix
        self.sweep_instance = sweep_instance
        self.sweep_dict = self.sweep_instance.to_dataframe().applymap(np.asarray).to_dict(orient='index')
        self.meta = meta
        self.constants = constants
        self.xml_seed = XMLAdaptor(str(self.seed_path.resolve()))
        self.number_of_files = len(self.sweep_instance.to_dataframe())
        self.generated_names = self.names()

    def all(self):
        self.xml()
        self.names_to_txt()
        self.csv()

    def xml(self):
        path_config = self.folder_path.joinpath(self.CONFIG_DIRECTORY)
        # Create directories, error if directories already exist to prevent data loss.
        path_config.mkdir()
        # Create JSON file
        self.sweep_instance.to_json(str(self.folder_path.joinpath('sweep').with_suffix('.json').resolve()))
        # Functionality that adds parameter to XML file if not contained in seed XML file
        for key in self.sweep_instance.to_dataframe().columns:
            try:
                self.xml_seed.get_text(key)
            except InvalidPathError:
                self.xml_seed.insert_element(key, 'placeholder', **self.meta.get(key, {}))
        # Create the configuration files for each parameter combination
        for index, (combination_id, combination_info) in enumerate(self.sweep_dict.items()):
            for key, value in combination_info.items():
                if isinstance(value, np.ndarray):
                    value = value.tolist()
                self.xml_seed.update_text(key, str(value))
            # Dump into new XML file
            total_config_path = path_config.joinpath(self.generated_names[index]).resolve()
            self.xml_seed.dump_to_file(str(total_config_path))
            # The following is a workaround for https://gitlab.com/Dominik1123/Anna/-/issues/23
            # `XMLAdaptor.dump_to_file` adds additional empty lines to the output XML file which are not present in the
            # seed file. This makes it more difficult to compare the two versions, hence removing empty lines here.
            total_config_path.write_text(re.sub(
                '^[ \t]*\r?\n',
                '',
                total_config_path.read_text(),
                flags=re.M,
            ))

    def names(self):
        config_names = []
        num_zeros = int(np.ceil(np.log10(len(self.sweep_instance.to_dataframe()))))
        for ii in range(self.number_of_files):
            config_names.append(self.config_prefix + str(ii).zfill(num_zeros) + '.xml')
        return config_names

    def names_to_txt(self):
        with open(self.folder_path.joinpath('names_to_txt').with_suffix('.txt').resolve(), 'w') as f:
            for x in self.generated_names:
                f.write(f'{Path(self.CONFIG_DIRECTORY).joinpath(x)!s}\n')

    def csv(self):
        dataframe = self.sweep_instance.to_dataframe()
        # Need to convert to `[v]*len(...)` since the constant values `v` might be lists themselves (VectorParameter).
        dataframe = dataframe.assign(**{k: [v]*len(self.sweep_instance) for k, v in self.constants.items()})
        dataframe.insert(0, 'Configuration filename', self.generated_names)
        dataframe = dataframe.applymap(np.asarray)
        path_csv_final = self.folder_path.joinpath('data').with_suffix('.csv')
        dataframe.to_csv(str(path_csv_final.resolve()))


if __name__ == "__main__":
    pass
