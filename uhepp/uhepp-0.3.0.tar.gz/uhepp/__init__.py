"""
Universal HEP plot defines a universal interchange format of plots used in
high-energy contexts.
"""

import json
import re
import os
from datetime import datetime
import operator as op
import dateutil.parser
from tzlocal import get_localzone
import requests
from requests.compat import urljoin

import yaml
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, LogLocator, ScalarFormatter
import atlasify

__version__ = "0.3.0"  # Also change in setup.py and docs

DEFAULT_API = "https://uhepp.org/api/"

HATCH_PATTERN = "/"*8
HATCH_COLOR = "#999999"
UNCERTAINTY = "Uncertainty"
AUTOMATRIC_AXIS_SCALING = True
X_ALIGN = 1
Y_ALIGN = 1

# Set a default value for the hatching pattern. This make the pattern appear
# finer
mpl.rcParams['hatch.linewidth'] = 0.4

# Style settings: font size, spacing and layout
LEGEND_FONT_SIZE = 9  # Can be None for default
LEGEND_ANCHOR = (0.985, 0.975)
atlasify.FONT_SIZE = 12
atlasify.LABEL_FONT_SIZE = 12
atlasify.SUB_FONT_SIZE = 10
mpl.rcParams['font.size'] = 10
mpl.rcParams["legend.labelspacing"] = 0.2

if hasattr(atlasify, "MAJOR_TICK_LENGTH"):
    atlasify.OFFSET = 7
    atlasify.INDENT = 10
    MAJOR_TICK_LENGTH = 8
    MINOR_TICK_LENGTH = 4
    atlasify.MAJOR_TICK_LENGTH = MAJOR_TICK_LENGTH
    atlasify.MINOR_TICK_LENGTH = MINOR_TICK_LENGTH
else:
    # Fall back to defaults if tick length not a var
    MAJOR_TICK_LENGTH = 6
    MINOR_TICK_LENGTH = 3

# pylint: disable=R0903
class UHepPlotModel:
    """Empty base class"""

class UHepParseError(Exception):
    """Invalid input data"""

def to_python(data):
    """Convert the data to pure python list and numbers"""
    if hasattr(data, "tolist"):
        return data.tolist()
    return list(data)

def from_caf(sample_folder, path, cut_stage, variable, include_bins=False):
    """
    Create and return a Yield object from a histogram in CAF.

    The base yield and statistical uncertainty are copied from the TH1F
    returned by the sample folder.

    Under and overflow bins are considered.

    If the include_overflow argument is True, the return value is a tuple of
    yield object and bin edges.

    The from_th1() method does not provide a method to set the total
    systematic uncertainty or variations.
    """
    th1 = sample_folder.getHistogram(path, f"{cut_stage}/{variable}")
    if not th1:
        raise KeyError(f"No histogram found for {cut_stage}/{variable} in"
                       f" {path}")
    return from_th1(th1, include_bins=include_bins)

def from_th1(base_th1, var_up=None, var_down=None, include_bins=False):
    """
    Create and return a Yield object from a ROOT TH1 object

    The base yield and statistical uncertainty are copied from a TH1 object
    given as first object. Optionally, var_up and var_down dicts with
    variation name and TH1 mapping are used to extract he variation yield.

    Under and overflow bins are considered.

    If the include_overflow argument is True, the return value is a tuple of
    yield object and bin edges.

    The from_th1() method does not provide a method to set the total
    systematic uncertainty.
    """
    bin_count = base_th1.GetNbinsX()

    def extract(th1, accessor=lambda x: x.GetBinContent):
        return [accessor(th1)(i) for i in range(bin_count + 2)]

    base = extract(base_th1)
    stat = extract(base_th1, lambda x: x.GetBinError)

    if var_up is None:
        var_up = {}

    if var_down is None:
        var_down = {}

    yield_obj = Yield(base, stat,
                      var_up={k: extract(v) for k, v in var_up.items()},
                      var_down={k: extract(v) for k, v in var_down.items()})

    if include_bins:
        x_axis = base_th1.GetXaxis()
        n_bins = x_axis.GetNbins()
        bin_edges = [x_axis.GetBinUpEdge(i) for i in range(n_bins + 1)]
        return yield_obj, bin_edges

    return yield_obj



class _SmartDict():
    """Wrapper around dicts with json-dot-style attribute retrieval"""

    def __init__(self, data):
        """Create wrapper around existing dict"""
        self.data = data

    def __contains__(self, key):
        """True if the dict contains the nested key"""
        tokens = key.split(".")

        value = self.data
        for token in tokens:
            if token not in value:
                return False
            value = value[token]
        return True

    def get(self, key, default=None):
        """Retrieve a dot-delimited, nested value of return the default"""
        tokens = key.split(".")

        value = self.data
        for token in tokens:
            if token not in value:
                return default
            value = value[token]
        return value

    def __getitem__(self, key):
        """Retrieve a dot-delimited, nested value of raise an KeyError"""
        if key not in self:
            raise KeyError(key)
        return self.get(key)


#pylint: disable=R0901
class _NoDatesSafeLoader(yaml.SafeLoader):
    """Safe yaml loader that doesn't convert dates"""
    yaml_implicit_resolvers = {
            k: [r for r in v if r[0] != 'tag:yaml.org,2002:timestamp'] for
                    k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
    }

def from_yamls(yaml_string):
    """Build and return a UHepPlot from a uhepp compliant yaml string"""
    data = yaml.load(yaml_string, Loader=_NoDatesSafeLoader)
    return from_data(data)

def from_yaml(filename):
    """Build and return a UHepPlot from a uhepp compliant yaml file"""
    with open(filename) as yaml_file:
        data = yaml.load(yaml_file, Loader=_NoDatesSafeLoader)
    return from_data(data)

def from_jsons(json_string):
    """Build and return a UHepPlot from a uhepp compliant json string"""
    data = json.loads(json_string)
    return from_data(data)

def from_json(filename):
    """Build and return a UHepPlot from a uhepp compliant json file"""
    with open(filename) as json_file:
        data = json.load(json_file)
    return from_data(data)

def from_data(data):
    """
    Build and return a UHepPlot from uhepp compliant dicts and lists
    """
    data = _SmartDict(data)

    version = data["version"]
    if float(version) >= 1:
        raise ValueError(f"Unsupported uhepp version: {version}")

    supported_types = {
        "histogram": _hist_from_data
    }

    uhepp_type = data["type"]
    if uhepp_type not in supported_types:
        raise ValueError(f"Unsupported uhepp type: {uhepp_type}")

    factor_method = supported_types[uhepp_type]
    return factor_method(data)

def _hist_from_data(data):
    """Build a :class:`UHeppHist` from uhepp compliant dicts and lists"""
    hist = UHeppHist(symbol=data["variable.symbol"],
                     bin_edges=data["bins.edges"])

    hist.version = str(data["version"])
    hist.date = data["metadata.date"]
    hist.filename = data["metadata.filename"]

    optional_fields = {
        "metadata.author": "author",
        "metadata.producer": "producer",
        "metadata.code_revision": "code_revision",
        "metadata.event_selection": "event_selection",
        "metadata.tags": "tags",
        "metadata.lumi_ifb": "lumi",
        "metadata.Ecm_TeV": "energy",
        "badge.brand": "brand",
        "badge.label": "brand_label",
        "badge.subtext": "subtext",
        "variable.unit": "unit",
        "variable.unit_in_brackets": "unit_in_brackets",
        "variable.name": "variable",
        "variable.log": "x_log",
        "bins.rebin": "rebin_edges",
        "bins.include_overflow": "include_overflow",
        "bins.include_underflow": "include_underflow",
        "bins.density_width": "density_width",
        "y_axis.max": "y_max",
        "y_axis.min": "y_min",
        "y_axis.label": "y_label",
        "y_axis.log": "y_log",
        "ratio_axis.label": "ratio_label",
        "ratio_axis.min": "ratio_min",
        "ratio_axis.max": "ratio_max",
        "ratio_axis.log": "ratio_log",
        "ratio_axis.diff": "ratio_diff",
        "layout.size": "figure_size",
        "layout.ratio_fraction": "ratio_fraction",
    }

    for key, attr in optional_fields.items():
        if key in data:
            setattr(hist, attr, data[key])

    # Stacks
    for stack_data in data["stacks"]:
        sitems = []
        for sitem_data in stack_data["content"]:
            yield_names = sitem_data["yield"]
            label = sitem_data["label"]
            style = sitem_data.get("style", {})
            sitem = StackItem(yield_names, label, **style)
            sitems.append(sitem)

        bartype = stack_data["type"]
        keep_zero = stack_data.get("keep_zero", False)
        error = stack_data.get("error", "stat")
        x_errorbar = stack_data.get("x_errorbar", True)
        stack = Stack(sitems, bartype=bartype, error=error,
                      x_errorbar=x_errorbar, keep_zero=keep_zero)
        hist.stacks.append(stack)

    # V Lines
    for v_line in data.get("v_lines", []):
        pos_x = v_line["x"]
        stretch = v_line.get("range")
        style = v_line.get("style", {})
        hist.v_lines.append(VLine(pos_x, stretch, **style))

    # H Lines
    for h_line in data.get("h_lines", []):
        pos_y = h_line["y"]
        stretch = h_line.get("range")
        style = h_line.get("style", {})
        hist.h_lines.append(HLine(pos_y, stretch, **style))

    # Graphs
    for graph in data.get("graphs", []):
        x_values = graph["x"]
        y_values = graph["y"]
        label = graph.get("label")
        graphtype = graph.get("type")
        x_errors = graph.get("x_errors")
        y_errors = graph.get("y_errors")
        style = graph.get("style", {})

        graph = Graph(x_values, y_values, label=label, graphtype=graphtype,
                      **style)
        graph.x_errors = x_errors
        graph.y_errors = y_errors
        hist.graphs.append(graph)

    # Ratio
    for ratio_data in data.get("ratio", []):
        numerator = ratio_data["numerator"]
        keep_zero = ratio_data.get("keep_zero", False)
        denominator = ratio_data.get("denominator")
        bartype = ratio_data["type"]
        error = ratio_data.get("error", "stat")
        x_errorbar = ratio_data.get("x_errorbar", True)
        den_error = ratio_data.get("den_error", error)
        style = ratio_data.get("style", {})
        ritem = RatioItem(numerator, denominator, bartype, error, den_error,
                          x_errorbar=x_errorbar, keep_zero=keep_zero, **style)
        hist.ratio.append(ritem)

    # Yields
    for name, yield_data in data["yields"].items():
        base = yield_data["base"]
        stat = yield_data.get("stat")
        syst = yield_data.get("syst")
        var_up = yield_data.get("var_up")
        var_down = yield_data.get("var_down")

        yield_obj = Yield(base, stat, syst, var_up, var_down)
        hist.yields[name] = yield_obj

    return hist

