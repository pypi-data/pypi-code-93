# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import copy
from logging import warning
from types import SimpleNamespace
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

from pysat.formula import WCNFPlus

from portmod.config.mask import get_masked, get_unmasked
from portmod.config.use import get_forced_use
from portmod.loader import load_pkg, load_pkg_fq
from portmod.pybuild import Pybuild
from portmodlib.atom import Atom, FQAtom, QualifiedAtom, atom_sat
from portmodlib.colour import blue, green
from portmodlib.usestr import human_readable_required_use, parse_usestr

from .tokens import expand_use_conditionals, negate, token_conflicts


class Target(SimpleNamespace):
    def __init__(self, pkgs: List[Pybuild], atom: Atom, source: Optional[str]):
        self.pkgs = pkgs
        self.atom = atom
        self.source = source


class Formula:
    """
    Intermediate representation of the integer WCNFPlus SAT formula accepted by pysat

    All flags are disabled by prepending a "-"

    Atom requirements are represented by the fully qualified atom,
    as produced by mod.ATOM

    Use flag requirements are represented by the fully qualified atom
    of the mod they apply to, followed by [flag]

    Custom variables are prefixed by an underscore and are
    used only for the calculation and ignored in the output
    """

    __i = 1  # Integer counter, for the numerical equivalent of tokens
    __j = 1  # Variable name counter.
    __numcache: Dict[str, int] = {}  # Strings are
    __stringcache: Dict[int, str] = {}
    __variabledesc: Dict[str, str] = {}

    class Clause:
        """Generic clause type"""

        def __init__(self, clause: Iterable[str]):
            self.requirements: Set[str] = set()
            self.clause = clause
            self.intclause: Optional[Iterable[int]] = None

        def str2num(self):
            """
            Converts the tokens in the clause to integers for use with pysat
            """
            result = copy.copy(self)
            result.intclause = list(map(Formula.getnum, self.clause))
            return result

        def sourceatom(self) -> Optional[Atom]:
            return None

    class MetaClause(Clause):
        def __init__(
            self,
            source: Optional[str],
            desc: Optional[str],
            clause: Iterable[str],
            weight: Optional[int],
            atmost: Optional[int],
        ):
            self.source = source
            self.desc = desc
            self.clause = clause
            self.weight = weight
            self.atmost = atmost
            self.requirements: Set[str] = set()

        def __str__(self):
            return f"{self.source} - {self.desc}"

        def sourceatom(self) -> Optional[Atom]:
            if isinstance(self.source, Atom):
                return self.source
            return None

    class DepClause(Clause):
        def __init__(self, source: str, clause: Iterable[str], dependency: Atom):
            super().__init__(clause)
            self.source = source
            self.dependency = dependency

        def __str__(self):
            return f"{green(self.dependency)}: required by {green(self.source)}"

        def blocks(self, model: Set[str], clause: "Formula.MetaClause") -> bool:
            if isinstance(clause, Formula.BlockerClause):
                if atom_sat(self.dependency, clause.blocked) and all(
                    req in model for req in self.requirements
                ):
                    return True

            return False

        def sourceatom(self) -> Optional[Atom]:
            if isinstance(self.source, Atom):
                return self.source
            return None

    class BlockerClause(Clause):
        def __init__(self, source: str, clause: Iterable[str], blocked: Atom):
            super().__init__(clause)
            self.source = source
            self.blocked = blocked

        def __str__(self):
            return f"{green(self.blocked)}: blocked by {green(self.source)}"

        def blocks(self, model: Set[str], clause: "Formula.MetaClause") -> bool:
            if isinstance(clause, Formula.DepClause):
                if atom_sat(self.blocked, clause.dependency) and all(
                    req in model for req in self.requirements
                ):
                    return True

            return False

        def sourceatom(self) -> Optional[Atom]:
            if isinstance(self.source, Atom):
                return self.source
            return None

    class UseDepClause(Clause):
        def __init__(
            self, source: str, clause: Iterable[str], depatom: Atom, flag: str
        ):
            super().__init__(clause)
            self.source = source
            self.depatom = depatom
            self.flag = flag

        def __str__(self):
            return (
                f"{green(self.depatom)}[{self.flag}]: required by {green(self.source)}"
            )

        def blocks(self, model: Set[str], clause: "Formula.MetaClause") -> bool:
            if isinstance(clause, Formula.UseDepClause):
                if (
                    atom_sat(self.depatom, clause.depatom)
                    and token_conflicts(self.flag, clause.flag)
                    and all(req in model for req in self.requirements)
                ):
                    return True
            elif isinstance(clause, Formula.RequiredUseClause):
                if (
                    atom_sat(clause.atom, self.depatom)
                    and token_conflicts(self.flag, clause.flag)
                    and all(req in model for req in self.requirements)
                ):
                    return True

            return False

    class RequiredUseClause(Clause):
        def __init__(
            self,
            atom: Atom,
            clause: Iterable[str],
            flag: str,
            tokens: List[Union[str, List]],
        ):
            super().__init__(clause)
            self.atom = self.source = atom
            self.flag = flag
            self.tokens = tokens

        def __str__(self):
            if self.flag.startswith("__"):  # If flag is a generated variable
                string = Formula.get_variable_desc(self.flag)
            else:
                if self.flag[0] == "-":
                    string = "-" + list(Atom(self.flag[1:]).USE)[0]
                else:
                    string = list(Atom(self.flag).USE)[0]
            parent = human_readable_required_use(self.tokens)
            # FIXME: Localize
            if string == parent:
                return f"{green(self.atom)} could not satisfy {blue(string)}"
            else:
                return (
                    f"{green(self.atom)} could not satisfy {blue(string)}, which is part of "
                    f"the larger clause {blue(parent)}"
                )

        def blocks(self, model: Set[str], clause: "Formula.MetaClause") -> bool:
            if isinstance(clause, Formula.UseDepClause):
                if (
                    atom_sat(self.atom, clause.depatom)
                    and token_conflicts(self.flag, clause.flag)
                    and all(req in model for req in self.requirements)
                ):
                    return True
            elif isinstance(clause, Formula.RequiredUseClause):
                if (
                    atom_sat(self.atom, clause.atom)
                    and token_conflicts(self.flag, clause.flag)
                    and all(req in model for req in self.requirements)
                ):
                    return True

            return False

        def sourceatom(self) -> Optional[Atom]:
            return self.atom

    def __init__(self):
        self.clauses = []
        self.atoms: Dict[QualifiedAtom, Set[FQAtom]] = {}
        self.flags: Set[FQAtom] = set()

    @classmethod
    def getnum(cls, string: str) -> int:
        if string in cls.__numcache:
            return cls.__numcache[string]

        if string[0] == "-":
            cls.__numcache[string] = -cls.__i
            cls.__numcache[string[1:]] = cls.__i
            cls.__stringcache[-cls.__i] = string
            cls.__stringcache[cls.__i] = string[1:]
        else:
            cls.__numcache[string] = cls.__i
            cls.__numcache["-" + string] = -cls.__i
            cls.__stringcache[cls.__i] = string
            cls.__stringcache[-cls.__i] = "-" + string

        cls.__i += 1
        return cls.__numcache[string]

    @classmethod
    def getstring(cls, num: int) -> str:
        return cls.__stringcache[num]

    @classmethod
    def genvariable(cls, desc: List[Any]) -> str:
        var = "__" + str(cls.__j)
        cls.__j += 1
        cls.__variabledesc[var] = human_readable_required_use(desc)
        return var

    @classmethod
    def get_variable_desc(cls, var: str) -> str:
        return cls.__variabledesc[var]

    def merge(self, other: "Formula"):
        self.clauses.extend(other.clauses)
        for clause in other.clauses:
            self.__update_for_clause__(clause.clause)
        return self

    def get_wcnfplus(self) -> WCNFPlus:
        formula = WCNFPlus()
        for clause in self.get_clauses():
            if isinstance(clause, Formula.MetaClause) and clause.weight is not None:
                formula.append(clause.intclause, weight=clause.weight)
            elif isinstance(clause, Formula.MetaClause) and clause.atmost is not None:
                formula.append([clause.intclause, clause.atmost], is_atmost=True)
            else:
                formula.append(clause.intclause)
        return formula

    def append(
        self,
        clause: Iterable[str],
        from_atom: Optional[str] = None,
        desc: Optional[str] = None,
        weight=None,
        atmost=None,
    ):
        self.clauses.append(Formula.MetaClause(from_atom, desc, clause, weight, atmost))
        self.__update_for_clause__(clause)

    def append_dep(self, clause: Iterable[str], from_atom: str, dependency: Atom):
        self.clauses.append(Formula.DepClause(from_atom, clause, dependency))
        self.__update_for_clause__(clause)

    def append_blocker(self, clause: Iterable[str], from_atom: str, blocked: Atom):
        self.clauses.append(Formula.BlockerClause(from_atom, clause, blocked))
        self.__update_for_clause__(clause)

    def append_required_use(
        self,
        clause: Iterable[str],
        from_atom: Atom,
        flag: str,
        tokens: List[Union[str, List]],
    ):
        self.clauses.append(Formula.RequiredUseClause(from_atom, clause, flag, tokens))
        self.__update_for_clause__(clause)

    def append_usedep(
        self, clause: Iterable[str], from_atom: str, dep_atom: Atom, flag: str
    ):
        self.clauses.append(Formula.UseDepClause(from_atom, clause, dep_atom, flag))
        self.__update_for_clause__(clause)

    def __update_for_clause__(self, clause: Iterable[str]):
        for token in clause:
            if not token.startswith("_") and not token.startswith("-_"):
                if "[" not in token:
                    atom = FQAtom(token.lstrip("-"))
                    if atom.CPN in self.atoms:
                        self.atoms[QualifiedAtom(atom.CPN)].add(atom)
                    else:
                        self.atoms[QualifiedAtom(atom.CPN)] = {atom}
                else:
                    self.flags.add(FQAtom(token.lstrip("-")))

    def extend(
        self,
        from_atom: Atom,
        clauses: List[List[str]],
        desc: Optional[str] = None,
        weight=None,
        atmost=None,
    ):
        for clause in clauses:
            self.append(clause, from_atom, desc, weight, atmost)

    def add_constraints(self, constraints: List[str]):
        self.__update_for_clause__(constraints)
        for clause in self.clauses:
            if not (
                isinstance(clause, Formula.MetaClause) and clause.atmost is not None
            ):
                clause.clause = list(clause.clause) + constraints
                clause.requirements |= {negate(token) for token in constraints}

    def get_clauses(self):
        for clause in self.clauses:
            yield clause.str2num()


