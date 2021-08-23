"""
Helper module to find common object usages in app, e.g. xml node.
"""

import bs4
import re
import os
import json


class xml_node(object):
    """
    XML Node Definition
    """

    def __init__(self, name):
        self.name = name


def find_xml_nodes_usages(xml_files, nodes):
    """
    Helper function to find xml node usage
    """
    #  Outputs not_applicable if no xml files found
    findings = []
    for relative_filepath, full_filepath in xml_files:
        soup = bs4.BeautifulSoup(open(full_filepath, "rb"), "lxml-xml")
        for node in nodes:
            if hasattr(node, "attrs"):
                findings_per_file = soup.find_all(node.name, attrs=node.attrs)
            else:
                findings_per_file = soup.find_all(node.name)
            findings_per_file = [(e, relative_filepath) for e in findings_per_file]
            findings += findings_per_file
    return findings

def unpack_absolute_path(paths_tuple):
    """ This function
        1. unpacks a tuple
        2. Pushes the second tuple value into an array

        @param:
        paths_tuple <Array of tuples>: Any tuple of the form (x,y)

        returns <Array>: Array of values

        Example:

        [('foo', 'bar'), ('candy', 'm&m'), ('icecream', 'chocolate')]

        returns

        ['bar', 'm&m', 'chocolate']
    """
    absolute_paths = []
    if paths_tuple is None:
        return absolute_paths

    for a, b in (paths_tuple):
        absolute_paths.append(b)

    return absolute_paths


def validate_imports(files, allowed_imports_set):
    """ This function returns paths of files which have require/define statements not present in the allowed imports set

        @param:
        files <Array>: Array of file paths
        allowed_imports_set <Set>: Set of file path imports

        Returns

        improper_files <Array>: Array of file paths which match paths from the given set

        Example:

        files = [
            "/splunk_appinspect/checks/a.py",
            "/splunk_appinspect/checks/b.py",
            "/splunk_appinspect/checks/c.py",
            "/splunk_appinspect/checks/d.py",

        allowed_imports_set = [
            "routers/Dashboards",
            "routers/SavedSearches",
            "routers/AppsLocal",
            "routers/AuthenticationUsers",
        ]

        Let's assume a.py and c.py have the lines routers/SavedSearches and routers/AuthenticationUsers respectively this would then return b.py and d.py

        returns

        ['a.py', 'c.py']
    """
    improper_files = []
    try:
        for filepath in files:
            with open(filepath, "r", encoding='utf-8') as my_file:
                matches = get_imported_matches(my_file.read())
                for match in matches:
                    if match not in allowed_imports_set:
                        improper_files.append((filepath, match))
    except Exception as exception:
        print("Exception while validating imports {}".format(exception))

    return improper_files

def get_imported_matches(file):
    """ Utility function that matches require js imports in a given file.

        @param
        file <String>: File path

        Returns
        matches <Array>: List of imports done by require statements

        Example:

        require(['jquery', 'underscore', 'splunkjs/mvc', 'util/console'], function ($, _, mvc, console) {
            // Do nothing
        })

        returns

        ['jquery', 'underscore', 'splunkjs/mvc', 'util/console']
    """
    matches = []
    pattern = re.compile(
        r"(require|define)(\s)*\((\s)*\[[^\[]+\]|(require|define)(\s)*\((\n|.)*\)")
    for matched_object in pattern.finditer(file):
        imported_matches = re.finditer(
            r"['\"]([^'\"]*)['\"]",
            matched_object.group())
        for imported in imported_matches:
            matches.append(imported.group(1))
    return matches

def find_xml_nodes_usages_absolute_path(xml_files, nodes):
    """ Unfortunately, need to duplicate this function as we need absolute paths
        Helper function to find xml node usage
    """
    #  Outputs not_applicable if no xml files found
    findings = []
    for relative_filepath, full_filepath in xml_files:
        soup = bs4.BeautifulSoup(open(full_filepath, "rb"), "lxml-xml")
        for node in nodes:
            if hasattr(node, "attrs"):
                findings_per_file = soup.find_all(node.name, attrs=node.attrs)
            else:
                findings_per_file = soup.find_all(node.name)
            findings_per_file = [(e, full_filepath) for e in findings_per_file]
            findings += findings_per_file
    return findings

def get_spa_template_file_paths(abs_paths, spa_referenced_files):
    """ This function returns intersection of Array A and B

        @param:
        abs_paths <Array>: Array of file paths
        spa_referenced_files <Array>: Array of file paths

        returns:
        final_paths <Array>: Intersection of Array A and B
    """
    final_paths = []

    for path in abs_paths:
        head, tail = os.path.split(path)    # Extract file name
        if tail in spa_referenced_files:  # filter HTML files referenced by SPA's
            final_paths.append(path)

    return final_paths

def populate_set_from_json(file_path):
    """ This function take a json file object as a parameter and returns a set from the json values in the file

        @param
        file_path <file object>: JSON file object obtained from open() function

        returns

        json_set <Set>: A set of values from the json file
     """
    json_set = set()
    try:
        array_from_json = json.load(file_path)
        for i in array_from_json:
            json_set.add(i)
    except Exception as exception:
        print("Error while loading json to a set. {}".format(exception))

    return json_set

def handle_multiple_scripts(scripts):
    seperated_scripts = []
    multiple_scripts = scripts.split(',')
    for script in multiple_scripts:
        seperated_scripts.append(script.strip())

    return seperated_scripts