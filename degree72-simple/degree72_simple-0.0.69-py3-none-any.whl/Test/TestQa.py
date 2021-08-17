from Core.QaBase import QaBase


class TestQa(QaBase):
    def before_run(self, **kwargs):
        super(TestQa, self).before_run(**kwargs)


if __name__ == '__main__':
    t = TestQa()
    t.before_run()