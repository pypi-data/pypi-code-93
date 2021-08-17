from stataLogObject.Supports import HeaderKeyExtractError, InvalidKeyExtract, extract_values

from dataclasses import dataclass, fields, field
from typing import Optional, List
from abc import ABC, abstractmethod


@dataclass
class VarField:
    extractor: str
    var_type: type = float

    def find_mf(self, lines_list, var_name):
        """Find the model fit parameter in the lines list"""
        for i, line in enumerate(lines_list):
            if self.extractor in " ".join(line):
                return self._extract_mf(i, lines_list, var_name)

        raise InvalidKeyExtract(self.extractor, var_name)

    @abstractmethod
    def _extract_mf(self, index, lines_list, var_name):
        """Extract the model fit parameter(s) from the raw table"""

    @abstractmethod
    def _extract_var(self, values_list, var_name):
        """Extract the variable(s) from the list of values for a given variable"""


@dataclass
class MFVar(VarField):
    """Extracting information for a given model fit variable"""
    key_extract: int = 0

    def _extract_mf(self, index, lines_list, var_name):
        values = extract_values(" ".join(lines_list[index]))

        if len(values) == 0:
            print(f"Warning: {var_name} not set yet requested")
            return "N/A"
        else:
            return self._extract_var(values, var_name)

    def _extract_var(self, values_list, var_name):
        try:
            return self.var_type(values_list[self.key_extract])
        except (KeyError, IndexError):
            raise HeaderKeyExtractError(self.key_extract, values_list, var_name)


@dataclass
class REVar(VarField):
    """Random effects parameters"""
    key_extract: List = field(default_factory=lambda: [0, 1, 2, 3])
    re_headers: List = field(default_factory=lambda: ["Est", "Std Err", "LB_95", "UB_95"])

    def _extract_mf(self, index, lines_list, var_name):
        # Extract each random parameter as a dict
        random_params = [self._extract_var(line, var_name) for i, line in enumerate(lines_list)
                         if i > index and ("|" in line) and (":" not in " ".join(line))]

        # Merge the dicts into a master dict to return
        return {list(rp.keys())[0]: list(rp.values())[0] for rp in random_params}

    def _extract_var(self, values_list, var_name):

        # Set this variable name from the elements that are not the last 4
        var_name = " ".join(values_list[:-4]).strip("|").strip(" ")

        # Extract the values that are the last 4, SE calculation can fail so allow for missing
        values = extract_values(" ".join(values_list[-4:]), False)
        if len(values) == 0:
            print(f"Warning: {var_name} not set yet requested")
            return "N/A"

        # For each key in RE return the header-value of the random effects parameters
        try:
            return {var_name: {h: values[i] if values[i] == "MISSING" else self.var_type(values[i])
                               for h, i in zip(self.re_headers, self.key_extract)}}
        except (KeyError, IndexError):
            raise HeaderKeyExtractError(self.key_extract, values, var_name)


@dataclass
class MF(ABC):
    """Model Fit base class"""

    def field_names(self):
        """Returns the summary information"""
        return [f.name for f in fields(self)]


@dataclass
class LinearMF(MF):
    """Linear Regression model fit parameters"""
    obs: MFVar
    f_stat: MFVar
    f_prob: MFVar
    r_sqr: MFVar
    r_mse: MFVar

    adj_r_sqr: Optional[MFVar] = None
    within_r_sqr: Optional[MFVar] = None


@dataclass
class TabMF(MF):
    total: MFVar


@dataclass
class PanelMF(MF):
    obs: MFVar
    groups: MFVar
    obs_group_min: MFVar
    obs_group_avg: MFVar
    obs_group_max: MFVar
    f_stat: MFVar
    f_prob: MFVar
    r_sqr_within: MFVar
    r_sqr_between: MFVar
    r_sqr_overall: MFVar
    sigma_u: MFVar
    sigma_e: MFVar
    rho: MFVar


@dataclass
class MixedMF(MF):
    obs: MFVar
    wald: MFVar
    chi2_prob: MFVar
    log_like: MFVar
    re_params: REVar


# TODO
@dataclass
class LogisticMF(MF):
    """Logistical Regression model fit parameters"""
    pass
