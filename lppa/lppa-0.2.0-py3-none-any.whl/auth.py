"""
Copyright (C) 2021 Athos Ribeiro

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from launchpadlib.launchpad import Launchpad

from lppa import config


class AuthenticationError(Exception):
    """Error for authentication failures"""


class Session():
    """Launchpad session interface"""
    def __init__(self, anonymous=False, lp_env=config['DEFAULT']['lp_env']):
        """Initializer

        param anonymous: bool, whether to use an anonimous session
        param lp_env: string, launchpad environment to pass to launchpadlib
        """
        self.anonymous = anonymous
        self.lp_env = lp_env

    def _get_authenticated_session(self, anonymous_fallback):
        """Retrieve a new launchpad authenticated session

        param anonymous_fallback: bool, whether to fallback to an anonimous session on
            authentication failures
        raises AithenticationError: Failed to authenticate without anonymous fallbacks enabled
        return: Launchpad session
        rtype: launchpadlib.launchpad.Launchpad
        """
        try:
            session = Launchpad.login_with(
                config['DEFAULT']['app_name'],
                self.lp_env,
                version=config['DEFAULT']['api_version'],
                credential_save_failed=self._no_auth_failure
            )
        except AuthenticationError:
            if not anonymous_fallback:
                raise

            self.anonymous = True
            session = self._get_anonymous_session()
        return session

    def _get_anonymous_session(self):
        """Retrieve a new anonymous launchpad session

        return: Launchpad session
        rtype: launchpadlib.launchpad.Launchpad
        """
        return Launchpad.login_anonymously(
            config['DEFAULT']['app_name'], self.lp_env, version=config['DEFAULT']['api_version']
        )

    def _no_auth_failure(self):
        """Callback for Launchpad.login_with credential_save_failed param"""
        raise AuthenticationError(f"Could not Authenticate with Launchpad in '{self.lp_env}'")

    def get_session(self, anonymous_fallback=False):
        """Retrieve a new launchpad session

        param anonymous_fallback: bool, whether to fallback to an anonimous session on
            authentication failures
        return: Launchpad session
        rtype: launchpadlib.launchpad.Launchpad
        """
        if self.anonymous:
            return self._get_anonymous_session()

        return self._get_authenticated_session(anonymous_fallback)
