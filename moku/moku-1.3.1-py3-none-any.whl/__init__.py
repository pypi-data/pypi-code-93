import hashlib
import logging
import os
import tarfile

import pkg_resources
from moku.session import RequestSession
from moku.utilities import validate_range
from moku.exceptions import IncompatibleMokuException

logger = logging.getLogger("moku")
logger.level = logging.INFO

__version__ = pkg_resources.get_distribution("moku").version
DATA_PATH = os.path.expanduser(os.environ.get('MOKU_DATA_PATH', None) or (
    pkg_resources.resource_filename("moku", 'data')))


class Moku:
    def __init__(self, ip=None, force_connect=False, session=None):
        if not ip and not session:
            raise Exception("Cannot create a Moku object without "
                            "an IP or existing session")
        self.session = session if session else RequestSession(ip)
        if force_connect:
            self.claim_ownership()
        description = self.describe()
        self.firmware_version = description['firmware']
        self.hardware = description['hardware'].replace(":", "").lower()
        self.bitstreams = description['bitstreams']

        if int(self.firmware_version) < 542:
            raise IncompatibleMokuException(
                "Incompatible Moku, firmware version should be 542 or above")

    def _get_server_bitstreams(self, bs_name):
        for b in self.bitstreams:
            if b.get('name') == bs_name:
                return bs_name, b.get('checksum')
        return None, None

    def _read_and_upload_stream(self, bs_name, chksum):
        upload_required = True
        with tarfile.open(self._get_data_file(self.firmware_version)) as _ts:
            bs_tarinfo = _ts.getmember(f"{self.hardware}/{bs_name}")
            bs_file = _ts.extractfile(bs_tarinfo)
            bs_data = bs_file.read()
            if chksum:
                local_chksum = hashlib.sha256(bs_data).hexdigest()
                upload_required = local_chksum != chksum
            if upload_required:
                self.upload("bitstreams", bs_name, bs_data)
            bs_file.close()

    def upload_bitstream(self, id):
        bs_name = f'01-{id:03}-00'
        _, pf_chksum = self._get_server_bitstreams('01-000')
        _, bs_chksum = self._get_server_bitstreams(bs_name)
        self._read_and_upload_stream('01-000', pf_chksum)
        self._read_and_upload_stream(bs_name, bs_chksum)

    @staticmethod
    def _get_data_file(hardware_version):
        file_name = f'mokudata-{hardware_version}.tar.gz'
        path = os.path.join(DATA_PATH, file_name)
        if not os.path.exists(path):
            raise Exception(
                'Instrument files not available, please run `moku download` to'
                'download latest instrument data')
        return path

    def claim_ownership(self):
        """
        Claim the ownership of Moku.
        """
        operation = "claim_ownership"

        return self.session.post("moku", operation)

    def relinquish_ownership(self):
        """
        Relinquish the ownership of Moku.
        """
        operation = "relinquish_ownership"

        return self.session.post("moku", operation)

    def name(self):
        """
        name.
        """
        operation = "name"

        return self.session.get("moku", operation)

    def serial_number(self):
        """
        serial_number.
        """
        operation = "serial_number"

        return self.session.get("moku", operation)

    def summary(self):
        """
        summary.
        """
        operation = "summary"

        return self.session.get("moku", operation)

    def describe(self):
        """
        describe.
        """
        operation = "describe"

        return self.session.get("moku", operation)

    def firmware_version(self):
        """
        firmware_version.
        """
        operation = "firmware_version"

        return self.session.get("moku", operation)

    def available_power_supplies(self):
        """
        readAllPowersupplies.
        """
        operation = "available_power_supplies"

        return self.session.get("moku", operation)

    def read_power_supply(self, id):
        """
        readPowersupply.

        :type id: `integer`
        :param id: ID of the power supply

        """
        operation = "read_power_supply"

        params = dict(
            id=id,)
        return self.session.post("moku", operation, params)

    def set_power_supply(self, id, enable=True, voltage=3, current=0.1):
        """
        setPowersupply.

        :type id: `integer`
        :param id: Target power supply

        :type enable: `boolean`
        :param enable: Enable/Disable power supply

        :type voltage: `number`
        :param voltage: Voltage set point

        :type current: `number`
        :param current: Current set point

        """
        operation = "set_power_supply"

        params = dict(
            id=id,
            enable=enable,
            voltage=voltage,
            current=current,)
        return self.session.post("moku", operation, params)

    def upload(self, target, file_name, data):
        """
        Upload files to bitstreams, ssd, persist.

        :type target: `string`, (bitstreams, ssd, persist)
        :param target: Destination where the file should be uploaded to.

        :type file_name: `string`
        :param file_name: Name of the file to be uploaded

        :type data: `bytes`
        :param data: File content

        """
        target = validate_range(target, list(['bitstreams', 'ssd', 'persist']))
        operation = f"upload/{file_name}"
        return self.session.post_file(target, operation, data)

    def delete(self, target, file_name):
        """
        Delete files from bitstreams, ssd, persist.

        :type target: `string`, (bitstreams, ssd, persist)
        :param target: Destination where the file should be uploaded to.

        :type file_name: `string`
        :param file_name: Name of the file to be deleted

        """
        target = validate_range(target, list(['bitstreams', 'ssd', 'persist']))
        operation = f"delete/{file_name}"
        return self.session.delete_file(target, operation)

    def list(self, target):
        """
        List files at bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, persist)
        :param target: Target directory to list files for

        """
        target = validate_range(target, list(
            ['bitstreams', 'ssd', 'logs', 'persist']))
        operation = "list"
        return self.session.get(target, operation)

    def download(self, target, file_name, local_path):
        """
        Download files from bitstreams, ssd, logs, persist.

        :type target: `string`, (bitstreams, ssd, persist)
        :param target: Destination where the file should be downloaded from.

        :type file_name: `string`
        :param file_name: Name of the file to be downloaded

        :type local_path: `string`
        :param local_path: Local path to download the file

        """
        target = validate_range(target, list(
            ['bitstreams', 'ssd', 'logs', 'persist']))
        operation = f"download/{file_name}"
        return self.session.get_file(target, operation, local_path)
