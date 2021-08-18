# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Dependency resolution module

Converts mod dependency links and REQUIRED_USE conditions into a MAX-SAT formula in
conjunctive normal form.
This formula is then solved using pysat (python-sat on pypi) and the resulting model
converted back into a list of installed mods and their use flag configuration.

Note that the hard requirements defined in DEPEND, RDEPEND and REQUIRED_USE are
converted into a SAT formula that must be solved in its entirety.
We use a MAX-SAT solver because there are also other soft requirements which are used
to avoid installing mods unnecessarily and to avoid changing the user's use flag
configuration, if possible.

See https://en.wikipedia.org/wiki/Boolean_satisfiability_problem for details on
the SAT problem
"""

import re
from logging import info
from typing import AbstractSet, Dict, Iterable, List, Set

from portmod.config.sets import get_set
from portmod.config.use import get_use
from portmod.loader import AmbiguousAtom, load_all_installed, load_pkg
from portmod.transactions import (
    PackageDoesNotExist,
    Transactions,
    UseDep,
    generate_transactions,
)
from portmodlib.atom import Atom, FQAtom, QualifiedAtom, atom_sat
from portmodlib.l10n import l10n

from .formula import Formula, Target, add_masked, generate_formula
from .weights import weigh_clauses


class DepError(Exception):
    """Indicates an unsatisfiable transaction"""


def resolve(
    enabled: Iterable[Atom],
    disabled: Iterable[Atom],
    explicit: AbstractSet[Atom],
    selected: AbstractSet[Atom],
    selected_sets: AbstractSet[str],
    *,
    deep: bool = False,
    noreplace: bool = False,
    update: bool = False,
    newuse: bool = False,
    depclean: bool = False,
    emptytree: bool = False,
) -> Transactions:
    """
    Calculates new mod configuration to match system after the given mods are installed

    Note: We have two modes of operation:

    Shallow
        We assume that all installed mods are fixed and will not
        change version. Any version of a newly selected mods may be installed.
        Note that use flags may change on installed mods.
    Deep
        We treat every mod as newly selected, and choose from among its versions

    args:
        enabled: Packages which are to be enabled/installed
        disabled: Packages which are to be disabled/removed
        selected: Enabled packages which were explicitly selected
        selected_sets: Sets which were explicitly selected (the contents of which
                would be in enabled)
        deep: Whether or not we are running in deep mode
        noreplace: Whether or not explicitly selected packages and sets should be rebuilt,
                   even if no other changes to them are necessary
        update: If true, packages will be updated, if possible.
        newuse: If true, packages with changes to their use flags will be rebuilt.
        depclean: If true, packages which were neither explicitly selected, nor
                  required as dependencies, will be removed.
        emptytree: If true, all packages in the dependency tree will be rebuilt, as
                   if nothing was installed.
    returns:
        Transactions object representing the package changes required
    """
    # Slow imports
    from pysat.examples.rc2 import RC2
    from pysat.solvers import Solver

    info(l10n("calculating-dependencies"))
    formula = Formula()

    # List of sets of mod objects, with each being a specific version of that mod
    oldselected: List[Target] = []
    newenabled: Dict[str, Target] = dict()

    CMD_ATOM = "mods passed on command line"
    WORLD_ATOM = "world favourites file"

    for atom in list(enabled) + list(disabled):
        if not load_pkg(atom):
            raise PackageDoesNotExist(atom)

    newenabledset = {
        atom: CMD_ATOM
        for atom in set(enabled)
        | {atom for set_name in selected_sets for atom in get_set(set_name)}
    }
    for atom in disabled:
        name = load_pkg(atom)[0].CPN
        if name in newenabledset:
            del newenabledset[name]

    for atom in disabled:
        for mod in load_pkg(atom):
            formula.append_dep(["-" + mod.ATOM], CMD_ATOM, atom)

    def create_modlist(atom):
        modlist = load_pkg(atom)

        # Raise exception if mod name is ambiguous (exists in multiple categories)
        if not all(mod.ATOM.C == modlist[0].ATOM.C for mod in modlist):
            raise AmbiguousAtom(atom, [mod.ATOM for mod in modlist])

        if not modlist:
            if atom in set(selected):
                raise PackageDoesNotExist(atom)

            raise PackageDoesNotExist(
                msg=l10n("package-does-not-exist-in-world", atom=atom)
            )
        return modlist

    for atom, source in newenabledset.items():
        modlist = create_modlist(atom)
        name = modlist[0].CPN
        if name in newenabled:
            newenabled[modlist[0].CPN].pkgs.extend(modlist)
            if newenabled[modlist[0].CPN].source is CMD_ATOM or source is CMD_ATOM:
                # Use generic atom if included multiple times on command line.
                # Not all versions in modlist will correspond to a specific version
                # passed on the command line.
                newenabled[modlist[0].CPN].atom = name
            # Prefer command line as source rather than world file
            if newenabled[modlist[0].CPN].source is WORLD_ATOM and source is CMD_ATOM:
                newenabled[modlist[0].CPN].source = CMD_ATOM
        else:
            newenabled[modlist[0].CPN] = Target(modlist, atom, source)

    for atom in get_set("world") - {load_pkg(atom)[0].CPN for atom in disabled}:
        if atom not in selected:
            modlist = create_modlist(atom)
            oldselected.append(Target(modlist, atom, "world favourites file"))

    # Any remaining installed mods don't need to remain installed if there aren't
    # any dependencies, so source is None
    installed = [Target([mod], mod.ATOM, None) for mod in load_all_installed()]

    selected_cpn = set()
    explicit_cpn = set()

    for atom in explicit:
        pkg = load_pkg(atom)[0]
        explicit_cpn.add(pkg.CPN)

    for atom in selected:
        pkg = load_pkg(atom)[0]
        selected_cpn.add(pkg.CPN)

    selected_from_sets: Set[QualifiedAtom] = set()
    for set_name in selected_sets:
        selected_from_sets |= {QualifiedAtom(atom) for atom in get_set(set_name)}

    depsadded: Set[FQAtom] = set()
    # Hard clauses
    formula.merge(
        generate_formula(list(newenabled.values()) + oldselected + installed, depsadded)
    )
    # Soft clauses
    formula.merge(
        weigh_clauses(
            formula.atoms,
            formula.flags,
            explicit=explicit_cpn,
            deep=deep,
            depclean=depclean,
            update=update,
            newuse=newuse,
            emptytree=emptytree,
        )
    )

    formula.merge(add_masked(formula.atoms, formula.flags))

    if depclean:
        for pkg in load_all_installed():
            # When depcleaning, installed packages should be frozen at their current
            # version, or else removed
            versions = load_pkg(Atom(pkg.ATOM.CPN))
            var = formula.genvariable(
                [f"No non-installed versions of {pkg.CPN} are allowed"]
            )
            # Clause requires that either the installed version should be removed,
            # or all other versions should be removed.
            # This means it is not possible for a version other than the installed version
            # to be kept
            formula.append_dep(
                ["-" + pkg.ATOM, var],
                "Selected packages must not be changed when depcleaning",
                pkg.ATOM,
            )
            # Var can only be true if all versions are not installed
            # as each clause requires that either a particular version is not installed,
            # or var is false.
            # Hence if var is true, every one of these clauses is satisfied by the left term
            for other in versions:
                if not other.INSTALLED:
                    formula.append(
                        ["-" + other.ATOM, "-" + var],
                        other.ATOM,
                        "Selected packages must not be changed when depcleaning",
                    )

            for flag in pkg.IUSE_EFFECTIVE:
                if flag in get_use(pkg)[0]:
                    formula.append_usedep(
                        [pkg.ATOM + "[" + flag + "]", "-" + pkg.ATOM],
                        "Selected packages must not be changed when depcleaning",
                        pkg.ATOM,
                        flag,
                    )
                else:
                    formula.append_usedep(
                        ["-" + pkg.ATOM + "[" + flag + "]", "-" + pkg.ATOM],
                        "Selected packages must not be changed when depcleaning",
                        pkg.ATOM,
                        "-" + flag,
                    )

    if not formula.clauses:
        return Transactions()

    wcnf = formula.get_wcnfplus()
    solver = RC2(wcnf, solver="mc")
    solver.compute()
    if solver.compute():
        info(l10n("done"))
        # Turn numbers in result back into strings
        result = list(
            filter(
                # Filter out custom variables that are only meaningful
                # for the computation
                lambda x: not x.startswith("_") and not x.startswith("-_"),
                [Formula.getstring(num) for num in solver.model],
            )
        )
        flags = [atom for atom in result if "[" in atom]
        enabled_final = [
            FQAtom(mod) for mod in result if "[" not in mod and mod[0] != "-"
        ]
        enablednames = [atom.CPN for atom in enabled_final]
        disabled_final = [
            FQAtom(mod.lstrip("-"))
            for mod in result
            if "[" not in mod and mod[0] == "-"
            # If mod is enabled and installed version is disabled,
            # ignore disabled version, and vice versa
            and Atom(mod.lstrip("-")).CPN not in enablednames
        ]
        usedeps = []

        for flag in flags:
            atom = FQAtom(flag.lstrip("-"))
            if flag[0] == "-":
                prefix = "-"
            else:
                prefix = ""

            # Ignore flags for mods that are to be uninstalled
            if re.sub(r"\[.*\]", "", atom) in enabled_final:
                usedeps.append(
                    UseDep(atom.strip_use(), prefix + list(atom.USE)[0], None)
                )

        transactions = generate_transactions(
            enabled_final,
            disabled_final,
            selected_cpn,
            usedeps,
            noreplace=noreplace,
            emptytree=emptytree,
            update=update,
        )
        return transactions

    # Find clause that caused the solver to fail
    # Backtrack mod that added that clause until we reach @selected by
    # looking for clauses containing the (enabled) mod as a token.
    # Display this trace.
    # Then also display trace for a mod that requires/blocks the clause that
    # caused the failure

    solver2 = Solver("mc")
    solveableformula = []
    # Add atmost clauses first, as they won't by themselves cause conflicts,
    # and are not very useful for explaining a failed transaction
    for clause in formula.get_clauses():
        if isinstance(clause, Formula.MetaClause) and clause.atmost is not None:
            solver2.add_atmost(clause.intclause, clause.atmost)

    model = set()
    for clause in formula.get_clauses():
        if isinstance(clause, Formula.MetaClause) and (
            clause.atmost is not None or clause.weight is not None
        ):
            continue
        else:
            solver2.add_clause(clause.intclause)

        if solver2.solve():
            model = set(map(Formula.getstring, solver2.get_model()))
            solveableformula.append(clause)
        else:
            conflict = None

            for solveableclause in solveableformula:
                # Find clause that contradicts failed clause
                # Note that metaclauses don't have a blocks function,
                if hasattr(solveableclause, "blocks") and solveableclause.blocks(
                    model, clause
                ):
                    conflict = solveableclause
                    break

            def find_dependency(modstr: str):
                # Ignore top-level dependencies
                if not isinstance(modstr, Atom):
                    return None

                for solveableclause in solveableformula:
                    if isinstance(solveableclause, Formula.DepClause):
                        if atom_sat(Atom(modstr), solveableclause.dependency) and all(
                            var in model for var in solveableclause.requirements
                        ):
                            return solveableclause
                return None

            exceptionstring = f"{clause}\n"
            parent = find_dependency(clause.source)
            i = 1
            while parent is not None:
                exceptionstring += i * "  " + f"{parent}\n"
                parent = find_dependency(parent.source)
                i += 1

            if conflict:
                exceptionstring += l10n("contradicts") + "\n"
                exceptionstring += f"{conflict}\n"
                parent = find_dependency(conflict.source)
                i = 1
                while parent is not None:
                    exceptionstring += i * "  " + f"{parent}\n"
                    parent = find_dependency(parent.source)
                    i += 1

            raise DepError(
                l10n("unable-to-satisfy-dependencies") + f"\n{exceptionstring}"
            )

    raise Exception(
        "Internal error: Unable to satisfy dependencies, "
        "but there are no clauses in the formula!"
    )
