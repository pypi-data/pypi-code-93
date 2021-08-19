#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2020  David Arroyo Menéndez

# Author: David Arroyo Menéndez <davidam@gnu.org>
# Maintainer: David Arroyo Menéndez <davidam@gnu.org>

# This file is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3, or (at your option)
# any later version.

# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with damewebutils; see the file LICENSE.  If not, write to
# the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA,

from unittest import TestCase
from SPARQLWrapper import SPARQLWrapper, JSON
import requests

class TestWikidata(TestCase):

    def test_dbpedia_asturias(self):
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
""")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        l = []
        for result in results["results"]["bindings"]:
            l.append(result["label"]["value"])
        self.assertEqual(l[0], 'Asturias')

    def test_surnames(self):
        url = 'https://query.wikidata.org/sparql'
        query = """
SELECT ?surname ?surnameLabel ?count
WHERE
{
  {
    SELECT ?surname (COUNT(?human) AS ?count) WHERE {
    # ?human wdt:P31 wd:Q5.
      ?human wdt:P734 ?surname.
    }
    GROUP BY ?surname ORDER BY DESC(?count) LIMIT 2
  }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
ORDER BY DESC(?count)
LIMIT 2
# limit to 10 results so we don't timeout
"""
        r = requests.get(url, params = {'format': 'json', 'query': query})
        data = r.json()
        l = []
        for result in data["results"]["bindings"]:
            elem = [result['surnameLabel']['value'], result['count']['value']]
            l.append(elem[0])
        self.assertEqual(l, ['Li','Wang'])

    def test_openstreetmap(self):
        # https://www.wikidata.org/wiki/Wikidata:OpenStreetMap
        url = 'https://query.wikidata.org/sparql'
        query = """
SELECT ?itemLabel ?item ?OSM ?code
WHERE
{
        ?item wdt:P31 wd:Q6465 . #French départements
        ?item wdt:P300 ?code . #with ISO 3166-2 code
        OPTIONAL { ?item wdt:P402 ?OSM }. #OSM relation if available
        SERVICE wikibase:label { bd:serviceParam wikibase:language "fr" }
}
"""
        r = requests.get(url, params = {'format': 'json', 'query': query})
        data = r.json()
        l = []
        vector = data['results']['bindings'][0]
        values = [vector['code']['value'], vector['OSM']['value'], vector['itemLabel']['value'], vector['item']['value']]
        self.assertEqual(values, ['FR-44', '7432', 'Loire-Atlantique', 'http://www.wikidata.org/entity/Q3068'])

    def test_conan_doyle(self):
        # See https://www.wikidata.org/wiki/Wikidata:SPARQL_tutorial#Arthur_Conan_Doyle_books
        url = 'https://query.wikidata.org/sparql'
        query = """
SELECT ?book ?bookLabel
WHERE
{
  ?book wdt:P50 wd:Q35610.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }
}
ORDER BY DESC(?book)
LIMIT 2

"""
        r = requests.get(url, params = {'format': 'json', 'query': query})
        data = r.json()
#        print(data['results']['bindings'][0]['bookLabel'])
        self.assertEqual(data['results']['bindings'][0]['bookLabel'], {'type': 'literal', 'value': 'Q45192'})

    def test_ue(self):
        # See https://towardsdatascience.com/a-brief-introduction-to-wikidata-bb4e66395eb1
        url = 'https://query.wikidata.org/sparql'
        query = """
        SELECT ?country ?countryLabel ?capitalLabel ?population
WHERE
{
  ?country wdt:P463 wd:Q458.
  ?country wdt:P36 ?capital.
  ?capital wdt:P1082 ?population.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "   [AUTO_LANGUAGE],en". }
}
ORDER BY DESC(?capital)
"""
        r = requests.get(url, params = {'format': 'json', 'query': query})
        data = r.json()
        self.assertEqual(data['results']['bindings'][0]['countryLabel']['value'], "Kingdom of the Netherlands")

    def test_cervantes(self):
        # http://www.cervantesvirtual.com/obra/la-serrana-de-la-vera--0/
        url = 'https://query.wikidata.org/sparql'
        query = """
SELECT ?workLabel WHERE {
 wd:Q165257 wdt:P2799 ?id
 BIND(uri(concat("http://data.cervantesvirtual.com/person/", ?id)) as ?bvmcID)
 SERVICE <http://data.cervantesvirtual.com/openrdf-sesame/repositories/data> {
 ?bvmcID <http://rdaregistry.info/Elements/a/authorOf> ?work .
 ?work rdfs:label ?workLabel
 }
}
ORDER BY (?id)
"""
        r = requests.get(url, params = {'format': 'json', 'query': query})
        data = r.json()
        self.assertEqual(data['results']['bindings'][0], {'workLabel': {'type': 'literal', 'value': 'El príncipe inocente : comedia'}})

    def test_number_of_computer_types(self):
        url = 'https://query.wikidata.org/sparql'
        query = """
        SELECT (count(*) as ?instances) WHERE  {
            ?instance wdt:P31 wd:Q473708     # Instance has a type of "home computers
        }
"""
        r = requests.get(url, params = {'format': 'json', 'query': query})
        data = r.json()
        print(data['results']['bindings'])
        self.assertTrue(int(data['results']['bindings'][0]['instances']['value']) > 80)
