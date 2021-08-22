

def report(path, contents):
    f = open(path, 'w', -1, "utf-8")
    f.write(contents)
    f.close()
