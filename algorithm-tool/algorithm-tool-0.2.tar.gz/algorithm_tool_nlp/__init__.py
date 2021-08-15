from algorithm_tool_nlp.algorithm_tool_core.build import nlp_algorithm


def edit_distance(s, t):
    return nlp_algorithm.LevenshteinDP(s, t)
