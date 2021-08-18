import pytest
from koalak.decorators import defaultdecorator  # merge_decorators,
from koalak.decorators import addinit, persistent_addinit


def addx(self, *args, **kwargs):
    self.x = True


def addy(self, *args, **kwargs):
    self.y = True


def addz(self, *args, **kwargs):
    self.z = True


def addu(self, *args, **kwargs):
    self.u = True


def addv(self, *args, **kwargs):
    self.v = True


def test_simple():
    @addinit(addx)
    class A:
        pass

    assert A().x


def test_cls_have_init():
    @addinit(addx)
    class A:
        def __init__(self):
            self.a = True

    a = A()
    assert a.a
    assert a.x
    """Brainstorm
    Pour que les deux init (decorated_init et original_init)
    soit executer c'est obligé d'executer le decorated_init
    et que le decorated_init execute l'original_init

    Comment le decorated init doit executer l'original_init?
    """


def test_cls_subclass_have_init_without_call_super():
    """If the subclass don't call"""

    @addinit(addx)
    class A:
        pass

    class B(A):
        def __init__(self):
            self.b = True

    b = B()
    assert b.b
    assert not hasattr(b, "x")


def test_cls_subclass_have_init_with_call_super():
    @addinit(addx)
    class A:
        pass

    class C(A):
        def __init__(self):
            super().__init__()
            self.c = True

    c = C()
    assert c.c
    assert c.x


def test_parent_cls_have_init_without_call_super():
    class A:
        def __init__(self):
            self.a = True

    @addinit(addx)
    class B(A):
        def __init__(self):
            self.b = True

    b = B()
    assert b.b
    assert not hasattr(b, "a")
    assert b.x


def test_parent_cls_have_init_with_call_super():
    class A:
        def __init__(self):
            self.a = True

    @addinit(addx)
    class B(A):
        def __init__(self):
            super().__init__()
            self.b = True

    b = B()
    assert b.b
    assert b.a
    assert b.x


"""
n: new_init (decorator)
o: old_init (__init__)

A: n(o)
B: n(o)

decorate init A
    inits exist pas crée inits
    rajoute __init__ au inits
    remplacer l'init
decorate B
    inits exist rajouter l'in
m2: chaque class on lui ajoute son init

Si class à pas d'init

An Ao
Bn Bo(s)
Bn => Bo => An

Rajouter un traitement X à l'initialisation d'un objet sans rien chambouler
def special_init(self, *args, **kwargs):
    self.x = "caca"

@addinit(special_init)
class A:
   def __init__(self):
       ...

X: spécial init (genre vérifie que la class est abstraite)
D: dispatcher (le nouveau __init__ qui sait qui appeler)
I: Init original

@D(X) A - I
@D(Y) B - I(S)
B()
D(B) c'est lui qui va mener la danse
D(B) => Y
D(B) => I  le I appel
I(S) == D(A) => (le B appele le super qui est le disptacher de A)
    appel X et appel Y

forcément n(B) va etre appelé
- execute n(b)
- n(b) va executer old (jusque la c'est bien)
- old va executer super (bien mais il va rappeler)

Je dois savoir si j'ai déjà executer init ou pas sur l'objet
- marquer l'objet!

Problem le même disptacher est appeler, deux solutions possibles
- faire en sorte qu'un dispatcher différent soit appelé
- le dispatcher gere tout

le même dispatcher est appeler veut dire

- un dispatccher qui gere tout =>

@A: x init
@B: y init (no super)
B(): b y (pas de x a)

@A: x init
@B: y init

"""


def test_two_subclasses_have_decorator_with_super():
    @addinit(addx)
    class A:
        def __init__(self):
            self.a = True

    @addinit(addy)
    class B(A):
        def __init__(self):
            super().__init__()
            self.b = True

    # Test that B don't affect A
    a = A()
    assert a.a
    assert a.x
    assert not hasattr(a, "b")
    assert not hasattr(a, "y")

    b = B()
    assert b.a
    assert b.b
    assert b.x
    assert b.y


