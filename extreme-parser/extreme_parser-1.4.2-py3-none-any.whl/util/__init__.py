def read_file(file) -> str:
    stream = open(file, encoding="utf8")
    text = stream.read()
    stream.close()
    return text
