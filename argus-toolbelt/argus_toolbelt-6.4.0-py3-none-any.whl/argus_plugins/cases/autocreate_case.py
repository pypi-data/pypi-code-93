import base64
import csv
import json
import logging
import sys
from io import StringIO
from json import JSONDecodeError
from string import Formatter
from datetime import datetime
from functools import lru_cache, partial
from itertools import groupby
from pathlib import Path

from argus_api.api.cases.v2.case import (
    advanced_case_search,
    create_case,
    add_comment,
    add_case_tag,
    close_case,
    add_attachment,
    update_case,
    request_workflow as request_case_workflow,
    acknowledge_workflow as acknowledge_case_workflow,
    list_workflows as list_case_workflows,
)
from argus_api.api.customers.v1.customer import get_customer
from argus_api.api.events.v1.aggregated import update_events
from argus_plugins import argus_cli_module
from jinja2 import Environment, FileSystemLoader, select_autoescape

from argus_cli import run
from argus_cli.helpers.log import log
from argus_cli.plugin import register_command
from argus_plugins.cases.utils import STATUSES, PRIORITIES, CASE_TYPES, format_tags_list
from argus_plugins.enrichments import EVENTS_ENRICHMENTS, enrich_data
from argus_plugins.cases.autocreate_case_output_template import (
    AUTOCREATE_OUTPUT_TEMPLATE,
)


# Cache the function to avoid multiple calls to the backend
from argus_plugins.datastore.synchronize import set_data_with_buffer

get_customer = lru_cache(maxsize=None)(get_customer)

#: Status assigned when reopening cases due to new events
REOPENED_CASE_STATUS = "pendingCustomer"

#: Action to take when new events are added to a closed case
#: - "reopen": the case is reopened.
#:   This is the default unless the autoreport is set to close cases on creation.
#: - "silent": events are added to the case, which remains closed.
#:   This is the default when the autoreport is set to close cases on creation.
#: - "new-case": create a new case with the new events, bypassing any timeout set.
CLOSED_CASE_UPDATE_METHODS = ("reopen", "silent", "new-case")


def _case_watcher_json(
    event: dict = None,
    case_watcher_from_field: str = None,
    case_watcher: str = None,
    watcher_type: str = "email",
    verbose: bool = False,
):
    """Creates an argus supported structure for case watchers"""
    watchers = [case_watcher] if case_watcher is not None else []
    if case_watcher_from_field is not None:
        watcher = value_from_nested_key(case_watcher_from_field, event)
        # Using extend avoids the possibility of adding None
        watchers.extend([watcher] if watcher is not None else [])

    structured_watchers = []
    for watcher in watchers:
        structured_watchers.append(
            {
                "type": watcher_type,
                "destination": watcher,
                "verbose": verbose,
            }
        )
    return structured_watchers


def customer_language(customer: dict) -> str:
    """Convenience function to get a customer's language"""
    try:
        return customer["language"]
    except KeyError:
        log.debug("Fetching language from Argus for {shortName}".format_map(customer))
        return get_customer(idOrShortname=customer["shortName"])["data"]["language"]


def value_from_nested_key(key: str, d: dict):
    """Allows the user to reference a variable with normal python string-format syntax.

    Example:
        >>> value_from_nested_key("a[b][c]", {"a": {"b": {"c": 1337}})
        1337
        >>> value_from_nested_key("a", {"a": 42})
        42
    """
    try:
        return Formatter().get_field(key, (), d)[0]
    except KeyError:
        return None
    except AttributeError:
        return None


def _get_field(field: str, event: dict):
    """Returns a hashable key for us to use

    Dicts and lists arn't hashable, so we have to make them hashable.
    This is a representation problem that could have been fixed by having objects
    representing the data in stead of dicts.
    """
    new = value_from_nested_key(field, event)

    if isinstance(new, dict):
        # Dicts arn't hashable
        new = tuple(sorted(new.items()))
    elif isinstance(new, list):
        # List ain't hashable either.
        new = tuple(new)
    elif new is None:
        log.warning(f"field {field} missing from event #{event.get('id')}")

    return new


def group_inputs(data: list, group_by: list) -> dict:
    """Groups the input based on the group_by parameter.

    The first field in group_by will be the outermost group in the dict.

    :param data: The input
    :param group_by: Field to group by
    :returns: A nested group dict
    """

    def _key(event):
        return tuple(_get_field(field, event) for field in group_by)

    # Has to be sorted, see groupby()'s documentation.
    sorted_data = sort_input(data, group_by)

    return {
        # groupby() returns the group as an iterator, so we have to unpack it.
        group_key: list(group)
        for group_key, group in groupby(sorted_data, key=_key)
    }


