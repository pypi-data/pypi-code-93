import unittest

from dv_data_generator.dv_data_director import DvDataDirector
from dv_data_generator.builder.dv_request_builder import DvRequestTypes


class DirectorTests(unittest.TestCase):
    def test_dbm_builder(self):
        director = DvDataDirector(credentials="", debug=True)

        report = director.advertisers_report()
        self.assertIn("kind", report.query,
                      msg="Advertiser repors should return a kind tag when using DBM api")
        self.assertEqual(report.query["kind"], "doubleclickbidmanager#query",
                         msg="DBM api kind is always `doubleclickbidmanager#query`")

        partner_filters = ["1", "2", "3"]

        self.assertNotIn("filters", report.query["params"],
                         msg="There should be no filters if not explicitly set")

        report = report.set_partner_filter(partner_filters)

        self.assertIn("filters", report.query["params"],
                      msg="There should be filters after being set")

        report = director.partner_list()
        self.assertEqual(DvRequestTypes.LIST_PARTNERS,
                         report.query, msg="Method must list all partners")

        report = director.partner_list_of_ids()
        self.assertEqual(DvRequestTypes.LIST_PARTNER_IDS,
                         report.query, msg="Method must list all partner ids")
