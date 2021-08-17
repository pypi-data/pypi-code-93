def compare(accepted, received):
    "Exact byte-wise comparison."
    return accepted == received


def extension(extension_point):
    extension_point.add(
        name='exact',
        description='Exact byte-wise comparison',
        activate=lambda _full, _ext: compare
    )
