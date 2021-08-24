import sys,csv,os
from .FileOutput import FileOutput
from datetime import datetime


class CsvFileOutput(FileOutput):

    def get_file_path(self, mrti):
        year_month_date = datetime.fromtimestamp(mrti.first_published / 1e3).strftime('%Y-%m-%d')

        output_path = self.verify_dirs(year_month_date)

        return output_path

    @staticmethod
    def get_summary(mrti):
        return {'id': mrti.threat_id,
                'first_published': mrti.first_published,
                'last_published': mrti.last_published,
                'report_url': mrti.human_readable_url}

    @staticmethod
    def need_headers(output_file):
        if os.path.isfile(output_file):
            return False
        else:
            return True

    def write_csv(self, output_file, data):
        need_headers = self.need_headers(output_file)

        write_mods = {2: 'ab', 3: 'a'}
        py_version = sys.version_info[0]

        with open(output_file, write_mods[py_version]) as outfile:
            csv_writer = csv.DictWriter(outfile, data.keys())

            if need_headers:
                csv_writer.writeheader()
            try:
                csv_writer.writerow(data)
            except UnicodeEncodeError:
                encoded_data = {}
                for key, value in data.items():
                    if isinstance(value, unicode):
                        encoded_data[key] = value.encode('utf-8')
                    else:
                        encoded_data[key] = value
                csv_writer.writerow(encoded_data)

    def write_malware_summary(self, mrti, output_dir):

        report_summary = self.get_summary(mrti)
        malware_summary = {'malware_families': mrti.malware_families, 'label': mrti.label}
        report_summary.update(malware_summary)

        output_file = os.path.join(output_dir, "malware_threat_reports.csv")

        self.write_csv(output_file, report_summary)

    def write_block_set(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "block_set.csv")

        for item in mrti.block_set:
            ip_details = {'latitude': '',
                          'longitude': '',
                          'time_zone': '',
                          'continent': '',
                          'cont_code': '',
                          'country': '',
                          'country_code': '',
                          'asn': '',
                          'asn_org': '',
                          'isp': '',
                          'organizatoin': ''}

            url_details = {'host': '', 'path': ''}

            if item.block_type == 'URL':
                url_details = {'host': item.watchlist_ioc_host, 'path': item.watchlist_ioc_path}

            if item.block_type == 'IPv4 Address':
                ip_detailed = item.json.get('ipDetail')
                if ip_detailed:
                    ip_details = {'latitude': ip_detailed.get('latitude'),
                                  'longitude': ip_detailed.get('longitude'),
                                  'time_zone': ip_detailed.get('timeZone'),
                                  'continent': ip_detailed.get('continentName'),
                                  'cont_code': ip_detailed.get('continentCode'),
                                  'country': ip_detailed.get('countryName'),
                                  'country_code': ip_detailed.get('countryIsoCode'),
                                  'asn': ip_detailed.get('asn'),
                                  'asn_org': ip_detailed.get('asnOrganization'),
                                  'isp': ip_detailed.get('isp'),
                                  'organization': ip_detailed.get('organization')}

            block_set = {'id': mrti.threat_id,
                         'indicator': item.watchlist_ioc,
                         'impact': item.impact,
                         'type': item.block_type,
                         'role': item.role,
                         'role_desc': item.role_description,
                         'malware_family': item.malware_family}

            block_set.update(url_details)
            block_set.update(ip_details)

            self.write_csv(output_file, block_set)

    def write_exec_set(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "executable_set.csv")

        for item in mrti.executable_set:
            exec_set = {'id': mrti.threat_id,
                        'file_name': item.file_name,
                        'type': item.type,
                        'md5': item.md5,
                        'sha1': item.sha1,
                        'sha224': item.sha224,
                        'sha256': item.sha256,
                        'sha384': item.sha384,
                        'sha512': item.sha512,
                        'ssdeep': item.ssdeep,
                        'malware_family': item.malware_family,
                        'subtype': item.subtype}

            self.write_csv(output_file, exec_set)

    def write_subjects(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "subjects.csv")

        for subject in mrti.subject_set:
            subject_data = {'id': mrti.threat_id,
                            'subject': subject.subject,
                            'count': subject.total_count}

            self.write_csv(output_file, subject_data)

    def write_sender_ips(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "sender_ips.csv")

        for ip in mrti.sender_ip_set:
            ip_data = {'id': mrti.threat_id,
                       'ip': ip.ip,
                       'count': ip.total_count}

            self.write_csv(output_file, ip_data)

    def write_sender_emails(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "sender_emails.csv")

        for email in mrti.sender_email_set:
            email_data = {'id': mrti.threat_id,
                          'email': email.sender_email,
                          'count': email.total_count}

            self.write_csv(output_file, email_data)

    def write_spam_urls(self, mrti, output_dir):
        output_file = os.path.join(output_dir, "spam_urls.csv")

        for url in mrti.spam_url_set:
            spam_url = {'id': mrti.threat_id,
                        'url': url.url,
                        'count': url.total_count}

            self.write_csv(output_file, spam_url)

    def write_malware(self, mrti, output_dir):
        self.write_malware_summary(mrti, output_dir)
        self.write_block_set(mrti, output_dir)
        self.write_exec_set(mrti, output_dir)
        self.write_subjects(mrti, output_dir)
        self.write_sender_ips(mrti, output_dir)
        self.write_sender_emails(mrti, output_dir)
        self.write_spam_urls(mrti, output_dir)

    def write_phish_summary(self, mrti, output_dir):
        # TODO: Include phish URLs and IPs

        report_summary = self.get_summary(mrti)
        phish_summary = {'confirmed_date': mrti.confirmed_date,
                         'title': mrti.title,
                         'language': mrti.language}

        report_summary.update(phish_summary)

        output_file = os.path.join(output_dir, 'phish_threat_reports.csv')
        self.write_csv(output_file, report_summary)

    def write_phish_kits(self, mrti, output_dir):
        output_file = os.path.join(output_dir, 'phish_kits.csv')

        for kit in mrti.kits:
            phish_kit = {'id': mrti.threat_id,
                         'name': kit.kit_name,
                         'size': kit.size,
                         'md5': kit.md5,
                         'sha1': kit.sha1,
                         'sha224': kit.sha224,
                         'sha256': kit.sha256,
                         'sha384': kit.sha384,
                         'sha512': kit.sha512,
                         'ssdeep': kit.ssdeep}

            self.write_csv(output_file, phish_kit)

    def write_reported_urls(self, mrti, output_dir):
        output_file = os.path.join(output_dir, 'phish_reported_urls.csv')

        for url in mrti.reported_url_list:
            reported_url = {'id': mrti.threat_id,
                            'url': url.url,
                            'domain': url.domain,
                            'host': url.host,
                            'path': url.path,
                            'protocol': url.protocol,
                            'query': url.query}

            self.write_csv(output_file, reported_url)

    def write_action_urls(self, mrti, output_dir):
        output_file = os.path.join(output_dir, 'phish_action_urls.csv')

        for url in mrti.action_url_list:
            action_url = {'id': mrti.threat_id,
                          'url': url.url,
                          'domain': url.domain,
                          'host': url.host,
                          'path': url.path,
                          'protocol': url.protocol,
                          'query': url.query}

            self.write_csv(output_file, action_url)

    def write_phish(self, mrti, output_dir):

        self.write_phish_summary(mrti, output_dir)
        self.write_phish_kits(mrti, output_dir)
        self.write_reported_urls(mrti, output_dir)
        self.write_action_urls(mrti, output_dir)

    def write_file(self, mrti, output_dir):

        if mrti.threat_type == 'MALWARE':
            self.write_malware(mrti, output_dir)
        elif mrti.threat_type == 'PHISH':
            self.write_phish(mrti, output_dir)

