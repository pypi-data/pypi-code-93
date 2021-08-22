
def create_main_tree(x, y, _from, _to, min_window, threshold):
    """
    Create a main tree.

    Args:
    """
    if (_to - _from) < min_window:
        return None
    # Search first point.
    start = binary_search(x, _from)
    if start < 0:
        start = ~start
    # Stop at last point.
    _sum = 0
    center = 0
    for i in range(start, len(x)):
        if x[i] >= _to:
            break
        _sum += y[i]
        center += x[i] * y[i]
    if _sum < threshold:
        return None
    center /= _sum
    if (center - _from < 1e-6) or (_to - center < 1e-6):
        return None
    if (center - _from < min_window / 4):
        return create_main_tree(x, y, center, _to, min_window, threshold)
    else:
        if (_to - center < min_window / 4):
            return create_main_tree(x, y, _from, center, min_window, threshold)
        else:
            return Tree(
                _sum=_sum,
                center=center,
                left=create_main_tree(x, y, _from, center, min_window, threshold),
                right=create_main_tree(x, y, center, _to, min_window, threshold),
            )


def create_tree(spectrum, options = {}):
    """
    Create a tree.
    """
    x = spectrum[0]
    min_window = options.get('min_window', 0.16)
    threshold = options.get('threshold', 0.01)
    _from = options.get('_from', x[0])
    _to = options.get('_to', x[-1])
    return create_main_tree(
        x=spectrum[0],
        y=spectrum[1],
        _from=_from,
        _to=_to,
        min_window=min_window,
        threshold=threshold,
    )


# Returns index of x in array if present, else -1.
# If the value is not in the array, then -(index + 1) is returned, where index is where the value should be inserted into the array to maintain sorted order.
def binary_search(arr, x, low=None, high=None):
    """
    Binary search.
    """
    if low is None:
        low = 0
    if high is None:
        high = len(arr) - 1
    # Confirm that array is sorted.
    if not check_sorted(arr):
        return None
    if high >= low:
        mid = low + (high - low) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] > x:
            return binary_search(arr, x, low, mid - 1)
        else:
            return binary_search(arr, x, mid + 1, high)
    else:
        return -(low + 1)

def check_sorted(arr):
    """
    Check if array is sorted.
    """
    for i in range(1, len(arr)):
        if arr[i] < arr[i - 1]:
            return False
    return True


class Tree:
    """Represents the tree structure of the NMR.
    """
    def __init__(self, _sum, center, left, right):
        """
        Args:
            sum (int): The sum of the tree.
            center (int): The center of the tree.
            left (int): The left child of the tree.
            right (int): The right child of the tree.
        """
        self._sum = _sum
        self._center = center
        self._left = left
        self._right = right