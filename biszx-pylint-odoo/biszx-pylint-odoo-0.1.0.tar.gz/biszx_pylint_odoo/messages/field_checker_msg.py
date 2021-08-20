from .. import settings

FIELD_CHECKER_MSGS = {
    f'C{settings.FIELD_MSG_ID}01': (
        'Many2one field name must be end with _id',
        'biszx-relation2one-field-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FIELD_MSG_ID}02': (
        'One2many and Many2many field name must be end with _ids',
        'biszx-relation2many-field-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FIELD_MSG_ID}03': (
        'Boolean field name must be start with is_',
        'biszx-boolean-field-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FIELD_MSG_ID}04': (
        'Date field name must be end with _date',
        'biszx-date-field-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FIELD_MSG_ID}05': (
        'Datetime field name must be end with _at',
        'biszx-datetime-field-name',
        settings.MSG_DESCRIPTION
    ),
}
