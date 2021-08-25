from cubicweb.devtools.testlib import CubicWebTC


class PeriodicallyResetCounterTC(CubicWebTC):
    def setup_database(self):
        with self.admin_access.cnx() as cnx:
            self.counter = cnx.create_entity("PeriodicallyResetCounter")
            cnx.commit()

    def test(self):
        with self.admin_access.cnx() as cnx:
            c_eid = self.counter.eid
            counter = cnx.find("PeriodicallyResetCounter", eid=c_eid).one()
            self.assertEqual(counter.initial_value, 0)
            self.assertEqual(counter.increment, 1)
            self.assertEqual(counter.reset_every, "year")
            entity = cnx.entity_from_eid(self.counter.eid)
            self.assertEqual(entity.next_value(), 1)
            self.assertEqual(entity.next_value(), 2)
            cnx.rollback()
            self.assertEqual(entity.next_value(), 1)


if __name__ == "__main__":
    from logilab.common.testlib import unittest_main

    unittest_main()
