import random
import os
from typing import List, Optional, Dict, Iterable, Union, Callable
import numpy as np
import pandas as pd

from lark import Lark, Tree, Token

import feyn
import _feyn
from feyn.losses import _get_loss_function

from ._program import Program
from ._httpclient import HttpClient

from feyn._typings import check_types

DIR, _ = os.path.split(__file__)
QUERY_GRAMMAR = os.path.join(DIR, "qlang/query_grammar.lark")


class Operator:
    def __init__(self, spec):
        self.spec = spec
        self.arity = len(self.spec.split("(")[1].split(")")[0].split(","))
        self.name = ""

    def __repr__(self):
        return f"<Operator {self.spec}>"

    def __eq__(self, other: "Operator") -> bool:
        return self.spec == other.spec


class Input:
    def __init__(self, name):
        self.name = name
        self.spec = "in:"
        self.arity = 0

    def __repr__(self):
        return f"<Input {self.name}>"

    def __eq__(self, other: "Input") -> bool:
        return self.name == other.name


class Output:
    def __init__(self, name):
        self.name = name
        self.spec = "out:linear(i)->f"
        self.arity = 1

    def __repr__(self):
        return f"<Output {self.name}>"


class Context:
    PARSER = Lark.open(QUERY_GRAMMAR, start="expr", parser="lalr")
    SPECIAL_OPCODES = {
        "register_any": 0,
        "interact1": 1,
        "interact2": 2,
        "wildcard": 3,
        "exclude": 4,
        # 50-80 are also reserved
    }

    def __init__(self, specs, input_names):
        self.arity_map = {}

        for name in input_names:
            self.arity_map.setdefault(0, []).append(Input(name))

        for spec in specs:
            if spec.find("b") == -1:
                op = Operator(spec)
                self.arity_map.setdefault(op.arity, []).append(op)

    def fname_opcode(self, fname: str, arity: int) -> int:
        """Recover the opcode of 'fname' with arity 'arity'."""
        assert arity <= 2
        if arity == 0:
            base = 10000
            obj = Input(fname)
        else:
            base = arity * 1000
            obj = Operator(f"cell:{fname}(i)->i") if arity == 1 else Operator(f"cell:{fname}(i,i)->i")
        try:
            return base + self.arity_map[arity].index(obj)
        except ValueError:
            raise ValueError(f"Unaware of '{fname}' with arity {arity} in the context.")

    def translate_ast(self, ast) -> int:
        """Translate a node in a lark AST to an opcode."""
        if isinstance(ast, Token):
            return self.fname_opcode(ast.value.strip("\"'"), 0)

        dat = ast.data
        if dat in Context.SPECIAL_OPCODES:
            return Context.SPECIAL_OPCODES[dat]
        if dat == "expr":
            return self.fname_opcode("add", 2)
        if dat == "term":
            return self.fname_opcode("multiply", 2)

        return self.fname_opcode(dat, len(ast.children))

    def query_to_program(self, user_query: str) -> Program:
        """Convert a user-written query into the program representation."""
        res_codes = []
        ast = Context.PARSER.parse(user_query)

        def _recurse(node):
            nonlocal res_codes
            if isinstance(node, Tree) and node.data == "wildcard":
                wc_codes = [Context.SPECIAL_OPCODES["wildcard"]]
                edges = 80

                for child in node.children:
                    if isinstance(child, Tree):
                        wc_codes.append(Context.SPECIAL_OPCODES["exclude"])
                        wc_codes.append(self.translate_ast(child.children[0]))
                    elif child.type in ["SINGLE_ESCAPED_STRING", "DOUBLE_ESCAPED_STRING"]:
                        wc_codes.append(self.fname_opcode(child.value.strip("\"'"), 0))
                    else:
                        edges = min(eval(child.value) + 50, 80)

                wc_codes.append(edges)
                res_codes += wc_codes
                return

            res_codes.append(self.translate_ast(node))
            if isinstance(node, Tree):
                nchildren = len(node.children)
                if nchildren:
                    _recurse(node.children[0])
                if nchildren == 2:
                    _recurse(node.children[1])
                if nchildren > 2:
                    _recurse(Tree(node.data, node.children[1:]))

        _recurse(ast)
        all_codes = sum([self.get_codes(i) for i in range(3)], [])
        noncoding = [random.choice(all_codes) for _ in range(Program.SIZE - len(res_codes))]

        p = Program(res_codes + noncoding)
        p.qid = -1
        return p

    def lookup(self, code: int):
        arity = Program.arity_of(code)
        base = 10000 if arity == 0 else arity * 1000
        m = self.arity_map[arity]
        return m[code - base]

    def get_codes(self, arity):
        m = self.arity_map[arity]
        return [Program.from_arity_and_index(arity, ix) for ix in range(len(m))]

    def to_model(self, program, output_name, stypes={}):
        l = len(program)
        if l == 0:
            # Invalid program
            return None

        model = feyn.Model(l + 1)

        for ix in range(l):
            code = program[ix]
            op = self.lookup(code)
            arity = program.arity_at(ix)
            if arity == 0:
                stype = stypes.get(op.name, "f")
                if stype in ["c", "cat", "categorical"]:
                    op.spec = "in:cat(c)->i"
                else:
                    op.spec = "in:linear(f)->i"

            reverse_ix = l - ix - 1
            model[reverse_ix] = _feyn.Interaction(op.spec, (ix, code, 0), None, op.name)

            if arity > 0:
                model[reverse_ix]._set_source(0, reverse_ix - 1)
            if arity > 1:
                offset = program.find_end(ix + 1) - ix
                model[reverse_ix]._set_source(1, reverse_ix - offset)

        stype = stypes.get(output_name, "f")
        if stype in ("b"):
            output_spec = "out:lr(i)->b"
        else:
            output_spec = "out:linear(i)->f"

        model[l] = _feyn.Interaction(output_spec, (-1, 0, 0), None, output_name)
        model[l]._set_source(0, l - 1)
        return model


