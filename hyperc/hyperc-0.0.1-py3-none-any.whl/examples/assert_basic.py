from hyperc.api import schedule


class CA:
    pass


class CB:
    pa: CA
    flag: bool


def myact(ob: CB):
    assert ob.flag == True
    ob.pa = oa1
#
#
# ob = CB()
# ob.pa = oa
# ob.flag = False
#
# ob1 = CB()
# ob1.pa = oa
# ob1.flag = True
#
# myact(ob, ob1)
# myact(ob1, ob)


def myact2():
    assert ob.flag == False
    ob.pa = CA()  # выбрать из кучи
    ob.flag = True
    return CA()

    # (:action myact2
    #     :parameters (?var-bool--4 - bool ?var-bool-flag-4 - bool ?var-CA-pa-6 - CA ?var-bool-flag-5 - bool)
    #     :precondition (and
    #         (= ?var-bool-flag-4 bool-4)
    #         (CB-flag CB--3 ?var-bool-flag-4)
    #         (CB-pa CB--3 ?var-CA-pa-6)
    #         (CB-flag CB--3 ?var-bool-flag-5)
    #     )
    #     :effect (and
    #         (not (CB-pa CB--3 ?var-CA-pa-1))
    #         (CB-pa CB--3 CA-6)
    #         (not (CB-flag CB--3 ?var-bool-flag-4))
    #         (CB-flag CB--3 bool-5)
    #         (increase (total-cost) 1)
    #     )
    # )


oa = CA()
oa1 = CA()

ob = CB()
ob.pa = oa
ob.flag = False


def _run():
    return schedule(lambda ob: ob.pa == oa1)


if __name__ == '__main__':
    _run()
