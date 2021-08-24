import requests, json, copy

from cofense_intelligence import PhishThreatReport, MalwareThreatReport
from cofense_intelligence.output import CofenseIntegration


class HttpOutput(CofenseIntegration):
    """
    Parent class for "generic" Cofense Intelligence integrations;
    extends :class:`cofense_intelligence.output.base_integration.CofenseIntegration`
    """
    def __init__(self, config, **kwargs):
        super(HttpOutput, self).__init__(config, **kwargs)

        self.proxy_settings = {}
        if self.args.http_proxy:
            self._setup_proxy()

        if self.args.http_basic_auth_user:
            self.auth = (self.args.http_basic_auth_user, self.args.http_basic_auth_pass)

        self.headers = {}
        if self.args.http_splunk_token:
            self.headers['Authorization'] = "Splunk {}".format(self.args.http_splunk_token)

        if self.args.http_header:
            for header in self.args.http_header:
                parts = [x.strip() for x in header.split(':')]
                self.headers[parts[0]] = parts[1]

    def _setup_proxy(self):
        if self.args.http_proxy.startswith("https"):
            proxy_address = self.args.http_proxy[8:]

            if self.args.http_proxy_user:
                proxy_address = "https://{}:{}@{}".format(self.args.http_proxy_user,
                                                          self.args.http_proxy_pass,
                                                          proxy_address)
            self.proxy_settings = {'https': proxy_address}

        elif self.args.http_proxy:
            proxy_address = self.args.http_proxy[7:]
            if self.args.http_proxy_user:
                proxy_address = "http://{}:{}@{}".format(self.args.http_proxy_user,
                                                         self.args.http_proxy_pass,
                                                         proxy_address)

            self.proxy_settings = {'http': proxy_address}

    def _format_splunk(self, data):
        base = {"event": data}
        if self.args.http_splunk_sourcetype:
            base["sourcetype"] = self.args.http_splunk_sourcetype
        return json.dumps(base)

    def _send(self, data):
        if self.args.http_splunk_token:
            data = self._format_splunk(data)

        response = requests.post(self.args.http_url,
                                 proxies=self.proxy_settings,
                                 headers=self.headers,
                                 data=data,
                                 verify=False)
        self.logger.info('Got a {} response from the server'.format(response.status_code))
        response.raise_for_status()

    def _handle_json_malware(self, mrti):
        """

        :param mrti: `cofense_intelligence.MalwareTreatReport`
        :return:
        """
        base_data = {
            "threat_id": mrti.threat_id,
            "threat_type": mrti.threat_type,
            "first_published": mrti.first_published,
            "threat_report_url": mrti.human_readable_url,
            "executive_summary": mrti.executive_summary
        }

        for block in mrti.block_set:
            new_data = copy.copy(base_data)
            new_data["block_type"] = block.block_type
            new_data["impact"] = block.impact
            new_data["role"] = block.role
            new_data["role_description"] = block.role_description
            new_data["malware_family"] = block.malware_family
            new_data["malware_family_description"] = block.malware_family_description
            new_data["watchlist_ioc"] = block.watchlist_ioc

            self._send(json.dumps(new_data))

        for executable in mrti.executable_set:
            new_data = copy.copy(base_data)
            new_data['file_name'] = executable.file_name
            new_data['type'] = executable.type
            new_data['md5'] = executable.md5
            new_data['sha1'] = executable.sha1
            new_data['sha256'] = executable.sha256
            new_data['sha384'] = executable.sha384
            new_data['sha512'] = executable.sha512
            new_data['ssdeep'] = executable.ssdeep
            new_data['malware_family'] = executable.malware_family
            new_data['malware_family_description'] = executable.malware_family_description
            new_data['severity'] = executable.severity

            self._send(json.dumps(new_data))

    def _handle_json_phish(self, mrti):
        """

        :param mrti: `cofense_intelligence.PhishThreatReport`
        :return:
        """
        base_data = {
            "threat_id": mrti.threat_id,
            "threat_type": mrti.threat_type,
            "first_published": mrti.first_published,
            "threat_report_url": mrti.human_readable_url,
        }

        for url in mrti.reported_url_list:
            new_data = copy.copy(base_data)
            new_data['reported_url'] = url.__dict__
            self._send(json.dumps(new_data))
        for url in mrti.action_url_list:
            new_data = copy.copy(base_data)
            new_data['action_url'] = url.__dict__
            self._send(json.dumps(new_data))

    def _handle_cef(self, mrti):
        self._send(mrti)

    def _handle_stix(self, mrti):
        self._send(mrti)

    def process(self, mrti):
        """

        :param mrti: `cofense_intelligence.ThreatReport`
        :return:
        """
        if self.config['INTEL_FORMAT'] == 'json':
            if isinstance(mrti, MalwareThreatReport):
                self._handle_json_malware(mrti)
            elif isinstance(mrti, PhishThreatReport):
                self._handle_json_phish(mrti)
        elif self.config['INTEL_FORMAT'] == 'cef':
            self._handle_cef(mrti)
        elif self.config['INTEL_FORMAT'] == 'stix':
            self._handle_stix(mrti)
        else:
            raise ValueError(
                "{} is not a supported http output format. If you think it should be supported please contact "
                "support@cofense.com".format(self.config['INTEL_FORMAT']))

