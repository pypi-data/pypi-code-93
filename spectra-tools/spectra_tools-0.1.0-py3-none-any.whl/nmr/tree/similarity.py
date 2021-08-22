from .tree import create_tree
from math import exp

def get_similarity(a, b, options={}):
    """
    Gets the similarity between two trees.
    """
    # Gets optional parameters
    alpha = options.get('alpha', 0.1)
    beta = options.get('beta', 0.33)
    gamma = options.get('gamma', 0.001)

    if a is None or b is None:
        return 0
    if isinstance(a, list):
        a = create_tree(a)
    if isinstance(b, list):
        b = create_tree(b)
    c = alpha * min(a._sum, b._sum) / max(a._sum, b._sum) + (1 - alpha) * exp(-gamma * abs(a._center - b._center))
    similarity = beta * c + (
        (1 - beta) * (
            get_similarity(a._left, b._left, options) + get_similarity(a._right, b._right, options)
        )
    ) / 2
    print(similarity)
    return similarity
