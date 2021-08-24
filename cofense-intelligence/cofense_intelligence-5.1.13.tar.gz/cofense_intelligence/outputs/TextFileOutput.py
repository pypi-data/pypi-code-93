import os,sys

from .FileOutput import FileOutput


class TextFileOutput(FileOutput):
    def get_file_path(self, mrti):
        self.logger.debug('Calling get_file_path')
        return self.verify_append_dirs()

    def write_file(self, mrti, output_dir):
        self.logger.debug('Calling write_file')
        if mrti.threat_type == 'MALWARE' and (self.args.intel_type == 'malware' or self.args.intel_type == 'all'):
            self._write_malware(mrti, output_dir)
        elif mrti.threat_type == 'PHISH' and (self.args.intel_type == 'phish' or self.args.intel_type == 'all'):
            self._write_phish(mrti, output_dir)

    def _write(self, data, file_name):
        self.logger.debug('Calling _write')
        write_mods = {2: 'ab', 3: 'a'}
        py_version = sys.version_info[0]

        if isinstance(data, list):
            output = "\n".join(data)
        elif isinstance(data, str):
            output = data
        else:
            raise TypeError("data coming into _write must be a string or a list")

        with open(file_name, write_mods[py_version]) as outfile:
            try:
                if not output.endswith("\n"):
                    output += "\n"
                outfile.write(output.lstrip())

            except Exception as e:
                self.logger.error(e)
                raise e

    def _get_list(self, mrti, block_type, impact):
        self.logger.debug('Calling _get_list')
        return [item.watchlist_ioc for item in mrti.block_set if item.block_type == block_type and item.impact == impact]

    def _write_malware(self, mrti, output_dir):
        self.logger.debug('Calling _write_malware')
        # URLs
        if self.args.txt_url_major:
            major_urls = self._get_list(mrti, 'URL', 'Major')
            self._write(major_urls, os.path.join(output_dir, self.args.txt_url_major_file))

        if self.args.txt_url_moderate:
            moderate_urls = self._get_list(mrti, 'URL', 'Moderate')
            self._write(moderate_urls, os.path.join(output_dir, self.args.txt_url_moderate_file))

        if self.args.txt_url_minor:
            minor_urls = self._get_list(mrti, 'URL', 'Minor')
            self._write(minor_urls, os.path.join(output_dir, self.args.txt_url_minor_file))

        # IP Addresses
        if self.args.txt_ip_major:
            major_ips = self._get_list(mrti, 'IPv4 Address', 'Major')
            self._write(major_ips, os.path.join(output_dir, self.args.txt_ip_major_file))

        if self.args.txt_ip_moderate:
            moderate_ips = self._get_list(mrti, 'IPv4 Address', 'Moderate')
            self._write(moderate_ips, os.path.join(output_dir, self.args.txt_ip_moderate_file))

        if self.args.txt_ip_minor:
            minor_ips = self._get_list(mrti, 'IPv4 Address', 'Minor')
            self._write(minor_ips, os.path.join(output_dir, self.args.txt_ip_minor_file))

        # Domain names
        if self.args.txt_domain_major:
            major_domain = self._get_list(mrti, 'Domain Name', 'Major')
            self._write(major_domain, os.path.join(output_dir, self.args.txt_domain_major_file))

        if self.args.txt_domain_moderate:
            moderate_domain = self._get_list(mrti, 'Domain Name', 'Moderate')
            self._write(moderate_domain, os.path.join(output_dir, self.args.txt_domain_moderate_file))

        if self.args.txt_domain_minor:
            minor_domain = self._get_list(mrti, 'Domain Name', 'Minor')
            self._write(minor_domain, os.path.join(output_dir, self.args.txt_domain_minor_file))

        # Files
        if self.args.txt_malicious_md5:
            files = [item.md5 for item in mrti.executable_set]
            self._write(files, os.path.join(output_dir, self.args.txt_malicious_md5_file))

    def _write_phish(self, mrti, output_dir):
        self.logger.debug('Calling _write_phish')

        for url in mrti.action_url_list:
            self._write_phish_action_url(url.url, output_dir)
        for url in mrti.reported_url_list:
            self._write_phish_reported_url(url.url, output_dir)

    def _write_phish_action_url(self, action_url, output_dir):
        self.logger.debug('Calling _write_phish_action_url')
        self._write(action_url, os.path.join(output_dir, "phish_action_url.txt"))

    def _write_phish_reported_url(self, reported_url, output_dir):
        self.logger.debug('Calling _write_phish_reported_url')
        self._write(reported_url, os.path.join(output_dir, "phish_reported_url.txt"))