def get_atmost_one_formulae(tokens: Sequence[str]) -> List[List[str]]:
    """
    Returns a list of clauses that enforce that at most one of the tokens may be true

    Note that this can also be achieved by using Formula.append with atmost set to 1,
    however  this does not provide a mechanism for handling additional conditions.
    Instead, you can use this function, and add the condition to each clause it produces
    """
    if len(tokens) <= 1:
        return []

    result = []
    # Enforce that for any two tokens in the list, one must be false
    for token in tokens[1:]:
        # Invert value of firsttoken
        if tokens[0].startswith("-"):
            firsttoken = tokens[0].lstrip("-")
        else:
            firsttoken = "-" + tokens[0]

        # Invert value of the other token
        if token.startswith("-"):
            othertoken = token.lstrip("-")
        else:
            othertoken = "-" + token
        result.append([firsttoken, othertoken])

    return result + get_atmost_one_formulae(tokens[1:])


def toggle(token: str) -> str:
    if token.startswith("-"):
        return token[1:]
    else:
        return "-" + token


def toggle_clause(tokens: List[str]) -> List[str]:
    newtokens = []
    for token in tokens:
        newtokens.append(toggle(token))
    return newtokens


def get_required_use_formula(
    mod: Pybuild, tokens: List[Union[str, List]], use_expand: Optional[str] = None
) -> Formula:
    """
    Adds clauses to the given formula for the given mod's REQUIRED_USE

    :param tokens: List of tokens corresponding to the REQUIRED_USE string, parsed
            beforehand by parse_usestr to be a list of tokens, with sublists
            corresponding to brackets in the original string
    """

    def get_required_use_formula_inner(
        tokens: List[Union[str, List]]
    ) -> Tuple[Formula, List[str]]:
        formula = Formula()
        clausevars = []

        for token in tokens:
            if isinstance(token, list):
                if token[0] != "??" and token[0].endswith("?"):
                    newvar = Formula.genvariable([token])
                    subformulae, subvars = get_required_use_formula_inner(token[1:])
                    if token[0].startswith("!"):
                        usedep = mod.ATOM + "[" + token[0].lstrip("!").rstrip("?") + "]"
                        subformulae.add_constraints([usedep, "-" + newvar])
                    else:
                        usedep = "-" + mod.ATOM + "[" + token[0].rstrip("?") + "]"
                        subformulae.add_constraints([usedep, "-" + newvar])
                    # for clause in get_atmost_one_formulae(subvars):
                    #    formula.append_required_use(
                    #        ["-" + newvar] + clause, mod.ATOM, token
                    #    )
                    formula.merge(subformulae)
                    # Generated variable is added to clausevars, and is free if
                    # condition is unsatisfied, and matches subformulae if condition
                    # is satisfied
                    clausevars.append(newvar)
                else:
                    subformulae, subvars = get_required_use_formula_inner(token[1:])
                    newvar = Formula.genvariable([token])
                    # Note: newvar will only have the value False if the formula
                    # is satisfied
                    if token[0] in ("??", "^^"):
                        for clause in get_atmost_one_formulae(subvars):
                            formula.append(
                                ["-" + newvar] + clause,
                                mod.ATOM,
                                human_readable_required_use(tokens),
                            )
                    if token[0] in ("||", "^^"):
                        formula.append(
                            ["-" + newvar] + subvars,
                            mod.ATOM,
                            human_readable_required_use(tokens),
                        )
                    if token[0] in ("||", "^^", "??"):
                        # If clause is satisfied, and the operator is not AND,
                        # then the subclauses don't need to be all satisfied
                        subformulae.add_constraints([newvar])
                    formula.merge(subformulae)
                    clausevars.append(newvar)

            else:
                flag = token.lstrip("!")
                if use_expand:
                    flag = use_expand + "_" + flag
                var = mod.ATOM + "[" + flag + "]"
                if token.startswith("!"):
                    formula.append_required_use(
                        ["-" + var], mod.ATOM, "-" + var, tokens
                    )
                    clausevars.append("-" + var)
                else:
                    formula.append_required_use([var], mod.ATOM, var, tokens)
                    clausevars.append(var)
        return formula, clausevars

    formula, clausevars = get_required_use_formula_inner(tokens)
    # Top level is an and, so require that all returned variables are satisfied
    for var in clausevars:
        formula.append_required_use([var], mod.ATOM, var, tokens)
    return formula


