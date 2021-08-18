

def chunk(array, chunk_size):
    return [array[i * chunk_size:(i + 1) * chunk_size] for i in range((len(array) + chunk_size - 1) // chunk_size)]
