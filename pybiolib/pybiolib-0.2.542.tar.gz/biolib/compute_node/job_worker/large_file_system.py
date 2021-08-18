import os
import subprocess
import time
from typing import Dict, Optional

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict

import requests
import docker.types  # type: ignore

from biolib.biolib_api_client import BiolibApiClient


class LargeFileSystemAttachResponse(TypedDict):
    aws_ebs_volume_id: str
    device_name: str


class DeviceInfo(TypedDict):
    attached_device_name: str
    aws_ebs_volume_id: str
    nvme_device_name: str


class LargeFileSystem:
    _EC2_INSTANCE_ID: Optional[str] = None

    def __init__(self, job_id: str, public_id: str, to_path: str):
        self.job_id = job_id
        self.public_id = public_id
        self.to_path = to_path

        self._mount_directory_path = f'/mnt/bl-lfs/{public_id}/'

    def get_as_docker_mount_object(self) -> docker.types.Mount:
        if not self._is_mounted():
            raise Exception('LargeFileSystem not mounted')

        return docker.types.Mount(
            read_only=True,
            source=self._mount_directory_path,
            target=self.to_path,
            type='bind',
        )

    def mount(self) -> None:
        if self._is_mounted():
            return

        try:
            api_client = BiolibApiClient.get()
            response = requests.post(
                url=f'{api_client.base_url}/lfs/{self.public_id}/attach/',
                json={
                    'ec2_instance_id': LargeFileSystem._get_ec2_instance_id(),
                    'job_id': self.job_id,
                },
            )
            if not response.ok:
                raise Exception(f'Failed to get response from {response.request.url}\n{response.content.decode()}')

            attach_response: LargeFileSystemAttachResponse = response.json()

            device_to_mount: Optional[DeviceInfo] = None
            for _ in range(10):
                time.sleep(0.5)
                device_to_mount = self._get_attached_ebs_devices().get(attach_response['aws_ebs_volume_id'])
                if device_to_mount is not None:
                    break

            if device_to_mount is None:
                raise Exception('LargeFileSystem device is not attached')

            subprocess.run(['sudo', 'mkdir', '--parents', self._mount_directory_path], check=True)
            subprocess.run(
                ['sudo', 'mount', f"/dev/{device_to_mount['nvme_device_name']}",
                 self._mount_directory_path],
                check=True,
            )
        except Exception as exception:
            raise Exception(f'Failed to mount LargeFileSystem with id {self.public_id}') from exception

    def unmount(self) -> None:
        if not self._is_mounted():
            return

        try:
            subprocess.run(['sudo', 'umount', '-d', self._mount_directory_path], check=True)
            # ensure directory is removed
            if os.path.exists(self._mount_directory_path):
                subprocess.run(['sudo', 'rm', '-r', self._mount_directory_path], check=True)
        except Exception as exception:
            raise Exception(f'Failed to unmount LargeFileSystem with id {self.public_id}') from exception

    def _is_mounted(self) -> bool:
        return os.path.exists(self._mount_directory_path)

    @staticmethod
    def _get_ec2_instance_id() -> str:
        if LargeFileSystem._EC2_INSTANCE_ID is None:
            # the IP address 169.254.169.254 is a link-local address and is valid only from the instance
            LargeFileSystem._EC2_INSTANCE_ID = requests.get('http://169.254.169.254/latest/meta-data/instance-id').text

        return LargeFileSystem._EC2_INSTANCE_ID

    @staticmethod
    def _get_attached_ebs_devices():
        lsblk_result = subprocess.run(['sudo', 'lsblk'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout_lines = lsblk_result.stdout.decode().splitlines()

        ebs_vol_id_to_device_info: Dict[str, DeviceInfo] = {}

        for line in stdout_lines:
            if line.startswith('nvme'):
                nvme_device_name = line.split()[0]
                ebsnvme_result = subprocess.run(
                    ['sudo', 'ebsnvme-id', f'/dev/{nvme_device_name}'],
                    check=False,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                # if command succeed the device is an EBS
                if ebsnvme_result.returncode == 0:
                    # we expect 2 lines
                    line1, line2 = ebsnvme_result.stdout.decode().splitlines()
                    device_info = DeviceInfo(
                        aws_ebs_volume_id=line1.replace('Volume ID: ', ''),
                        attached_device_name=line2,
                        nvme_device_name=nvme_device_name,
                    )
                    ebs_vol_id_to_device_info[device_info['aws_ebs_volume_id']] = device_info

        return ebs_vol_id_to_device_info
