

from flask_kraken_wq import Queue

from flask_kraken_wq import WorkTask


def test1(a,b):
    print('args a {a}')
    print("args b {b}")
def aa():
    import sys
    print(sys.argv)
    q = Queue()
    kwargs = {'a': 'a', 'b': 'b'}
    q.add(test1, kwargs=kwargs)

    WorkTask().start()

aa()