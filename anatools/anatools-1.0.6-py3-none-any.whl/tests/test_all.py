import unittest2
import HtmlTestRunner
import os
import datetime
from .anaclient.test_anaclient import TestAnaClient
from .api.test_api import TestAPI
from atlassian import Confluence
from pathlib import Path


def test_all():
    print("Running tests...", end='')

    curpath = os.path.abspath(os.curdir)
    fname = curpath+'/tests/test_output/outfile.txt'

    outfile = open(fname,"w")    

    suite = unittest2.TestSuite([
        unittest2.TestLoader().loadTestsFromTestCase(TestAnaClient),
        unittest2.TestLoader().loadTestsFromTestCase(TestAPI)
    ])

    runner=HtmlTestRunner.HTMLTestRunner(output=curpath+'/tests/test_reports', report_name="report", add_timestamp=False, verbosity=2, stream=outfile, combine_reports=True)        
    runner.run(suite)
    outfile.close()
    print('Complete!')


def upload_results():
    print("Publishing Results to Confluence")

    curpath = os.path.abspath(os.curdir)
    fname = curpath+'/tests/test_output/outfile.txt'
    token = 'ixy4JzPFtBa001TnnXdKD836'

    confluence = Confluence(
        url='https://dadoes.atlassian.net',
        username='sam@rendered.ai',
        password=token)

    tests_body = Path(fname).read_text()

    new_confluence_data = ""
    confluence_data_lines = tests_body.splitlines()
    for line in confluence_data_lines:
        if "OK" in line:
            line = "<p style='color:green'>" + line + "</p>"
        elif "FAIL" in line:
            line = "<p style='color:red'>" + line + "</p>"
        elif "ERROR" in line:
            line = "<p style='color:orange'>" + line + "</p>"
        else:
            line = "<p>" + line + "</p>"

        new_confluence_data += line

    test_time = datetime.datetime.now().strftime('%b %d %Y %H:%M ET')

    title = 'Test Run on: ' + test_time
    parent_id='1449951314'
    space = 'ANA'

    status = confluence.create_page(
        parent_id=parent_id,
        space=space,
        title=title,
        body=new_confluence_data)

    attach_file = curpath+"/tests/test_reports/report.html"
    name = "report.html"
    page_id = confluence.get_page_by_title(space=space, title=title).get("id") or None
    confluence.attach_file(filename=attach_file, name=name, content_type='html', page_id=page_id, space=space)

    link = """<p>
    <ac:link>
        <ri:attachment ri:filename="{}"/>
    </ac:link>
    </p>""".format(
        name
    )

    confluence.append_page(page_id, title, link)

if __name__ == '__main__':
    test_all()
    #upload_results()