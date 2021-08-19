from typing import List

import DPGM as AF
from labeling_scheme import l_out, l_undec, l_in, LabelingScheme
from distribution import Distribution


class Labeling:
    """
    A mapping of the arguments from an AF to one of the labels 'in, 'out' or 'undec'.
    String representation is the sets of arguments labeled 'in', 'out' and 'undec' in that order, i.e. '{A,B}{C}{}' for
    A and B labeled 'in', C labeled 'out' and no argument labeled 'undec'.
    """

    def __init__(self, labeling_scheme: LabelingScheme, distribution: Distribution, af: AF):
        self.af = af
        self.distribution = distribution
        self.labeling_scheme = labeling_scheme

        self.label_dict = dict()
        self.labeled_in = []
        self.labeled_out = []
        self.labeled_undec = []

        self._compute_labeling()

    def _compute_labeling(self):
        for argument in self.af.get_nodes():
            label = self.labeling_scheme.get_label(argument, self.distribution)
            self.label_dict[argument.id] = label
            if label == l_in:
                self.labeled_in.append(argument)
            elif label == l_out:
                self.labeled_out.append(argument)
            elif label == l_undec:
                self.labeled_undec.append(argument)
            else:
                assert False, "unknown label " + label

    def get_label(self, argument: AF.Node) -> str:
        return self.label_dict[argument.id]

    def get_in(self):
        """
        Returns the list of all nodes labelled 'in'.
        """
        return self.labeled_in

    def get_out(self):
        """
        Returns the list of all nodes labelled 'out'.
        """
        return self.labeled_out

    def get_undec(self):
        """
        Returns a list of all nodes labelled 'undec'.
        """
        return self.labeled_undec

    def get_labeling_triple(self):
        """
        Returns the lists of arguments labelled 'in', 'out' and 'undec' in that order as tuple.
        """
        return self.labeled_in, self.labeled_out, self.labeled_undec

    def __repr__(self):
        repr_set = lambda s: "{" + ",".join(sorted(map(repr, s))) + "}"
        set_in = repr_set(self.labeled_in)
        set_out = repr_set(self.labeled_out)
        set_undec = repr_set(self.labeled_undec)
        return set_in + set_out + set_undec

    def __eq__(self, other):
        return isinstance(other, Labeling) and self.get_labeling_triple() == other.get_labeling_triple()

    def __hash__(self):
        return hash(repr(self))

    def __lt__(self, other):
        return self.get_labeling_triple() < other.get_labeling_triple()


def print_labelings(labelings: List[Labeling], printer=print):
    labelings_formatted = sorted(list(set(map(repr, labelings))))
    assert len(labelings) == len(labelings_formatted)
    for labeling_string in labelings_formatted:
        printer(labeling_string)
