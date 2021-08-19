from typing import List

CHUNK_SIZE: int = 20


def chunk(data: List[str], sizes: List[int]) -> List[List[str]]:
    i = 0
    output = []

    for size in sizes:
        a_slice: List[str] = data[i : i + size]
        if len(a_slice) > 0:
            output.append(a_slice)
        i += size

    return output


def to_chunk_sizes(collection_length: int, chunk_size: int = CHUNK_SIZE) -> List[int]:
    whole_size: int = int(collection_length / chunk_size)
    parts: int = collection_length % chunk_size

    return [chunk_size for _ in range(whole_size)] + [parts]
