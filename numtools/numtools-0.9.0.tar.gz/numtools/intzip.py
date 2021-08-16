"""
Provide several ways to show sequences of integers
"""

from itertools import groupby
from operator import itemgetter
from collections import UserList
import re


def _get_groups(seq):
    for k, g in groupby(enumerate(seq), key=lambda i_x: i_x[0] - i_x[1]):
        yield list(map(itemgetter(1), g))


def _cons2str(seq, sep=", ", linkword="to"):
    """transform a sequence of consecutive integers to
    human-friendly string

    >>> _cons2str([4])
    '4'
    >>> _cons2str([4, 5])
    '4, 5'
    >>> _cons2str([4, 5, 6 ,7, 8])
    '4 to 8'
    """
    tokens = [str(i) for i in seq]
    if len(seq) <= 2:
        ret = sep.join(tokens)
    else:
        ret = "%d %s %d" % (seq[0], linkword, seq[-1])
    return ret


def _cons2tuple(seq, couple_alone=None, astype=tuple):
    """
    >>> _cons2tuple((4,))
    4
    >>> _cons2tuple((4,), couple_alone=0, astype=list)
    [4, 0]
    >>> _cons2tuple((4, 5, 6, 7))
    (4, 7)
    """
    if len(seq) == 1:
        ret = seq[0]
        if couple_alone is not None:
            if couple_alone != "duplicate":
                ret = astype((seq[0], couple_alone))
            else:
                ret = astype((seq[0], seq[0]))
        return ret
    return astype((min(seq), max(seq)))


def hzip(seq, sort=True, sep=", ", last_sep=" and ", linkword="to"):
    """
    Create a human friendly (hence the ``hzip`` name) string from a
    sorted iterable of integers.

    :param seq: iterable to parse
    :type seq: any iterable made of **integers**
    :param sort: if ``True``, sort ``seq`` as a preliminary.
    :type sort: bool
    :param sep: separator to use
    :type sep: str
    :param last_sep: last token for trailing data
    :type last_sep: str
    :param linkword: token to ling groups of integers
    :type lnkword: str

    :returns: a human-friendly string describing ``seq``

    >>> seq =   (1, 2, 6, 5, 11, 7, 8, 9, 3, 12, 0)
    >>> hzip(seq, sort=False)
    '1, 2, 6, 5, 11, 7 to 9, 3, 12 and 0'
    >>> hzip(seq, sep='; ', sort=True, linkword='thru', last_sep=' and finally ' )
    '0 thru 3; 5 thru 9; 11 and finally 12'
    >>> # zipping an empty sequence is olso OK
    >>> hzip([])
    ''
    """
    if sort:
        seq = sorted(list(seq))
    tokens = [_cons2str(grp, sep=sep, linkword=linkword) for grp in _get_groups(seq)]
    s = sep.join(tokens)
    # replace last occurence of `sep` by `last_sep`
    ix = s.rfind(sep)
    if ix > 0:
        s = s[:ix] + last_sep + s[(ix + len(sep)) :]

    return s


def hunzip(hseq, sep=", ", last_sep=" and ", linkword="to"):
    """
    Revert back a hzip to python list.

    :param hseq: representation of a sequence
    :type hseq: string
    :param sep: separator to search for
    :type sep: str
    :param last_sep: trailing separator to search for
    :type last_sep: str
    :param linkword: token group separator to search for
    :type linkword: str

    :returns: list of integers desgribed by ``hseq``

    >>> s = '0 to 3, 5 to 9, 11 and 12'
    >>> hunzip(s)
    [0, 1, 2, 3, 5, 6, 7, 8, 9, 11, 12]
    >>> femap_output = ('         32              ,         62              ,         '
    ... '65 thru       99, 14439              ,      20343              ,      22601, '
    ... ' 39496              ,      46966              ,      51287, '
    ... ' 111501 thru   111505,     117556 thru   117563,     119179,        '
    ... ' 119228              ,     119292              ,     119689,           '
    ... ' 119738              ,     128720 thru   128721,     128733 thru   128734,'
    ... ' 140106 thru   192518,                         ,          ')
    >>> hunzip(femap_output, sep=',', linkword='thru')
    [32, 62, ... 192517, 192518]
    """
    # last_sep can safely be replaced by sep
    hseq = hseq.replace(last_sep, sep)
    hseq = re.sub(" +", " ", hseq)  # consecutive blanks by single blank
    hseq = re.sub(r",\s*,", ", ", hseq)  # consecutive coma by single coma
    hseq = re.sub(r",\s*$", "", hseq)
    _hseq = hseq.split(sep)
    hseq = []
    for token in _hseq:
        if linkword in token:
            min, max = map(int, token.split(" %s " % linkword))
            hseq += list(range(min, max + 1))
        elif last_sep in token:
            min, max = map(int, token.split(last_sep))
            hseq += [min, max]
        else:
            hseq.append(int(token))
    return hseq


def zip_list(seq, couple_alone=None, astype=tuple):
    """
    Zip a sequence of integers into an iterable of intervals.

    :param seq: iterable of integers
    :param couple_alone: how to handle alone values
    :type couple_alone: default integer or string ('duplicate' only)
    :param astype: type of returned iterable
    :type astype: type within *list*, *tuple*, *frozenset*


    >>> input_list=(1, 2, 3, 13, 7, 8, 10, 11, 12, 5)
    >>> zip_list(input_list)
    ((1, 3), 5, (7, 8), (10, 13))
    >>> zip_list(input_list, couple_alone=0)
    ((1, 3), (5, 0), (7, 8), (10, 13))
    >>> zip_list(input_list, couple_alone='duplicate', astype=list)
    [[1, 3], [5, 5], [7, 8], [10, 13]]
    >>> # zipping an empty sequence is also OK
    >>> zip_list((), couple_alone=0)
    ()
    """
    seq = sorted(list(set(seq)))
    groups = astype(
        [
            _cons2tuple(grp, astype=astype, couple_alone=couple_alone)
            for grp in _get_groups(seq)
        ]
    )
    return groups


if __name__ == "__main__":
    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS)