class Yield(UHepPlotModel):
    """
    Collection of yields and uncertainties of a single process

    A yield object stores binned yields for a process including underflow and
    overflow bins. This means the number of bins is the number bin boundaries
    plus one: n - 1 + 1 (for underflow) + 1 (for overflow) = n + 1.

    Additionally, the object stores the statistical uncertainty of each bin.
    The values stored as uncertainties correspond to the 1-sigma deviations
    form the central value. Optionally, the yield object can store a
    precomputed, overall systematic uncertainty for each bin. The central
    value is referred to as `base`.

    Besides the bin-by-bin statistical and systematic uncertainties, the yield
    object also provides a way to store binned systematic variations of the
    base histogram. Variations are identified by a string key. For each
    key, an up-variation and down-variation can be set as a replacement for
    the base values. Variations are stored as absolute yields and not as
    deviations from base. If a down-variation is not set, the up-variation
    is symmetrized such that the absolute differences to the base values are
    identical.

    The option to store variations can be used during plotting. A total
    systematic uncertainty can be computed with the "env" option assuming that
    all variations are independent. Please note that in that case the computed
    uncertainties are not generally statistically independent between the
    bins. Alternatively, it is possible to use variations as histogram items
    in their own right, for example to compare the shape of a variation to
    nominal.

    The class provides overload arithmetic operations. Yields objects can be
    multiplied and divided by integers and floats. Scaling a yield object will
    also scale the uncertainties and variations. Two yield objects can also be
    added, subtracted, multiplied and divided bin-wise. Statistical and
    systematic Uncertainties are propagated under the assumption that the
    two involved histograms are independent. If a variation is present in both
    yield objects, the varied arrays are added, subtracted, multiplied or
    divided. If a variation is absent in one of the yield objects, the base
    values are used as a fallback for the arithmetic operation.

    Please note that the yields stored in a yield object are "number of events
    per bin", not normalized to the bin width. Merging two adjacent bins yields
    a bin with the sum of the two yields. Normalizing the yield to the bin
    width, should happen during visualization.

    The class is intended and well-suited for specific use-cases. The
    following is a list of limitations what this class cannot do:

      (1) A yield object does not store the bin boundaries. This means a
          standalone yield object, i.e. a yield object without binning
          information or a :class:`UHeppHist`, does not make sense.

      (2) When adding variations or using arithmetics, only the number of bins
          is checked not the actual binning.  Mismatching bin edges lead to
          nonsensical results.

      (3) The class does not provide a way to construct the yield arrays. For
          example, use :func:`numpy.histogram` instead to convert an array of
          events to a histogram.

      (4) The variations cannot store an uncertainty. This is assumed to be a
          secondary effect. If an uncertainty is required, assess whether
          taking the statistical uncertainty of the base yield instead is
          applicable.

      (5) The class does not store process names or style information. This is
          handled by a :class:`UHeppHist` object.

      (6) Asymmetric statistical and systematic uncertainties are not
          supported. The up- and down-variations, however, might be
          asymmetric.

      (7) Except for adding variations, :class:`Yield` objects are considered to be
          immutable.
    """

    # pylint: disable=R0913
    def __init__(self, base, stat=None, syst=None, var_up=None, var_down=None):
        """
        Create a new Yield object with given base values and uncertainties

        The required `base` argument sets the base values of the yield object.
        The argument must be an iterable of numbers. The first item is the
        underflow bin, the last item is the overflow bin. The number of items
        must equal the number of bins plus one.

        The optional `stat` argument specifies the binned statistical
        uncertainty of the base values. The argument must be an iterable of
        numbers. The length must equal the length of base. If this argument is
        absent, the uncertainty is assumed to be zero.

        The optional `syst` argument specifies the binned, precomputed,
        overall systematic uncertainty.  See `stat` argument.

        The optional `var_up` and `var_down` arguments accepts a dict with
        varied yields. The keys of the dicts should be strings identifying the
        variation. Corresponding up and down variations should use the same
        keys in both arrays. If a key is only present in `var_up` (or only in
        `var_down`), the down (or up) variation is computed as a symmetric
        deviation from the base values.
        """
        self._base = np.array(base, copy=True)
        self._stat = self._sanitize(stat)

        self._syst = self._sanitize(syst)

        if var_up is None:
            var_up = {}
        self._var_up = {k: self._sanitize(v)
                        for k, v in var_up.items()}

        if var_down is None:
            var_down = {}
        self._var_down = {k: self._sanitize(v)
                          for k, v in var_down.items()}

    def _sanitize(self, array):
        """Return copy of array or None. Raises an error if bins don't match"""
        if array is None:
            return None
        if len(array) != len(self._base):
            raise ValueError("Bin count mismatch: %d vs %d"
                             % (len(array), len(self._base)))
        return np.array(array, copy=True)

    def _zeros(self):
        """Return a list of zeros with the same length as base"""
        return np.zeros(len(self.base))

    @property
    def base(self):
        """List of base yields of the process including under- and overflow"""
        return self._base.tolist()

    @property
    def stat(self):
        """Return the binned absolute, statistical uncertainty of the process"""
        if self._stat is None:
            return self._zeros().tolist()
        return self._stat.tolist()

    @property
    def syst(self):
        """Return the binned precomputed systematic uncertainty of the process"""
        if self._syst is None:
            return self._zeros().tolist()
        return self._syst.tolist()

    @property
    def variations(self):
        """List of variation names present as up and/or down variation"""
        names = set()
        names.update(self.var_up_names)
        names.update(self.var_down_names)
        return list(names)

    @property
    def var_up_names(self):
        """List of variation names present as up variation"""
        return list(self._var_up)

    @property
    def var_down_names(self):
        """List of variation names present as down variation"""
        return list(self._var_down)

    def var_up(self, var_name):
        """
        Return the binned, up-varied yield for the given variation

        If the variation is present in the up dict, return that variation. If
        the variation is only present in the down dict, compute and return the
        down variation as a symmetrized variation. If the variation is not
        present in neither dict, return base.
        """
        if var_name in self._var_up:
            return self._var_up[var_name].tolist()

        if var_name in self._var_down:
            symmetrized = 2 * self._base - self._var_down[var_name]
            return symmetrized.tolist()

        return self.base

    def var_down(self, var_name):
        """
        Return the binned, down-varied yield for the given variation

        If the variation is present in the down dict, return that variation. If
        the variation is only present in the up dict, compute and return the
        up variation as a symmetrized variation. If the variation is not
        present in neither dict, return base.
        """
        if var_name in self._var_down:
            return self._var_down[var_name].tolist()

        if var_name in self._var_up:
            symmetrized = 2 * self._base - self._var_up[var_name]
            return symmetrized.tolist()

        return self.base

    def iter_vars(self):
        """Return an iterator for the tuples of (name, up, down)"""
        for var_name in self.variations:
            yield (var_name,
                   self.var_up(var_name),
                   self.var_down(var_name))


    def add_var(self, var_name, var_up=None, var_down=None):
        """
        Add a new variation or set yield of an existing variation

        If var_up (or var_down) is None, the var_up (or var_down) dict is left
        untouched. If a variation exists, it is overwritten.
        """
        if var_up is not None:
            self._var_up[var_name] = self._sanitize(var_up)
        if var_down is not None:
            self._var_down[var_name] = self._sanitize(var_down)

    def __repr__(self):
        return f"<Yield bins={len(self.base)} total={sum(self.base):g}>"

    @staticmethod
    def _linear(array_a, array_b, operator):
        """Return linear op of the array items or None if arrays are None"""
        if array_a is not None and array_b is not None:
            return operator(np.asarray(array_a), np.asarray(array_b))
        if array_a is not None:
            return array_a
        if array_b is not None:
            return array_b
        return None

    @staticmethod
    def _quadratic(array_a, array_b, operator):
        """Return quadratic sum of the array items or None if arrays are None"""
        if array_a is not None and array_b is not None:
            return np.sqrt(operator(np.asarray(array_a)**2,
                                    np.asarray(array_b)**2))
        if array_a is not None:
            return array_a
        if array_b is not None:
            return array_b
        return None


    def __add__(self, other):
        """
        Return the bin-by-bin sum of two yields or a number

        When used with a number, the number is added to each bin of the base
        yield and systematic variations.

        When used with another yield object and the number of bins are not
        identical, an ValueError is raised. This method does not check
        equality of bin edges.

        Statistical uncertainties are added in quadrature. Overall systematic
        uncertainties are added in quadrature. Please note that this is only
        correct if the statistical and systematic uncertainties are
        statistically independent.

        Systematic variations that appear in both yield objects are added. If a
        variation appears in only one of the variations, the base yield of
        the other yield object is used. This assumes that the absence of a
        variation implies the invariance of the yield under said variation.
        """
        if isinstance(other, Yield):
            result = Yield(self._base + other._base,
                           Yield._quadratic(self._stat, other._stat, op.add),
                           Yield._quadratic(self._syst, other._syst, op.add))
            for var_name in set(self.variations + other.variations):
                var_up = Yield._linear(self.var_up(var_name),
                                       other.var_up(var_name),
                                       op.add)
                var_down = Yield._linear(self.var_down(var_name),
                                         other.var_down(var_name),
                                         op.add)
                result.add_var(var_name, var_up=var_up, var_down=var_down)
            return result

        return Yield(self._base + other, self._stat, self._syst,
                     var_up={k: v + other for k, v in self._var_up.items()},
                     var_down={k: v + other for k, v in self._var_down.items()})


    def __radd__(self, other):
        """See __add__()"""
        return self + other

    def __sub__(self, other):
        """
        Return the bin-by-bin difference of two yields or a number

        See __add__()
        """
        return self + (-other)

    def __rsub__(self, other):
        """
        See __sub__()
        """
        return -self + other

    def __mul__(self, other):
        """
        Return the bin-by-bin product of the two yields or a number

        When used with a number, the each bin of the base yield, the
        uncertainties and the variations is scaled by that number.

        When used with another yield object and the number of bins are not
        identical, an ValueError is raised. This method does not check
        equality of bin edges.

        Relative statistical uncertainties are added in quadrature. Relative
        systematic uncertainties are added in quadrature. Please note that
        this is only correct if the statistical and systematic uncertainties
        are statistically independent.

        Systematic variations that appear in both yield objects are
        multiplied. If a variation appears in only one of the variations, the
        base yield of the other yield object is used. This assumes that the
        absence of a variation implies the invariance of the yield under said
        variation.
        """
        def id0(array):
            if array is None:
                return self._zeros()
            return array

        if isinstance(other, Yield):
            stat = None
            if self._stat is not None or other._stat is not None:
                stat = np.sqrt(self._base**2 * id0(other._stat)**2 +
                               other._base**2 * id0(self._stat)**2)
            syst = None
            if self._syst is not None or other._syst is not None:
                syst = np.sqrt(self._base**2 * id0(other._syst)**2 +
                               other._base**2 * id0(self._syst)**2)

            result = Yield(self._base * other._base, stat, syst)
            for var_name in set(self.variations + other.variations):
                var_up = Yield._linear(self.var_up(var_name),
                                       other.var_up(var_name),
                                       op.mul)
                var_down = Yield._linear(self.var_down(var_name),
                                         other.var_down(var_name),
                                         op.mul)
                result.add_var(var_name, var_up=var_up, var_down=var_down)
            return result

        stat = None
        if self._stat is not None:
            stat = self._stat * np.abs(other)

        syst = None
        if self._syst is not None:
            syst = self._syst * np.abs(other)

        return Yield(self._base * other, stat, syst,
                     var_up={k: v * other for k, v in self._var_up.items()},
                     var_down={k: v * other for k, v in self._var_down.items()})

    def __rmul__(self, other):
        """See __mul__()"""
        return self * other

    def __truediv__(self, other):
        """
        Return the bin-by-bin division of the two yields or with a number

        See __mul__()
        """
        def id0(array):
            if array is None:
                return self._zeros()
            return array

        if isinstance(other, Yield):
            stat = None
            if self._stat is not None or other._stat is not None:
                stat = np.sqrt(id0(self._stat)**2 / other._base**2 +
                               id0(other._stat)**2 * self._base**2 /
                               other._base**4)
            syst = None
            if self._syst is not None or other._syst is not None:
                syst = np.sqrt(id0(self._syst)**2 / other._base**2 +
                               id0(other._syst)**2 * self._base**2 /
                               other._base**4)

            result = Yield(self._base / other._base, stat, syst)
            for var_name in set(self.variations + other.variations):
                var_up = Yield._linear(self.var_up(var_name),
                                       other.var_up(var_name),
                                       op.truediv)
                var_down = Yield._linear(self.var_down(var_name),
                                         other.var_down(var_name),
                                         op.truediv)
                result.add_var(var_name, var_up=var_up, var_down=var_down)
            return result

        stat = None
        if self._stat is not None:
            stat = self._stat / np.abs(other)

        syst = None
        if self._syst is not None:
            syst = self._syst / np.abs(other)

        return Yield(self._base / other, stat, syst,
                     var_up={k: v / other for k, v in self._var_up.items()},
                     var_down={k: v / other for k, v in self._var_down.items()})

    def __rtruediv__(self, other):
        """See __trutdiv__()"""
        stat = None
        if self._stat is not None:
            stat = np.abs(other) / self._base**2 * self._stat

        syst = None
        if self._syst is not None:
            syst = np.abs(other) / self._base**2 * self._syst

        return Yield(other / self._base, stat, syst,
                     var_up={k: other / v for k, v in self._var_up.items()},
                     var_down={k: other / v for k, v in self._var_down.items()})

    def __neg__(self):
        """Return the yield multiplied by -1"""
        return Yield(-self._base, self.stat, self.syst,
                     var_up={k: -v for k, v in self._var_up.items()},
                     var_down={k: -v for k, v in self._var_down.items()})

    def __pos__(self):
        """Return the yield multiplied by +1"""
        return Yield(self._base, self.stat, self.syst,
                     var_up=dict(self._var_up),
                     var_down=dict(self._var_down))

    def __len__(self):
        """Return then number of bins including over- and underflow bins"""
        return len(self.base)

    def __getitem__(self, index):
        """Return a value of the base yield, identical to base[index]"""
        return self.base[index]

    def rebin(self, orig_edges, new_edges):
        """
        Return a rebinned version of the yield object

        Merged bins are added for the base yield and variation yields. The
        statistical and systematic uncertainties of merged bins are added in
        quadrature. This is only correct, if the statistical and systematic
        uncertainty is not correlated between bins.
        """
        if not set(new_edges).issubset(orig_edges):
            raise ValueError(f"New edges {new_edges!r} not subset of original "
                             f"edges {orig_edges!r}")

        def pad(edges):
            """Enlarge under and overflow bins"""
            padded = [orig_edges[0] - 1] + list(edges) + [orig_edges[-1] + 1]
            return np.asarray(padded)

        orig_edges = pad(orig_edges)
        bin_centers = (orig_edges[1:] + orig_edges[:-1]) / 2

        new_edges = pad(new_edges)

        def rby(yield_):
            new_yield, _ = np.histogram(bin_centers,
                                        bins=new_edges,
                                        weights=yield_)
            return new_yield

        stat = None
        if self._stat is not None:
            stat = np.sqrt(rby(self._stat**2))

        syst = None
        if self._syst is not None:
            syst = np.sqrt(rby(self._syst**2))

        return Yield(rby(self._base), stat, syst,
                     var_up={k: rby(v) for k, v in self._var_up.items()},
                     var_down={k: rby(v) for k, v in self._var_down.items()})

    def total(self):
        """Return the total sum of yields of all bins for base and variations"""
        orig_edges = list(range(len(self) - 1))
        return self.rebin(orig_edges, [])

    def sum(self):
        """Return the sum of all base bins"""
        total = self.total()
        return total.base[0]

    def vary(self, **variations):
        """
        Returns the yield given a dict of variation pulls.

        The keyword arguments must be of the form variation_name=pull_value.
        The pull_value defines the direction and amount of a variation. If
        pull_value is 1, the var_up yields are used, if pull_value is -1, the
        var_down yields are used, if the pull_value is 0 (default for not
        listed variations) the base yields are used.

        For any other value, the method interpolates between the variations.

        A variation passed to the method which is not found in var_down nor
        var_up is not an error. It will not effect the return value.
        """
        contributions = [self._base]
        for variation, pull_value in variations.items():
            if pull_value > 0:
                delta = self.var_up(variation) - self._base
            else:
                delta = self._base - self.var_down(variation)

            contributions.append(pull_value * delta)

        return sum(contributions)


    def __int__(self):
        """Return the sum of all base bins"""
        return int(self.sum())

    def __float__(self):
        """Return the sum of all base bins"""
        return float(self.sum())

    def to_data(self):
        """Return a uhepp compatible dict/list version"""

        result = {"base": self.base}

        if self._stat is not None and (self._stat != 0).any():
            result["stat"] = self.stat

        if self._syst is not None and (self._syst != 0).any():
            result["syst"] = self.syst

        if self._var_up:
            result["var_up"] = {k: self.var_up(k) for k in self._var_up}

        if self._var_down:
            result["var_down"] = {k: self.var_down(k) for k in self._var_down}

        return result


