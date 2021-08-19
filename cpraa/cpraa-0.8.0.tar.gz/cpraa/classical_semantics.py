from typing import List, Set

import DPGM as AF


class ClassicalSemantics:

    def __init__(self, af: AF.DPGM):
        self.af = af

    def get_extensions(self) -> List[Set[AF.Node]]:
        # implemented by subclasses
        pass


class CF(ClassicalSemantics):
    """Conflict-freeness: A set of arguments S is conflict free iff there is no A and B in S with A->B or B->A."""
    def get_extensions(self):
        extension_candidates = [set()]
        for node in self.af.get_nodes():
            conflicting_nodes = node.get_parents().union(node.get_children())
            new_extension_candidates = []
            for candidate in extension_candidates:
                if not conflicting_nodes.intersection(candidate):
                    new_candidate = candidate.copy()
                    new_candidate.add(node)
                    new_extension_candidates.append(new_candidate)
            extension_candidates.extend(new_extension_candidates)
        return extension_candidates


def defends(af: AF.DPGM, nodes: Set[AF.Node]):
    """
    A node is defended by a set of arguments if all its attackers are in turn attacked from within the set.
    :return: the set of nodes defended by the given set
    """
    defended = set()
    for node in af.get_nodes():
        if node.is_initial():
            defended.add(node)
            continue
        # check whether all attackers of the node are attacked from within the given set of nodes
        all_attacked = True
        for attacker in node.get_parents():
            if not attacker.get_parents().intersection(nodes):
                all_attacked = False
                break
        if all_attacked:
            defended.add(node)
    return defended


class Admissible(ClassicalSemantics):
    """
    A set of arguments is admissible if it is conflict free and defends itself.
    """
    def get_extensions(self):
        scf = CF(self.af)
        adm_extensions = []
        for candidate in scf.get_extensions():
            if candidate.issubset(defends(self.af, candidate)):
                adm_extensions.append(candidate)
        return adm_extensions


class Complete(ClassicalSemantics):
    """
    A set of arguments is complete if it is conflict free and defends exactly itself, i.e. the set equals the set of
    arguments it defends.
    """
    def get_extensions(self):
        scf = CF(self.af)
        cmp_extensions = []
        for candidate in scf.get_extensions():
            if candidate == defends(self.af, candidate):
                cmp_extensions.append(candidate)
        return cmp_extensions


class Grounded(ClassicalSemantics):
    """
    The grounded extension is the complete extension which is minimal w.r.t. set inclusion among all complete
    extensions. It always exists and is unique.
    """
    def get_extensions(self):
        cmp = Complete(self.af)
        cmp_extensions = cmp.get_extensions()
        grn_extensions = []
        for candidate in cmp_extensions:
            if all(map(candidate.issubset, cmp_extensions)):
                grn_extensions.append(candidate)
        assert len(grn_extensions) == 1
        return grn_extensions


class Preferred(ClassicalSemantics):
    """
    A set of nodes is a preferred extension if it is a complete extension and maximal w.r.t. set inclusion among all
    complete extensions. There can be multiple preferred extensions.
    """
    def get_extensions(self):
        cmp = Complete(self.af)
        cmp_extensions = cmp.get_extensions()
        prf_extensions = []
        for candidate in cmp_extensions:
            if all(map(lambda s: not candidate.issubset(s) or candidate == s, cmp_extensions)):
                prf_extensions.append(candidate)
        return prf_extensions


class SemiStable(ClassicalSemantics):
    def get_extensions(self):
        raise NotImplementedError  # TODO


class Stable(ClassicalSemantics):
    """
    A set of nodes is a stable extension if it is a complete extension and each node not in the set is attacked from
    within the set.
    """
    def get_extensions(self):
        cmp = Complete(self.af)
        cmp_extensions = cmp.get_extensions()
        stl_extensions = []
        for candidate in cmp_extensions:
            failed = False
            for A in self.af.get_nodes():
                if A not in candidate:
                    # look for an attack on A from within the candidate extension
                    if not any([B in candidate for B in A.get_parents()]):
                        failed = True
                        break
            if not failed:
                stl_extensions.append(candidate)
        return stl_extensions
