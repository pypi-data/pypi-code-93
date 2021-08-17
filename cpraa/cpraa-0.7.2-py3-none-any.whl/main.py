import argparse
from typing import List

import af_parser
import labeling_scheme as lab
from labeling import Labeling
from linear_solver import LinearSolver
from DPGM import DPGM
import semantics as sem
import tasks
from solver_instance import SolverInstance
from z3_instance import Z3Instance
from timer import Timer

# TODO:
#  - produce log files
#  - set verbosity level, or add silent mode
#  - re-add assume-independence flag

#  - task to get distribution unequal to a given other distribution?#
#  - Flag for extensions
#  - flag to generate unsat core; this needs named assertions, see assert_and_track() in z3.py
#  - credulous and skeptical acceptance wrt. a labeling scheme

__version__ = "0.7.2"

# Solvers
Z3_LEGACY = "z3-legacy"
# from https://pysmt.readthedocs.io/en/latest/getting_started.html#the-basics
# noinspection SpellCheckingInspection
pysmt_solvers = ["z3", "msat", "cvc4", "yices", "btor", "picosat", "bdd"]
linear_solvers = ["cvxopt", "glpk", "mosek"]
other_solvers = [Z3_LEGACY]
all_solvers = pysmt_solvers + linear_solvers + other_solvers