class _ErrorBarItemMixin:
    """
    Mix-in for items with an uncertainty and different visualization types

    Classes using this mix-in must override VALID_TYPES and VALID_ERRORS.
    """
    VALID_TYPES = []
    VALID_ERRORS = []

    @property
    def bartype(self):
        """Type of the stack"""
        return self._type

    @bartype.setter
    def bartype(self, new_type):
        if new_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid stack type: {new_type}")
        self._type = new_type

    @property
    def error(self):
        """Error computation method"""
        return self._error

    @error.setter
    def error(self, new_error):
        if new_error not in self.VALID_ERRORS:
            raise ValueError(f"Invalid error method: {new_error}")
        self._error = new_error

class _DenErrorBarItemMixin(_ErrorBarItemMixin):
    """
    Mix-in for items with an uncertainty for numerator and denominator, and
    different visualization types.

    Classes using this mix-in must override VALID_TYPES and VALID_ERRORS.
    """

    @property
    def den_error(self):
        """Error computation method"""
        return self._den_error

    @den_error.setter
    def den_error(self, new_error):
        if new_error not in self.VALID_ERRORS:
            raise ValueError(f"Invalid den. error method: {new_error}")
        self._den_error = new_error

class Stack(UHepPlotModel, _ErrorBarItemMixin):
    r"""
    Representation of a collection of stacked items of the main plot

    A stack defines a collection of :class:`StackItem`\ s. In each bin, the bar heights
    of all stack items are added and drawn vertically on top of each other to
    form an overall bar. The items of the stack collection are refered to as
    content.

    A stack can be of different types: "step", "stepfilled" or "points". The
    type defines the plotting type. The default bar type is "stepfilled".

    The error property defnes how the total uncertainty band if the stack is
    computed. Possible values are: "no", "stat", "syst", "env", "stat+syst",
    "stat+env", "syst+env" or "stat+syst+env". Depending on the value, the
    uncertainty includes the statistical uncertainties of the yield objects,
    the total systematic uncertinaties of the yield objects, the quadratic
    sum of all variations of the yield objects, or combinations thereof.
    Combinations of different uncertainties are added in quadrature. The
    default error computation method is "stat".

    Content, type and error are accessible via properties.
    """

    VALID_TYPES = ["step", "stepfilled", "points"]
    VALID_ERRORS = ["no", "stat", "syst", "env", "stat+syst", "stat+env",
                    "syst+env", "stat+syst+env"]

    # pylint: disable=R0913
    def __init__(self, content, bartype="stepfilled", error="stat",
                 x_errorbar=True, keep_zero=False):
        """Create a new Stack"""
        self.content = content
        self.bartype = bartype
        self.error = error
        self.x_errorbar = x_errorbar
        self.keep_zero = keep_zero

    @property
    def content(self):
        """Return list of StackItems"""
        return self._content

    @content.setter
    def content(self, new_content):
        self._content = list(new_content)

    def __repr__(self):
        return f"<Stack {self.bartype}: " \
               f"{', '.join(item.label for item in self.content)}>"

    def to_data(self):
        """Return a uhepp compatible dict/list version"""
        return {
            "type": self.bartype,
            "error": self.error,
            "x_errorbar": self.x_errorbar,
            "keep_zero": self.keep_zero,
            "content": [stackitem.to_data() for stackitem in self.content],
        }

    def vary(self):
        """See Yield.vary()"""
        raise NotImplementedError()

    def var_up(self):
        """See Yield.var_up()"""
        raise NotImplementedError()

    def var_down(self):
        """See Yield.var_down()"""
        raise NotImplementedError()

    def stat(self):
        """See Yield.stat()"""
        raise NotImplementedError()

    def syst(self):
        """See Yield.syst()"""
        raise NotImplementedError()

    def base(self):
        """See Yield.base()"""
        raise NotImplementedError()

