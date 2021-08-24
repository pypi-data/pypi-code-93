from lingoshell.basic import run


def start(filename):
    with open(filename, "r") as file:
        text = file.read()
    if len(text) == 0:
        print(f'RUNTIME ERROR: file "{filename}" is empty')
        return
    result, error = run("<stdin>", text)

    if error:
        print(error.as_string())
    elif result:
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))
