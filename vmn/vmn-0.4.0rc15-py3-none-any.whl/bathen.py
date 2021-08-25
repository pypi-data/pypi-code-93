class Person(object):
    def __init__(self, a1, b1):
        self.name = a1
        self.age = b1
        self.hobbie = 'sport'

    def speakbaboo(self):
        print(
            f"My hobbie is {self.hobbie}"
        )


class MyString(object):
    def __init__(self, bla):
        self.str = bla
        self.length = len(self.str)

    def toUpperCase(self):
        return self.str.upper()


d = Person("bathen", 33)
d.speakbaboo()

b = Person("pavel", 30)

c = MyString("ghfhgfgfdtg")
print(c.length)
print(c.toUpperCase())


print(d.name)

pass