# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import Blok
from sqlalchemy import Column, Integer
from logging import getLogger


logger = getLogger(__name__)


class AttachmentBlok(Blok):
    """Add attachment in AnyBlok"""

    version = '2.0.0'
    required = ['anyblok-core', 'anyblok-mixins']
    author = 'Suzanne Jean-Sébastien'

    def pre_migration(self, latest_version):
        if latest_version is None:
            return

        if latest_version < '2.0.0':
            logger.info('Start migration to change primary keys')
            table = self.registry.migration.table('attachment_document')
            table.primarykey().drop()
            table.column().add(Column('version_number', Integer, default=None))
            has_line_to_migrate = True
            query_has_line_to_migrate = """
                SELECT uuid, version
                FROM attachment_document
                WHERE version_number is null
                LIMIT 10
            """
            while has_line_to_migrate:
                batch = self.registry.execute(
                    query_has_line_to_migrate).fetchall()
                if len(batch) < 10:
                    has_line_to_migrate = False

                for uuid, version in batch:
                    version_number = int(version[2:])
                    query = """
                        UPDATE attachment_document
                        SET version_number = %d
                        WHERE
                            uuid = '%s'
                            AND version = '%s';
                    """ % (version_number, str(uuid), version)
                    self.registry.execute(query)

                self.registry.flush()

            has_seq_to_delete = True
            query_has_seq_to_delete = """
                SELECT id, seq_name
                FROM system_sequence
                WHERE code ilike 'Attachment.Document#%'
                LIMIT 10
            """
            while has_seq_to_delete:
                batch = self.registry.execute(
                    query_has_seq_to_delete).fetchall()
                if len(batch) < 10:
                    has_seq_to_delete = False

                for id, seq_name in batch:
                    self.registry.execute("DROP SEQUENCE %s" % seq_name)
                    self.registry.execute(
                        "DELETE FROM system_sequence where id = %d" % id)

                self.registry.flush()

            table.primarykey().add(table.column('uuid'),
                                   table.column('version_number'))
            logger.info('Migration finished to change primary keys')

    @classmethod
    def import_declaration_module(cls):
        from . import attachment  # noqa
        from . import document  # noqa
        from . import mixin  # noqa

    @classmethod
    def reload_declaration_module(cls, reload):
        from . import attachment
        reload(attachment)
        from . import document
        reload(document)
        from . import mixin
        reload(mixin)
