# Copyright 2019 Splunk Inc. All rights reserved.

"""
### Deprecated features from Splunk Enterprise 6.2

The following features should not be supported in Splunk 6.2 or later.
https://docs.splunk.com/Documentation/Splunk/6.2.0/ReleaseNotes/Deprecatedfeatures
"""

# Python Standard Libraries
import re

# Third-Party Libraries
# N/A

# Custom Libraries
import splunk_appinspect
from splunk_appinspect.check_routine import (
    report_on_xml_findings,
    xml_node,
    find_xml_nodes,
)


@splunk_appinspect.tags(
    "splunk_appinspect",
    "splunk_6_2",
    "splunk_6_5",
    "deprecated_feature",
    "removed_feature",
    "cloud",
    "private_app"
)
@splunk_appinspect.cert_version(min="1.2.1")
def check_for_dashboard_xml_list_element(app, reporter, target_splunk_version):
    """Check Dashboard XML files for `<list>` element. `<list>` was deprecated in Splunk 6.2
    and removed in Splunk 6.5.
    """
    if target_splunk_version < "splunk_6_2":
        return
    if target_splunk_version < "splunk_6_5":
        reporter_output = "<list> element is detected. <list> was deprecated since Splunk 6.2. Please do not use it."
        reporter_action = reporter.fail
    else:
        reporter_output = "<list> element is detected. <list> was removed since Splunk 6.5. Please do not use it."
        reporter_action = reporter.fail
    report_on_xml_findings(
        find_xml_nodes(app, [xml_node("list")]),
        reporter,
        reporter_output,
        reporter_action,
    )


@splunk_appinspect.tags("splunk_appinspect", "splunk_6_2", "deprecated_feature", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_simple_xml_row_grouping(app, reporter, target_splunk_version):
    """Check for the deprecated grouping attribute of `row` node in Simple XML files.
    Use the `<panel>` node instead.
    """
    if target_splunk_version < "splunk_6_2":
        return
    grouping_re_obj = re.compile(r"""[0-9,"'\s]+""")
    node = xml_node("row")
    node.attrs = {"grouping": grouping_re_obj}
    finding_action, reporter_output = (
        reporter.fail,
        (
            "Detect grouping attribute of <row>, which is deprecated in Splunk 6.2. Please use "
            "the <panel> node instead."
        ),
    )
    report_on_xml_findings(
        find_xml_nodes(app, [node], path="default/data/ui/views"),
        reporter,
        reporter_output,
        finding_action,
    )


@splunk_appinspect.tags("splunk_appinspect", "splunk_6_2", "deprecated_feature", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_populating_search_element_in_dashboard_xml(app, reporter):
    """Check for the deprecated `<populatingSearch>` and `<populatingSavedSearch>` elements in dashboard XML files.
    Use the `<search>` element instead.
    """
    nodes = [xml_node("populatingSearch"), xml_node("populatingSavedSearch")]
    reporter_output = (
        "<{}> element was deprecated in Splunk 6.2 and supposed to be removed in future releases, "
        "please use the <search> element instead."
    )
    report_on_xml_findings(
        find_xml_nodes(app, nodes, path="default/data/ui/views"),
        reporter,
        reporter_output,
        reporter.fail,
    )


@splunk_appinspect.tags("splunk_appinspect", "splunk_6_2", "deprecated_feature", "cloud", "private_app")
@splunk_appinspect.cert_version(min="1.7.0")
def check_for_earliest_time_and_latest_time_elements_in_dashboard_xml(
    app, reporter, target_splunk_version
):
    """Check for the deprecated `<earliestTime>` and `<latestTime>` elements in dashboard XML files.
    As of version 6.2 these elements are replaced by `<earliest>` and `<latest>` elements.
    """
    if target_splunk_version < "splunk_6_2":
        return
    nodes = [xml_node("earliestTime"), xml_node("latestTime")]
    reporter_output = (
        "<{}> element was deprecated in Splunk 6.2. "
        "please use the <earliest>/<latest> element instead."
    )
    report_on_xml_findings(
        find_xml_nodes(app, nodes, path="default/data/ui/views"),
        reporter,
        reporter_output,
        reporter.fail,
    )