class _StyledItemMixin:
    """
    Mix-in for items with style attributes

    Classes using this mix-in must define VALID_STYLES.
    """
    VALID_STYLES = []

    def __init__(self, style):
        """Augment object with internal style dict"""
        self._style = {}

        if not set(style).issubset(self.VALID_STYLES):
            illegal = set(style) - set(self.VALID_STYLES)
            raise ValueError(f"Illegal style(s): {', '.join(illegal)}" )

        if "linestyle" in style:
            self.linestyle = style["linestyle"]
        if "linewidth" in style:
            self.linewidth = style["linewidth"]
        if "color" in style:
            self.color = style["color"]
        if "edgecolor" in style:
            self.edgecolor = style["edgecolor"]
        if "markersize" in style:
            self.markersize = style["markersize"]
        if "marker" in style:
            self.marker = style["marker"]

    @staticmethod
    def _parse_color(color):
        """Parse a color spec and return a hex string of 6 or 8 chars"""
        hex_str = mpl.colors.to_hex(color, keep_alpha=True)
        if hex_str.endswith('ff'):
            return hex_str[:-2]
        return hex_str

    @property
    def linewidth(self):
        """Width of the line or outline"""
        return self._style.get("linewidth", None)

    @linewidth.setter
    def linewidth(self, width):
        self._style["linewidth"] = float(width)

    @property
    def linestyle(self):
        """Style of the line or outline"""
        return self._style.get("linestyle", None)

    @linestyle.setter
    def linestyle(self, style):
        if style not in ["--", "-.", ":", "-"]:
            raise ValueError(f"Illegal line style: {style}")
        self._style["linestyle"] = style

    @property
    def color(self):
        """Primary color"""
        return self._style.get("color", None)

    @color.setter
    def color(self, value):
        self._style["color"] = self._parse_color(value)

    @property
    def edgecolor(self):
        """Color of outline/edges"""
        return self._style.get("edgecolor", None)

    @edgecolor.setter
    def edgecolor(self, value):
        self._style["edgecolor"] = self._parse_color(value)

    @property
    def markersize(self):
        """Size of the datapoint marker"""
        return self._style.get("markersize", None)

    @markersize.setter
    def markersize(self, value):
        self._style["markersize"] = value

    @property
    def marker(self):
        """The shape of the datapoint marker"""
        return self._style.get("marker", None)

    @marker.setter
    def marker(self, value):
        self._style["marker"] = value

    @property
    def style(self):
        """Return a dict containing all styles"""
        return dict(self._style)


# pylint: disable=R0902
class StackItem(UHepPlotModel, _StyledItemMixin):
    """
    Representation of an item within a stack of the main plot

    The StackItem object stores a list of names referring to yield objects.
    The binned sum of all referenced yields is the content of this stack item.
    Additionally, each stack object stores a label and style options used
    during plotting.

    The styles can be set or retrieved via properties. While setting an
    attribute, values are converted to the interal format, i.e. color names
    are converted to hex. If a style is not set, the corresponding attribute
    returns None.

    The complete set of styles can be retrieved via the style attribute. Unset
    attributes do not appear in the dict.

    Possible styles are:
      - linewidth (float)
      - linestyle (-- or - or -, or :)
      - color (matplotlib compliant)
      - edgecolor (matplotlib compliant)
      - markersize
      - marker

    Any legal matplotlib color might be used to set color attributes, althout
    the uhepp standard only allows hex string. Internally, all colors are
    converted to hex strings.
    """

    VALID_STYLES = ["linestyle", "linewidth", "color", "edgecolor",
                    "markersize", "maker"]

    def __init__(self, yield_names, label, **style):
        """
        Create a new StackItem

        The mandatory yield_names argument names a set of yields whose binned
        sum defines the height of the bars in the stack plot.

        The label is used during plotting as an identifier in the legend.
        """
        self.yield_names = list(yield_names)
        self.label = label

        _StyledItemMixin.__init__(self, style)

    def __repr__(self):
        return f"<StackItem {self.label}: {', '.join(self.yield_names)}>"

    def to_data(self):
        """Return a uhepp compliant version using dict and lists"""
        result = {
            "label": self.label,
            "yield": list(self.yield_names)
        }

        if self.style:
            result["style"] = self.style

        return result


class RatioItem(UHepPlotModel, _StyledItemMixin, _DenErrorBarItemMixin):
    """
    Representation of an item drawn in the ratio plot

    The RatioItem object stores a list of yield names for the numerator and
    the denominator. The binned sum of all referenced yields is the content of
    the numerator and denominator of this stack item. Additionally, each stack
    item object stores style options used during plotting, a bar type defining
    the representation (step or points) and a method to computed the
    uncertainty, see Stack.

    The styles can be set or retrieved via properties. While setting an
    attribute, values are converted to the internal format, i.e. color names
    are converted to hex. If a style is not set, the corresponding attribute
    returns None.

    The complete set of styles can be retrieved via the style attribute. Unset
    attributes do not appear in the dict.

    Possible styles are:
      - linewidth (float)
      - linestyle (-- or - or -, or :)
      - color (matplotlib compliant)
      - edgecolor (matplotlib compliant)
      - markersize
      - marker

    Any legal matplotlib color might be used to set color attributes, although
    the uhepp standard only allows hex string. Internally, all colors are
    converted to hex strings.
    """

    VALID_STYLES = ["linestyle", "linewidth", "color", "edgecolor",
                    "markersize", "maker"]
    VALID_TYPES = ["step", "stepfilled", "points"]
    VALID_ERRORS = ["no", "stat", "syst", "env", "stat+syst", "stat+env",
                    "syst+env", "stat+syst+env"]


    # pylint: disable=R0913
    def __init__(self, numerator, denominator=None, bartype='step',
                 error='stat', den_error=None, x_errorbar=True,
                 keep_zero=False, **style):
        """
        Create a new RatioItem

        The mandatory numerator argument defines a list of yields. The
        optional argument denominator can be a list of yields. If it is
        missing, the denominator of the ratio is unity.

        For type, error and style, see Stack and StackItem.
        """
        self.numerator = list(numerator)
        if not denominator:
            denominator = []
        self.denominator = list(denominator)

        self.x_errorbar = x_errorbar
        self.error = error
        if den_error is None:
            den_error = error
        self.den_error = den_error
        self.bartype = bartype
        self.keep_zero = keep_zero

        _StyledItemMixin.__init__(self, style)

    def __repr__(self):
        return f"<RatioItem {self.bartype}: " \
               f"{', '.join(self.numerator)} / " \
               f"{', '.join(self.denominator)}>"

    def to_data(self):
        """Return a uhepp compliant version using dict and lists"""
        result = {
            "type": self.bartype,
            "error": self.error,
            "x_errorbar": self.x_errorbar,
            "keep_zero": self.keep_zero,
            "numerator": list(self.numerator),
        }

        if self.den_error != self.error:
            result["den_error"] = self.den_error

        if self.denominator:
            result["denominator"] = list(self.denominator)

        if self.style:
            result["style"] = self.style

        return result

    def vary(self):
        """See Yield.vary()"""
        raise NotImplementedError()

    def var_up(self):
        """See Yield.var_up()"""
        raise NotImplementedError()

    def var_down(self):
        """See Yield.var_down()"""
        raise NotImplementedError()

    def stat(self):
        """See Yield.stat()"""
        raise NotImplementedError()

    def syst(self):
        """See Yield.syst()"""
        raise NotImplementedError()

    def base(self):
        """See Yield.base()"""
        raise NotImplementedError()