def main():
    main_timer = Timer(output_string="Overall runtime:")

    #########################
    # set up argument parser
    #########################
    arg_parser = argparse.ArgumentParser(prog="cpraa", add_help=False,
                                         description="CPrAA - a Checker for Probabilistic Abstract Argumentation")
    base_group = arg_parser.add_argument_group("basic parameters")
    base_group.add_argument("-f", "--file", help="the argumentation framework as .tgf file")
    base_group.add_argument("-s", "--semantics", nargs="+", default=[],
                            help="the probabilistic semantics to check against")
    base_group.add_argument("-cs", "--complement_semantics", nargs="+", default=[], metavar="SEMANTICS",
                            help="probabilistic semantics with negated constraints")
    base_group.add_argument("-a", "--arguments", nargs="+", default=[], metavar="NODE",
                            help="one or more nodes from the AF to be used in one of tasks")
    base_group.add_argument("-OD", "--one_distribution", action="store_true",
                            help="compute one distribution satisfying the semantics")
    base_group.add_argument("-CD", "--corner_distributions", action="store_true",
                            help="compute the distributions forming the corners of the convex hull of the solution "
                                 "space spanned by the semantics' linear constraints")
    # base_group.add_argument("-i", "--assume_independence", action="store_true",
    #                         help="treat the arguments' probabilities as independent "
    #                              "(warning: this leads to incorrect results for some semantics)")
    base_group.add_argument("-b", "--backend_solver", metavar="SOLVER", type=str,
                            help="the solver used as backend. Options are all SMT solvers available via pySMT ("
                                 + ", ".join(pysmt_solvers) + "), linear solvers via CVXOPT ("
                                 + ", ".join(linear_solvers) + "), and a direct integration of Z3 ("
                                 + Z3_LEGACY + ")")
    base_group.add_argument("-smt", "--smt_file", help="add additional constraints from a file in SMT-LIB format")

    lp_group = arg_parser.add_argument_group("optimization")
    lp_group.add_argument("-MIN", "--minimize_probability", action="store_true",
                          help="find the distribution minimizing the marginal probabilities of the arguments passed "
                               "with -a while satisfying the given semantics")
    lp_group.add_argument("-MAX", "--maximize_probability", action="store_true",
                          help="find the distribution maximizing the marginal probabilities of the arguments passed "
                               "with -a while satisfying the given semantics")

    ac_group = arg_parser.add_argument_group("acceptance checking")
    ac_group.add_argument("-CA", "--credulous_acceptance",
                          nargs="?", metavar="THRESHOLD", type=float, const=1.0,
                          help="check credulous acceptance of given arguments, "
                               "optionally taking a threshold into account")
    ac_group.add_argument("-SA", "--skeptical_acceptance",
                          nargs="?", metavar="THRESHOLD", type=float, const=1.0,
                          help="check skeptical acceptance of given arguments, "
                               "optionally taking a threshold into account")
    ac_group.add_argument("-CAA", "--credulous_acceptance_all",
                          nargs="?", metavar="THRESHOLD", type=float, const=1.0,
                          help="check credulous acceptance of all arguments, "
                               "optionally taking a threshold into account")
    ac_group.add_argument("-SAA", "--skeptical_acceptance_all",
                          nargs="?", metavar="THRESHOLD", type=float, const=1.0,
                          help="check skeptical acceptance of all arguments, "
                               "optionally taking a threshold into account")

    lab_group = arg_parser.add_argument_group("generate labelings")
    lab_group.add_argument("-l", "--labeling_scheme", metavar="SCHEME", help="the labeling scheme to use")
    lab_group.add_argument("-OL", "--one_labeling", action="store_true",
                           help="compute one labeling satisfying the semantics")
    lab_group.add_argument("-AL", "--all_labelings", action="store_true",
                           help="compute all labelings satisfying the semantics")
    lab_group.add_argument("-lt", "--labeling_threshold", nargs="+", metavar="T", type=float,
                           help="the optional thresholds needed for some labeling schemes")

    info_group = arg_parser.add_argument_group('informational parameters')
    info_group.add_argument("-h", "--help", action="help", help="show this help message")
    info_group.add_argument("-v", "--version", action="version", version="%(prog)s " + __version__)
    info_group.add_argument("-ls", "--list_semantics", action="store_true",
                            help="list all available probabilistic semantics")
    info_group.add_argument("-ll", "--list_labeling_schemes", action="store_true",
                            help="list all available labeling schemes")
    info_group.add_argument("-d", "--documentation", nargs="+", default=[], metavar="NAME",
                            help="display a short documentation for the listed semantics or labeling schemes")
    info_group.add_argument("-t", "--time", action="store_true", help="time the execution")
    info_group.add_argument("-o", "--distribution_output_format", metavar="FORMAT", type=str, default="S",
                            help="how to output distributions: (M) marginal node probabilities, (F) full distribution, "
                                 "(S) support of distribution, (Z) Z3 output, (T) SMT2 format.")
    info_group.add_argument("-p", "--output_precision", metavar="PRECISION", type=int, default=5,
                            help="precision of floats that are output")
    info_group.add_argument("-dc", "--display_constraints", action="store_true",
                            help="print the constraints generated by the semantics (note that for complemented "
                                 "semantics, the constraints are displayed without the subsequent conjunction and "
                                 "negation)")

    ###############################
    # parse command line arguments
    ###############################
    args = arg_parser.parse_args()

    af = None
    solver = None
    z3i = None
    ls = None
    si = None
    labeling_scheme = None
    semantics = []
    arguments = None
    args.assume_independence = False  # legacy option

    main_timer.enable_printing = args.time
    Timer.enable_printing_default = args.time

    sem.CONSTRAINT_LOGGING = args.display_constraints

    if args.list_semantics:
        print("Available semantics:", ", ".join(reversed(sem.all_semantics_names())))

    if args.list_labeling_schemes:
        print("Available labeling schemes:", ", ".join(reversed(lab.get_all_labeling_scheme_names())))

    if args.documentation:
        for name in args.documentation:
            semantics_class = sem.get_semantics_class_by_name(name)
            if semantics_class:
                print("Semantics '" + semantics_class.__name__ + "':")
                if semantics_class.__doc__:
                    print(semantics_class.__doc__.strip("\n"))
                else:
                    print("    No documentation available.")
            else:
                labeling_scheme_class = lab.get_labeling_scheme_class(name)
                if labeling_scheme_class:
                    print("Labeling scheme '" + labeling_scheme_class.__name__ + "':")
                    if labeling_scheme_class.__doc__:
                        print(labeling_scheme_class.__doc__.strip("\n"))
                    else:
                        print("    No documentation available.")
                else:
                    arg_parser.error("no semantics or labeling scheme called '" + name + "' exists")

    if args.file:
        af = af_parser.parse_tgf(args.file)
        # print(af)

    if args.backend_solver:
        if not af:
            arg_parser.error("no AF provided")
        solver = args.backend_solver
        if solver not in all_solvers:
            arg_parser.error("Unknown solver name '" + solver + "'. Possible solvers are " + ", ".join(all_solvers)
                             + " (though some of those need to be installed separately)")

    if args.semantics:
        if not af:
            arg_parser.error("an AF must be provided when checking semantics")

        for semantics_name in args.semantics:
            semantics_class = sem.get_semantics_class_by_name(semantics_name)
            if not semantics_class:
                arg_parser.error("No semantics called '"
                                 + semantics_name + "' exists. Use -ls to list all available semantics.")
            semantics.append(semantics_class(af))

    if args.complement_semantics:
        if not af:
            arg_parser.error("an AF must be provided when checking semantics")

        for semantics_name in args.complement_semantics:
            semantics_class = sem.get_semantics_class_by_name(semantics_name)
            if not semantics_class:
                arg_parser.error("No semantics called '"
                                 + semantics_name + "' exists. Use -ls to list all available semantics.")
            semantics.append(semantics_class(af, complemented=True))

    if args.labeling_scheme:
        labeling_scheme_class = lab.get_labeling_scheme_class(args.labeling_scheme)
        if not labeling_scheme_class:
            arg_parser.error("no labeling scheme called '" + args.labeling_scheme + "' exists")
        num_args_required = labeling_scheme_class.num_args
        if args.labeling_threshold:
            num_args_given = len(args.labeling_threshold)
        else:
            num_args_given = 0
        if num_args_given < num_args_required:
            error_message = "mismatch in the number of thresholds: required by labeling scheme '" \
                            + args.labeling_scheme + "': " + str(num_args_required) + ", given: " + str(num_args_given)
            arg_parser.error(error_message)
        if num_args_given > num_args_required:
            warning_message = "warning: mismatch in the number of thresholds: required by labeling scheme '" \
                              + args.labeling_scheme + "': " + str(num_args_required) + ", given: " \
                              + str(num_args_given) + " - i'm ignoring the surplus ones"
            print(warning_message)
        if num_args_required == 0:
            labeling_scheme = labeling_scheme_class()
        elif num_args_required == 1:
            labeling_scheme = labeling_scheme_class(args.labeling_threshold[0])
        elif num_args_required == 2:
            labeling_scheme = labeling_scheme_class(args.labeling_threshold[0], args.labeling_threshold[1])
        else:
            raise NotImplementedError("labeling schemes with more than 2 thresholds")

    if args.arguments:
        if not af:
            arg_parser.error("no AF provided")
        try:
            arguments = [af.get_node_by_name(argument_name) for argument_name in args.arguments]
        except ValueError as e:
            arg_parser.error(str(e))

    if args.smt_file:
        if not af:
            arg_parser.error("no AF provided")
        if solver == Z3_LEGACY or solver in linear_solvers:
            arg_parser.error("smt constraints only available via pysmt solvers")
        # solver in pysmt_solvers or solver is None
        si = get_smt_solver(si, af, solver)
        with open(args.smt_file, "r") as smt_file:
            si.add_constraints_from_smt(smt_file)

    ########
    # tasks
    ########

    if args.one_distribution:
        if not af:
            arg_parser.error("an AF must be provided to compute a distribution")

        od_timer = Timer(output_string="Computing one distribution took", start=False)
        print("Computing one distribution satisfying the following semantics:", repr_list(semantics))

        if solver == Z3_LEGACY:
            z3i = get_z3_solver(z3i, af, args.assume_independence)
            od_timer.start()
            distribution = tasks.get_one_distribution_z3(z3i, semantics)
        elif solver in linear_solvers:
            ls = get_linear_solver(ls, af, solver)
            od_timer.start()
            distribution = tasks.get_one_distribution_linear(ls, semantics)
        else:  # solver in pysmt_solvers or solver is None
            si = get_smt_solver(si, af, solver)
            od_timer.start()
            distribution = tasks.get_one_distribution(si, semantics)

        if distribution:
            distribution.print_formatted(args.distribution_output_format, precision=args.output_precision)
        else:
            print("No distribution satisfying the given semantics exists.")
        od_timer.stop()

    if args.corner_distributions:
        if not af:
            arg_parser.error("an AF must be provided to compute the corner distribution")
        if args.smt_file:
            arg_parser.error("task not available with additional SMT constraints")
        assert_linear_semantics_availability(semantics, arg_parser)
        if solver in linear_solvers:
            ls = get_linear_solver(ls, af, solver)
        else:
            ls = get_linear_solver(ls, af, None)

        cd_timer = Timer(output_string="Computing the corner distributions took")
        print("Computing the corner distributions for the following semantics:", repr_list(semantics))
        distributions = tasks.get_corner_distributions(ls, semantics)
        num_results = len(distributions)
        if num_results == 0:
            print("No distribution satisfying the given semantics exists.")
        elif num_results == 1:
            print("The solution is unique:")
            distributions[0].print_formatted(args.distribution_output_format)
        else:
            for i in range(num_results):
                print("\nResult {} of {}:".format(i + 1, num_results))
                distributions[i].print_formatted(args.distribution_output_format)
        cd_timer.stop()

    if args.minimize_probability:
        if not af:
            arg_parser.error("no AF given, use -f to load one from a TGF file")
        if not arguments:
            arg_parser.error("no arguments from the AF given, provide one or more with -a")
        if args.smt_file:
            arg_parser.error("task not available with additional SMT constraints")
        assert_linear_semantics_availability(semantics, arg_parser)
        if solver in linear_solvers:
            ls = get_linear_solver(ls, af, solver)
        else:
            ls = get_linear_solver(ls, af, None)
        timer = Timer(output_string="Computing optimal distribution took")
        print("Computing optimal distribution minimizing the probability of argument" + plural(args.arguments),
              repr_list_i(args.arguments), "while satisfying the following semantics:", repr_list(semantics))
        distribution = tasks.minimize_marginal_probabilities(ls, arguments, semantics)
        if distribution:
            distribution.print_formatted(args.distribution_output_format)
        else:
            print("No distribution satisfying the given semantics exists.")
        timer.stop()

    if args.maximize_probability:
        if not af:
            arg_parser.error("no AF given, use -f to load one from a TGF file")
        if not arguments:
            arg_parser.error("no arguments from the AF given, provide one or more with -a")
        if args.smt_file:
            arg_parser.error("task not available with additional SMT constraints")
        assert_linear_semantics_availability(semantics, arg_parser)
        if solver in linear_solvers:
            ls = get_linear_solver(ls, af, solver)
        else:
            ls = get_linear_solver(ls, af, None)
        timer = Timer(output_string="Computing optimal distribution took")
        print("Computing optimal distribution maximizing the probability of argument" + plural(args.arguments),
              repr_list_i(args.arguments), "while satisfying the following semantics:", repr_list(semantics))
        distribution = tasks.maximize_marginal_probabilities(ls, arguments, semantics)
        if distribution:
            distribution.print_formatted(args.distribution_output_format)
        else:
            print("No distribution satisfying the given semantics exists.")
        timer.stop()

    if args.one_labeling:
        if not af:
            arg_parser.error("an AF must be provided to compute a labeling")
        if not labeling_scheme:
            arg_parser.error("no labeling scheme provided")

        ol_timer = Timer(output_string="Computing one labeling took", start=False)
        print("Computing one", args.labeling_scheme, "labeling satisfying the following semantics:",
              repr_list(semantics))

        if solver == Z3_LEGACY:
            z3i = get_z3_solver(z3i, af, args.assume_independence)
            ol_timer.start()
            distribution = tasks.get_one_distribution_z3(z3i, semantics)
        elif solver in linear_solvers:
            assert_linear_semantics_availability(semantics, arg_parser)
            ls = get_linear_solver(ls, af, solver)
            ol_timer.start()
            distribution = tasks.get_one_distribution_linear(ls, semantics)
        else:  # solver in pysmt_solvers or solver is None
            si = get_smt_solver(si, af, solver)
            ol_timer.start()
            distribution = tasks.get_one_distribution(si, semantics)

        if distribution:
            labeling = Labeling(labeling_scheme, distribution, af)
            print(labeling)
        else:
            print("No distribution satisfying the given semantics exists.")
        ol_timer.stop()

    if args.all_labelings:
        if not af:
            arg_parser.error("an AF must be provided to compute a labeling")
        if not labeling_scheme:
            arg_parser.error("no labeling scheme provided (use -l)")

        if solver in linear_solvers:
            arg_parser.error("all labelings task not available with linear solver '" + solver + "'")
        elif solver == Z3_LEGACY:
            z3i = get_z3_solver(z3i, af, args.assume_independence)
        else:  # solver in pysmt_solvers or solver is None
            si = get_smt_solver(si, af, solver)

        al_timer = Timer(output_string="Computing all labelings took")
        print("Computing all", args.labeling_scheme, "labelings satisfying the following semantics:",
              repr_list(semantics))
        if solver == Z3_LEGACY:
            labelings = tasks.get_all_satisfying_labelings_z3(z3i, labeling_scheme, semantics)
        else:
            labelings = tasks.get_all_satisfying_labelings(si, labeling_scheme, semantics)
        print("Number of labelings:", len(labelings))
        # for ext in sorted([labeling.labeled_in for labeling in labelings]):
        #     print(ext)
        for labeling in sorted(labelings):
            print(labeling)
        # for labeling in sorted(list(set(map(repr, labelings)))):
        #     print(labeling)
        al_timer.stop()

    if args.credulous_acceptance is not None:
        if not af:
            arg_parser.error("an AF must be provided to check acceptance")
        if not arguments:
            arg_parser.error("no arguments given to check acceptance, provide one or more with -a")

        if solver in linear_solvers:
            arg_parser.error("credulous acceptance checking not available with linear solver '" + solver + "'")
        elif solver == Z3_LEGACY:
            z3i = get_z3_solver(z3i, af, args.assume_independence)
        else:  # solver in pysmt_solvers or solver is None
            si = get_smt_solver(si, af, solver)

        threshold = args.credulous_acceptance

        ca_timer = Timer(output_string="Checking credulous acceptance took")
        for argument in arguments:
            print("Checking credulous acceptance of argument", argument, "with threshold", threshold,
                  "under the following semantics:", repr_list(semantics))
            if solver == Z3_LEGACY:
                (acceptable, distribution) = tasks.check_credulous_acceptance_z3(z3i, semantics, argument, threshold)
            else:
                (acceptable, distribution) = tasks.check_credulous_acceptance(si, semantics, argument, threshold)

            if acceptable:
                print(argument, "is credulously accepted.")
                print("Satisfying distribution:")
                distribution.print_formatted(args.distribution_output_format)
            else:
                print(argument, "is not credulously accepted.")
        ca_timer.stop()

    if args.skeptical_acceptance is not None:
        if not af:
            arg_parser.error("an AF must be provided to check acceptance")
        if not arguments:
            arg_parser.error("no arguments given to check acceptance, provide one or more with -a")

        if solver in linear_solvers:
            arg_parser.error("skeptical acceptance checking not available with linear solver '" + solver + "'")
        elif solver == Z3_LEGACY:
            z3i = get_z3_solver(z3i, af, args.assume_independence)
        else:  # solver in pysmt_solvers or solver is None
            si = get_smt_solver(si, af, solver)

        threshold = args.skeptical_acceptance

        sa_timer = Timer(output_string="Checking skeptical acceptance took")
        for argument in arguments:
            print("Checking skeptical acceptance of argument", argument, "with threshold", threshold,
                  "under the following semantics:", repr_list(semantics))
            if solver == Z3_LEGACY:
                (acceptable, counterexample) = tasks.check_skeptical_acceptance_z3(z3i, semantics, argument, threshold)
            else:
                (acceptable, counterexample) = tasks.check_skeptical_acceptance(si, semantics, argument, threshold)
            if acceptable:
                print(argument, "is skeptically accepted.")
            else:
                print(argument, "is not skeptically accepted.")
                print("Counterexample:")
                counterexample.print_formatted(args.distribution_output_format)
        sa_timer.stop()

    if args.credulous_acceptance_all is not None:
        if not af:
            arg_parser.error("an AF must be provided to check acceptance")

        if solver in linear_solvers:
            arg_parser.error("credulous acceptance checking not available with linear solver '" + solver + "'")
        elif solver == Z3_LEGACY:
            z3i = get_z3_solver(z3i, af, args.assume_independence)
        else:  # solver in pysmt_solvers or solver is None
            si = get_smt_solver(si, af, solver)

        threshold = args.credulous_acceptance_all

        ca_timer = Timer(output_string="Checking credulous acceptance for all arguments took")
        print("Checking credulous acceptance of all arguments with threshold", threshold,
              "under the following semantics:", repr_list(semantics))
        accepted_args = []
        not_accepted_args = []
        for argument in af.get_nodes():
            if solver == Z3_LEGACY:
                acceptable, distribution = tasks.check_credulous_acceptance_z3(z3i, semantics, threshold, argument)
            else:
                acceptable, distribution = tasks.check_credulous_acceptance(si, semantics, threshold, argument)
            if acceptable:
                accepted_args.append(argument)
                # print(argument.name, "is credulously accepted.")
                # print("Satisfying distribution:")
                # distribution.print_formatted("SM")
            else:
                not_accepted_args.append(argument)
                # print(argument.name, "is not credulously accepted.")
        print("Credulously accepted:", accepted_args)
        print("Not credulously accepted:", not_accepted_args)
        ca_timer.stop()

    if args.skeptical_acceptance_all is not None:
        if not af:
            arg_parser.error("an AF must be provided to check acceptance")

        if solver in linear_solvers:
            arg_parser.error("sceptical acceptance checking not available with linear solver '" + solver + "'")
        elif solver == Z3_LEGACY:
            z3i = get_z3_solver(z3i, af, args.assume_independence)
        else:  # solver in pysmt_solvers or solver is None
            si = get_smt_solver(si, af, solver)

        threshold = args.skeptical_acceptance_all

        ca_timer = Timer(output_string="Checking skeptical acceptance for all arguments took")
        print("Checking skeptical acceptance of all arguments with threshold", threshold,
              "under the following semantics:", repr_list(semantics))
        accepted_args = []
        not_accepted_args = []
        for argument in af.get_nodes():
            if solver == Z3_LEGACY:
                acceptable, counterexample = tasks.check_skeptical_acceptance_z3(z3i, semantics, threshold, argument)
            else:
                acceptable, counterexample = tasks.check_skeptical_acceptance(si, semantics, threshold, argument)
            if acceptable:
                accepted_args.append(argument)
                # print(argument.name, "is skeptically accepted.")
            else:
                not_accepted_args.append(argument)
                # print(argument.name, "is not skeptically accepted.")
                # print("Counterexample:", counterexample)
                # counterexample.print_formatted("SM")
        print("Skeptically accepted:", accepted_args)
        print("Not skeptically accepted:", not_accepted_args)
        ca_timer.stop()

    main_timer.stop()

    # CSV friendly print of timing results
    # semantics_names = ",".join([semantics_obj.__class__.__name__ for semantics_obj in semantics])
    # timings = ";".join([str(timer.last_timing) for timer in Timer.all_timers])
    # # print(semantics_names + ";" + timings)
    # print(af.name + ";" + timings)


