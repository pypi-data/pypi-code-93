from __future__ import unicode_literals, absolute_import
'''
 Copyright 2013-2019 Cofense, Inc.  All rights reserved.

 This software is provided by PhishMe, Inc. ("Cofense") on an "as is" basis and any express or implied warranties,
 including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
 disclaimed in all aspects.  In no event will Cofense be liable for any direct, indirect, special, incidental or
 consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
 this software is pursuant to, and permitted only in accordance with, the agreement between you and Cofense.
'''

import logging
import os
import random
import copy
import sys
import time
from datetime import datetime, timedelta

from .api import IntelligenceAPI
from .outputs.JsonFileOutput import JsonFileOutput

# Determine the major version of python running this script.
PYTHON_MAJOR_VERSION = sys.version_info[0]


class CFIntelBase(object):
    '''
    Base Cofense Intelligence object. Manages API credentials, format, threat type and other basics on an integration

    :param integration_root: Integration root directory. Defaults to script run directory
    :param kwargs: Configuration parameters to be passed:


    .. table::

        =================    =========================================        ====================
        Parameter            Description                                      Default
        =================    =========================================        ====================
        CF_USER              Cofense API User Token                           COFENSE_USER
                                                                              environment variable
        CF_PASS              Cofense API Password Token                       COFENSE_PASSWORD
                                                                              environment variable
        INTEL_FORMAT         Report format (json, stix, cef)                  json
        THREAT_TYPE          Threat type (brand, malware)                     malware
        PROXY_URL            Web Proxy URL                                    None
        PROXY_AUTH           Proxy requires authentication                    False
        PROXY_USER           Proxy username                                   None
        PROXY_PASS           Proxy password                                   None
        SSL_VERIFY           Verify SSL certificates for requests.            False
        HALT_ON_ERROR        Stop execution on errors occuring with           False
                             individual reports
        INTEGRATION          Class name of integration being used             JsonFileOutput
        MAX_RETRIES          Max number of attempts to connect                3
        BASE_URL             Cofense API base URL (optional)                  https://www.threathq.com/apiv1/

        =================    =========================================        ====================

    '''

    default_config = {'CF_USER': None,
                      'CF_PASS': None,
                      'INTEL_FORMAT': 'json',
                      'THREAT_TYPE': 'malware',
                      'PROXY_URL': None,
                      'PROXY_AUTH': False,
                      'PROXY_USER': None,
                      'PROXY_PASS': None,
                      'SSL_VERIFY': False,
                      'HALT_ON_ERROR': False,
                      'INTEGRATION': JsonFileOutput}

    def __init__(self, integration_root=None, **kwargs):

        if not integration_root:
            integration_root = os.getcwd()

        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(logging.NullHandler())
        self.logger.info('Initialized Cofense Intelligence Sync')

        self.config = copy.deepcopy(self.default_config)
        self.config['BASE_DIR'] = integration_root

        self.config.update(kwargs)

        if not self.config.get('CF_USER'):
            self.config['CF_USER'] = os.environ.get('COFENSE_USER')
        if not self.config.get('CF_PASS'):
            self.config['CF_PASS'] = os.environ.get('COFENSE_PASSWORD')

        self.api_mgr = self.api_config()

    def api_config(self):
        auth = (self.config['CF_USER'], self.config['CF_PASS'])
        max_retries = self.config.get('MAX_RETRIES') or 3
        proxy = self.config.get('PROXY_URL') or None
        if self.config['PROXY_AUTH']:
            proxy_auth = (self.config['PROXY_USER'], self.config['PROXY_PASS'])
        else:
            proxy_auth = None
        verify = self.config['SSL_VERIFY']
        integration = self.config['INTEGRATION']

        return IntelligenceAPI(auth=auth,
                               max_retries=max_retries,
                               proxy=proxy,
                               proxy_auth=proxy_auth,
                               verify=verify,
                               url=self.config.get('BASE_URL', 'https://www.threathq.com/apiv1/'),
                               integration=integration)

    def run(self, **kwargs):
        pass


