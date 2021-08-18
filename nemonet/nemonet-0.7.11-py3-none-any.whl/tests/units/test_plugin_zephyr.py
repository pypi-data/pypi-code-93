# Created by Jan Rummens at 18/01/2021
import unittest
import json
from requests.auth import HTTPBasicAuth
import requests

from nemonet.plugin.handle_zephyr import merge_json_xml, set_jira_item_status

xml_file="""<graph>
    <nodes>
        <node name="selenium"/>
        <node name="phrase"/>
        <node name="waiting"/>
    </nodes>
    <edges>
        <edge from="selenium" to="phrase"/>
        <edge from="phrase" to="waiting"/>
    </edges>
    <actions>
        <action xpath="" type="OPENURL" nodename="selenium" value="https://www.selenium.dev/"/>
        <action xpath="//*[@id='gsc-i-id1']" type="TEXTABLE-ENTER" nodename="phrase" value="computer vision"/>
        <action xpath="" type="WAIT" nodename="waiting" value="5"/>
    </actions>
</graph>"""

json_file="""{
    "plugin": {
        "zephyr": {
            "project" : "FORE",
            "summary" : "summary",
            "description" : "description"
        }
    }
}"""

class MyTestCase(unittest.TestCase):

    def setUp(self):
        fp = open("dummy.xml","w")
        fp.write(xml_file)
        fp.close()
        fp = open("dummy.json","w")
        fp.write(json_file)
        fp.close()

    def test_read_json(self):
        data = None
        with open('dummy.json') as json_file:
            data = json.load(json_file)
            json_file.close()

        self.assertTrue( data['plugin']['zephyr']['project'] == "FORE" )
        self.assertTrue( data['plugin']['zephyr']['summary'] == "summary")
        self.assertTrue( data['plugin']['zephyr']['description'] == "description")


    def test_merge_xml_json(self):
        merge_json_xml("dummy")
        # TODO check the files (json, xml) with assert statements

if __name__ == '__main__':
    unittest.main()
