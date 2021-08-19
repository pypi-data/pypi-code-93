from typing import Any, Dict, Optional, Union
from io import StringIO
from collections import deque
from UniversalParser._exception import *
from UniversalParser._ntype import *

__all__ = [
    'unparse_odict',
]

__author__ = 'jiyang'
__version__ = '0.0.1'
__license__ = 'MIT'

def _init_head(out_stream, xml_declare, encoding: str) -> None:
    if xml_declare is None:
        out_stream.write(f'<?xml version="1.0" encoding="{encoding}"?>')
    else:
        version = xml_declare.get('version')
        encoding = xml_declare.get('encoding')
        standalone = xml_declare.get('standalone')

        xml_declare = '<?xml'
        xml_declare += f' version="{version}"'
        if encoding is not None:
            xml_declare += f' encoding="{encoding}"'
        if -1 != standalone:
            real_v = 'yes' if 1==standalone else 'no'
            xml_declare += f' standalone="{real_v}"'
        xml_declare += '?>'
        out_stream.write(xml_declare)

def _build_body(out_stream
        , dict_data
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , cdata_self_key: str = CDATA_SELF_KEY
        , comment_key: str = COMMENT_KEY
        , cdata_separator: str = CDATA_SEPARATOR
        , loc_key: str = LOC_KEY
    ) -> None:

    loc_attr_name = f'{attr_prefix}{loc_key}'

    root = list(dict_data.items())[0]
    queue = deque([[root[0], root[1], ''], ])

    while queue:
        pop_obj = queue.popleft()
        pop_tag = pop_obj[0]
        pop_node = pop_obj[1]

        attr_nodes = ''
        comment_nodes = ''
        text_nodes = ''
        cdata_nodes = ''
        sub_nodes = []

        for tag, value in pop_node.items():
            if tag.startswith(attr_prefix) and tag != loc_attr_name:
                attr_nodes += f' {tag[len(attr_prefix):]}="{value}"'
            elif cdata_key == tag:
                text_nodes += value
            elif cdata_self_key == tag:
                cdata_nodes += f'<![CDATA[{value}]]>'
            elif comment_key == tag:
                comment_nodes += f'<!-- {value} -->'
            else:
                if isinstance(value, dict):
                    sub_nodes.append([tag, value, ''])
                elif isinstance(value, (list, tuple)):
                    sub_nodes.extend([[tag, _1, ''] for _1 in value])
                else:
                    pass

        # sorted
        sub_nodes.sort(key=lambda x: int(x[1][loc_attr_name]), reverse=False)
        
        if len(sub_nodes) > 0:
            sub_nodes[-1][2] = f'</{pop_tag}>{pop_obj[2]}'
            pop_obj[2] = ''
            out_stream.write(f'<{pop_tag}{attr_nodes}>{comment_nodes}{cdata_nodes}{text_nodes}')
            queue.extendleft(reversed(sub_nodes))
        else:
            if comment_nodes or text_nodes or cdata_nodes:
                out_stream.write(f'<{pop_tag}{attr_nodes}>{comment_nodes}{cdata_nodes}{text_nodes}</{pop_tag}>')
            else:
                out_stream.write(f'<{pop_tag}{attr_nodes}/>')
        if pop_obj[2]:
            out_stream.write(pop_obj[2])

def unparse_dict(
        dict_data: Dict[str, Any]
        , xml_declare: Dict[str, Union[str, int]] = None
        , out_stream = None
        , encoding: str = 'utf-8'
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , cdata_self_key: str = CDATA_SELF_KEY
        , comment_key: str = COMMENT_KEY
        , cdata_separator: str = CDATA_SEPARATOR
        , loc_key: str = LOC_KEY
    ) -> Optional[str]:

    if not (isinstance(dict_data, dict) and 1 == len(dict_data)):
        raise UnparseDictError('Only one root node is allowed.')

    self_stream = False
    if out_stream is None:
        out_stream: StringIO = StringIO()
        self_stream = True

    _init_head(out_stream, xml_declare, encoding)
    _build_body(
        out_stream
        , dict_data
        , attr_prefix = attr_prefix
        , cdata_key = cdata_key
        , cdata_self_key = cdata_self_key
        , comment_key = comment_key
        , cdata_separator = cdata_separator
        , loc_key = loc_key
    )

    if self_stream:
        return_str = out_stream.getvalue()
        out_stream.close()
        return return_str
