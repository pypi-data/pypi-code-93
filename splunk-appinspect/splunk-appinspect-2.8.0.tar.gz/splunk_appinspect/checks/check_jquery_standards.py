"""
### jQuery vulnerabilities
"""
import os
import re
import splunk_appinspect
import splunk_appinspect.check_routine.util as util

""" This function throws a warning message during app inspect if the dashboards of the app
do not have a version attribute OR have the version attribute set to a value other than 1.1

@param:
app: An app object
reporter: Reporter object """

@splunk_appinspect.tags("cloud", "jquery", "private_app", "future")
@splunk_appinspect.cert_version(min="2.5.0")
def check_simplexml_standards_version(app, reporter):
    """ Check that the dashboards in your app have a valid version attribute.
    """

    xml_files = list(app.get_filepaths_of_files(types=[".xml"]))
    nodes = [util.xml_node("dashboard"), util.xml_node("form")]
    query_nodes = util.find_xml_nodes_usages(xml_files, nodes)
    for query_node, relative_filepath in query_nodes:
        version = query_node.get('version')
        if version is None:
            message = (
                "Change the version attribute in the root node of your Simple XML dashboard {} to " +
                "`<version=1.1>`. Earlier dashboard versions introduce security vulnerabilities " +
                "into your apps and are not permitted in Splunk Cloud"
            ).format(relative_filepath)
            reporter.fail(message, relative_filepath)
        elif version.strip() == "2" or version.strip() == "1.1":    # If UDF or simple XML dashboard 1.1, continue
            continue
        else:
            message = (
                "Version attribute of the dashboard {} is set to {}.Change the version attribute " +
                "in the root node of your Simple XML dashboard to " +
                "`<version=1.1>`. Earlier dashboard versions introduce security vulnerabilities " +
                "into your apps and are not permitted in Splunk Cloud"
            ).format(relative_filepath, version)
            reporter.fail(message, relative_filepath)


""" This function throws a warning message during app inspect if the app's HTML and JS files
have unsupported imports

@param:
app: An app object
reporter: Reporter object """

@splunk_appinspect.tags("cloud", "jquery", "private_app", "future")
@splunk_appinspect.cert_version(min="2.5.0")
def check_hotlinking_splunk_web_libraries(app, reporter):
    """ Check that the app files are not importing files directly from the
        search head.
    """

    html_files = list(app.get_filepaths_of_files(basedir="appserver/template", types=[".html"]))
    xml_files = list(app.get_filepaths_of_files(types=[".xml"]))
    js_files = list(app.get_filepaths_of_files(basedir="appserver/static", types=[".js"]))
    spa_referenced_template_files = []  # Single page application referenced HTML files
    spa_referenced_js_files = [] # spa_referenced_template_files which have <script src="***.js">
    sxml_dashboard_scripts = []    # Simple XML dashboards referenced files

    # Get all SPA's (https://docs.google.com/document/d/1Q4BZvZtn7ee4G6m7lMUB7M6ZbxxXB09WWwHXB9SWMBg/edit#heading=h.1atn2axm0c7p)
    view_nodes = [util.xml_node("view")]
    view_dashboard_nodes = util.find_xml_nodes_usages_absolute_path(xml_files, view_nodes)

    # Get SXML dashboards
    dashboard_nodes = [util.xml_node("dashboard"), util.xml_node("form")]
    sxml_dashboard_nodes = util.find_xml_nodes_usages_absolute_path(xml_files, dashboard_nodes)

    # Get all supported modules from supported_modules.json
    supported_modules_json_path = os.path.abspath(os.path.join(__file__, "../../splunk/jquery_checks_data/supported_modules.json"))

    with open(supported_modules_json_path, 'r', encoding='utf-8', errors='ignore') as supported_modules_file:
        supported_modules_imports = util.populate_set_from_json(supported_modules_file)

    # Get all template attributes in SPA  files
    for query_node, absolute_file_path in view_dashboard_nodes:
        reference_template = query_node.get('template')
        if reference_template is not None:
            if ',' not in reference_template:
                spa_referenced_template_files.append(reference_template)
            else: # Handle multiple template files scenario
               spa_referenced_template_files = spa_referenced_template_files + util.handle_multiple_scripts(reference_template)             

    # Check for scripts references in dashboards
    for query_node, absolute_file_path in sxml_dashboard_nodes:
        reference_script = query_node.get('script')
        if reference_script is not None:
            if ',' not in reference_script:
                sxml_dashboard_scripts.append(reference_script)
            else: # Handle multiple script files scenario
                sxml_dashboard_scripts = sxml_dashboard_scripts + util.handle_multiple_scripts(reference_script) 

    # Get absolute paths of js files
    unpacked_js_files = util.unpack_absolute_path(js_files)
    # paths to scripts referenced by simple xml dashboards inside the appserver directory
    sxml_js_files_ref_paths = util.get_spa_template_file_paths(unpacked_js_files, sxml_dashboard_scripts)
    # paths to templates referenced by SPA
    template_paths = util.get_spa_template_file_paths(util.unpack_absolute_path(html_files), spa_referenced_template_files)

    for each_template in template_paths:
        with open(each_template, "r", encoding='utf-8') as my_file:
            file_content = my_file.read()
        reference_script = re.search(r'script[ ]*src=[ ]*(?:\'|").*\.js(?:\'|")', file_content)
        if reference_script is not None:
            template_script = re.search(
                    r'(?:\'|")([^"\']*.js)(?:\'|")',
                    reference_script.group(0)).group(1).strip()
            if template_script is not None:
                spa_referenced_js_files.append(template_script)

    message = ("Embed all your app's front-end JS dependencies in the /appserver directory. " +
               "If you import files from Splunk Web, your app might fail when Splunk Web updates."
               )

    # Check for any imports in SPA

    for files, errors in util.validate_imports(template_paths, {}):
        reporter.warn(message, files)

    # Check for only non exposed modules in SXML dashboards

    for files, errors in util.validate_imports(sxml_js_files_ref_paths, supported_modules_imports):
        reporter.warn(message, files)

    # Check for any imports in SPA referenced JS files
    abs_path_spa_ref_js_files = util.get_spa_template_file_paths(unpacked_js_files, spa_referenced_js_files)

    for files, errors in util.validate_imports(abs_path_spa_ref_js_files, {}):
        reporter.warn(message, files)   
