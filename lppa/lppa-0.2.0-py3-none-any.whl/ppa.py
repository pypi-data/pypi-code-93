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
import logging

from lazr.restfulclient.errors import BadRequest, NotFound

from lppa.auth import Session
from lppa.processors import Processors


logger = logging.getLogger(__name__)


class PPA():
    """Launchpad PPA manager class"""
    def __init__(self, name, architectures):
        """Initializer

        param name: str, the name for the PPA to be managed
        param architectures: list[str], list of launchpad processors, such as arm64
        """
        self.name = name
        self.session = Session().get_session()
        self.me = self.session.me
        self.team = self.session.people[self.me.name]
        self.architectures = architectures
        self.archive = None

    def set_existing_archive(self):
        """Set the PPA archive interface if one already exists with the requested name"""
        try:
            self.archive = self.me.getPPAByName(name=self.name)
        except NotFound:
            logger.debug(
                'No %s PPA available. Try creating one with the "create" method', self.name
            )

    def create(self, displayname=None, description=None):
        """Create the PPA archive

        param displayname: str, the display name for the PPA to be managed
        param description: str, the description for the PPA to be managed
        """
        self.set_existing_archive()
        if self.archive:
            logger.debug('A PPA named %s already exists', self.name)
        else:
            logger.debug('Creating PPA: %s', self.name)
            displayname = displayname or self.name
            self.archive = self.team.createPPA(
                name=self.name,
                displayname=displayname,
                description=description,
            )
        processors_api = Processors(session=self.session)
        processor_urls = []
        for arch in self.architectures:
            logger.debug('Fetching processor url for "%s"', arch)
            processor_urls.append(processors_api.get_by_name(arch).self_link)
        self.archive.setProcessors(processors=processor_urls)
        logger.info('PPA: "%s" is available for arches: %s', self.name, self.get_processors())

    def get_processors(self):
        """get the processors enabled for the PPA archive

        raises RuntimeError: PPA was not created yet
        return: List of strings representing LP processor names such as amd64
        rtype: list
        """
        self.set_existing_archive()
        arches = []
        if not self.archive:
            logger.warning('PPA "%s" does not exist', self.name)
        else:
            for arch in self.archive.processors:
                arches.append(arch.name)

        return arches

    def get_dput_str(self):
        """Get a dput upload string

        The returned string will be in the form:

        dput ppa:LP_USERNAME/PPA_NAME <source.changes>

        return: dput command to upload an artifact to the PPA
        rtype: str
        """
        return f'dput ppa:{self.me.name}/{self.name} <source.changes>'

    def delete(self):
        """Request removal of the PPA archive

        param ppa: lazr.restfulclient.resource.Entry, An Entry representing an LP archive
        """
        self.set_existing_archive()
        if not self.archive:
            logger.warning('PPA "%s" does not exist; No action taken', self.name)
            return
        logger.info('Requesting removal of PPA "%s"', self.name)
        try:
            self.archive.lp_delete()
        except BadRequest as err:
            logger.warn(
                'Error requesting "%s" removal. %s (%s): %s',
                self.name, err.response.reason,
                err.response.status,
                err.content.decode()
            )
