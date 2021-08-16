import os

from Core.JobBase import JobBase
import json
from Test.TestDao import TestDao
from Util.DumperHelper import DumperHelper
from Util.CSVHelper import get_data_from_csv
from Test.TestEntity import TestEntity
from Util.MySqlHelper import MysqlHelper


class TestAction(JobBase):
    api_key = ''

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.initialize()

    def initialize(self):
        self.maxHourlyPageView = 1000000
        self.proxy = [self.PROXY_SQUID_US_3]
        if self.debug():
            self.proxy = [self.NONE_PROXY]
            self.proxy = [self.LOCALHOST]
        self._dao = TestDao(run_id=self.run_id,run_date=self.run_date, log=self.log, buffer_count=100000)
        self.dumper = DumperHelper(schedule_interval='hour')

    def on_run(self, **kwargs):
        try:
            self.log.info("%s has started" % self.__class__.__name__,
                          "jobID:[%s]" % self.job_id)
            self.api_key = ''
            # self.test()
            self.test_insert_data()
            self.log.info("%s has finished" % self.__class__.__name__,
                          "jobID:[%s]" % self.job_id)
        except Exception as e:
            self.log.error("Unexpected/Unhandled Error", str(e))

    # def get_popularity(self, place_id):
    #     response = populartimes.get_id(self.api_key, place_id)
    #     # self.
    #     # for each in

    def test(self):
        t = TestEntity()
        # self.test_export_data()
        self.log.error('error test')
        self.log.error('error test')
        self.log.error('error test')
        self.log.error('error test')
        url = 'http://ip-api.com/json'
        # url = 'https://www.baidu.com'
        # page = self.download_page(url, self.init_http_manager(default_header=True), validate_str_list=[''])
        # self.http_manager = self.init_http_manager(default_header=True)
        # page = self.download_page(url, self.http_manager, validate_str_list=[''])
        # page = 'Test page'
        # self.dumper.dump_page(page, file_name='test.json')
        # self._dao.export_data_to_csv('test.csv')
        # self.after_run()
        # self.send_bot_error_email(to='will.wei@72degreedata.cn')
    pass

    def test_file_name(self):
        import uuid
        check_dict = {}
        for i in range(0, 100):
            test = uuid.uuid4()

    def test_export_data(self):
        input_file = r"E:\test\wikimedia\wikimedia_view_count_2020-05-26.csv"
        rows = get_data_from_csv(input_file)
        for each in rows:
            self._dao.save(each)

    def test_insert_data(self):
        m = MysqlHelper(host='192.168.2.120', table='fiverr_user_url', user='srs', password='password472Srs', db='srs')
        m.connect()

        check_dict = {}
        for each in m.select('SELECT distinct url  FROM srs.fiverr_user_url'):
            check_dict[each.get('url')] = ''
        folder = r"E:\test\fiverr\url"
        for each in os.listdir(folder):
            file = os.path.join(folder, each)
            rows = get_data_from_csv(file)
            for row in rows:
                url = row.get('url')
                if url in check_dict:
                    continue
                else:
                    m.save(row)
                check_dict[url] = ''




if __name__ == '__main__':
    import datetime
    t = TestAction(run_date=datetime.datetime.now())
    t.run(email='will.wei@72degreedata.cn;gaoyue@72degreedata.cn')