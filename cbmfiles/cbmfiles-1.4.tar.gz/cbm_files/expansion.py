def vic20_expansion_required(start, length):
    """Return a tuple describing what memory expansion a memory range uses."""

    def _in_range(s, e, rs, re):
        return (e >= rs and e < re) or (s >= rs and s < re) or (s < rs and e > re)

    end = start + length

    x_3k = _in_range(start, end, 0x0400, 0x1000)
    x_blk1 = _in_range(start, end, 0x2000, 0x4000)
    x_blk2 = _in_range(start, end, 0x4000, 0x6000)
    x_blk3 = _in_range(start, end, 0x6000, 0x8000)
    x_blk5 = _in_range(start, end, 0xA000, 0xC000)

    return x_3k, x_blk1, x_blk2, x_blk3, x_blk5
