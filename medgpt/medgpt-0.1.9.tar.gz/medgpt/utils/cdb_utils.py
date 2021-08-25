def get_parents_map(cuis, pt2ch, depth=3):
    r''' Get a map from a concept to all of its parents up to the `depth`, meaning parents of parents and so on.

    Args:
        pt2ch (`Dict`):
            map from parent concept to children (this is
            usually what we have when building a CDB).

        depth (`int`, optional defaults to 3):
            Get only parents, or parents of parents also, or ...
    '''

    # First convert pt2ch into ch2pt
    ch2pt = {}
    for pt in pt2ch:
        for ch in pt2ch[pt]:
            if ch in ch2pt:
                ch2pt[ch].add(pt)
            else:
                ch2pt[ch] = {pt}

    def get_parents(concept, ch2pt, depth):
        parents = set()
        parents.update(ch2pt.get(concept, []))
        if depth > 0:
            for pt in ch2pt.get(concept, []):
                parents.update(get_parents(pt, ch2pt, depth=depth-1))
        return parents

    ch2all_pt = {}
    for cui in cuis:
        ch2all_pt[cui] = get_parents(cui, ch2pt, depth=depth)

    return ch2all_pt
