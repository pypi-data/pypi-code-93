tol=1e-10

def say_hello(name=None):
    if not(name):
        print('Hello, stranger!')
    else:
        print(f'Hello, {name}!')