class CFIntelSearch(CFIntelBase):
    """
    Cofense Intelligence Search object, inherits configuration and root directory from CFIntelBase. Used to search for
    specific indicators (or other search criteria) and run the Intellegience report object through the defined
    integration's process method
    """

    def run(self, **kwargs):
        '''
        Primary search run method. Converts key word arguments to search parameters and runs the configured integration's
        process method on each report object

        :param kwargs: Any accepted search parameter for Cofense Intelligence API

        .. todo Add proper linking

        '''
        integration_cls = self.config['INTEGRATION']
        integration = integration_cls(self.config)

        results = self.api_mgr.threat_search(**kwargs)

        for result in results:
            integration.process(result)


class CFIntelSync(CFIntelBase):
    '''
    Cofense Intelligence Sync object, inherits configuration and root directory from CFIntelBase. Used to do period
    syncs and collect most recent Intelligence Reports and indicators

    :param kwargs: Configuration parameters to be passed. All parameters configurable in CFIntelBase are available as well as the following:


    .. table::

        =================    =========================================        ======================
        Parameter            Description                                      Default
        =================    =========================================        ======================
        INIT_DATE            Initial date to collect reports from on          30 days ago
                             first run
        JITTER               Add a randomized time offset before              True
                             running. Only set to false during testing
        SCHEDULER_OFFSET     Range (in seconds) of JITTER offset.             600
        POSITION_FILE        File used to track position file                 BASE_DIR/cf_intel.pos
        POSITION             The position UUID of the last run.               None
                             By default on first run POSITION_FILE is
                             created and used to pass this value.
        USE_LOCK             State locking file. *WARNING* setting to         True
                             false may result in integrations running
                             from the same position and result in
                             duplicate data.
        LOCK_FILE            File used to lock run state                      BASE_DIR/cf_intel.lock
        =================    =========================================        ======================

    '''

    sync_defaults = {'JITTER': True,
                     'POSITION': None,
                     'USE_LOCK': True}

    def __init__(self, **kwargs):
        super(CFIntelSync, self).__init__(**kwargs)

        self.config.update(self.sync_defaults)
        self.config.update(kwargs)

        self.begin_date = self.config.get('INIT_DATE')

        self.scheduler_offset = self.config.get('JITTER')

        if not self.config.get('LOCK_FILE'):
            self.config['LOCK_FILE'] = self.config['BASE_DIR'] + '/cf_intel.lock'

        if not self.config.get('POSITION'):
            if not self.config.get('POSITION_FILE'):
                self.config['POSITION_FILE'] = self.config['BASE_DIR'] + '/cf_intel.pos'

            if os.path.isfile(self.config['POSITION_FILE']):
                with open(self.config['POSITION_FILE'], 'r') as pos_file:
                    self.config['POSITION'] = pos_file.read().rstrip()

    @property
    def begin_date(self):
        return self._begin_date

    @begin_date.setter
    def begin_date(self, init_date):
        if not init_date:
            self._begin_date = int(time.time() - (86400 * 30))
        else:
            if not isinstance(init_date, int):
                raise ValueError('INIT_DATE must be a integer')

            self._begin_date = init_date

    @property
    def scheduler_offset(self):
        return self._scheduler_offset

    @scheduler_offset.setter
    def scheduler_offset(self, jitter):
        if jitter:
            if not self.config.get('SCHEDULER_OFFSET'):
                offset = random.randint(0, 600) - 1
                self._scheduler_offset = offset
            else:
                self._scheduler_offset = self.config['SCHEDULER_OFFSET']

    def backfill_cef(self, begin_time, end_time):
        threat_type = self.config.get('THREAT_TYPE')
        message_types = {'intelligence': 'malware', 'brand intelligence': 'phish'}

        while begin_time < end_time:
            if (end_time - begin_time) > 86400:
                block_end_time = begin_time + 86400
            else:
                block_end_time = end_time

            cef_messages = self.api_mgr.get_aggregate_t3('cef', begin_time=begin_time, end_time=block_end_time)

            for message in cef_messages.splitlines():
                if threat_type == 'all':
                    yield message
                else:
                    message_type = message.split('|')[2].lower()
                    if message_types[message_type] == threat_type:
                        yield message

            begin_time += 86400

    def backfill_standard(self, begin_time, end_time, fmt):
        threat_type = self.config.get('THREAT_TYPE')

        threat_reports = self.api_mgr.threat_search(threatType=threat_type, beginTimestamp=begin_time, endTimestamp=end_time)

        if fmt == 'stix':
            return self.backfill_stix(threat_reports)
        else:
            return threat_reports

    def backfill_stix(self, threat_reports):

        for report in threat_reports:
            yield self.api_mgr.get_t3(report.threat_id, 'stix', report.threat_type.lower())

    def backfill(self, fmat, begin_time):
        now = time.time()
        end_time = int(now)
        if fmat == 'cef':
            threat_reports = self.backfill_cef(begin_time, end_time)
        else:
            threat_reports = self.backfill_standard(begin_time, end_time, fmat)

        return threat_reports

    def get_json_update(self, threat_id, threat_type):
        return self.api_mgr.get_threat(threat_type, threat_id)

    def get_cef_update(self, threat_id, threat_type):
        return self.api_mgr.get_t3(threat_id, 'cef', threat_type)

    def get_stix_update(self, threat_id, threat_type):
        return self.api_mgr.get_t3(threat_id, 'stix', threat_type)

    def get_update(self, threat_id, threat_type):
        format_methods = {'json': self.get_json_update, 'cef': self.get_cef_update, 'stix': self.get_stix_update}

        format_method = format_methods[self.config['INTEL_FORMAT']]

        threat_report = format_method(threat_id, threat_type)

        return threat_report

    def update_position(self, position):
        '''

        Update position tracking file with provided position UUID

        :param position: UUID string for last position pulled


        '''
        self.config['POSITION'] = position
        if self.config.get('POSITION_FILE'):
            with open(self.config['POSITION_FILE'], 'w') as pos_file:
                pos_file.write(position)

    def jitter_pause(self):
        self.logger.info('Jitter set. Delaying sync start by {} seconds'.format(self.scheduler_offset))
        time.sleep(self.scheduler_offset)

    def bulk_update(self, updates):
        update_ids = ['{}_{}'.format(update['threatType'].lower()[0], update['threatId']) for update in updates if update['deleted'] != True]

        if not update_ids:
            return

        # Chunk the ids in groups of 100
        for i in range(0, len(update_ids), 100):
            for report in self.api_mgr.threat_search(threatId=update_ids[i:i+100]):
                yield report

    def first_run(self, integration, threat_type=None):
        if self.config['POSITION']:
            return

        self.logger.info('No position marker set. Backfilling from {} date'.format(self.begin_date))
        end_time = int(time.time())
        backfill_reports = self.backfill(self.config['INTEL_FORMAT'], self.begin_date)

        for report in backfill_reports:
            integration.process(report)

        position, updates = self.api_mgr.threat_updates(threat_type=threat_type, begin_time=end_time)

        if self.config['INTEL_FORMAT'] == 'json':
            for report in self.bulk_update(updates):
                integration.process(report)

        else:
            for update in updates:
                report = self.get_update(update.get('threatId'), update.get('threatType'))
                integration.process(report)

        self.update_position(position)

    def run(self, **kwargs):
        '''
        Main run method. Will execute a sync from last position or backfill date and run the  configured INTEGRATION
        object's process method

        '''

        if self.config['USE_LOCK']:
            if os.path.isfile(self.config['LOCK_FILE']):
                return False
            lock_handler = open(self.config['LOCK_FILE'], 'w')
            lock_handler.close()

        integration_cls = self.config['INTEGRATION']
        integration = integration_cls(self.config)

        if self.config['THREAT_TYPE'] != 'all':
            threat_type = self.config['THREAT_TYPE']
        else:
            threat_type = None

        if self.config.get('JITTER'):
            self.jitter_pause()

        # self.first_run(integration, threat_type)

        position, updates = self.api_mgr.threat_updates(threat_type=threat_type, position=self.config['POSITION'], begin_time=self.config['INIT_DATE'])

        if self.config['INTEL_FORMAT'] == 'json':
            reports = self.bulk_update(updates)
            if reports:
                for report in reports:
                    integration.process(report)

        else:
            for update in updates:
                try:
                    report = self.get_update(update.get('threatId'), update.get('threatType'))
                    integration.process(report)
                except Exception as e:
                    self.logger.error('There was an error while processing threatId: {}, error: {}'
                                      .format(update.get('threatId'), e))
                    if self.config['HALT_ON_ERROR']:
                        raise e

        self.update_position(position)

        self.logger.info('Sync Complete. Most recent position: ' + position)
        self.logger.info('Calling post run')
        integration.post_run()

        if self.config['USE_LOCK']:
            os.remove(self.config['LOCK_FILE'])
