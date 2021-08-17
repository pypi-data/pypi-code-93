# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 10:17:57 2021

@author: Michael Nauge, Université de Poitiers
"""



# un dictionnaire permettant de faciliter l'attribution d'un data_type
# pour des humains.
VOCABTYPE = {
	"text":"http://purl.org/coar/resource_type/c_18cf",
    "image":"http://purl.org/coar/resource_type/c_c513",
    "video":"http://purl.org/coar/resource_type/c_12ce",
    "sound":"http://purl.org/coar/resource_type/c_18cc",
    "journal article":"http://purl.org/coar/resource_type/c_6501",
    "conference poster":"http://purl.org/coar/resource_type/c_6670",
    "conference object":"http://purl.org/coar/resource_type/c_c94f",
    "learning object":"http://purl.org/coar/resource_type/c_e059",
    "book":"http://purl.org/coar/resource_type/c_2f33",
    "map":"http://purl.org/coar/resource_type/c_12cd",
    "dataset":"http://purl.org/coar/resource_type/c_ddb1",
    "software":"http://purl.org/coar/resource_type/c_5ce6",
    "other":"http://purl.org/coar/resource_type/c_1843"
    }


VOCABTYPE_reverse = {
	"http://purl.org/coar/resource_type/c_18cf":"text",
    "http://purl.org/coar/resource_type/c_c513":"image",
    "http://purl.org/coar/resource_type/c_12ce":"video",
    "http://purl.org/coar/resource_type/c_18cc":"sound",
    "http://purl.org/coar/resource_type/c_6501":"journal article",
    "http://purl.org/coar/resource_type/c_6670":"conference poster",
    "http://purl.org/coar/resource_type/c_c94f":"conference object",
    "http://purl.org/coar/resource_type/c_e059":"learning object",
    "http://purl.org/coar/resource_type/c_2f33":"book",
    "http://purl.org/coar/resource_type/c_12cd":"map",
    "http://purl.org/coar/resource_type/c_ddb1":"dataset",
    "http://purl.org/coar/resource_type/c_5ce6":"software",
    "http://purl.org/coar/resource_type/c_1843":"other"
    }