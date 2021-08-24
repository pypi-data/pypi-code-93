import re
import sys


class SortMacrosByDepedency(object):
    def __init__(self, macros):
        self.macros = macros

    # Sort macros by dependency from the most independent to the most dependent ones
    def sort(self, reverse=False):
        weights = SortMacrosByDepedency._gen_weighted_macro_list(self.macros)
        for macro in self.macros:
            macro['weight'] = weights[macro['name']]
        sorted_macros_by_weight = sorted(self.macros, key=lambda macro: macro['weight'], reverse=reverse)
        return sorted_macros_by_weight

    # Generates a list of key => value where the key is the name of the macro
    # and the value is a set of macros that depend on the key.
    @staticmethod
    def _gen_macro_dependency_graph(macros):
        graph = {}

        for macro in macros:
            if macro['name'] not in graph:
                graph[macro['name']] = set()

            regex = re.compile(f"[^\\w]*{macro['name']}[^\\w]*")
            for macro_to_compare in macros:
                if macro['name'] == macro_to_compare['name']:
                    continue

                # If the condition of macro_to_compare has a regex matching the macro name,
                # then macro is a dependency of macro_to_compare.
                if regex.search(macro_to_compare['condition']['condition']) is not None:
                    graph[macro['name']].add(macro_to_compare['name'])

        return graph

    # Based on the macro dependency graph, it calculates the weight of
    # each macro based on the order in which they should be removed and no
    # dependency errors should arise
    # For example those macros that are not used by any other macro, can be
    # instantly removed and will have a weight of 0. Those that depend on weight 0 will
    # have weight 1 and so on.
    # If a macro depends on multiple macros, the weight of this macro will be
    # at least higher than the max weight of its dependencies.
    @staticmethod
    def _gen_weighted_macro_list(macros):
        graph = SortMacrosByDepedency._gen_macro_dependency_graph(macros)
        weights = {}

        def calculate_macro_weight(macro_name, macro_dependencies):
            if macro_name in weights:
                return weights[macro_name]
            if len(macro_dependencies) == 0:
                weights[macro_name] = 0
                return 0
            dependencies_weight = [calculate_macro_weight(dependency, graph[dependency]) for dependency in
                                   macro_dependencies]

            weight = max(dependencies_weight) + 1
            weights[macro_name] = weight
            return weight

        for macro_name, macro_dependencies in graph.items():
            calculate_macro_weight(macro_name, macro_dependencies)

        return weights
