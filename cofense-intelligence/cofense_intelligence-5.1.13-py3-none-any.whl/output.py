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

class CofenseIntegration(object):
    """
    Base Class of all PhishMe Integration classes
    """

    def __init__(self, config, **kwargs):

        self.config = config

        self.config.update(kwargs)

        self.logger = logging.getLogger('{}'.format(config['INTEGRATION']))

        self.logger.debug('Integration logging setup')
        if 'ARGS' in config:
            self.args = config['ARGS']

    def process(self, mrti):
        """
        Method stub for process; this will be overridden by child integration classes

        :param str mrti: PhishMe Intelligence ThreatReport ID data
        :return: None
        """

        pass

    def post_run(self):
        """
        Method stub for post_run; this will be overridden by child integration classes as needed

        :return: None
        """

        pass

    def sync(self):
        pass
