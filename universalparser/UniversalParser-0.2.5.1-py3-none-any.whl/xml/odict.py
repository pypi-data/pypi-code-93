from collections import OrderedDict
from typing import Dict, List, Optional
from xml.parsers.expat import ParserCreate, XMLParserType
from UniversalParser._ntype import *

__author__ = 'jiyang'
__version__ = '0.0.1'   
__license__ = 'MIT'

def parse_odict(xml_data: str
        , encoding: str='utf-8'
        , attr_prefix: str = ATTR_PREFIX
        , cdata_key: str = CDATA_KEY
        , cdata_self_key: str = CDATA_SELF_KEY
        , comment_key: str = COMMENT_KEY
        , combine_cdata: bool = True
        , include_comment: bool = False
        , cdata_separator: str = CDATA_SEPARATOR
        , loc_key: str = LOC_KEY
        , include_loc: bool = False
    ) -> OrderedDict:

    xml_declares = {'version': '1.0', 'encoding': f'{encoding}', 'standalone': -1}
    documentation: OrderedDict = OrderedDict({})
    stack_nodes: List[OrderedDict] = [[documentation, [], 0], ]
    is_cdata: bool = False
    temp_loc: int = 0
    flag_out: int = 0

    def onXmlDeclHandler(version: int, encoding: Optional[str], standalone: int):
        nonlocal xml_declares
        xml_declares['version'] = version
        xml_declares['encoding'] = encoding
        xml_declares['standalone'] = standalone

    def onStartElementHandler(name: str, attrs: Dict[str, str]):
        nonlocal stack_nodes, temp_loc, flag_out
        if 0 == flag_out: # only in.
            temp_loc = 0
        current_node = stack_nodes[-1][0]
        node = OrderedDict({})
        stack_nodes.append([node, [], temp_loc])
        for attr_name, attr_value in attrs.items():
            node[f'{attr_prefix}{attr_name}'] = attr_value
        if include_loc:
            node[f'{attr_prefix}{loc_key}'] = f'{temp_loc}'
        if name in current_node:
            sub_node = current_node[name]
            if isinstance(sub_node, OrderedDict):
                current_node[name] = [sub_node, node, ]
            elif isinstance(sub_node, list):
                current_node[name].append(node)
        else:
            current_node.update(OrderedDict({name: node}))
        flag_out = 0

    def onEndElementHandler(name: str):
        nonlocal stack_nodes, temp_loc, flag_out
        node = stack_nodes.pop()
        node[0][cdata_key] = cdata_separator.join(node[1])

        flag_out = 1
        temp_loc = f'{int(node[2])+1}'

    def onStartCdataSectionHandler():
        nonlocal is_cdata
        is_cdata = True

    def onEndCdataSectionHandler():
        nonlocal is_cdata
        is_cdata = False

    def onCommentHandler(data: str):
        nonlocal stack_nodes
        if include_comment:
            node = stack_nodes[-1][0]
            if comment_key in node:
                node[comment_key].append(data.strip())
            else:
                node[comment_key] = [data.strip(), ]

    def onCharacterDataHandler(data: str):
        nonlocal stack_nodes, is_cdata
        t_data = data.strip()
        if not combine_cdata and is_cdata:
            node = stack_nodes[-1][0]
            if cdata_self_key not in node:
                node[cdata_self_key] = [t_data, ]
            else:
                node[cdata_self_key].append(t_data)
        else:
            if t_data:
                stack_nodes[-1][1].append(t_data)

    xmlParser: XMLParserType = ParserCreate(encoding=encoding)
    xmlParser.XmlDeclHandler = onXmlDeclHandler
    xmlParser.StartElementHandler = onStartElementHandler
    xmlParser.EndElementHandler = onEndElementHandler
    xmlParser.CommentHandler = onCommentHandler
    xmlParser.CharacterDataHandler = onCharacterDataHandler
    xmlParser.StartCdataSectionHandler = onStartCdataSectionHandler
    xmlParser.EndCdataSectionHandler = onEndCdataSectionHandler

    xmlParser.Parse(xml_data, 1)

    return documentation, xml_declares