def assert_linear_semantics_availability(semantics: List[sem.Semantics], arg_parser):
    """
    Test availability of linear constraints for given semantics without constructing potentially expensive constraints.
    """
    dummy_af = DPGM()
    dummy_ls = LinearSolver(dummy_af)
    for s in semantics:
        dummy_s = s.__class__(dummy_af, complemented=s.complemented)
        try:
            dummy_s.get_linear_constraints(dummy_ls)
        except NotImplementedError:
            arg_parser.error("No linear constraints available (or implemented) for semantics '" + str(dummy_s) + "'")


def get_linear_solver(ls, af, solver_name) -> LinearSolver:
    if ls is None:
        ls_setup_timer = Timer(output_string="linear solver setup took")
        ls = LinearSolver(af, solver_name)
        ls_setup_timer.stop()
    return ls


def get_z3_solver(z3i, af, assume_independence=False) -> Z3Instance:
    if z3i is None:
        z3i_setup_timer = Timer(output_string="z3i setup took")
        z3i = Z3Instance(af, assume_independence)
        z3i_setup_timer.stop()
    return z3i


def get_smt_solver(si, af, solver_name) -> SolverInstance:
    if si is None:
        si_setup_timer = Timer(output_string="solver instance setup took")
        si = SolverInstance(af, solver_name=solver_name)
        si_setup_timer.stop()
    return si


def repr_list(s: List[str]):
    if len(s) > 0:
        return ", ".join(map(str, s))
    else:
        return "(none)"


def repr_list_i(s: List[str]):
    assert len(s) > 0
    if len(s) == 1:
        return str(s[0])
    else:
        return ", ".join(map(str, s[:-1])) + " and " + str(s[-1])


def plural(s: List[str]):
    if len(s) > 1:
        return "s"
    else:
        return ""


if __name__ == "__main__":
    main()
