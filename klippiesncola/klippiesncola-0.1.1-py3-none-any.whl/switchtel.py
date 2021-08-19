import requests
from bs4 import BeautifulSoup
import time
import json
import csv
import logging
import os
import urllib.parse
from functools import partial
from pathlib import Path

logger = logging.getLogger(__name__)

base_url = 'https://www.switchtel.co.za'
services_url = base_url+'/czServer/src/services'
class Account(object):
    """docstring for Account."""
    loggedin = False
    user = {
    'username':os.environ.get('SWITCHTEL_USERNAME'),
    'password':os.environ.get('SWITCHTEL_PASSWORD')
    }
    data = {
    'vpbxname':os.environ.get('SWITCHTEL_VPBXNAME'),
    'vpbxid':os.environ.get('SWITCHTEL_VPBXID')
    }
    session = requests.session()
    def __init__(self, user=user):
        super(Account, self).__init__()

    def login(self):
        url = base_url+'/clientzone/index.php?controller=login'
        data = self.user
        if not self.loggedin:
            req = self.session.get(url)
            soup = BeautifulSoup(req.content,features="html.parser")
            hidden_tags = soup.find_all("input", type="hidden")

            for tag in hidden_tags:
                print(tag)
                data[tag.get('name')] = tag.get('value')
            print(data)
            req = self.session.post(url,data)
            if req.status_code == 200:
                self.loggedin = True
                self.session.headers = req.headers
            else:
                self.loggedin = False
            return req

class CallRecording(Account):
    def __init__(self):
        pass

    def get(self,uniqueid,sequence,to=None):
        self.data.update({
        'userid':'',
        'format':'mp3-stream',
        'legacy':'false'
        })
        url = services_url+'/showCallRecording'
        if not self.loggedin:
            try:
                self.login()
            except Exception as e:
                return e
        self.data.update({'uniqueid':uniqueid,'sequence':sequence})
        print(uniqueid,self.data)
        recording = self.session.post(url,data=self.data)
        # recording = self.session.get(url,self.data)
        file_name = '%s-%s.mp3'%(uniqueid,sequence)
        if to:
            p = Path('exports/%s/'%to)
        else:
            p = Path('exports/')

        p.mkdir(parents=True, exist_ok=True)
        with open(p/file_name, 'wb') as f:
            f.write(recording.content)
        return recording

    def list(self,starting,ending=None,url=None):
        #format for dates 2021-08-13 23:59:59
        #TODO: accept kwargs and pass to data

        url = url if url else services_url+'/getHostedCdrs'
        data = {'vpbxId':'3128'}
        if not self.loggedin:
            try:
                self.login()
            except Exception as e:
                return e
        if ending:
            data['dateEnd'] = ending
        data['dateStart'] = starting
        data['exportCdrs'] = False
        data['legacy'] = False
        clean_data = [(k, str(v).lower() if isinstance(v, bool) else v) for k, v in data.items()]
        data = urllib.parse.urlencode(clean_data)
        print(data,url)
        self.session.headers.update({'Content-Type':'application/x-www-form-urlencoded'})
        req = self.session.post(url,data)
        recordings = []
        if req.status_code == 200 and len(req.content) != 0:
                recordings = req.json()
                new_recordings = []
                for record in recordings:
                    print(record.get('uniqueid'),record.get('sequence'))
                    record['download'] =lambda x=record.get('uniqueid'), y=record.get('sequence'),z=record.get('to') :self.get(x,y,z)
                    new_recordings.append(record)
                recordings = new_recordings
        return recordings

    def parse_csv(self,csv_url):
        data = {
        'meta':{
            'size':0
            },
        'objects': []
        }
        try:
            with open(csv_url) as csv_file:
                csv_objects = csv.reader(csv_file.readlines())
                header = None
                objects = []
                for line in csv_objects:
                    if not header:
                        header = line
                    else:
                        object = dict(zip(header,line))
                        uniqueid = object.get('Call Recording File Name')
                        objects.append({uniqueid:object})
                data['objects'] = objects
                data['meta']['size'] = len(objects)
        except Exception as e:
            logger.warning(e)
            data['error']: e.message

        return data
