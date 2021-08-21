def chunk_list(list_to_be_chunked, chunk_size):
    """Splits the given list into evenly-sized "chunks", each of size chunk_size"""
    return [
        list_to_be_chunked[i : i + chunk_size]
        for i in range(0, len(list_to_be_chunked), chunk_size)
    ]
