""" Customer model
"""
from anyblok import Declarations
from anyblok_postgres.column import LargeObject
from sqlalchemy import and_


@Declarations.register(Declarations.Model.Attachment)
class Document:
    lobject = LargeObject(keep_blob=True)

    @classmethod
    def get_file_fields(cls):
        fields = super(Document, cls).get_file_fields()
        fields.append('lobject')
        return fields

    def get_file(self):
        res = super(Document, self).get_file()
        if res['lobject']:
            res['file'] = res.pop('lobject')

        return res

    def set_file(self, file_):
        self.lobject = file_

    def has_file(self):
        if self.lobject:
            return True

        return super(Document, self).has_file()

    @classmethod
    def filter_has_not_file(cls):
        return and_(super(Document, cls).filter_has_not_file(),
                   cls.lobject == None)  # noqa


@Declarations.register(Declarations.Model.Attachment.Document)
class Latest:

    def is_unmodified_file(self, modified_fields):
        res = super(Latest, self).is_unmodified_file(modified_fields)
        if res and ('lobject' not in modified_fields or not self.lobject):
            return True

        return False

    def update_copied_value(self, modified_fields, old_version):
        lobject = None
        if 'lobject' in modified_fields:
            del modified_fields['lobject']
            query = """
                SELECT lobject
                FROM attachment_document
                WHERE uuid = %r
                      AND version = %r
            """ % (str(self.uuid), old_version)
            lobject = self.register.execute(query).fetchone()[0]

        res = super(Latest, self).update_copied_value(
            modified_fields, old_version)
        res['lobject'] = lobject
        return res