def get_dep_formula(mod: Pybuild, tokens) -> Tuple[Formula, Set[FQAtom]]:
    """
    Adds clauses to the given formula for the dependency strings of the given mod

    :param tokens: List of tokens corresponding to the dependency string, parsed
            beforehand by parse_usestr to be a list of tokens, with sublists
            corresponding to brackets in the original string
    """

    def fstr(atom: Atom, flag: str) -> str:
        """
        Produces a flag token for the formula given an atom and a flag

        This function does not produce disabled tokens. If a disabled token is
        desired, "-" should be applied to the result.
        """
        return atom + "[" + flag.rstrip("?=").lstrip("!-") + "]"

    def cond_flagstr(atom: Atom, flag: str) -> str:
        """
        Given an atom and a flag from a use conditional,
        produces a token for use in the dependency formula
        """
        disabled = flag.startswith("!")
        flag = flag.rstrip("?").lstrip("!")
        # Note: If flag was disabled, we want the flag enabled in the clause, as it
        # should either be enabled,
        # or some other part of the clause must be true if disabled
        if disabled:
            return fstr(atom, flag)
        # Note: If flag was enabled, we produce the clause (flag => dep),
        # which is equivalent to (-flag | dep)
        return "-" + fstr(atom, flag)

    formula = Formula()
    deps: Set[FQAtom] = set()

    for token in expand_use_conditionals(tokens):
        if isinstance(token, list):
            if token[0] == "||":
                # If token is an or, next token is a list, at least one of the elements of
                # which must be satisfied
                orvars = []

                # Create clause for each part of the || expression.
                for subclause in token[1:]:
                    # Create new variable to represent clause
                    var = Formula.genvariable([token])
                    orvars.append(var)
                    # Either one part of the or must be true, or the variable for
                    # the clause should be false
                    new_formula, new_deps = get_dep_formula(mod, [subclause])
                    new_formula.add_constraints(["-" + var])
                    formula.merge(new_formula)
                    deps |= new_deps

                # We should be able to set at least one of the new variables we
                # introduced to be true, meaning that some other part of their clause
                # must be satisfied
                formula.append(orvars, mod.ATOM, human_readable_required_use([token]))
            elif token[0].endswith("?"):
                new_formula, new_deps = get_dep_formula(mod, token[1:])
                new_formula.add_constraints([cond_flagstr(mod.ATOM, token[0])])
                formula.merge(new_formula)
                deps |= new_deps
            else:
                raise Exception(
                    f"Internal Error: dependency structure {tokens} is invalid"
                )
        # Handle regular dependencies
        else:
            blocker = token.startswith("!!")
            atom = Atom(token.lstrip("!"))

            # Note that load_pkg will only return mods that completely match atom
            # I.e. it will handle any versioned atoms itself
            specificpkgs = [m for m in load_pkg(atom)]
            specificatoms = [m.ATOM for m in load_pkg(atom)]

            deps |= set(specificatoms)

            # !!foo[A,B] is equivalent to
            # || ( !!foo foo[-A] foo[-B] )
            # What about !!foo[A?,B]
            # A? ( || ( !!foo foo[-A] foo[-B] ) || ( !!foo foo[-B] ) )

            # At least one specific version of this mod must be enabled
            if blocker and not atom.USE:
                for specatom in specificatoms:
                    formula.append_blocker(
                        ["-" + specatom], mod.ATOM, Atom(token.lstrip("!"))
                    )
            elif not blocker:
                formula.append_dep(specificatoms, mod.ATOM, atom)

            # For each use flag dependency, add a requirement that the flag must be set
            # This depends on the operators used on the flag. See PMS 8.2.6.4
            for flag in atom.USE:
                for spec in specificpkgs:
                    # Either specific version should not be installed,
                    # or flag must be set (depending on flag operators)

                    # Use requirement is unnecessary unless this specific version
                    # of the mod is enabled
                    new_formula = Formula()
                    if flag.lstrip("-") not in spec.IUSE_EFFECTIVE:
                        continue

                    if flag.startswith("-"):  # dep[-flag]
                        # 2-style disabled
                        if blocker:
                            new_formula.append_usedep(
                                [fstr(spec.ATOM, flag)],
                                mod.ATOM,
                                atom.strip_use(),
                                flag,
                            )
                        else:
                            new_formula.append_usedep(
                                ["-" + fstr(spec.ATOM, flag)],
                                mod.ATOM,
                                atom.strip_use(),
                                flag,
                            )
                    else:  # dep[flag]
                        # 2-style enabled
                        if blocker:
                            new_formula.append_usedep(
                                ["-" + fstr(spec.ATOM, flag)],
                                mod.ATOM,
                                spec.ATOM.strip_use(),
                                flag,
                            )
                        else:
                            new_formula.append_usedep(
                                [fstr(spec.ATOM, flag)],
                                mod.ATOM,
                                spec.ATOM.strip_use(),
                                flag,
                            )

                    new_formula.add_constraints(["-" + spec.ATOM])
                    formula.merge(new_formula)
    return formula, deps


