import unittest
from flask import Flask
from bws_crontab import Crontab 
from datetime import datetime, time, date, datetime, timedelta


class CrontabMethods(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(Crontab._parse_value(time(1, 30)), [30, 1, '*', '*', '*'])
        self.assertEqual(Crontab._parse_value(timedelta(days=3, minutes=30)), ["*/30", "*", '*/3', '*', '*'])
        self.assertEqual(Crontab._parse_value(timedelta(minutes=30)), ["*/30", "*", '*', '*', '*'])
        self.assertEqual(Crontab._parse_value(time(10, 2)), [2, 10, '*', '*', '*'])
        self.assertEqual(Crontab._parse_value("1:10:00"), ['*/10', '*/1', '*', '*', '*'])


  
    def test_add_jobs(self):
        app = Flask(__name__)
        cron = Crontab(app)
        
        cron.job(timedelta(minutes=30))(print)
        cron.job(minute=1)(print)
        cron.job(time(10, 2))(print)
        