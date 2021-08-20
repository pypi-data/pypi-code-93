# -*- coding: utf-8 -*-
# copyright 2013-2021 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import hashlib

from cubicweb.utils import json_dumps


class RqlIOSchemaHolder(object):
    """Class used to load the schema and its hash.
    Both can be fetched by the client via dedicated views,
    so it can decide to update the locally stored schema if
    the integrity is not valid.
    """

    _schema = None
    _hash = None

    @staticmethod
    def format_schema(
        typeNames, specializes, attributeNames, relationsTo, relationsFrom
    ):
        return {
            "eid": typeNames[0][0],
            "name": typeNames[0][1],
            "modificationDate": typeNames[0][2].strftime("%Y/%m/%d %H:%M:%S"),
            "specializes": specializes[0][0] if specializes else None,
            "attributes": [
                {"eid": row[0], "name": row[1], "type": row[2], "cardinality": row[3]}
                for row in attributeNames
            ],
            "relationsTo": [
                {
                    "eid": row[0],
                    "name": row[1],
                    "from": row[2],
                    "fromName": typeNames[0][1],
                    "fromCardinality": row[6],
                    "to": row[3],
                    "toName": row[4],
                    "toCardinality": row[6],
                    "description": row[5],
                }
                for row in relationsTo
            ],
            "relationsFrom": [
                {
                    "eid": row[0],
                    "name": row[1],
                    "from": row[2],
                    "fromName": row[3],
                    "fromCardinality": row[6],
                    "to": row[4],
                    "toName": typeNames[0][1],
                    "toCardinality": row[6],
                    "description": row[5],
                }
                for row in relationsFrom
            ],
        }

    @classmethod
    def get_schema(cls, cnx):
        if cls._schema is not None:
            return cls._schema

        entities = []
        etypes = cnx.execute("Any T WHERE T is CWEType")
        for etype in etypes:
            eid = etype[0]
            rql_requests = [
                (
                    f"Any TYPE,NAME,MD WHERE TYPE eid {eid}, TYPE name NAME, "
                    "TYPE modification_date MD"
                ),
                (f"Any PARENT WHERE TYPE eid {eid}, TYPE specializes PARENT"),
                (
                    f"""Any ATTR,NAME,ATTRTYPENAME,CARD ORDERBY ON WHERE TYPE eid {eid},
                    ATTR from_entity TYPE,
                    ATTR to_entity ATTRTYPE,
                    ATTR relation_type RELTYPE,
                    RELTYPE name NAME,
                    ATTR is CWAttribute,
                    ATTR cardinality CARD?,
                    ATTR ordernum ON,
                    ATTRTYPE name ATTRTYPENAME"""
                ),
                (
                    f"""Any ATTR,NAME,SUBJECT,OBJECT,ONAME,DESC,
                    CARD ORDERBY ON WHERE SUBJECT eid {eid},
                    ATTR from_entity SUBJECT,
                    ATTR to_entity OBJECT,
                    OBJECT name ONAME,
                    ATTR relation_type RELTYPE,
                    RELTYPE name NAME,
                    RELTYPE description DESC,
                    ATTR is CWRelation,
                    ATTR cardinality CARD?,
                    ATTR ordernum ON"""
                ),
                (
                    f"""Any ATTR,NAME,SUBJECT,SNAME,OBJECT,DESC,
                    CARD ORDERBY ON WHERE OBJECT eid {eid},
                    ATTR to_entity OBJECT,
                    ATTR from_entity SUBJECT,
                    SUBJECT name SNAME,
                    ATTR relation_type RELTYPE,
                    RELTYPE name NAME,
                    RELTYPE description DESC,
                    ATTR is CWRelation,
                    ATTR cardinality CARD?,
                    ATTR ordernum ON"""
                ),
            ]
            rsets = [cnx.execute(request) for request in rql_requests]
            entities.append(RqlIOSchemaHolder.format_schema(*rsets))
        cls._schema = {"entities": entities}
        return cls._schema

    @classmethod
    def get_schema_hash(cls, cnx):
        if cls._hash is not None:
            return cls._hash
        cls._hash = hashlib.md5(
            json_dumps(cls.get_schema(cnx)["entities"]).encode(cnx.encoding)
        ).hexdigest()
        return cls._hash