def test_three_subclasses_with_super():
    @addinit(addx)
    class A:
        def __init__(self):
            self.a = True

    a = A()
    assert a.a
    assert not hasattr(a, "b")
    assert not hasattr(a, "c")
    assert a.x
    assert not hasattr(a, "y")
    assert not hasattr(a, "z")

    @addinit(addy)
    class B(A):
        def __init__(self):
            super().__init__()
            self.b = True

    a = A()
    assert a.a
    assert not hasattr(a, "b")
    assert not hasattr(a, "c")
    assert a.x
    assert not hasattr(a, "y")
    assert not hasattr(a, "z")

    b = B()
    assert b.a
    assert b.b
    assert not hasattr(b, "c")
    assert b.x
    assert b.y
    assert not hasattr(b, "z")

    @addinit(addz)
    class C(B):
        def __init__(self):
            super().__init__()
            self.c = True

    a = A()
    assert a.a
    assert not hasattr(a, "b")
    assert not hasattr(a, "c")
    assert a.x
    assert not hasattr(a, "y")
    assert not hasattr(a, "z")

    b = B()
    assert b.a
    assert b.b
    assert not hasattr(b, "c")
    assert b.x
    assert b.y
    assert not hasattr(b, "z")

    c = C()
    assert c.a
    assert c.b
    assert c.c
    assert c.x
    assert c.y
    assert c.z


def test_args():
    @addinit(addx)
    class A:
        def __init__(self, a):
            self.a = a

    a = A(5)
    assert a.x
    assert a.a == 5


def test_args_kwargs():
    def myinit_x(self, a, b=2):
        self.x = a + b

    @addinit(myinit_x)
    class A:
        def __init__(self, a, b=2):
            self.a = a
            self.b = b

    a1 = A(5)
    assert a1.a == 5
    assert a1.b == 2
    assert a1.x == 7

    a2 = A(2, 3)
    assert a2.a == 2
    assert a2.b == 3
    assert a2.x == 5


def test_runfirst():
    def init_10(self):
        self.a = 10

    @addinit(init_10, runfirst=False)
    class A:
        def __init__(self):
            self.a = 5

    a = A()
    assert a.a == 10

    @addinit(init_10, runfirst=True)
    class A:
        def __init__(self):
            self.a = 5

    a = A()
    assert a.a == 5


def test_runfirst_default():
    # Testt that by default runfirst if False
    # ie: the added__init__ will run at the end
    # to not break code of others
    def init_10(self):
        self.a = 10

    @addinit(init_10, runfirst=False)
    class A:
        def __init__(self):
            self.a = 5

    a = A()
    assert a.a == 10


def test_many_added__inits__in_addinit():
    @addinit(addx, addy)
    class A:
        def __init__(self):
            self.a = True

    a = A()
    assert hasattr(a, "x")
    assert hasattr(a, "y")
    assert hasattr(a, "a")


def test_many_addinit_in_same_cls():
    @addinit(addy)
    @addinit(addx)
    class A:
        def __init__(self):
            self.a = True

    a = A()
    assert hasattr(a, "x")
    assert hasattr(a, "y")
    assert hasattr(a, "a")


def test_many_addinit_and_many_addes_inits():
    @addinit(addz, addu)
    @addinit(addx, addy)
    class A:
        def __init__(self):
            self.a = True

    a = A()
    assert hasattr(a, "x")
    assert hasattr(a, "y")
    assert hasattr(a, "z")
    assert hasattr(a, "u")
    assert hasattr(a, "a")


def test_parent_without_init():
    @addinit(addx)
    class A:
        pass

    class B(A):
        def __init__(self):
            super().__init__()
            self.b = True

    b = B()
    assert b.b
    assert b.x


def test_complecated_01():
    @addinit(addx, addy)
    class A:
        def __init__(self):
            self.a = True

    a = A()
    assert a.a
    assert a.x
    assert a.y

    @addinit(addz, addu)
    @addinit(addv)
    class B(A):
        def __init__(self):
            super().__init__()
            self.b = True

    a = A()
    assert a.a
    assert a.x
    assert a.y
    assert not hasattr(a, "b")
    assert not hasattr(a, "z")
    assert not hasattr(a, "u")
    assert not hasattr(a, "v")

    b = B()
    assert b.a
    assert b.x
    assert b.y

    assert b.b
    assert b.z
    assert b.u
    assert b.v


def test_persistant_addinit():
    @persistent_addinit
    def myinit_x(self, *args, **kwargs):
        self.x = True

    @myinit_x
    class A:
        pass

    a = A()
    assert a.x


def test_persistant_addinit_real_example_abstract():
    # asbtract must run first
    @persistent_addinit
    def enable_abstract(self, *args, **kwargs):
        if "abstract" in self.__class__.__dict__:
            raise TypeError("Can't instantiate abstract class")

    @enable_abstract
    class A:
        pass

    a = A()

    class B(A):
        abstract = True

    with pytest.raises(TypeError):
        B()


def test_persistant_addinit_runfirst():
    @persistent_addinit(runfirst=True)
    def runfirst(self):
        self.x = 10

    @runfirst
    class A:
        def __init__(self):
            self.x = 5

    a = A()
    assert a.x == 5