def generate_formula(mods: Iterable[Target], depsadded: Set[FQAtom]) -> Formula:
    """
    Generates a hard dependency formula for the given mods

    :param mods: Each entry should contain a list of mods with the same base
                 category and name, the atom that pulled those mods in, and a
                 string describing where the mods were pulled from.
    :param depsadded: Mods that have already been included in the formula and
                      should not be added again
    :returns: The resulting formula
    """
    formula = Formula()
    # Queue of mods to add to the formula
    new: List[Pybuild] = []
    # Ensure newselected and oldselected mods are satisfied
    for target in mods:
        if target.source:
            # If a source is specified, at least one version of the mod must be
            # installed
            # Otherwise, we only include it for the purpose of dependency resolution
            formula.append_dep(
                [mod.ATOM for mod in target.pkgs], target.source, target.atom
            )
            if target.atom.USE:
                for flag in target.atom.USE:
                    sflag = flag.lstrip("-")
                    if flag.startswith("-"):
                        prefix = "-"
                    else:
                        prefix = ""
                    for mod in target.pkgs:
                        formula.append_usedep(
                            ["-" + mod.ATOM, prefix + mod.ATOM + f"[{sflag}]"],
                            target.source,
                            target.atom.strip_use(),
                            flag,
                        )

        new += target.pkgs

    while new:
        # Mods to parse in next iteration, mapped to the mod that depends on them
        nextmods: Set[FQAtom] = set()
        for mod in new:
            # Either mod must not be installed, or mods dependencies must be satisfied
            new_formula, deps = get_dep_formula(
                mod, parse_usestr(mod.DEPEND + " " + mod.RDEPEND, token_class=Atom)
            )
            new_formula.merge(
                get_required_use_formula(mod, parse_usestr(mod.REQUIRED_USE))
            )
            # Exactly one texture_size flag must be enabled
            if mod.TEXTURE_SIZES.strip():
                new_formula.merge(
                    get_required_use_formula(
                        mod,
                        [["^^"] + parse_usestr(mod.TEXTURE_SIZES)],
                        use_expand="texture_size",
                    )
                )
            new_formula.add_constraints([f"-{mod.ATOM}"])
            formula.merge(new_formula)
            for flag in get_forced_use(mod.ATOM):
                if flag.lstrip("-") not in mod.IUSE_EFFECTIVE:
                    continue

                if flag[0] == "-":
                    formula.append(
                        [f"-{mod.ATOM}[{flag[1:]}]"],
                        "profile use.force or mod.use.force",
                        f"Flag {flag} is forced on mod {mod.ATOM}",
                    )
                else:
                    formula.append(
                        [f"{mod.ATOM}[{flag}]"], "use.force", "Forced flag from profile"
                    )

            depsadded.add(mod.ATOM)
            # Add this mod's dependencies to the next set of mods to parse
            nextmods |= deps
        new = []
        for atom in nextmods:
            if atom not in depsadded:
                new.append(load_pkg_fq(atom))

    return formula


def is_unmasked(atom: FQAtom) -> bool:
    for unmasked_atom in get_unmasked().get(atom.CPN, []):
        if atom_sat(atom, unmasked_atom):
            return True
    return False


def add_masked(atoms: Dict[QualifiedAtom, Set[FQAtom]], flags: Iterable[FQAtom]):
    formula = Formula()
    masked = get_masked()
    for cpn in atoms:
        if cpn in masked:
            for atom in atoms[cpn]:
                for masked_atom, comment in masked[cpn].items():
                    if atom_sat(atom, masked_atom) and not is_unmasked(atom):
                        if comment:
                            description = (
                                "package.mask with the following comment:\n  "
                                + blue("\n  ".join(comment))
                            )
                        else:
                            description = "package.mask"
                        # Masks don't apply to installed packages
                        # (i.e. the user should remove them manually)
                        if atom.R.endswith("::installed"):
                            warning(
                                f"Installed package {atom.CPF} is masked by {description}"
                            )
                        else:
                            formula.append_blocker(
                                ["-" + atom], description, masked_atom
                            )

    return formula
