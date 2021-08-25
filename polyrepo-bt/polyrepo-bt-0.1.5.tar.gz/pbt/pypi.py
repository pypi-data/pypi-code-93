from typing import Optional
import requests


class PyPI:
    index = "https://pypi.org"

    @classmethod
    def set_test_package_index(cls):
        cls.index = "https://test.pypi.org"

    @classmethod
    def does_package_exist(
        cls, package_name: str, package_version: Optional[str] = None
    ) -> bool:
        """Check if a package exist in pypi index"""
        resp = requests.get(cls.index + f"/pypi/{package_name}/json")
        if resp.status_code == 404:
            return False

        assert resp.status_code == 200
        if package_version is None:
            return True
        releases = resp.json()['releases']
        return package_version in releases
