def _2str(u):
    return u if u is str else str(u)

def _reverse_endpoint(tag):
    if tag == '>':
        return '<'
    else:
        return tag

def _edge_data2str_beautify(edge):
    u, v, tags = edge
    utag, vtag = tags[_2str(u)], tags[_2str(v)]

    if vtag != '>' and utag == '>':
        u, v, utag, vtag = v, u, vtag, utag

    return f"{u} {_reverse_endpoint(utag)}" \
           f"-" \
           f"{vtag} {v}"