class Graph(UHepPlotModel, _StyledItemMixin):
    """
    Representation of arbitrary graph lines or points

    The styles can be set or retrieved via properties. While setting an
    attribute, values are converted to the internal format, i.e. color names
    are converted to hex. If a style is not set, the corresponding attribute
    returns None.

    The complete set of styles can be retrieved via the style attribute. Unset
    attributes do not appear in the dict.

    Possible styles are:
      - linewidth (float)
      - linestyle (-- or - or -, or :)
      - color (matplotlib compliant)
      - makersize
      - marker

    Any legal matplotlib color might be used to set color attributes, although
    the uhepp standard only allows hex string. Internally, all colors are
    converted to hex strings.
    """
    VALID_STYLES = ["linestyle", "linewidth", "color", "edgecolor",
                    "makersize", "marker"]
    VALID_TYPES = ["points", "line"]

    def __init__(self, x_values, y_values, graphtype="points", label=None,
                 **style):
        """
        Create a new Graph object

        The position arguments marks the x-values and y-values of the line of
        points. The graphtype allows changing the default type from "points"
        to "line". Optionally, the label used in the legend and style options
        can be set.
        """
        self._x_values = None
        self._y_values = None
        self._x_errors = None
        self._y_errors = None

        self.x_values = to_python(x_values)
        self.y_values = to_python(y_values)
        self.label = label
        self._type = graphtype
        _StyledItemMixin.__init__(self, style)

    @property
    def x_values(self):
        """Return a copy of the x values"""
        return list(self._x_values)
    @x_values.setter
    def x_values(self, values):
        """Set the x values of the graph"""
        self._x_values = to_python(values)

    @property
    def y_values(self):
        """Return a copy of the y values"""
        return list(self._y_values)
    @y_values.setter
    def y_values(self, values):
        """Set the y values of the graph"""
        self._y_values = to_python(values)

    @property
    def x_errors(self):
        """Return a copy of the x errors"""
        if self._x_errors is None:
            return None
        return list(self._x_errors)

    @x_errors.setter
    def x_errors(self, errors):
        """Set the x errors of the graph"""
        if errors is None:
            self._x_errors = None
        else:
            self._x_errors = to_python(errors)

    @property
    def y_errors(self):
        """Return a copy of the y errors"""
        if self._y_errors is None:
            return None
        return list(self._y_errors)
    @y_errors.setter
    def y_errors(self, errors):
        """Set the y errors of the graph"""
        if errors is None:
            self._y_errors = None
        else:
            self._y_errors = to_python(errors)

    def to_data(self):
        """Return the graph object as python native dicts and lists"""
        result = {
            "x": self.x_values,
            "y": self.y_values,
        }
        if self.x_errors:
            result["x_errors"] = self.x_errors
        if self.y_errors:
            result["y_errors"] = self.y_errors
        if self.label:
            result["label"] = self.label
        if self.graphtype:
            result["type"] = self.graphtype
        if self.style:
            result["style"] = self.style
        return result

    @property
    def graphtype(self):
        """Type of the graph"""
        return self._type

    @graphtype.setter
    def graphtype(self, new_type):
        if new_type not in self.VALID_TYPES:
            raise ValueError(f"Invalid graph type: {new_type}")
        self._type = new_type

    def __repr__(self):
        """Return a string representation"""
        return f"<Graph {self.graphtype} n={len(self.x_values)}>"

class Line(UHepPlotModel, _StyledItemMixin):
    """
    Representation of vertical or horizontal lines

    The styles can be set or retrieved via properties. While setting an
    attribute, values are converted to the internal format, i.e. color names
    are converted to hex. If a style is not set, the corresponding attribute
    returns None.

    The complete set of styles can be retrieved via the style attribute. Unset
    attributes do not appear in the dict.

    Possible styles are:
      - linewidth (float)
      - linestyle (-- or - or -, or :)
      - color (matplotlib compliant)
      - edgecolor (matplotlib compliant)

    Any legal matplotlib color might be used to set color attributes, although
    the uhepp standard only allows hex string. Internally, all colors are
    converted to hex strings.
    """
    VALID_STYLES = ["linestyle", "linewidth", "color", "edgecolor"]

    def __init__(self, pos, stretch=None, **style):
        """
        Create a new Line object

        The position arguments marks the x-value (y-value) of a vertical
        (horizontal) line. The optional stretch argument is a pair defining
        the start and end values on the orthogonal axes.
        """
        self.pos = pos
        self.stretch = stretch
        _StyledItemMixin.__init__(self, style)


class VLine(Line):
    """A vertical line"""
    @property
    def pos_x(self):
        """The position on the x-axis of the line"""
        return self.pos

    @pos_x.setter
    def pos_x(self, pos_x):
        self.pos = pos_x

    def to_data(self):
        """Return a uhepp compatible dict/list version"""
        result = {"x": self.pos_x}

        if self.stretch:
            result["range"] = self.stretch
        if self.style:
            result["style"] = self.style

        return result

class HLine(Line):
    """Horizontal line"""
    @property
    def pos_y(self):
        """The position on the y-axis of the line"""
        return self.pos

    @pos_y.setter
    def pos_y(self, pos_y):
        self.pos = pos_y

    def to_data(self):
        """Return a uhepp compatible dict/list version"""
        result = {"y": self.pos_y}

        if self.stretch:
            result["range"] = self.stretch
        if self.style:
            result["style"] = self.style

        return result

class _AxisFormatter(ScalarFormatter):
    """Automatic axis scaling by 10^{..., -6, -3, 0, 3, 6, ...}"""
    def __init__(self, limit=4):
        """Create formatter and compute scaling"""
        super().__init__()
        self.set_useMathText(True)
        self.set_powerlimits((0, limit))
        self._limit = limit

    def _set_order_of_magnitude(self):
        """Compute module-3 order of magnitue"""
        super()._set_order_of_magnitude()
        self.orderOfMagnitude -= self.orderOfMagnitude % 3

    def get_dependent(self):
        """Return formatter for a dependent axis"""
        return _DependentFormatter(self, self._limit)

class _DependentFormatter(ScalarFormatter):
    """Axis scaling formatter driven by the scale of another axis"""
    def __init__(self, master, limit=4):
        """Create new dependent formatter"""
        super().__init__()
        self.set_powerlimits((0, limit))
        self._master = master

    def _set_order_of_magnitude(self):
        """Copy ordre of magnitue from master axis"""
        self._master._set_order_of_magnitude()  # pylint: disable=W0212
        self.orderOfMagnitude = self._master.orderOfMagnitude

    def get_offset(self):
        """Remove scaling label"""
        return ""