def groupby_jinja_filter(value, key):
    """Custom groupby for jinja templates that supports dots in the keys

    This is implemented as pallets have decided not to support this syntax in
    jinja. See https://github.com/pallets/jinja/issues/1142

    This implmenetation wraps around another input grouping that already exists
    in this codebase, group_inputs(), and modifies the output from that to match
    Jinja's own implementation of groupby. For Jinja's implementation, see:
    https://github.com/pallets/jinja/blob/master/src/jinja2/filters.py#L930

    :param value: The iterable with the data that should be grouped
    :param key: A python-style dictionary reference. See value_from_nested_key()
                for examples.
    """

    # A note on the implementation seen under:
    #       group_inputs() allows for multiple keys, which is not supported
    #       by jinja's groupby. Thus we have wrap the key in a list and unpack
    #       the resulting group key that was returned.
    return [
        (group_key[0], group) for group_key, group in group_inputs(value, [key]).items()
    ]


def sort_input(data: list, sort_by: list) -> list:
    """Sorts the given inputs based on the given list.

    The first field in sort_by will be the one with most precedence (primary key).

    :param data: The input
    :param sort_by: Fields to sort by
    :returns: A sorted list of events
    """

    def _key(event):
        # "None" is not sortable, so adding an extra sorting value for that.
        k = []
        for field in sort_by:
            val = _get_field(field, event)
            k.append((val is None, val))
        return k

    return sorted(data, key=_key)


def group_data(data: list, groups: list):
    """Gives the data groups based on the customer and groups"""
    customer_events = group_inputs(data, ["customerInfo"])
    for customer, data in customer_events.items():
        # Workaround because group_inputs()'s key is a tuple.
        customer = dict(customer[0])
        log.info('Handling data for customer "{}"'.format(customer["shortName"]))

        groupings = group_inputs(data, groups)
        for group, data in groupings.items():
            # Argus requires the group to be a string
            yield (customer, str(group), data)


def put_data_in_case(
    data: list,
    customer: dict,
    group: str,
    find_existing_case: callable,
    create_description: callable,
    create_comment: callable,
    create_case: callable,
    event_accociator: callable,
    on_case_created: callable,
    on_case_updated: callable,
    set_initial_comment: bool = False,
    new_case_on_closed: bool = False,
):
    """Puts the data into the given group for the given customer.

    :param data: List of data
    :param customer: The customer object to associate with the data
    :param group: The group that the data belongs to
    :param find_existing_case:
    :param create_description:
    :param create_comment:
    :param create_case:
    :param event_accociator:
    :param set_initial_comment: Add internal comment on case creation
    :param on_case_created: callback used whenever a new case is created
    :param on_case_updated: callback used whenever an existing case is updated
    :param new_case_on_closed: if set to True, create a new case when there is an existing
      case that is in a closed state. Used to implement the "new-case" method for the
      "--closed-case-update" option.
    :returns: The case that got commented or created.
    """
    case = find_existing_case(customer, group)

    if case and case["status"] == "closed" and new_case_on_closed:
        log.info(f"Ignoring existing closed case #{case['id']}")
        case = None
    description = create_description(data, customer, comment=True if case else False)
    log.debug("Description for the given group: {}".format(description))
    if case:
        create_comment(case["id"], comment=description)
        log.info("Created comment on case #{id}".format_map(case))
        on_case_updated(case)
    else:
        case = create_case(customer, group, description, data[0])
        log.info("Created new case #{id}".format_map(case))
        if set_initial_comment:
            initial_comment = create_description(
                data, customer, comment=False, internal=True
            )
            create_comment(case["id"], comment=initial_comment, internal=True)
            log.debug(
                "Added internal comment after creating case #{id}".format_map(case)
            )
        on_case_created(case)
        log.debug("Executed on_case_created callback for case #{id}".format_map(case))

    event_accociator(case["id"], data)
    log.debug(
        "Associated these events with case {id}:\n{events}".format(
            id=case["id"], events=[event["id"] for event in data]
        )
    )

    return case


def print_results(events: list, cases: dict, dry: bool):
    if dry:
        print("\nThis was a dry run, script would have done the following:\n")
    stats = ""
    for customer, group, case, _ in cases.values():
        stats += "\n\t{} (#{}) - {} - {}".format(
            case["subject"], case["id"], customer, group
        )

    print(
        "Analyzed {event_amount} events, and associated them with "
        "{case_amount} cases.\n\t{stats}".format(
            event_amount=len(events), case_amount=len(cases), stats=stats
        )
    )

    for customer, group, case, events in cases.values():
        subject = f"{case['subject']} (#{case['id']})"
        case_output = AUTOCREATE_OUTPUT_TEMPLATE.substitute(
            subject=subject,
            subject_line="=" * len(subject),
            description=case["description"],
            description_line="-" * len("Description"),
            associated_events_line="-" * len("Associated events"),
            associated_events="\n".join(event["id"] for event in events),
        )
        print(case_output)


