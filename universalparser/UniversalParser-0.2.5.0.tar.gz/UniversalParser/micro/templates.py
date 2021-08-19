from typing import List
from UniversalParser._tools import patt_template_replace

HTML_TABLE = """\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css" integrity="sha384-HSMxcRTRxnN+Bdg0JdbxYKrThecOKuH5zCYotlSAcp1+c8xmyTe9GYg1l9a69psu" crossorigin="anonymous">
    <title>${title}</title>
</head>
<body>
    ${tables}
</body>
</html>
"""

def parse_html_table(
        datas: List[List[List[str]]]
        , title: str = 'Table'
        , caption: str = ''
        , tfoot: str = ''
    ) -> str:

    template_table = """
    <table class="table table-bordered">
        <caption></caption>
        <thead>
            ${tr_ths}
        </thead>
        <tbody>
            ${tr_tds}
        </tbody>
        <tfoot></tfoot>
    </table>
    """

    tables = ''

    for rows in datas:

        tr_ths = rows[0]
        tr_tds = rows[1:]

        insert_tr_ths = ''
        insert_tr_tds = ''

        t_str = '<tr>'
        for th in tr_ths:
            t_str += f'<th>{th}</th>'
        t_str += '</tr>'
        insert_tr_ths += t_str

        for tr_td in tr_tds:
            t_str = '<tr>'
            for td in tr_td:
                t_str += f'<td>{td}</td>'
            t_str += '</tr>'
            insert_tr_tds += t_str

        tables += patt_template_replace(template_table
            , tr_ths = insert_tr_ths
            , tr_tds = insert_tr_tds
        )
    
    return patt_template_replace(HTML_TABLE
        , title = title
        , tables = tables
    )