class QLNew:
    def __init__(self, cfg):
        """Construct a new 'QLattice' object."""
        headers = {
            "Authorization": f'Bearer {cfg.api_token or "none"}',
            "User-Agent": f"feyn/{feyn.__version__}",
        }

        qlattice_server = cfg.server.rstrip("/")
        api_base_url = f"{qlattice_server}/api/v2/qlattice/{cfg.qlattice}"
        self._qlattice_id = cfg.qlattice
        self._http_client = HttpClient(api_base_url, headers)

    def update(self, models):
        """Update QLattice with learnings from a list of models. When updated, the QLattice learns to produce models that are similar to what is included in the update. Without updating, the QLattice will keep generating models with a random structure.

        Arguments:
            models {Union[Model, Iterable[Model]]} -- The models to use in a QLattice update.

        Raises:
            TypeError: if inputs don't match the correct type.
        """
        programs_json = []
        for m in models:
            p = m._program
            programs_json.append(p.to_json())

        req = self._http_client.post("/update", json={"programs": programs_json})

        if req.status_code == 422:
            raise ValueError(req.text)

        req.raise_for_status()

    @check_types(exceptions=["stypes"])
    def sample_models(
        self,
        input_names: Iterable[str],
        output_name: str,
        kind: str = "regression",
        stypes: Optional[Dict[str, str]] = {},
        max_complexity: int = 10,
        query_string: Optional[str] = None,
        function_names: Optional[List[str]] = None,
    ) -> List[feyn.Model]:
        """
        Sample models from the QLattice simulator. The QLattice has a probability density for generating different models, and this function samples from that density.

        Arguments:
            input_names {List[str]} -- The names of the input features.
            output_name {str} -- The name of the output feature.

        Keyword Arguments:
            kind {str} -- Specify the kind of models that are sampled. One of ["classification", "regression"]. (default: {"regression"})
            stypes {Optional[Dict[str, str]]} -- An optional map from feature names to semantic types. (default: {None})
            max_complexity {int} -- The maximum complexity for sampled models. Currently the maximum number of edges that the graph representation of the models has. (default: {10})
            query_string {Optional[str]} -- An optional query string for specifying specific model structures. (default: {None})
            function_names {Optional[List[str]]} -- A list of function names to use in the QLattice simulation. Defaults to all available functions being used. (default: {None})

        Raises:
            TypeError: if inputs don't match the correct type.
            ValueError: if input_names contains duplicates.
            ValueError: if max_complexity is negative.
            ValueError: if kind is not a regressor or classifier.
            ValueError: if function_names is not recognised.

        Returns:
            List[Model] -- The list of sampled models.
        """
        if len(input_names) == 0:
            raise ValueError("input_names cannot be empty.")
        if len(list(input_names)) != len(set(input_names)):
            raise ValueError("input_names must consist of only unique values.")
        if max_complexity <= 0:
            raise ValueError(f"max_complexity must be greater than 0, but was {max_complexity}.")

        stypes = stypes or {}
        stypes[output_name] = _kind_to_output_stype(kind)

        regmap = {}
        for reg in input_names:
            stype = stypes.get(reg, "f")

            if stype in ["cat", "categorical"]:
                stype = "c"
            if stype in ["float", "numerical"]:
                stype = "f"
            if reg == output_name:
                pattern = f"out:*(*)->{stype}"
            else:
                pattern = f"in:*({stype})->*"

            regmap[reg] = pattern

        self.context = Context(
            _build_spec_list(function_names),
            [name for name in input_names if name != output_name],
        )

        res = []
        ar0_codes = self.context.get_codes(0)
        ar1_codes = self.context.get_codes(1)
        ar2_codes = self.context.get_codes(2)

        if query_string is not None:
            qp = self.context.query_to_program(query_string)
            query_program = qp.to_json()
        else:
            query_program = {}

        req = self._http_client.post(
            "/generate",
            json={
                "ar0_codes": ar0_codes,
                "ar1_codes": ar1_codes,
                "ar2_codes": ar2_codes,
                "max_complexity": max_complexity,
                "output_name": output_name,
                "query_program": query_program,
            },
        )

        if req.status_code == 422:
            raise ValueError(req.text)

        req.raise_for_status()

        programs = []
        for json in req.json()["programs"]:
            p = Program(json["codes"])
            p.data = json["data"]
            p.qid = json["qid"]
            programs.append(p)

        for p in programs:
            model = self.context.to_model(p, output_name=output_name, stypes=stypes)
            if model is None:
                # Silently ignore invalid programs
                continue

            model._qid = p.qid
            model._program = p

            res.append(model)

        return res

    def reset(self, random_seed=-1):
        """Clear all learnings in this QLattice.

        Keyword Arguments:
            random_seed {int} -- If not -1, seed the qlattice and feyn random number generator to get reproducible results. (default: {-1})
        """
        req = self._http_client.post("/reset", json={"seed": random_seed})
        req.raise_for_status()

        if random_seed != -1:
            np.random.seed(random_seed)
            _feyn.srand(random_seed)

        self.context = None

    @check_types()
    def auto_run(
        self,
        data: pd.DataFrame,
        output_name: str,
        kind: str = "regression",
        stypes: Optional[Dict[str, str]] = None,
        n_epochs: int = 10,
        threads: Union[int, str] = "auto",
        max_complexity: int = 10,
        query_string: Optional[str] = None,
        loss_function: Optional[Union[str, Callable]] = None,
        criterion: Optional[str] = None,
        sample_weights: Optional[Iterable[float]] = None,
        function_names: Optional[List[str]] = None,
        starting_models: Optional[List[feyn.Model]] = None,
    ) -> List[feyn.Model]:
        """A convenience function for running the QLattice simulator for many epochs. This process can be interrupted with a KeyboardInterrupt, and you will get back the best models that have been found thus far. Roughly equivalent to the following:

        >>> models = []
        >>> for i in range(n_epochs):
        >>>     models += ql.sample_models(data, output_name, kind, stypes, max_complexity, query_string, function_names)
        >>>     models = feyn.fit_models(models, data, loss_function, criterion, None, sample_weights)
        >>>     models = feyn.prune_models(models)
        >>>     best = feyn.best_diverse_models(models)
        >>>     ql.update(best)

        Arguments:
            data {Iterable} -- The data to train models on. Feature names are inferred from the columns (pd.DataFrame) or keys (dict) of this variable.
            output_name {str} -- The name of the output feature.

        Keyword Arguments:
            kind {str} -- Specify the kind of models that are sampled. One of ["classification", "regression"]. (default: {"regression"})
            stypes {Optional[Dict[str, str]]} -- An optional map from feature names to semantic types. (default: {None})
            n_epochs {int} -- Number of training epochs. (default: {10})
            threads {int} -- Number of concurrent threads to use for fitting. If a number, that many threads are used. If "auto", set to your CPU count - 1. (default: {"auto"})
            max_complexity {int} -- The maximum complexity for sampled models. (default: {10})
            query_string {Optional[str]} -- An optional query string for specifying specific model structures. (default: {None})
            loss_function {Optional[Union[str, Callable]]} -- The loss function to optimize models for. If None (default), 'MSE' is chosen for regression problems and 'binary_cross_entropy' for classification problems. (default: {None})
            criterion {Optional[str]} -- Sort by information criterion rather than loss. Either "aic", "bic" or None. (default: {None})
            sample_weights {Optional[Iterable[float]]} -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample. (default: {None})
            function_names {Optional[List[str]]} -- A list of function names to use in the QLattice simulation. Defaults to all available functions being used. (default: {None})
            starting_models {Optional[List[feyn.Model]]} -- A list of preexisting feyn models you would like to start finding better models from. The inputs and output of these models should match the other arguments to this function. (default: {None})

        Raises:
            TypeError: if inputs don't match the correct type.

        Returns:
            List[feyn.Model] -- The best models found during this run.
        """
        if loss_function is None:
            output_type = _kind_to_output_stype(kind)
            loss_function = _get_loss_function(output_type)

        if threads == "auto":
            # TODO: Is this sane?
            found = os.cpu_count()
            if found is None:
                threads = 4
            else:
                threads = os.cpu_count() - 1

        # TODO: Make immutable copy of starting models
        models = starting_models or []
        m_count = len(models)

        try:
            for i in range(n_epochs):
                new_sample = self.sample_models(
                    data,
                    output_name,
                    kind,
                    stypes,
                    max_complexity,
                    query_string,
                    function_names,
                )
                models += new_sample
                m_count += len(new_sample)

                models = feyn.fit_models(models, data, loss_function, criterion, None, sample_weights)
                models = feyn.prune_models(models)

                feyn.show_model(
                    models[0],
                    f"Epoch no. {i+1} - Tried {m_count} models - Best loss: {models[0].loss_value:.2e}",
                    update_display=True,
                )

                best = feyn.best_diverse_models(models)
                self.update(best)
            return best
        except KeyboardInterrupt:
            return feyn.best_diverse_models(models)
        except Exception as ex:
            raise ex


def _kind_to_output_stype(kind: str) -> str:
    """Parse kind into an output spec for the QLattice."""
    if kind in ["regression", "regressor"]:
        return "f"
    if kind in ["classification", "classifier"]:
        return "b"
    raise ValueError("Model kind not understood. Please choose either a 'regression' or a 'classification'.")


def _build_spec_list(fnames: List[str]) -> List[str]:
    """From a list of function names, build a list of specs for the simulator."""
    all_specs = [spec for spec in _feyn.get_specs() if spec.startswith("cell:")]
    if not fnames:
        return all_specs

    ret = []
    for spec_str in all_specs:
        if _spec_to_fname(spec_str) in fnames:
            ret.append(spec_str)

    for name in fnames:
        if name not in list(map(_spec_to_fname, ret)):
            raise ValueError(f"Do not recognise {name} as a valid function name")

    return ret


def _spec_to_fname(spec: str) -> str:
    """Separate a function name from a QLattice spec."""
    return spec.split(":")[1].split("(")[0]