@register_command(extending="cases", module=argus_cli_module)
def autocreate(
    data: sys.stdin,
    key: str,
    template_folder: Path,
    group_by: list = [],
    sort_by: list = [],
    timeout: datetime = datetime.now(),
    case_title: str = "Autocreated based on group {group}",
    case_status: STATUSES = "pendingCustomer",
    case_priority: PRIORITIES = "medium",
    case_type: CASE_TYPES = "securityIncident",
    case_service: str = "ids",
    case_category: str = None,
    case_watcher: str = None,
    case_watcher_from_field: str = None,
    skip_notifications: bool = False,
    initial_internal_comment: bool = False,
    internal_case: bool = False,
    request_workflow: str = None,
    acknowledge_workflow: str = None,
    workflow_comment: str = None,
    dry: bool = False,
    close_after_create: bool = False,
    enrich: EVENTS_ENRICHMENTS = None,
    tags: dict = None,
    attach_events: ["json", "csv"] = False,
    closed_case_update: CLOSED_CASE_UPDATE_METHODS = None,
    test_data: bool = False,
):
    """A tool for automatically creating a case based on events and similar.

    Customers will automatically be extracted from the given data.
    There will be one case per group, meaning that if you group by email addresses,
    you'll get one case per email address.

    Examples:
        New case every time the script runs:
        $ argus-cli ./data.json "protocol-data" ./
            --group-by protocol
            --case-title "We've spotted some protocols"

        New case every week based on the alarm ID
        $ echo "<List of JSON objects>"| argus-cli cases autocreate "scary-events" ./templates/
            --group-by attackInfo[alarmId]
            --timeout "1 week"
            --case-title "This week, scary stuff happened."

    :param data: JSON-data to parse. Will typically be passed via stdin.
    :param key: A unique ID for this autocreate instance. Will be associated to the case as a tag.
    :param template_folder: Folder with JINJA templates. Filenames are: <key>.<language>.html
    :param group_by: Identifiers in the data to group by (Unique cases will be created per group).
    :param sort_by: Identifiers in the data to sort by
    :param timeout: The timeframe between new cases. If not specified a new case will be created every run.
    :param case_title: The title of the created case. Can be used with python string formatting.
    :param case_status: The status of the created case.
    :param case_priority: The priority of the created case.
    :param case_type: The type of the created case.
    :param case_service: The service of the created case.
    :param case_category: The category of the created case.
    :param case_watcher: Watcher that should be added to the case.
    :param case_watcher_from_field: String that points to where e-mail address
        for case watcher is in the event. The format is like python's dict
        access. For example: properties[property.name]
    :param skip_notifications: If set, no notifications will be sent on case creation.
    :param initial_internal_comment: Creates a new internal comment on case creation. This can be added with a block checking for "internal" in your template.
    :param internal_case: Makes new cases only visible internally for techs.
    :param request_workflow: Request a new workflow of the specified type. Note: If workflow is already requested, this request will be ignored.
    :param acknowledge_workflow: Acknowledge a new workflow of the specified type. Note: If this workflow is not active, this request will be ignored.
    :param workflow_comment: An optional comment to pass when requesting or acknowledging a workflow
    :param dry: If set, no data will be commited.
    :param close_after_create: If set, the case will be closed immediately after creation.
    :param list enrich: optional enrichments to perform on the events.
    :param tags: key-value tags to add to the created case. Expects JSON key-values {"tag": "value"}, for mutliple tags use a JSON object or list : {"tag1" : "tag1-value", "tag2": "tag2-value"}
    :param attach_events: Format to attach events in. If left unset, no events
            are attached.
    :param closed_case_update: Action to take when new events are added to a closed case. "reopen": reopen the case. "silent": leave the case closed. "new-case": create a new case.
    :param test_data: create the case as test data.
    """
    # Encapsulate data into functions to avoid tramp data
    _add_comment = partial(
        add_comment,
        notification={"skipEmail": skip_notifications, "skipSMS": skip_notifications},
    )

    def _create_description(
        events: list, customer: dict, comment: bool = False, internal: bool = False
    ) -> str:
        """Creates a case description from a template file"""
        # Argus returns long names for languages, let's use 2 letter versions.
        language_map = {"NORWEGIAN": "no", "ENGLISH": "en"}

        jinja_env = Environment(
            # jinja doesn't accept Path objects
            loader=FileSystemLoader(str(template_folder.absolute())),
            autoescape=select_autoescape(["html", "xml"]),
        )
        jinja_env.filters["custom_groupby"] = groupby_jinja_filter

        template = jinja_env.get_template(
            "{key}.{language}.html".format(
                key=key, language=language_map[customer_language(customer)]
            )
        )
        return template.render(data=events, comment=comment, internal=internal)

    def _existing_case(customer: dict, group: str):
        """Returns an existing case based on the customer, key and group"""
        # If it turns out that there are a lot of search requests, then
        # this could probably be changed in favor of a single request to the "key"
        # and then filter for customer and group internally.
        cases = advanced_case_search(
            startTimestamp=int(
                timeout.timestamp() * 1000
            ),  # Only get cases within the timeout
            timeFieldStrategy=["createdTimestamp"],
            customerID=[customer["id"]],
            tag=[{"key": "case-autocreate-key", "values": [key]}],
            # Tags are OR-ed together, we want to AND them
            subCriteria=[
                {
                    "required": True,
                    "tag": [{"key": "case-autocreate-group", "values": [group]}],
                }
            ],
        )["data"]

        # There should only be one case within the timeout for a key-group-customer pair!
        return cases[0] if cases else None

    def _create_case(customer: dict, group: str, description: str, data: dict):
        """Creates a new case and adds tags to it.

        :param customer: The customer to create the case for.
        :param group: The group that the case is created from. Used for tagging and the title.
        :param description: Description of the case
        :param data: The data of the event. Used for the title.
        """
        case = create_case(
            customerID=customer["id"],
            service=case_service,
            category=case_category,
            type=case_type,
            priority=case_priority,
            accessMode="readRestricted" if internal_case else None,
            status=case_status if not internal_case else "pendingSoc",
            notification={
                "skipEmail": skip_notifications,
                "skipSMS": skip_notifications,
            },
            publish=(not internal_case),
            watchers=_case_watcher_json(
                event=data,
                case_watcher_from_field=case_watcher_from_field,
                case_watcher=case_watcher,
            ),
            subject=case_title.format(group=group, **data),
            description=description,
            testData=test_data,
        )["data"]

        case_tags = [
            {"key": "case-autocreate-key", "value": key},
            {"key": "case-autocreate-group", "value": group},
        ]

        case_tags.extend(tags)
        log.debug(f"adding tags to case: {case_tags}")

        add_case_tag(caseID=case["id"], tags=case_tags)

        return case

    def _event_accociator(case_id: int, events: list):
        """Associates the events to the case"""
        buffered_update = set_data_with_buffer(
            update_events, buffered_argument="eventIdentifiers"
        )
        buffered_update(
            eventIdentifiers=[event["id"] for event in events],
            update={
                "comment": "Automatically assessed by cases autocreate "
                "(Key: {})".format(key),
                "associateToCase": case_id,
            },
        )

        if attach_events:
            # In some cases, the customer wants to get the raw data of the event.
            if attach_events == "json":
                data = StringIO(json.dumps(events))
            elif attach_events == "csv":
                modified_events = [
                    {
                        "Event ID": event["id"],
                        "Customer": event["customerInfo"]["name"],
                        "Start time": event["startTimestamp"],
                        "End time": event["endTimestamp"],
                        "Source IP": event["source"]["networkAddress"]["address"],
                        "Source port": event["source"]["port"],
                        "Destination IP": event["destination"]["networkAddress"][
                            "address"
                        ],
                        "Destination port": event["destination"]["port"],
                        "Signature": event["attackInfo"]["signature"],
                        "Alarm ID": event["attackInfo"]["alarmID"],
                        "Description": event["attackInfo"]["alarmDescription"],
                        "Location": event["location"]["name"],
                        "Severity": event["severity"],
                        "Count": event["count"],
                    }
                    for event in events
                ]

                data = StringIO()
                csv_writer = csv.DictWriter(data, modified_events[0].keys())
                csv_writer.writeheader()
                csv_writer.writerows(modified_events)

            add_attachment(
                caseID=case_id,
                name=f"events.{attach_events}",
                mimeType=f"text/{attach_events}",
                data=base64.b64encode(data.getvalue().encode()).decode(),
            )

    def _on_case_created(case: dict):
        """Called whenever a new case is created"""
        if close_after_create:
            id_ = case["id"]
            if not dry:
                close_case(
                    caseID=id_,
                    notification={
                        "skipEmail": True,
                        "skipSMS": True,
                    },
                )
            log.info(f"Closed case #{id_}")
        if request_workflow:
            _request_workflow(case, request_workflow, workflow_comment)
        elif acknowledge_workflow:
            _acknowledge_workflow(case, acknowledge_workflow, workflow_comment)

    def _on_case_updated(case: dict):
        """Called when a case is updated

        (when a case already existed, as opposed to _on_case_created)
        """
        id_ = case["id"]
        if case["status"] == "closed" and closed_case_update == "reopen":
            if not dry:
                update_case(case["id"], status=REOPENED_CASE_STATUS)
            log.info(f"reopened case #{id_}")
        if request_workflow:
            _request_workflow(case, request_workflow, workflow_comment)
        elif acknowledge_workflow:
            _acknowledge_workflow(case, acknowledge_workflow, workflow_comment)

    def _request_workflow(case: dict, flow: str, comment: str = None):
        """Request a workflow"""
        id_ = case["id"]
        if not dry:
            for w in list_case_workflows(caseID=id_)["data"]:
                if w["workflow"] == flow:
                    log.info(
                        f"Ignoring request of workflow {flow} which is already active"
                    )
                    return
            request_case_workflow(id_, flow, comment)
        log.info(f"Requested workflow {flow} for case #{id_}")

    def _acknowledge_workflow(case: dict, flow: str, comment: str = None):
        """Request a workflow"""
        id_ = case["id"]
        target = None
        if not dry:
            for w in list_case_workflows(caseID=id_)["data"]:
                if w["workflow"] == flow and not w["acknowledgedByUser"]:
                    target = w
            if target:
                acknowledge_case_workflow(id_, flow, comment)
                log.info(f"Acknowledged workflow {flow} for case #{id_}")
            else:
                log.info(f"Ignoring acknowledge of workflow {flow} which is not active")
        else:
            log.info(f"Acknowledged workflow {flow} for case #{id_}")

    if not closed_case_update:
        closed_case_update = "silent" if close_after_create else "reopen"
    if dry:
        log.info("--- Running in DRY mode! No data will be committed. ---")
        log.setLevel(logging.DEBUG)
        for handler in log.handlers:
            handler.setLevel(logging.DEBUG)
        log.debug("Due to dry mode, debug output has been enabled.")
    if test_data:
        log.info(
            "--- Running in TEST-DATA mode! Cases will be created as test data. ---"
        )

    # process the tags early to fail before the case has been created
    try:
        if tags:
            tags = format_tags_list(tags)
        else:
            tags = []
    except ValueError:
        log.error(f"Invalid tags format: {tags}")
        exit(1)

    try:
        data = json.load(data)  # Input is a file, so we'll have to parse it.
    except JSONDecodeError as e:
        if e.pos == 0:
            raise ValueError(
                "The supplied JSON input is empty. "
                "Your event-search most likely returned no result."
            ) from e
        else:
            raise e

    log.info("Received {} events".format(len(data)))

    data = sort_input(data, sort_by)

    if enrich is not None:
        log.debug(f"Enriching events with {' '.join(enrich)}")
        enrich_data(data, enrich)

    cases = {}

    putter = partial(
        put_data_in_case,
        find_existing_case=_existing_case,
        create_description=_create_description,
        create_comment=_add_comment if not dry else lambda *a, **kw: None,
        create_case=(
            _create_case
            if not dry
            else lambda *a, **kw: {"id": f"DRY {len(cases.values())}"}
        ),
        event_accociator=_event_accociator if not dry else lambda *a, **kw: None,
        on_case_created=_on_case_created,
        on_case_updated=_on_case_updated,
        set_initial_comment=initial_internal_comment,
        new_case_on_closed=(closed_case_update == "new-case"),
    )

    for customer, group, event in group_data(data, group_by):

        # We should already have events grouped by customer here, so this is
        # just an extra verification
        if any(customer["shortName"] != e["customerInfo"]["shortName"] for e in event):
            raise RuntimeError(
                "Not all events belong to the specified "
                + f"customer {customer['shortName']}: {event}"
            )

        case = putter(
            data=event,
            customer=customer,
            group=group,
        )
        if dry:
            # [0] here to replicate behaviour in put_data_in_case.
            case["subject"] = case_title.format(group=group, **event[0])
            case["description"] = _create_description(event, customer, group)

        cases[case["id"]] = (customer["shortName"], group, case, event)

    print_results(data, cases, dry)


if __name__ == "__main__":
    run(autocreate)