# pylint: disable=R0904
class UHeppHist(UHepPlotModel):
    """
    Uhepp Histogram class

    The class represents a typical stacked, HEP histogram including the style
    information and the raw bin contents and its uncertainty. The actual
    objects is composed of Stacks, RatioItems, Lines and Yield objects.
    """

    # pylint: disable=R0913
    def __init__(self, symbol, bin_edges, stacks=None, yields=None):
        """
        Create a new UHepp histogram.

        The mandatory argument bin_edges defines the boundary of all bins.
        Please not that regardless of plotting settings, yield objects contain
        additional bins to the left and right of the outer bins to account for
        underflow and overflow.

        Optional the constructor accepts a list of stacks, a list of ratio
        items and a dict mapping of yield names to yield objects.
        """
        self._version = "0.2"

        # Bins
        self.bin_edges = to_python(bin_edges)
        self.include_overflow = False
        self.include_underflow = False
        self.rebin_edges = None
        self.density_width = None

        # Badge
        self.brand = None
        self.brand_label = None
        self.subtext = None

        # metadata
        self.filename = "unnamed"
        self.energy = None
        self.date = self._now_iso()
        self.lumi = None
        self.author = None
        self.producer = None
        self.code_revision = None
        self.event_selection = None
        self.tags = {}

        # Variable
        self.symbol = symbol
        self.variable = None
        self.unit = None
        self.unit_in_brackets = None
        self.x_log = False

        # Stacks
        if stacks is None:
            stacks = []
        self.stacks = stacks

        # Ratio
        self.ratio = []

        # Lines
        self.h_lines = []
        self.v_lines = []

        # Ratio axis
        self.ratio_min = None
        self.ratio_max = None
        self.ratio_log = False
        self.ratio_label = None
        self.ratio_diff = False

        # Y axis
        self.y_min = None
        self.y_max = None
        self.y_log = False
        self.y_label = None

        # Yield
        if yields is None:
            yields = {}

        self.yields = yields

        # Graph
        self.graphs = []

        # Layout
        self.ratio_fraction = None
        self.figure_size = None

    def clone(self):
        """Return a deep copy of the histogram."""
        return from_jsons(self.to_jsons())

    @property
    def version(self):
        """The version of the uhepp specification"""
        return self._version

    @property
    def atlas(self):
        """True if the plot is ATLAS-branded"""
        return self.brand == "ATLAS"

    @version.setter
    def version(self, value):
        if float(value) >= 1:
            raise ValueError("Unsupported uhepp version")
        self._version = value


    def to_data(self):
        """Convert to uhepp compliant dicts and lists"""
        def filt(**kwds):
            """Filter None values"""
            return {k: v for k, v in kwds.items() if v is not None}

        result = {
            "version": self.version if self.version > "0.2" else "0.2",
            "type": "histogram",
            "metadata": dict(filename=self.filename,
                             date=self.date,
                             **filt(Ecm_TeV=self.energy,
                                    lumi_ifb=self.lumi,
                                    author=self.author,
                                    producer=self.producer,
                                    code_revision=self.code_revision,
                                    event_selection=self.event_selection,
                                    tags=self.tags)),
            "stacks": [stack.to_data() for stack in self.stacks],
            "ratio": [ratio_item.to_data() for ratio_item in self.ratio],
            "y_axis": filt(label=self.y_label,
                           min=self.y_min,
                           max=self.y_max),
            "badge": dict(brand=self.brand,
                          **filt(label=self.brand_label,
                                 subtext=self.subtext)),
            "ratio_axis": filt(label=self.ratio_label,
                               min=self.ratio_min,
                               max=self.ratio_max,
                               diff=self.ratio_diff,
                               log=self.ratio_log),
            "variable": dict(symbol=self.symbol,
                              **filt(unit=self.unit,
                                     unit_in_brackets=self.unit_in_brackets,
                                     name=self.variable)),
            "bins": dict(edges=self.bin_edges,
                         **filt(rebin=self.rebin_edges,
                                density_width=self.density_width)),
            "yields": {k: v.to_data() for k, v in self.yields.items()},
        }

        if self.include_underflow:
            result["bins"]["include_underflow"] = True
        if self.include_overflow:
            result["bins"]["include_overflow"] = True
        if self.x_log:
            result["variable"]["log"] = True
        if self.y_log:
            result.setdefault("y_axis", {})["log"] = True
        if self.v_lines:
            result["v_lines"] = [line.to_data() for line in self.v_lines]
        if self.h_lines:
            result["h_lines"] = [line.to_data() for line in self.h_lines]
        if self.figure_size is not None or self.ratio_fraction is not None:
            result["layout"] = filt(size=self.figure_size,
                                    ratio_fraction=self.ratio_fraction)
        if self.graphs:
            result["graphs"] = [graph.to_data() for graph in self.graphs]

        return result

    def to_yamls(self):
        """Convert the hist to a yaml-encoded string"""
        return yaml.dump(self.to_data(), sort_keys=True)

    def to_jsons(self):
        """Convert the hist to a json-encoded string"""
        return json.dumps(self.to_data(), sort_keys=True)

    def to_yaml(self, filename):
        """Convert the hist to a yaml-encoded file"""
        with open(filename, "w") as file_obj:
            yaml.dump(self.to_data(), file_obj, sort_keys=True)

    def to_json(self, filename):
        """Convert the hist to a json-encoded file"""
        with open(filename, "w") as file_obj:
            json.dump(self.to_data(), file_obj, sort_keys=True)

    @staticmethod
    def _now_iso():
        """Return the current time as iso string"""
        local_tz = get_localzone()
        return datetime.now(local_tz).isoformat()

    def get_base(self, name):
        """Return the rebinned yields for name"""
        variation = None
        if "/" in name:
            name, variation, updown = name.split("/")

        process = self.yields[name]
        if self.rebin_edges is not None:
            process = process.rebin(self.bin_edges, self.rebin_edges)

        if variation is None:
            return np.asarray(process.base)

        if updown == "up":
            return np.asarray(process.var_up(variation))

        if updown == "down":
            return np.asarray(process.var_down(variation))

        raise ValueError("Yield name with variation must end with "
                         "'/up' or '/down'")


    def get_stat(self, name):
        """Return the rebinned stat uncert for name"""
        is_variation =  "/" in name
        if is_variation:
            name = name.split("/")[0]

        process = self.yields[name]
        if self.rebin_edges is not None:
            process = process.rebin(self.bin_edges, self.rebin_edges)

        result = np.asarray(process.stat)
        if is_variation:
            result *= 0
        return result

    def get_syst(self, name):
        """Return the rebinned syst uncert for name"""
        is_variation =  "/" in name
        if is_variation:
            name = name.split("/")[0]

        process = self.yields[name]
        if self.rebin_edges is not None:
            process = process.rebin(self.bin_edges, self.rebin_edges)

        result = np.asarray(process.syst)
        if is_variation:
            result *= 0
        return result

    def render(self, filename=None):
        """
        Render the universal plot.

        The methods return the axes objecft. If the optional argument filename
        is set, the plot is written to the file.
        """
        # Handle range/bins
        bins = np.asarray(self.rebin_edges or self.bin_edges)
        bin_centers = (bins[1:] + bins[:-1]) / 2
        bin_widths = bins[1:] - bins[:-1]
        equidistant_bins = (len(np.unique(bin_widths)) == 1)

        def handle_outside(array, square=False):
            if self.include_underflow:
                array[1] += array[0]

            if self.include_overflow:
                array[-2] += array[-1]

            # Drop under- and overflow bins
            array = array[1:-1]

            # Normalize to density width
            if self.density_width:
                norm = bin_widths / self.density_width
                if square:
                    norm = norm**2

                array = array / norm
            return array

        # Handle axes, figure
        if self.figure_size is None:
            figure_size = (5, 5) if self.ratio else (5, 4.2)
        else:
            figure_size = tuple(self.figure_size)

        if self.ratio:
            # Make plot area (without enlargement) match golden ratio
            ratio_fraction = self.ratio_fraction
            if ratio_fraction is None:
                ratio_fraction = 1 / 4

            # Convert fraction of total height to main/ratio
            ratio_fraction = ratio_fraction / (1 - ratio_fraction)

            subplot_kwds = {
                "gridspec_kw": {"height_ratios": [1, ratio_fraction]},
                "figsize": figure_size,
                "sharex": True
            }
            figure, (axes, axes_ratio) = plt.subplots(2, 1,
                                                      **subplot_kwds)
            all_axes = [axes, axes_ratio]

        else:
            figure, axes = plt.subplots(figsize=figure_size)
            all_axes = [axes]

        max_content = 0
        stat_in_label = False

        total_items = sum(len(s.content) for s in self.stacks)
        counter = 0
        for stack in self.stacks:
            bottom = 0
            uncert2_up = 0
            uncert2_down = 0
            uncert_components = stack.error.split("+")
            for item in stack.content:
                counter += 1
                index = 1 + counter / total_items / 10

                histogram = 0
                for process_name in item.yield_names:
                    this_h = self.get_base(process_name)
                    histogram = histogram + handle_outside(this_h)

                    if "no" in uncert_components:
                        this_uncert2 = self.get_base(process_name) * 0
                        this_uncert2 = handle_outside(this_uncert2, True)
                        uncert2_up = uncert2_up + this_uncert2
                        uncert2_down = uncert2_down + this_uncert2
                    if "stat" in uncert_components:
                        this_uncert2 = self.get_stat(process_name)**2
                        this_uncert2 = handle_outside(this_uncert2, True)
                        uncert2_up = uncert2_up + this_uncert2
                        uncert2_down = uncert2_down + this_uncert2
                    if "syst" in uncert_components:
                        this_uncert2 = self.get_syst(process_name)**2
                        this_uncert2 = handle_outside(this_uncert2, True)
                        uncert2_up = uncert2_up + this_uncert2
                        uncert2_down = uncert2_down + this_uncert2
                    if "env" in uncert_components:
                        variations = self.yields[process_name].variations
                        for var_name in variations:
                            var_up_path = "%s/%s/up" % (process_name, var_name)
                            var_down_path = "%s/%s/down" % (process_name, var_name)

                            base = handle_outside(self.get_base(process_name))
                            v_up = handle_outside(self.get_base(var_up_path))
                            v_down = handle_outside(
                                self.get_base(var_down_path)
                            )

                            uncert2_up = uncert2_up + (v_up - base)**2
                            uncert2_down = uncert2_down + (base - v_down)**2


                # Draw process
                if stack.bartype == "points":
                    kwds = {'markersize': 4, 'fmt': 'o', 'color': 'k'}
                    UHeppHist._update_style(kwds, item.style)
                    uncertainty_up = np.sqrt(uncert2_up)
                    uncertainty_down = np.sqrt(uncert2_down)

                    if stack.keep_zero:
                        non_empty = ~np.isnan(histogram)
                    else:
                        non_empty = (histogram != 0) | (uncertainty_up + uncertainty_down != 0)

                    uncertainty = [uncertainty_down[non_empty],
                                   uncertainty_up[non_empty]]

                    x_errorbar = [(bin_widths / 2)[non_empty]]
                    if not stack.x_errorbar:
                        x_errorbar = []

                    axes.errorbar(bin_centers[non_empty],
                                  (bottom + histogram)[non_empty],
                                  uncertainty,
                                  *x_errorbar,  # might be empty if disabled
                                  zorder=index,
                                  label=item.label, **kwds)
                else:
                    kwds = {}
                    UHeppHist._update_style(kwds, item.style)
                    axes.hist(bin_centers, bins=bins, bottom=bottom,
                              label=item.label, weights=histogram,
                              histtype=stack.bartype,
                              zorder=index,
                              **kwds)

                bottom = bottom + histogram
            # (end of process loop)

            counter += 1
            index = 1 + counter / total_items / 10

            # Draw uncertainty band
            if stack.bartype != "points" and ((uncert2_up + uncert2_down) > 0).any():
                uncertainty_up = np.sqrt(uncert2_up)
                uncertainty_down = np.sqrt(uncert2_down)


                if stat_in_label:
                    label = None
                else:
                    label = UNCERTAINTY
                stat_in_label = True
                band_lower = bottom - uncertainty_down
                axes.hist(bin_centers, bins=bins, bottom=band_lower,
                          weights=uncertainty_up + uncertainty_down,
                          fill=False, linewidth=0,
                          hatch=HATCH_PATTERN, edgecolor=HATCH_COLOR,
                          zorder=index,
                          label=label)


            # Track highest point
            uncertainty = np.sqrt(uncert2_up)
            max_content = max(max_content, np.max(bottom + uncertainty))

        # Handle ratio plot
        if self.ratio:
            self._draw_ratio(axes_ratio)

        # Draw horizontal lines
        orig_lim = axes.get_xlim()
        for hline in self.h_lines:
            pos_y = hline.pos_y
            kwds = {'color': 'red'}
            UHeppHist._update_style(kwds, hline.style)

            x_range = hline.stretch or orig_lim
            axes.plot(x_range, [pos_y, pos_y], **kwds)

        # Draw vertical lines
        for this_ax in all_axes:
            orig_lim = this_ax.get_ylim()
            for vline in self.v_lines:
                pos_x = vline.pos_x
                kwds = {'color': 'red'}
                UHeppHist._update_style(kwds, vline.style)

                y_range = vline.stretch or orig_lim
                this_ax.plot([pos_x, pos_x], y_range, **kwds)

        # Draw graphs
        for graph in self.graphs:
            x_values = graph.x_values
            y_values = graph.y_values
            x_errors = graph.x_errors
            y_errors = graph.y_errors

            kwds = {"label": graph.label}
            UHeppHist._update_style(kwds, graph.style)

            if graph.graphtype == "points":
                kwds["fmt"] = "o"
                axes.errorbar(x_values, y_values, y_errors, x_errors, **kwds)
            else:
                axes.plot(x_values, y_values, **kwds)

        if (self.brand is not None) or (self.subtext is not False):
            pre_brand = atlasify.ATLAS
            if self.brand is not None:
                atlasify.ATLAS = self.brand
                label = self.brand_label or True
            else:
                label = None

            atlasify.atlasify(label, self.subtext, enlarge=1.0, axes=axes)
            atlasify.ATLAS = pre_brand

        # Configure x-axis
        axes.set_xlim((bins.min(), bins.max()))

        # Configure y-axis
        if self.y_log:
            y_min = self.y_min if self.y_min is not None else 1
            y_max = self.y_max if self.y_max is not None else 40 * max_content
            axes.set_yscale('log')
        else:
            y_min = self.y_min if self.y_min is not None else 0
            y_max = self.y_max if self.y_max is not None else 1.6 * max_content

        if y_min == 0 and y_max == 0:
            y_max = 1

        axes.set_ylim((y_min, y_max))

        kwds = {
            "frameon": False,
            "loc": 1,
            "bbox_to_anchor": LEGEND_ANCHOR,
        }
        if LEGEND_FONT_SIZE:
            kwds["prop"] = {"size": LEGEND_FONT_SIZE}

        leg_handles, leg_labels = axes.get_legend_handles_labels()
        axes.legend(leg_handles[::-1], leg_labels[::-1], **kwds)

        x_label_axes = axes_ratio if self.ratio else axes
        x_label_tokens = []
        if self.variable is not None:
            x_label_tokens.append(self.variable)

        x_label_tokens.append(self.symbol)

        if self.unit is not None:
            if self.unit_in_brackets:
                x_label_tokens.extend(["[" + self.unit + "]"])
            else:
                x_label_tokens.extend(["/", self.unit])

        x_label_axes.set_xlabel(" ".join(x_label_tokens),
                                horizontalalignment='right', x=X_ALIGN)

        # subject = "Fraction" if density else "Events"
        y_label_tokens = ["Events", "/"]
        if self.density_width or equidistant_bins:
            if self.density_width:
                y_label_tokens.append("%g" % self.density_width)
            else:
                y_label_tokens.append("%g" % (bins[1] - bins[0]))

            if self.unit is not None:
                y_label_tokens.append(self.unit)
        else:
            y_label_tokens.append("Bin")

        if not self.y_label:
            axes.set_ylabel(" ".join(y_label_tokens),
                            horizontalalignment='right', y=Y_ALIGN)
        else:
            axes.set_ylabel(self.y_label,
                            horizontalalignment='right', y=Y_ALIGN)

        for this_ax in all_axes:
            this_ax.tick_params("both", which="both", direction="in")
            this_ax.tick_params("both", which="major",
                                length=MAJOR_TICK_LENGTH)
            this_ax.tick_params("both", which="minor",
                                length=MINOR_TICK_LENGTH)
            this_ax.tick_params("x", which="both", top=True)
            this_ax.tick_params("y", which="both", right=True)
            this_ax.xaxis.set_minor_locator(AutoMinorLocator())

        if not self.y_log:
            axes.yaxis.set_minor_locator(AutoMinorLocator())

            if AUTOMATRIC_AXIS_SCALING:
                fmttr = _AxisFormatter()
                axes.yaxis.set_major_formatter(fmttr)
                if self.ratio:
                    axes_ratio.yaxis.set_major_formatter(fmttr.get_dependent())


        figure.tight_layout()

        if self.ratio:
            figure.subplots_adjust(hspace=0.025)

        if filename:
            figure.savefig(filename, dpi=300)

        if self.ratio:
            return figure, (axes, axes_ratio)

        return figure, axes

    def _draw_ratio(self, axes_ratio):

        for index, item in enumerate(self.ratio):
            index = 1 + index / len(self.ratio) / 10
            num_hist = 0
            num_uncert2_up = 0
            num_uncert2_down = 0
            uncert_components = item.error.split("+")
            for process_name in item.numerator:
                num_hist = num_hist + self.get_base(process_name)

                if "no" in uncert_components:
                    num_uncert2_up = num_uncert2_up + self.get_base(process_name) * 0
                    num_uncert2_down = num_uncert2_down + self.get_base(process_name) * 0
                if "stat" in uncert_components:
                    num_uncert2_up = num_uncert2_up + self.get_stat(process_name)**2
                    num_uncert2_down = num_uncert2_down + self.get_stat(process_name)**2
                if "syst" in uncert_components:
                    num_uncert2_up = num_uncert2_up + self.get_syst(process_name)**2
                    num_uncert2_down = num_uncert2_down + self.get_syst(process_name)**2
                if "env" in uncert_components:
                    variations = self.yields[process_name].variations
                    for var_name in variations:
                        base = self.get_base(process_name)
                        var_up_path = "%s/%s/up" % (process_name, var_name)
                        var_down_path = "%s/%s/down" % (process_name, var_name)

                        diff_up = self.get_base(var_up_path) - base
                        num_uncert2_up  = num_uncert2_up + diff_up**2
                        diff_down = base - self.get_base(var_down_path)
                        num_uncert2_down = num_uncert2_down + diff_down**2

            den_hist = 0
            den_uncert2_up = 0
            den_uncert2_down = 0
            uncert_components = item.den_error.split("+")
            for process_name in item.denominator:
                den_hist = den_hist + self.get_base(process_name)

                if "no" in uncert_components:
                    den_uncert2_up = den_uncert2_up + self.get_base(process_name) * 0
                    den_uncert2_down = den_uncert2_down + self.get_base(process_name) * 0
                if "stat" in uncert_components:
                    den_uncert2_up = den_uncert2_up + self.get_stat(process_name)**2
                    den_uncert2_down = den_uncert2_down + self.get_stat(process_name)**2
                if "syst" in uncert_components:
                    den_uncert2_up = den_uncert2_up + self.get_syst(process_name)**2
                    den_uncert2_down = den_uncert2_down + self.get_syst(process_name)**2
                if "env" in uncert_components:
                    variations = self.yields[process_name].variations
                    for var_name in variations:
                        base = self.get_base(process_name)
                        var_up_path = "%s/%s/up" % (process_name, var_name)
                        var_down_path = "%s/%s/down" % (process_name, var_name)

                        diff_up = self.get_base(var_up_path) - base
                        den_uncert2_up  = den_uncert2_up + diff_up**2
                        diff_down = base - self.get_base(var_down_path)
                        den_uncert2_down = den_uncert2_down + diff_down**2

            if self.include_underflow:
                den_hist[1] += den_hist[0]
                num_hist[1] += num_hist[0]
                den_uncert2_up[1] += den_uncert2_up[0]
                den_uncert2_down[1] += den_uncert2_down[0]
                num_uncert2_up[1] += num_uncert2_up[0]
                num_uncert2_down[1] += num_uncert2_down[0]

            if self.include_overflow:
                den_hist[-2] += den_hist[-1]
                num_hist[-2] += num_hist[-1]
                den_uncert2_up[-2] += den_uncert2_up[-1]
                den_uncert2_down[-2] += den_uncert2_down[-1]
                num_uncert2_up[-2] += num_uncert2_up[-1]
                num_uncert2_down[-2] += num_uncert2_down[-1]

            # Drop under- and overflow bins
            den_hist = den_hist[1:-1]
            num_hist = num_hist[1:-1]
            den_uncert2_up = den_uncert2_up[1:-1]
            den_uncert2_down = den_uncert2_down[1:-1]
            num_uncert2_up = num_uncert2_up[1:-1]
            num_uncert2_down = num_uncert2_down[1:-1]

            den_uncert_up = np.sqrt(den_uncert2_up)
            den_uncert_down = np.sqrt(den_uncert2_down)
            num_uncert_up = np.sqrt(num_uncert2_up)
            num_uncert_down = np.sqrt(num_uncert2_down)

            # Draw
            if item.bartype == "points":
                # valid bins with non-zero denominator
                if item.keep_zero:
                    non_empty = ~np.isnan(num_hist)
                else:
                    non_empty = (num_hist != 0) | (num_uncert_up + num_uncert_down != 0)
                if not self.ratio_diff:
                    non_empty *= (den_hist != 0)

                bins = np.asarray(self.rebin_edges or self.bin_edges)
                bin_centers = ((bins[1:] + bins[:-1]) / 2)
                bin_widths = (bins[1:] - bins[:-1])

                bin_centers = bin_centers[non_empty]
                bin_widths = bin_widths[non_empty]

                if self.ratio_diff:
                    ratio = num_hist[non_empty] - den_hist[non_empty]
                    ratio_uncert_up = num_uncert_up[non_empty]
                    ratio_uncert_down = num_uncert_down[non_empty]
                else:
                    ratio = num_hist[non_empty] / den_hist[non_empty]
                    ratio_uncert_up = num_uncert_up[non_empty] / den_hist[non_empty]
                    ratio_uncert_down = num_uncert_down[non_empty] / den_hist[non_empty]

                kwds = {'markersize': 4, 'fmt': 'o', 'color': 'k'}
                UHeppHist._update_style(kwds, item.style)

                x_errorbar = [bin_widths / 2]
                if not item.x_errorbar:
                    x_errorbar = []

                axes_ratio.errorbar(bin_centers,
                                    ratio,
                                    [ratio_uncert_down, ratio_uncert_up],
                                    *x_errorbar,  # might be empty if disabled
                                    zorder=index,
                                    **kwds)
            else:
                # valid bins with non-zero denominator
                non_empty = (den_hist != 0)
                if self.ratio_diff:
                    non_empty = (num_hist != 0)

                bins = np.asarray(self.rebin_edges or self.bin_edges)
                bin_centers = ((bins[1:] + bins[:-1]) / 2)
                bin_widths = (bins[1:] - bins[:-1])

                bottom = 0
                if self.ratio_diff:
                    ratio = num_hist - den_hist
                    ratio_uncert_up = num_uncert_up
                    ratio_uncert_down = num_uncert_down
                else:
                    den_hist[~non_empty] = 1
                    ratio = num_hist / den_hist
                    ratio_uncert_up = num_uncert_up / den_hist
                    ratio_uncert_down = num_uncert_down / den_hist

                    ratio[~non_empty] = 1
                    ratio_uncert_up[~non_empty] = 0
                    ratio_uncert_down[~non_empty] = 0

                    if item.bartype == "stepfilled":
                        bottom = 1

                kwds = dict(linewidth=1.2)
                UHeppHist._update_style(kwds, item.style)

                axes_ratio.hist(bin_centers, bins=bins,
                                weights=ratio - bottom,
                                histtype=item.bartype,
                                zorder=index,
                                bottom=bottom,
                                **kwds)

                # Draw uncertainty band
                if (ratio_uncert_up + ratio_uncert_down > 0).any():
                    band_lower = ratio - ratio_uncert_down
                    axes_ratio.hist(bin_centers, bins=bins, bottom=band_lower,
                                    weights=ratio_uncert_down + ratio_uncert_up,
                                    fill=False, linewidth=0,
                                    zorder=index,
                                    hatch=HATCH_PATTERN, edgecolor=HATCH_COLOR)

            if self.ratio_diff:
                non_empty = np.ones(len(num_hist), dtype='bool')
                rel_error_up = den_uncert_up
                rel_error_down = den_uncert_down
                band_lower = 0 - rel_error_down
            else:
                non_empty = (den_hist != 0)
                den_hist[~non_empty] = 1
                num_uncert_up[non_empty] = 0
                num_uncert_down[non_empty] = 0
                rel_error_up = den_uncert_up / den_hist
                rel_error_down = den_uncert_down / den_hist
                band_lower = 1 - rel_error_down

            axes_ratio.hist(bins[:-1][non_empty],
                            bins=bins,
                            bottom=band_lower,
                            weights=(rel_error_down + rel_error_up)[non_empty],
                            fill=False, linewidth=0,
                            zorder=index,
                            hatch=HATCH_PATTERN, edgecolor=HATCH_COLOR)

        if self.ratio_diff:
            r_min, r_max = axes_ratio.get_ylim()
            r_min = self.ratio_min if self.ratio_min is not None else r_min
            r_max = self.ratio_max if self.ratio_max is not None else r_max
        else:
            r_min = self.ratio_min if self.ratio_min is not None else 0.4
            r_max = self.ratio_max if self.ratio_max is not None else 1.6

        axes_ratio.set_ylim((r_min, r_max))

        if self.ratio_label is not None:
            axes_ratio.set_ylabel(self.ratio_label)

    @staticmethod
    def _update_style(kwds, style):
        """Map and apply valid styles to kwds"""

        names = {"linestyle": "linestyle",
                 "linewidth": "linewidth",
                 "markersize": "markersize",
                 "edgecolor": "edgecolor",
                 "marker": "marker",
                 "color": "color"}

        for key, value in style.items():
            if key in names:
                kwds[names[key]] = value


    def __repr__(self):
        label_token = []
        if self.variable is not None:
            label_token.append(self.variable)

        label_token.append(self.symbol)

        return f"<UHepHist: {' '.join(label_token)} = " \
               f"{min(self.bin_edges)}..{max(self.bin_edges)}, " \
               f"n={len(self.bin_edges) + 1}>"


    def push(self, collection_id, api_url=None, api_key=None):
        """Upload the plot object to a central server"""
        if api_url is None:
            api_url = os.environ.get("UHEPP_API", DEFAULT_API)

        if api_key is None:
            api_key = os.environ.get("UHEPP_TOKEN", None)

        headers = {}
        if api_key is not None:
            headers["Authorization"] = f"Token {api_key}"

        data = {
            'uhepp': self.to_data(),
            'collection': urljoin(api_url, f"collections/{collection_id}/")
        }

        response = requests.post(urljoin(api_url, "plots/"),
                                 json=data,
                                 headers=headers)

        if not response.ok:
            raise RuntimeError(f"Publishing failed: {response.status_code}")

        if "Location" not in response.headers:
            raise RuntimeError("Resource location not in server response")

        if "Link" not in response.headers:
            raise RuntimeError("UI Link not in server response (1)")

        links = requests.utils.parse_header_links(response.headers["Link"])
        links = [link for link in links if link["rel"] == "ui"]

        if not links:
            raise RuntimeError("UI Link not in server response (2)")

        json_data = response.json()
        uuid = json_data["uuid"]

        return PushReceipt(response.headers["Location"],
                              links[0]["url"],
                              uuid)

    def show(self):
        """Render the plot and show it"""
        fig, _ = self.render()
        fig.show()

