from .. import settings

FUNCTION_CHECKER_MSGS = {
    f'C{settings.FUNCTION_MSG_ID}01': (
        'Default function name must be start with _default_',
        'biszx-default-func-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FUNCTION_MSG_ID}02': (
        'Search function name must be start with _search_',
        'biszx-search-func-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FUNCTION_MSG_ID}03': (
        'Compute function name must be start with _compute_',
        'biszx-compute-func-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FUNCTION_MSG_ID}04': (
        'Onchange function name must be start with _onchange_',
        'biszx-onchange-func-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FUNCTION_MSG_ID}05': (
        'Constrains function name must be start with _check_',
        'biszx-constrains-func-name',
        settings.MSG_DESCRIPTION
    ),
    f'C{settings.FUNCTION_MSG_ID}06': (
        'Domain function name must be start with _domain_',
        'biszx-domain-func-name',
        settings.MSG_DESCRIPTION
    ),
}