def pull(uuid, api_url=None, api_key=None, full_link=None):
    """Retrieve a :class:`UHepPlot` from a central server"""
    if api_key is None:
        api_key = os.environ.get("UHEPP_TOKEN", None)

    headers = {}
    if api_key is not None:
        headers["Authorization"] = f"Token {api_key}"

    if full_link is None:
        if api_url is None:
            api_url = os.environ.get("UHEPP_API", DEFAULT_API)
        api_url = urljoin(api_url, "plots/")
        full_link = urljoin(api_url, uuid)

    response = requests.get(full_link, headers=headers)

    if not response.ok:
        raise RuntimeError(f"Receiving failed: {response.status_code}")

    json_data = response.json()
    return from_data(json_data["uhepp"])

def pull_collection(collection_id, api_url=None, api_key=None):
    """Retrieve a collection of UHepPlot from a central server"""
    if api_key is None:
        api_key = os.environ.get("UHEPP_TOKEN", None)

    headers = {}
    if api_key is not None:
        headers["Authorization"] = f"Token {api_key}"

    if api_url is None:
        api_url = os.environ.get("UHEPP_API", DEFAULT_API)

    headers = {"Authorization": f"Token {api_key}"}
    collection_url = urljoin(api_url, f"collections/{collection_id}")
    response = requests.get(collection_url, headers=headers)

    if not response.ok:
        raise RuntimeError(f"Receiving failed: {response.status_code}")

    json_data = response.json()
    plots = json_data["plots"]

    return [pull(None, api_url, api_key, url) for url in plots]

class PushReceipt(UHepPlotModel):
    """
    A PushReceipt stores the confirmation that a plot has been uploaded to
    a central server. The object also contains the human-readable web endpoint
    at the central server.
    """
    def __init__(self, api_url, ui_url, uuid):
        self.api_url = api_url
        self.ui_url = ui_url
        self.uuid = uuid

    def __repr__(self):
        return self.ui_url
