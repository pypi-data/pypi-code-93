import json
import os
import pytest
import re
import requests
import shutil
import tempfile
import time
import uuid

import pandas as pd

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy.workbooks._content import Content
from seeq.spy.workbooks.tests import test_load
from seeq.spy.workbooks._data import StoredSignal, CalculatedSignal
from seeq.spy.workbooks._item import Item
from seeq.spy.workbooks._workbook import Workbook, Analysis, Topic
from seeq.spy.workbooks._worksheet import Worksheet, AnalysisWorksheet
from seeq.spy import _common
from seeq.spy import _config
from seeq.spy import _login
from seeq.spy.tests import test_common


def setup_module():
    test_common.login()


def _get_exports_folder():
    return os.path.join(os.path.dirname(__file__), 'Exports')


def _get_full_path_of_export(subfolder):
    return os.path.join(_get_exports_folder(), subfolder)


def _load_and_push(subfolder):
    workbooks = spy.workbooks.load(_get_full_path_of_export(subfolder))
    return _push(workbooks)


def _push(workbooks):
    push_df = spy.workbooks.push(workbooks, refresh=False)
    return push_df.iloc[0]['Pushed Workbook ID']


@pytest.mark.export
def test_export_example_and_test_data():
    # Use this function to re-create the Example Export and test-related exports.
    # First copy the contents of "crab/sdk/pypi/spy-example-and-test-data-folder.zip" into "crab/sq-run-data-dir"
    # and start Seeq Server by doing "sq run" from crab.
    #
    # You MUST log in as "mark.derbecker@seeq.com" with password "SeeQ2013!". (If you don't log in as
    # mark.derbecker@seeq.com, then some of the ACL tests may get screwed up.)
    #
    # If you add workbooks, make sure to share them with Everyone because the tests will log in as Agent API Key.
    #
    # When finished, change the sdk-system-tests Run Configuration in IntelliJ to have an "-m export" flag so that only
    # this test gets executed. It will copy everything into the right spot.
    #
    # Then make sure to zip up the contents of "crab/sq-run-data-dir" and replace
    # "crab/sdk/pypi/spy-example-and-test-data-folder.zip" and commit it to the repo.

    search_df = spy.workbooks.search({
        'Path': 'Example Export'
    }, content_filter='ALL')

    spy.workbooks.options.pretty_print_html = True

    workbooks = spy.workbooks.pull(search_df)
    for workbook in workbooks:
        # Make "Isolate By User" true so that, by default, a label will be added on spy.workbooks.push() that will
        # isolate users from each other.
        workbook.definition['Isolate By User'] = True

    path = test_load.get_example_export_path()
    if os.path.exists(path):
        shutil.rmtree(path)

    spy.workbooks.save(workbooks, path)
    spy.workbooks.save(workbooks, path + '.zip')

    search_df = spy.workbooks.search({}, content_filter='ALL')

    workbooks = spy.workbooks.pull(search_df)
    path = _get_exports_folder()
    if os.path.exists(path):
        shutil.rmtree(path)
    spy.workbooks.save(workbooks, path)

    _delete_max_capsule_duration_on_bad_metric()

    search_df = spy.workbooks.search({
        'Path': 'ACL Test Folder'
    }, content_filter='ALL')

    workbooks = spy.workbooks.pull(search_df)

    spy.workbooks.save(workbooks, _get_exports_folder())


def _delete_max_capsule_duration_on_bad_metric():
    with open(os.path.join(_get_exports_folder(),
                           'Bad Metric (0459C5F0-E5BD-491A-8DB7-BA4329E585E8)', 'Items.json'), 'r') as f:
        bad_metrics_items_json = json.load(f)

    del bad_metrics_items_json['1541C121-A38E-41C3-BFFA-AB01D0D0F30C']["Formula Parameters"][
        "Measured Item Maximum Duration"]

    del bad_metrics_items_json['1AA91F16-D476-4AF8-81AB-A2120FDA68E5']["Formula Parameters"][
        "Bounding Condition Maximum Duration"]

    with open(os.path.join(_get_exports_folder(),
                           'Bad Metric (0459C5F0-E5BD-491A-8DB7-BA4329E585E8)', 'Items.json'), 'w') as f:
        json.dump(bad_metrics_items_json, f, indent=4)


def _find_item(original_id, isolate_by_user=False):
    items_api = ItemsApi(test_common.get_client())
    data_id = '[%s] %s' % (_login.user.username if isolate_by_user else None, original_id)
    _filters = [
        'Datasource Class==%s && Datasource ID==%s && Data ID==%s' % (
            _common.DEFAULT_DATASOURCE_CLASS, _common.DEFAULT_DATASOURCE_ID, data_id),
        '@includeUnsearchable']

    search_results = items_api.search_items(
        filters=_filters,
        offset=0,
        limit=2)  # type: ItemSearchPreviewPaginatedListV1

    if len(search_results.items) == 0:
        return None

    if len(search_results.items) > 1:
        raise RuntimeError('Multiple items found with Data ID of "%s"', data_id)

    return search_results.items[0]


@pytest.mark.system
def test_example_export():
    workbooks = test_load.load_example_export()

    # Make sure the Topic is processed first, so that we test the logic that ensures all Topic dependencies are
    # pushed before the Topic is pushed. (Otherwise the IDs in the Topic will not be properly replaced.)
    reordered_workbooks = list()
    reordered_workbooks.extend(filter(lambda w: w['Workbook Type'] == 'Topic', workbooks))
    reordered_workbooks.extend(filter(lambda w: w['Workbook Type'] == 'Analysis', workbooks))

    assert isinstance(reordered_workbooks[0], Topic)
    assert isinstance(reordered_workbooks[1], Analysis)

    status_df = spy.workbooks.push(reordered_workbooks, refresh=False).set_index('ID')

    analysis_result = status_df.loc['D833DC83-9A38-48DE-BF45-EB787E9E8375']['Result']
    assert 'Success' in analysis_result

    smooth_temperature_signal = _find_item('FBBCD4E0-CE26-4A33-BE59-3E215553FB1F', isolate_by_user=True)

    items_api = ItemsApi(test_common.get_client())
    item_output = items_api.get_item_and_all_properties(id=smooth_temperature_signal.id)  # type: ItemOutputV1
    item_properties = {p.name: p.value for p in item_output.properties}

    # Make sure we don't change the Data ID format, since users will have pushed lots of items in this format.
    assert item_properties['Data ID'] == '[agent_api_key] FBBCD4E0-CE26-4A33-BE59-3E215553FB1F'

    assert 'UIConfig' in item_properties
    ui_config_properties_dict = json.loads(item_properties['UIConfig'])
    assert ui_config_properties_dict['type'] == 'low-pass-filter'

    high_power_condition = _find_item('8C048548-8E83-4380-8B24-9DAD56B5C2CF', isolate_by_user=True)

    item_output = items_api.get_item_and_all_properties(id=high_power_condition.id)  # type: ItemOutputV1
    item_properties = {p.name: p.value for p in item_output.properties}

    assert 'UIConfig' in item_properties
    ui_config_properties_dict = json.loads(item_properties['UIConfig'])
    assert ui_config_properties_dict['type'] == 'limits'


@pytest.mark.system
def test_push_repeatedly():
    workbooks = test_load.load_example_export()
    workbooks = [w for w in workbooks if isinstance(w, Analysis)]

    push1_df = spy.workbooks.push(workbooks, path='test_push_repeatedly')
    assert push1_df.iloc[0]['ID'] != push1_df.iloc[0]['Pushed Workbook ID'] == workbooks[0].id

    # CRAB-22768: Ensure that the Data property is not present
    assert 'Data' not in workbooks[0].definition

    push2_df = spy.workbooks.push(workbooks, path='test_push_repeatedly', refresh=False)
    assert push2_df.iloc[0]['ID'] == push2_df.iloc[0]['Pushed Workbook ID'] == workbooks[0].id

    push3_df = spy.workbooks.push(workbooks, use_full_path=True)
    assert push3_df.iloc[0]['ID'] == push3_df.iloc[0]['Pushed Workbook ID'] == workbooks[0].id

    # CRAB-22768: See above
    assert 'Data' not in workbooks[0].definition

    push4_df = spy.workbooks.push(workbooks, use_full_path=True, refresh=False)
    assert push4_df.iloc[0]['ID'] == push4_df.iloc[0]['Pushed Workbook ID'] == workbooks[0].id


@pytest.mark.system
def test_workbook_paths():
    workbooks = test_load.load_example_export()

    # This call will put the folder of workbooks ('Example Export') in a top-level 'Use Full Path Folder'
    status_df = spy.workbooks.push(workbooks, path='Use Full Path Folder', use_full_path=True, refresh=False) \
        .set_index('ID')
    analysis_result = status_df.loc['D833DC83-9A38-48DE-BF45-EB787E9E8375']['Result']
    assert 'Success' in analysis_result

    workbooks_df = spy.workbooks.search({
        'Path': 'Use Full Path Folder >> Example Export'
    })
    assert len(workbooks_df) == 2

    # This call will effectively move the folder of workbooks ('Example Export') to the user's home folder and clean
    # out the 'Use Full Path Folder'
    status_df = spy.workbooks.push(workbooks, path=_common.PATH_ROOT, use_full_path=True, refresh=False).set_index('ID')
    analysis_result = status_df.loc['D833DC83-9A38-48DE-BF45-EB787E9E8375']['Result']
    assert 'Success' in analysis_result

    workbooks_df = spy.workbooks.search({
        'Path': 'Use Full Path Folder'
    })
    assert len(workbooks_df) == 0

    workbooks_df = spy.workbooks.search({
        'Path': 'Example Export'
    })
    assert len(workbooks_df) == 2

    # This call will not move the workbooks out of the 'Example Export' folder, because the 'Search Folder ID' property
    # in the workbook gives them a no-op "relative path" such that they will be put in the folder specified in the
    # spy.workbooks.push(path='<path>') argument. Since a zero-length path argument is specified here, they will not
    # be moved.
    status_df = spy.workbooks.push(workbooks, path='', refresh=False).set_index('ID')
    analysis_result = status_df.loc['D833DC83-9A38-48DE-BF45-EB787E9E8375']['Result']
    assert 'Success' in analysis_result

    workbooks_df = spy.workbooks.search({
        'Path': 'Example Export'
    })
    assert len(workbooks_df) == 2

    workbooks_df = spy.workbooks.search({
        'Name': '/Example (?:Analysis|Topic)/'
    })
    assert len(workbooks_df) == 0

    # Remove the "Search Folder ID" so that the workbooks have an "absolute path"
    for workbook in workbooks:
        del workbook['Search Folder ID']

    # This call will once again put the workbooks in the 'Example Export' folder, using the "absolute path" mentioned
    # above.
    status_df = spy.workbooks.push(workbooks, path='', refresh=False).set_index('ID')
    analysis_result = status_df.loc['D833DC83-9A38-48DE-BF45-EB787E9E8375']['Result']
    assert 'Success' in analysis_result

    workbooks_df = spy.workbooks.search({
        'Path': 'Example Export'
    })
    assert len(workbooks_df) == 2

    workbooks_df = spy.workbooks.search({
        'Name': '/Example (?:Analysis|Topic)/'
    })
    assert len(workbooks_df) == 0


@pytest.mark.system
def test_workbook_path_with_folder_id():
    folders_api = FoldersApi(test_common.get_client())
    folder_name = f'test_workbook_path_with_folder_id_Folder_{_common.new_placeholder_guid()}'
    folder_output = folders_api.create_folder(body=FolderInputV1(
        name=folder_name))

    workbook_name = f'test_workbook_path_with_folder_id_Analysis_{_common.new_placeholder_guid()}'
    workbook = Analysis(workbook_name)
    workbook.worksheet('The Worksheet')

    # First push it to the root of My Items
    spy.workbooks.push(workbook)

    # Make sure it's there
    search_df = spy.workbooks.search({
        'Name': workbook_name
    }, recursive=False)
    assert len(search_df) == 1

    # Now move it to the folder
    spy.workbooks.push(workbook, path=folder_output.id)

    # Make sure it's no longer in the root of My Items
    search_df = spy.workbooks.search({
        'Name': workbook_name
    }, recursive=False)
    assert len(search_df) == 0

    # Make sure it's in the folder
    search_df = spy.workbooks.search({
        'Path': folder_name,
        'Name': workbook_name
    })
    assert len(search_df) == 1


@pytest.mark.system
def test_owner():
    workbook_name = str(uuid.uuid4())
    workbook = Analysis({
        'Name': workbook_name
    })
    workbook.worksheet('one_and_only')
    workbooks = [workbook]

    def _confirm(username, in_my_folder):
        assert workbook['Owner']['Username'] == username
        search_df = spy.workbooks.search({
            'Name': workbook_name
        }, content_filter='owner')
        assert len(search_df) == (1 if in_my_folder else 0)

    push_df1 = spy.workbooks.push(workbooks)
    _confirm(spy.user.username, True)

    try:
        test_common.login(admin=True)
        user_janna = test_common.add_normal_user('Janna', 'Contact', 'janna@seeq.com', 'jannacontact')

        with pytest.raises(RuntimeError, match='User "agent_api_key" not found'):
            # agent_api_key is not discoverable via user search, it is purposefully hidden
            spy.workbooks.push(workbooks, refresh=False, owner='agent_api_key')

        push_df2 = spy.workbooks.push(workbooks, owner=user_janna.id)
        _confirm(user_janna.username, False)

        push_df3 = spy.workbooks.push(workbooks, owner=spy.workbooks.FORCE_ME_AS_OWNER)
        _confirm(test_common.ADMIN_USER_NAME, True)

        push_df4 = spy.workbooks.push(workbooks, owner=user_janna.username)
        _confirm(user_janna.username, False)

        assert push_df1.iloc[0]['Pushed Workbook ID'] == push_df2.iloc[0]['Pushed Workbook ID'] == push_df3.iloc[0][
            'Pushed Workbook ID'] == push_df4.iloc[0]['Pushed Workbook ID']

        with pytest.raises(RuntimeError):
            spy.workbooks.push(workbooks, refresh=False, owner='non_existent_user')

    finally:
        # Go back to normal user
        test_common.login(admin=False)


@pytest.mark.system
def test_worksheet_order():
    workbooks = spy.workbooks.load(_get_full_path_of_export('Worksheet Order (2BBDCFA7-D25C-4278-922E-D99C8DBF6582)'))

    spy.workbooks.push(workbooks, refresh=False)
    workbook_item = _find_item('2BBDCFA7-D25C-4278-922E-D99C8DBF6582')

    pushed_worksheet_names = [
        '1',
        '2',
        '3'
    ]

    workbooks_api = WorkbooksApi(test_common.get_client())
    worksheet_output_list = workbooks_api.get_worksheets(workbook_id=workbook_item.id)  # type: WorksheetOutputListV1
    assert len(worksheet_output_list.worksheets) == 3
    assert [w.name for w in worksheet_output_list.worksheets] == pushed_worksheet_names

    workbooks[0].worksheets = list(reversed(workbooks[0].worksheets))
    spy.workbooks.push(workbooks, refresh=False)
    worksheet_output_list = workbooks_api.get_worksheets(workbook_id=workbook_item.id)  # type: WorksheetOutputListV1
    assert len(worksheet_output_list.worksheets) == 3
    assert [w.name for w in worksheet_output_list.worksheets] == list(reversed(pushed_worksheet_names))

    workbooks[0].worksheets = list(filter(lambda w: w.id != '2BEC414E-2F58-45A0-83A6-AAB098812D38',
                                          reversed(workbooks[0].worksheets)))
    pushed_worksheet_names.remove('3')
    spy.workbooks.push(workbooks, refresh=False)
    worksheet_output_list = workbooks_api.get_worksheets(workbook_id=workbook_item.id)  # type: WorksheetOutputListV1
    assert len(worksheet_output_list.worksheets) == 2
    assert [w.name for w in worksheet_output_list.worksheets] == pushed_worksheet_names


@pytest.mark.system
def test_missing_worksteps():
    with tempfile.TemporaryDirectory() as temp_folder:
        missing_worksteps_folder = os.path.join(temp_folder, 'Missing Worksteps')
        shutil.copytree(test_load.get_example_export_path(), missing_worksteps_folder)

        # Removing this workstep will cause an error because it is referenced in the Example Topic document
        os.remove(os.path.join(
            missing_worksteps_folder,
            'Example Analysis (D833DC83-9A38-48DE-BF45-EB787E9E8375)',
            'Worksheet_1F02C6C7-5009-4A13-9343-CDDEBB6AF7E6_Workstep_221933FE-7956-4888-A3C9-AF1F3971EBA5.json'))

        # Removing this workstep will cause an error because it is referenced in an Example Analysis journal
        os.remove(os.path.join(
            missing_worksteps_folder,
            'Example Analysis (D833DC83-9A38-48DE-BF45-EB787E9E8375)',
            'Worksheet_10198C29-C93C-4055-B313-3388227D0621_Workstep_FD90346A-BF72-4319-9134-3922A012C0DB.json'))

        workbooks = spy.workbooks.load(missing_worksteps_folder)
        topic = [w for w in workbooks if w['Workbook Type'] == 'Topic'][0]
        for worksheet in topic.worksheets:
            if worksheet.name == 'Static Doc':
                fields = {'Name': f'content_1',
                          'Width': 1,
                          'Height': 1,
                          'Worksheet ID': '1F02C6C7-5009-4A13-9343-CDDEBB6AF7E6',
                          'Workstep ID': '221933FE-7956-4888-A3C9-AF1F3971EBA5',
                          'Workbook ID': 'D833DC83-9A38-48DE-BF45-EB787E9E8375'}
                content_1 = Content(fields, worksheet.document)

            worksheet.document.content = {'content_1': content_1}

        push_df = spy.workbooks.push(workbooks, refresh=False, errors='catalog')

        topic_row = push_df[push_df['Name'] == 'Example Topic'].iloc[0]
        analysis_row = push_df[push_df['Name'] == 'Example Analysis'].iloc[0]

        assert '221933FE-7956-4888-A3C9-AF1F3971EBA5' in topic_row['Result']
        assert 'FD90346A-BF72-4319-9134-3922A012C0DB' in analysis_row.loc['Result']


@pytest.mark.system
def test_bad_workstep():
    workbooks = spy.workbooks.load(_get_full_path_of_export('Bad Metric (0459C5F0-E5BD-491A-8DB7-BA4329E585E8)'))
    worksheet = workbooks[0].worksheets[0]
    current_workstep = worksheet.worksteps[worksheet.definition['Current Workstep ID']]
    bad_item_workstep = current_workstep
    bad_item_workstep.data['state']['stores']['sqTrendSeriesStore']['items'].append({
        'name': 'id? What id?'
    })
    assert bad_item_workstep.display_items.empty
    no_data_workstep = current_workstep
    no_data_workstep.definition['Data'] = None
    assert no_data_workstep.display_items.empty


@pytest.mark.system
def test_bad_metric():
    _load_and_push('Bad Metric (0459C5F0-E5BD-491A-8DB7-BA4329E585E8)')

    metrics_api = MetricsApi(test_common.get_client())

    # To see the code that this exercises, search for test_bad_metric in _workbook.py
    metric_item = _find_item('1AA91F16-D476-4AF8-81AB-A2120FDA68E5')
    threshold_metric_output = metrics_api.get_metric(id=metric_item.id)  # type: ThresholdMetricOutputV1
    assert threshold_metric_output.bounding_condition_maximum_duration.value == 40
    assert threshold_metric_output.bounding_condition_maximum_duration.uom == 'h'


@pytest.mark.system
def test_ancillaries():
    pushed_workbook_id = _load_and_push('Ancillaries (54C62C9E-629B-4A76-B8D6-5348D7D59D5F)')

    items_api = ItemsApi(test_common.get_client())

    item_search_list = items_api.search_items(
        types=['StoredSignal'],
        filters=['Data ID == Area A_Wet Bulb.sim.ts.csv'],
        scope=pushed_workbook_id,
        limit=1)  # type: ItemSearchPreviewPaginatedListV1

    assert len(item_search_list.items) == 1

    item_output = items_api.get_item_and_all_properties(id=item_search_list.items[0].id)  # type: ItemOutputV1

    wet_bulb_upper = _find_item('C33AB410-7B16-41FA-A374-BEB63900A857')
    wet_bulb_lower = _find_item('67796251-BE83-4047-975E-89D5D5858814')

    assert len(item_output.ancillaries) == 1
    assert len(item_output.ancillaries[0].items) == 2
    for ancillary_item in item_output.ancillaries[0].items:  # type: ItemAncillaryOutputV1
        if ancillary_item.name == 'Wet Bulb Warning Upper':
            assert ancillary_item.id == wet_bulb_upper.id
        if ancillary_item.name == 'Wet Bulb Warning Lower':
            assert ancillary_item.id == wet_bulb_lower.id

    item_search_list = items_api.search_items(
        types=['StoredSignal'],
        filters=['Data ID == Area A_Relative Humidity.sim.ts.csv'],
        scope=pushed_workbook_id,
        limit=1)  # type: ItemSearchPreviewPaginatedListV1

    assert len(item_search_list.items) == 1

    item_output = items_api.get_item_and_all_properties(id=item_search_list.items[0].id)  # type: ItemOutputV1

    humid_upper = _find_item('C2334AD9-4152-4CAA-BCA6-728A56E47F16')
    humid_lower = _find_item('A33334D3-6E92-40F2-80E3-95B18D08FAF2')

    # Because Relative Humidity is not present on any worksheets, the ancillary will not have been pushed. The
    # upper/lower boundary signals will have been pushed though.
    assert len(item_output.ancillaries) == 0
    assert humid_upper is not None
    assert humid_lower is not None

    # Now make sure that a Workbook that references Wet Bulb does not have ancillaries pulled when they're not scoped
    # to that workbook
    workbook = spy.workbooks.Analysis({'Name': 'No Ancillaries'})
    worksheet = workbook.worksheet('Wet Bulb')
    worksheet.display_items = spy.search({'Path': 'Example >> Cooling Tower 1 >> Area A', 'Name': 'Wet Bulb'})
    spy.workbooks.push(workbook)

    for item in workbook.item_inventory.values():
        assert item['Data ID'] is None or 'C33AB410-7B16-41FA-A374-BEB63900A857' not in item['Data ID']
        assert item['Data ID'] is None or '67796251-BE83-4047-975E-89D5D5858814' not in item['Data ID']


def _find_worksheet(workbook_id, worksheet_name, is_archived=False):
    workbooks_api = WorkbooksApi(test_common.get_client())
    worksheet_output_list = workbooks_api.get_worksheets(
        workbook_id=workbook_id, is_archived=is_archived)  # type: WorksheetOutputListV1

    return [w for w in worksheet_output_list.worksheets if w.name == worksheet_name][0]


@pytest.mark.system
def test_archived_worksheets():
    workbooks = list()
    workbooks.extend(spy.workbooks.load(_get_full_path_of_export(
        'Archived Worksheet - Topic (F662395E-FEBB-4772-8B3B-B2D7EB7C0C3B)')))
    workbooks.extend(spy.workbooks.load(_get_full_path_of_export(
        'Archived Worksheet - Analysis (DDB5F823-3B6A-42DC-9C44-566466C2BA82)')))

    push_df = spy.workbooks.push(workbooks, refresh=False)

    analysis_workbook_id = push_df[push_df['ID'] == 'DDB5F823-3B6A-42DC-9C44-566466C2BA82'] \
        .iloc[0]['Pushed Workbook ID']

    archived_worksheet = _find_worksheet(analysis_workbook_id, 'Archived', is_archived=True)

    items_api = ItemsApi(test_common.get_client())
    assert items_api.get_property(id=archived_worksheet.id, property_name='Archived').value


@pytest.mark.system
def test_images():
    pushed_workbook_id = _load_and_push('Images (130FF777-26B3-4A2D-BA95-0AFE7A2CA946)')

    image_worksheet = _find_worksheet(pushed_workbook_id, 'Main')

    doc = _get_journal_html(image_worksheet.id)

    assert doc.find('/api/annotations/A3757559-163D-4DDF-81EE-043B61332B12/images/1573580600045_v1.png') == -1

    match = re.match(r'.*src="/api(.*?)".*', doc, re.DOTALL)

    assert match is not None

    api_client_url = _config.get_api_url()
    request_url = api_client_url + match.group(1)
    response = requests.get(request_url, headers={
        "Accept": "application/vnd.seeq.v1+json",
        "x-sq-auth": test_common.get_client().auth_token
    }, verify=Configuration().verify_ssl)

    with open(os.path.join(_get_full_path_of_export('Images (130FF777-26B3-4A2D-BA95-0AFE7A2CA946)'),
                           'Image_A3757559-163D-4DDF-81EE-043B61332B12_1573580600045_v1.png'), 'rb') as f:
        expected_content = f.read()

    assert response.content == expected_content


@pytest.mark.system
def test_copied_workbook_with_journal():
    workbook_id = _load_and_push('Journal - Copy (3D952B33-70A7-460B-B71C-E2380EDBAA0A)')

    copied_worksheet = _find_worksheet(workbook_id, 'Main')

    doc = _get_journal_html(copied_worksheet.id)

    # We should not find mention of the "original" workbook/worksheet IDs. See _workbook.Annotation.push() for the
    # relevant code that fixes this stuff up.
    assert doc.find('1C5F8E9D-93E5-4C38-B4C6-4DBDBB4CF3D2') == -1
    assert doc.find('35D190B1-6AD7-4DEA-B8B7-178EBA2AFBAC') == -1

    _verify_workstep_links(workbook_id, copied_worksheet.id)

    duplicated_worksheet = _find_worksheet(workbook_id, 'Main - Duplicated')
    _verify_workstep_links(workbook_id, duplicated_worksheet.id)

    copy_and_paste_worksheet = _find_worksheet(workbook_id, 'Copy and Paste')
    _verify_workstep_links(workbook_id, copy_and_paste_worksheet.id)


def _verify_workstep_links(workbook_id, worksheet_id):
    doc = _get_journal_html(worksheet_id)

    workbooks_api = WorkbooksApi(test_common.get_client())
    for match in re.finditer(_common.WORKSTEP_LINK_REGEX, doc):
        # Make sure we don't get a 404
        workbooks_api.get_workstep(workbook_id=match.group(1),
                                   worksheet_id=match.group(2),
                                   workstep_id=match.group(3))


def _get_journal_html(worksheet_id):
    annotations_api = AnnotationsApi(test_common.get_client())
    annotations = annotations_api.get_annotations(
        annotates=[worksheet_id])  # type: AnnotationListOutputV1
    journal_annotations = [a for a in annotations.items if a.type == 'Journal']
    assert len(journal_annotations) == 1
    annotation_output = annotations_api.get_annotation(id=journal_annotations[0].id)  # AnnotationOutputV1
    return annotation_output.document


@pytest.mark.system
def test_topic_links():
    # Log in slightly differently so that the URLs change
    test_common.login('http://127.0.0.1:34216')

    workbooks = list()
    workbooks.extend(spy.workbooks.load(_get_full_path_of_export(
        'Referenced By Link - Topic (1D589AC0-CA54-448D-AC3F-B3C317F7C195)')))
    workbooks.extend(spy.workbooks.load(_get_full_path_of_export(
        'Referenced By Link - Analysis (3C71C580-F1FA-47DF-B953-4646D0B1F98F)')))

    push_df = spy.workbooks.push(workbooks, refresh=False)

    analysis_workbook_id = push_df[push_df['ID'] == '1D589AC0-CA54-448D-AC3F-B3C317F7C195'] \
        .iloc[0]['Pushed Workbook ID']

    document_worksheet = _find_worksheet(analysis_workbook_id, 'Only Document')

    annotations_api = AnnotationsApi(test_common.get_client())

    annotations = annotations_api.get_annotations(
        annotates=[document_worksheet.id])  # type: AnnotationListOutputV1

    report_annotations = [a for a in annotations.items if a.type == 'Report']
    assert len(report_annotations) == 1

    annotation_output = annotations_api.get_annotation(id=report_annotations[0].id)  # AnnotationOutputV1

    assert annotation_output.document.find('http://localhost') == -1

    test_common.login()


@pytest.mark.system
def test_replace_acl():
    workbooks = spy.workbooks.load(_get_full_path_of_export(
        'ACL Test (FF092494-FB04-4578-A12E-249417D93125)'))

    # First we'll push with acls='replace,loose', which will work but won't push all the ACLs
    push_df = spy.workbooks.push(workbooks, refresh=False, use_full_path=True, access_control='replace,loose')
    assert len(push_df) == 1
    assert push_df.iloc[0]['Result'] == 'Success'

    acl_test_workbook = _find_item('FF092494-FB04-4578-A12E-249417D93125')
    acl_test_folder = _find_item('6C513058-C1DA-4603-9498-75492B9BC119')

    items_api = ItemsApi(test_common.get_client())

    def _assert_acl_entry(_acl_output, name, _type, has_origin, role, read, write, manage):
        matches = [e for e in _acl_output.entries if
                   (e.identity.username == name if _type == 'User' else e.identity.name == name) and
                   e.identity.type == _type and
                   e.role == role and
                   ((e.origin is not None) if has_origin else (e.origin is None)) and
                   e.permissions.read == read and
                   e.permissions.write == write and
                   e.permissions.manage == manage]

        assert len(matches) == 1

    def _confirm_loose():
        _acl_output = items_api.get_access_control(id=acl_test_workbook.id)  # type: AclOutputV1
        assert len(_acl_output.entries) == 3
        _assert_acl_entry(_acl_output, 'agent_api_key', 'User', has_origin=False, role='OWNER',
                          read=True, write=True, manage=True)
        _assert_acl_entry(_acl_output, 'agent_api_key', 'User', has_origin=True, role=None,
                          read=True, write=True, manage=True)
        _assert_acl_entry(_acl_output, 'Everyone', 'UserGroup', has_origin=True, role=None,
                          read=True, write=False, manage=False)

        _acl_output = items_api.get_access_control(id=acl_test_folder.id)  # type: AclOutputV1
        assert len(_acl_output.entries) == 3
        _assert_acl_entry(_acl_output, 'agent_api_key', 'User', has_origin=False, role='OWNER',
                          read=True, write=True, manage=True)
        _assert_acl_entry(_acl_output, 'Everyone', 'UserGroup', has_origin=False, role=None,
                          read=True, write=False, manage=False)

    _confirm_loose()

    # Next we'll push with access_control='add,loose' and confirm that duplicate ACLs are not created
    push_df = spy.workbooks.push(workbooks, refresh=False, use_full_path=True, access_control='add,loose')
    assert len(push_df) == 1
    assert push_df.iloc[0]['Result'] == 'Success'

    _confirm_loose()

    with pytest.raises(_common.SPyDependencyNotFound):
        # Now we'll try access_control='replace,strict' which won't work because we don't know how to map the
        # "Just Mark" group or the "mark.derbecker@seeq.com" user
        spy.workbooks.push(workbooks, refresh=False, use_full_path=True, access_control='replace,strict')

    # Now we'll try access_control='replace,strict' again but this time provide a map that will convert the group and
    # user to the built-in Everyone and Agent API Key
    with tempfile.TemporaryDirectory() as temp:
        datasource_map = {
            "Datasource Class": "Auth",
            "Datasource ID": "Seeq",
            "Datasource Name": "Seeq",
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "User",
                    },
                    "New": {
                        "Type": "User",
                        "Datasource Class": "Auth",
                        "Datasource ID": "Seeq",
                        "Username": "agent_api_key"
                    }
                },
                {
                    "Old": {
                        "Type": "UserGroup",
                    },
                    "New": {
                        "Type": "UserGroup",
                        "Datasource Class": "Auth",
                        "Datasource ID": "Seeq",
                        "Name": "Everyone"
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_Auth_Seeq_Seeq.json'), 'w') as f:
            json.dump(datasource_map, f)

        spy.workbooks.push(workbooks, refresh=False, use_full_path=True, access_control='replace,strict',
                           datasource_map_folder=temp)

    push_df = spy.workbooks.push(workbooks, refresh=False, use_full_path=True, access_control='replace,loose')
    assert len(push_df) == 1
    assert push_df.iloc[0]['Result'] == 'Success'

    acl_output = items_api.get_access_control(id=acl_test_workbook.id)  # type: AclOutputV1
    assert len(acl_output.entries) == 4
    _assert_acl_entry(acl_output, 'agent_api_key', 'User', has_origin=False, role='OWNER',
                      read=True, write=True, manage=True)
    _assert_acl_entry(acl_output, 'agent_api_key', 'User', has_origin=True, role=None,
                      read=True, write=True, manage=True)
    _assert_acl_entry(acl_output, 'Everyone', 'UserGroup', has_origin=False, role=None,
                      read=True, write=False, manage=False)
    _assert_acl_entry(acl_output, 'Everyone', 'UserGroup', has_origin=True, role=None,
                      read=True, write=True, manage=True)

    acl_output = items_api.get_access_control(id=acl_test_folder.id)  # type: AclOutputV1
    assert len(acl_output.entries) == 3
    _assert_acl_entry(acl_output, 'agent_api_key', 'User', has_origin=False, role='OWNER',
                      read=True, write=True, manage=True)
    _assert_acl_entry(acl_output, 'Everyone', 'UserGroup', has_origin=False, role=None,
                      read=True, write=True, manage=True)


@pytest.mark.system
def test_tree_items():
    # If a CalculatedItem is part of a tree, then it is most likely that we want to find it using the datasource map
    # as opposed to creating a standalone CalculatedItem that is not in the tree. In other words, you expect that
    # when you push a workbook that has items from the TreeFileConnector, the worksheets will reference those items
    # and not some new CalculatedSignal that has no asset.

    tests_folder = os.path.dirname(__file__)
    mydata_trees_folder = os.path.join(test_common.get_test_data_folder(), 'mydata', 'trees')
    connector_config_folder = os.path.join(test_common.get_test_data_folder(), 'configuration', 'link')

    # Copy over the Tree File Connector stuff so that it gets indexed
    shutil.copy(os.path.join(tests_folder, 'tree1.csv'), mydata_trees_folder)
    shutil.copy(os.path.join(tests_folder, 'tree2.csv'), mydata_trees_folder)
    shutil.copy(os.path.join(tests_folder, 'Tree File Connector.json'), connector_config_folder)

    example_signals = spy.search({
        'Datasource Name': 'Example Data',
        'Name': 'Area ?_*',
        'Type': 'StoredSignal'
    })

    metadata_df = pd.DataFrame()

    metadata_df['ID'] = example_signals['ID']
    metadata_df['Type'] = example_signals['Type']
    metadata_df['Path'] = 'test_item_references'
    metadata_df['Asset'] = example_signals['Name'].str.extract(r'(.*)_.*')
    metadata_df['Name'] = example_signals['Name'].str.extract(r'.*_(.*)')
    metadata_df['Reference'] = True

    data_lab_items_df = spy.push(metadata=metadata_df, workbook=None)

    timer = _common.timer_start()
    while True:
        tree_file_items_df = pd.DataFrame()

        try:
            tree_file_items_df = spy.search({
                'Path': 'Tree 1 >> Cooling Tower - Area A',
                'Name': 'Compressor'
            })

        except RuntimeError:
            # If tree is not there yet, we'll get an exception
            pass

        if len(tree_file_items_df) == 2:
            break

        if _common.timer_elapsed(timer).seconds > 60:
            raise TimeoutError('Timed out waiting for Tree File Connector to finished indexing')

        time.sleep(0.1)

    workbooks = spy.workbooks.load(_get_full_path_of_export(
        'Item References (23DC9E6A-FCC3-456E-9A58-62D5CFF05816)'))

    spy.workbooks.push(workbooks, refresh=False)
    search_df = spy.workbooks.search({
        'Name': 'Item References'
    })
    workbooks = spy.workbooks.pull(search_df)

    def _verify_correct_items(_area):
        _correct_item_ids = [
            data_lab_items_df[(data_lab_items_df['Asset'] == _area) &
                              (data_lab_items_df['Name'] == 'Compressor Power')].iloc[0]['ID'],
            data_lab_items_df[(data_lab_items_df['Asset'] == _area) &
                              (data_lab_items_df['Name'] == 'Compressor Stage')].iloc[0]['ID'],
            tree_file_items_df.iloc[0]['ID'],
            tree_file_items_df.iloc[1]['ID']
        ]

        for _worksheet in workbooks[0].worksheets:  # type: Worksheet
            _current_workstep = _worksheet.worksteps[_worksheet['Current Workstep ID']]
            for _trend_item in _current_workstep.data['state']['stores']['sqTrendSeriesStore']['items']:
                assert _trend_item['id'] in _correct_item_ids

    _verify_correct_items('Area A')

    # Now map to a different Area
    with tempfile.TemporaryDirectory() as temp:
        sdl_datasource_map = {
            "Datasource Class": "Seeq Data Lab",
            "Datasource ID": "Seeq Data Lab",
            "Datasource Name": "Seeq Data Lab",
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "CalculatedSignal",
                        "Path": "test_item_references",
                        "Asset": "Area A",
                        "Name": "(?<name>.*)"
                    },
                    "New": {
                        "Type": "CalculatedSignal",
                        "Path": "test_item_references",
                        "Asset": "Area B",
                        "Name": "${name}"
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_Seeq_Data_Lab.json'), 'w') as f:
            json.dump(sdl_datasource_map, f)

        spy.workbooks.push(workbooks, refresh=False, datasource_map_folder=temp)

    workbooks = spy.workbooks.pull(search_df)

    _verify_correct_items('Area B')


@pytest.mark.system
def test_datasource_map_by_name():
    # In this test we push a few signals, two of which have the same name but one of which is archived because there
    # is special code in data.py to choose the un-archived signal if multiple signals are returned.
    push_df = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_datasource_map_by_name-Old',
        'Data ID': 'test_datasource_map_by_name-Old'
    }, {
        'Type': 'Signal',
        'Name': 'test_datasource_map_by_name-New',
        'Data ID': 'test_datasource_map_by_name-New'
    }, {
        'Type': 'Signal',
        'Name': 'test_datasource_map_by_name-New',
        'Data ID': 'test_datasource_map_by_name-New-Archived',
        'Archived': True
    }]), workbook=None)

    workbook = spy.workbooks.Analysis({
        'Name': 'test_datasource_map_by_name'
    })
    worksheet = workbook.worksheet('the one worksheet')

    display_items = push_df.loc[0:0]
    worksheet.display_items = display_items
    spy.workbooks.push(workbook, path='test_datasource_map_by_name')

    with tempfile.TemporaryDirectory() as temp:
        sdl_datasource_map = {
            "Datasource Class": "Seeq Data Lab",
            "Datasource ID": "Seeq Data Lab",
            "Datasource Name": "Seeq Data Lab",
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "StoredSignal",
                        "Name": "test_datasource_map_by_name-Old",
                    },
                    "New": {
                        "Type": "StoredSignal",
                        "Name": "test_datasource_map_by_name-New",
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_Seeq_Data_Lab.json'), 'w') as f:
            json.dump(sdl_datasource_map, f)

        spy.workbooks.push(workbook, path='test_datasource_map_by_path', datasource_map_folder=temp)

    assert workbook.worksheet('the one worksheet').display_items.iloc[0]['ID'] == push_df.iloc[1]['ID']


@pytest.mark.system
def test_datasource_map_multiple_matching_datasources():
    datasources_api = DatasourcesApi(test_common.get_client())

    datasource_input = DatasourceInputV1()
    datasource_input.datasource_class = 'test_push'
    datasource_input.datasource_id = 'datasource_id_1'
    datasource_input.name = 'test_datasource_map_multiple_matching_datasources'
    datasource_output_1 = datasources_api.create_datasource(body=datasource_input)  # type: DatasourceOutputV1

    datasource_input.datasource_id = 'datasource_id_2'
    datasources_api.create_datasource(body=datasource_input)  # type: DatasourceOutputV1

    analysis = Analysis({
        'Name': datasource_input.name
    })

    analysis.worksheet('the only worksheet')

    signal = StoredSignal()
    signal['ID'] = _common.new_placeholder_guid()
    signal['Name'] = 'A Signal'
    signal['Datasource Class'] = datasource_output_1.datasource_class
    signal['Datasource ID'] = datasource_output_1.datasource_id
    analysis.item_inventory[signal['ID']] = signal

    with tempfile.TemporaryDirectory() as temp:
        datasource_map = {
            "Datasource Class": datasource_output_1.datasource_class,
            "Datasource ID": datasource_output_1.datasource_id,
            "Datasource Name": datasource_output_1.name,
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "(?<type>.*)",
                        "Datasource Class": datasource_output_1.datasource_class,
                        "Datasource Name": datasource_output_1.name,
                        'Name': "(?<name>.*)"
                    },
                    "New": {
                        "Type": "${type}",
                        "Datasource Class": datasource_output_1.datasource_class,
                        "Datasource Name": datasource_output_1.name,
                        'Name': "${name}"
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_1.json'), 'w') as f:
            json.dump(datasource_map, f)

        with pytest.raises(
                RuntimeError,
                match='.*Multiple datasources found that match "test_datasource_map_multiple_matching_datasources".*'):
            spy.workbooks.push(analysis, datasource_map_folder=temp)


@pytest.mark.system
def test_datasource_map_push_errors():
    analysis = Analysis({
        'Name': 'test_datasource_map_push_errors'
    })

    analysis.worksheet('the only worksheet')

    stored_signal = StoredSignal()
    stored_signal['ID'] = _common.new_placeholder_guid()
    stored_signal['Name'] = 'A Stored Signal'
    stored_signal['Datasource Class'] = 'Seeq - Signal Datasource'
    stored_signal['Datasource ID'] = 'default'
    analysis.item_inventory[stored_signal['ID']] = stored_signal

    calculated_signal = CalculatedSignal()
    calculated_signal['ID'] = _common.new_placeholder_guid()
    calculated_signal['Name'] = 'A Calculated Signal'
    calculated_signal['Formula'] = '$a'
    calculated_signal['Formula Parameters'] = {
        '$a': stored_signal['ID']
    }
    analysis.item_inventory[calculated_signal['ID']] = calculated_signal

    try:
        spy.workbooks.push(analysis)
    except RuntimeError as e:
        assert re.match(r'.*"A Stored Signal".*not successfully mapped.*', str(e), re.DOTALL)
        assert re.match(r'.*Item\'s ID.*not found directly.*', str(e), re.DOTALL)

    with tempfile.TemporaryDirectory() as temp:
        datasource_map = {
            "Datasource Class": "Seeq - Signal Datasource",
            "Datasource ID": "default",
            "Datasource Name": "Seeq Signal Datasource",
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "Alien",
                    },
                    "New": {
                        "Type": "Predator",
                    }
                },
                {
                    "Old": {
                        "Type": "(?<type>.*)",
                        "Datasource Class": "Seeq - Signal Datasource",
                        "Datasource Name": "Seeq Signal Datasource",
                        'Name': "(?<name>.*)"
                    },
                    "New": {
                        "Type": "${type}",
                        "Datasource Class": "Seeq - Signal Datasource",
                        "Datasource Name": "Seeq Signal Datasource",
                        'Name': "${name}"
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_1.json'), 'w') as f:
            json.dump(datasource_map, f)

        try:
            spy.workbooks.push(analysis, datasource_map_folder=temp)
        except RuntimeError as e:
            assert re.match(r'.*Using overrides.*', str(e), re.DOTALL)
            assert re.match(r'.*RegEx-Based Map 0: Type "StoredSignal" does not match RegEx "Alien"*', str(e),
                            re.DOTALL)
            assert re.match(r'.*RegEx-Based Map 1: No match for search:*', str(e), re.DOTALL)
            assert re.match(r'.*Item\'s ID .* not found:*', str(e), re.DOTALL)
            assert re.match(r'.*formula parameter \$a=.* not found:*', str(e), re.DOTALL)

        datasource_map = {
            "Datasource Class": "Seeq - Signal Datasource",
            "Datasource ID": "default",
            "Datasource Name": "Seeq Signal Datasource",
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "StoredSignal",
                        "Datasource Class": "Seeq - Signal Datasource",
                        "Datasource Name": "Seeq Signal Datasource",
                        'Name': "Wallace and Gromit"
                    },
                    "New": {
                        "Type": "StoredSignal",
                        "Datasource Class": "Time Series CSV Files",
                        "Datasource Name": "Example Data",
                        'Name': "Area A_Temperature"
                    }
                },
                {
                    "Old": {
                        "Type": "StoredSignal",
                        "Datasource Class": "Seeq - Signal Datasource",
                        "Datasource Name": "Seeq Signal Datasource",
                        'Name': "A Stored Signal"
                    },
                    "New": {
                        "Type": "StoredSignal",
                        "Datasource Class": "Time Series CSV Files",
                        "Datasource Name": "Example Data",
                        'Name': "Area *_Temperature"
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_2.json'), 'w') as f:
            json.dump(datasource_map, f)

        try:
            spy.workbooks.push(analysis, datasource_map_folder=temp)
        except RuntimeError as e:
            assert re.match(r'.*Name "A Stored Signal" does not match RegEx "Wallace and Gromit".*', str(e), re.DOTALL)
            assert re.match(r'.*Multiple matches for search:*', str(e), re.DOTALL)


@pytest.mark.system
def test_datasource_map_by_path():
    temperature_signals = spy.search({
        'Datasource ID': 'Example Data',
        'Path': 'Example',
        'Name': 'Temperature'
    })
    workbook = spy.workbooks.Analysis({
        'Name': 'test_datasource_map_by_path'
    })
    worksheet = workbook.worksheet('the one worksheet')

    worksheet.display_items = temperature_signals.sort_values(by='Asset')
    spy.workbooks.push(workbook, path='test_datasource_map_by_path')

    search_df = spy.search({
        'Type': 'Signal',
        'Datasource ID': 'Example Data',
        'Path': 'Example',
        'Name': 'Temperature'
    })

    new_tree_df = search_df.copy()
    new_tree_df = new_tree_df[['ID', 'Type', 'Path', 'Asset', 'Name']]
    new_tree_df['Path'] = 'test_datasource_map_by_path >> ' + search_df['Path']
    new_tree_df['Reference'] = True
    spy.push(metadata=new_tree_df, workbook=workbook.id)

    with tempfile.TemporaryDirectory() as temp:
        example_datasource_map = {
            "Datasource Class": "Time Series CSV Files",
            "Datasource ID": "Example Data",
            "Datasource Name": "Example Data",
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "(?<type>.*)",
                        "Datasource Class": "Time Series CSV Files",
                        "Datasource Name": "Example Data",
                        'Path': "(?<path>Example >> .*)",
                        'Asset': "(?<asset>.*)",
                        'Name': "(?<name>.*)"
                    },
                    "New": {
                        "Type": "${type}",
                        'Path': "test_datasource_map_by_path >> ${path}",
                        'Asset': "${asset}",
                        'Name': "${name}"
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_Time Series CSV Files_Example Data_Example Data.json'), 'w') as f:
            json.dump(example_datasource_map, f)

        sdl_datasource_map = {
            "Datasource Class": "Seeq Data Lab",
            "Datasource ID": "Seeq Data Lab",
            "Datasource Name": "Seeq Data Lab",
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "(?<type>.*)",
                        "Datasource Class": "Seeq Data Lab",
                        "Datasource Name": "Seeq Data Lab",
                        'Data ID': "(?<data_id>.*)"
                    },
                    "New": {
                        "Type": "${type}",
                        "Data ID": "${data_id}"
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_Seeq_Data_Lab.json'), 'w') as f:
            json.dump(sdl_datasource_map, f)

        spy.workbooks.push(workbook, path='test_datasource_map_by_path', datasource_map_folder=temp)

        display_items = spy.search(worksheet.display_items, all_properties=True)

        for _, display_item in display_items.iterrows():
            assert display_item['Datasource Class'] == 'Seeq Data Lab'
            assert display_item['Path'].startswith('test_datasource_map_by_path')


@pytest.mark.system
def test_datasource_map_by_data_id():
    # This test ensures that, if a datasource_map_folder argument is supplied, it will cause existing items to be
    # mapped to new items, which supports the case where you want to pull a workbook and swap to a different datasource.

    workbooks = spy.workbooks.load(_get_full_path_of_export('Worksheet Order (2BBDCFA7-D25C-4278-922E-D99C8DBF6582)'))
    workbooks[0].name = 'Datasource Map Test'
    push_df = spy.workbooks.push(workbooks, refresh=False, label='test_datasource_map_by_data_id')

    push_df.drop(columns=['ID'], inplace=True)
    push_df.rename(columns={'Pushed Workbook ID': 'ID'}, inplace=True)
    push_df['Type'] = 'Workbook'

    workbooks = spy.workbooks.pull(push_df)

    # This map will simply convert the tree-based example signals to their flat-name equivalents
    with tempfile.TemporaryDirectory() as temp:
        datasource_map = {
            "Datasource Class": "Time Series CSV Files",
            "Datasource ID": "Example Data",
            "Datasource Name": "Example Data",
            "Item-Level Map Files": [],
            "RegEx-Based Maps": [
                {
                    "Old": {
                        "Type": "(?<type>.*)",
                        "Datasource Class": "Time Series CSV Files",
                        "Datasource Name": "Example Data",
                        "Data ID": "(?<data_id>.*)"
                    },
                    "New": {
                        "Type": "${type}",
                        "Datasource Class": "Time Series CSV Files",
                        "Datasource Name": "Example Data",
                        # Note that only Name and Description can contain wildcards
                        "Data ID": "[Tag] ${data_id}"
                    }
                }
            ]
        }

        with open(os.path.join(temp, 'Datasource_Map_Time Series CSV Files_Example Data_Example Data.json'), 'w') as f:
            json.dump(datasource_map, f)

        spy.workbooks.push(workbooks, refresh=False, datasource_map_folder=temp)

    workbooks = spy.workbooks.pull(push_df)

    _confirm_flat_tag(workbooks)


@pytest.mark.system
def test_datasource_map_by_file():
    workbooks = spy.workbooks.load(_get_full_path_of_export('Worksheet Order (2BBDCFA7-D25C-4278-922E-D99C8DBF6582)'))
    workbooks[0].name = 'Datasource Map By File Test'

    spy.workbooks.push(workbooks)

    tree_tags = spy.search({
        'Datasource ID': 'Example Data',
        'Path': 'Example',
        'Type': 'Signal'
    })

    flat_tags = spy.search({
        'Datasource ID': 'Example Data',
        'Name': 'Area*',
        'Data ID': '[Tag]*'
    })

    tree_tags['Flat Name'] = tree_tags['Asset'] + '_' + tree_tags['Name']

    tree_tags.drop(columns=['Name'], inplace=True)
    tree_tags.rename(columns={'ID': 'Old ID', 'Flat Name': 'Name'}, inplace=True)
    flat_tags.rename(columns={'ID': 'New ID'}, inplace=True)

    mapped_tags = tree_tags.merge(flat_tags, on='Name')

    with tempfile.TemporaryDirectory() as temp:
        csv_filename = os.path.join(temp, 'example_map.csv')
        mapped_tags.to_csv(csv_filename)

        datasource_map = {
            "Datasource Class": "Time Series CSV Files",
            "Datasource ID": "Example Data",
            "Datasource Name": "Example Data",
            "Item-Level Map Files": [csv_filename],
            "RegEx-Based Maps": []
        }

        with open(os.path.join(temp, 'Datasource_Map_Time Series CSV Files_Example Data_Example Data.json'), 'w') as f:
            json.dump(datasource_map, f)

        spy.workbooks.push(workbooks, datasource_map_folder=temp)

    _confirm_flat_tag(workbooks)


def _confirm_flat_tag(workbooks):
    items_api = ItemsApi(test_common.get_client())
    search_output = items_api.search_items(
        filters=['Name==Area C_Compressor Power'])  # type: ItemSearchPreviewPaginatedListV1
    area_c_compressor_power_id = search_output.items[0].id
    first_worksheet = workbooks[0].worksheets[0]  # type: AnalysisWorksheet
    display_item = first_worksheet.display_items.iloc[0]
    assert display_item['ID'] == area_c_compressor_power_id


@pytest.mark.system
def test_workbook_push_and_refresh():
    workbooks_api = WorkbooksApi(test_common.get_client())
    items_api = ItemsApi(test_common.get_client())

    with pytest.raises(TypeError, match='Workbook may not be instantiated directly, create either Analysis or Topic'):
        Workbook({'Name': 'My First From-Scratch Workbook'})

    workbook = Analysis({'Name': 'My First From-Scratch Workbook'})

    with pytest.raises(TypeError, match='Worksheet may not be instantiated directly, create either AnalysisWorksheet '
                                        'or TopicWorksheet'):
        Worksheet(workbook, {'Name': 'My First From-Scratch Worksheet'})

    worksheet = workbook.worksheet('My First From-Scratch Worksheet')

    sinusoid = CalculatedSignal({
        'Name': 'My First Sinusoid',
        'Formula': 'sinusoid()'
    })

    workbook.add_to_scope(sinusoid)

    worksheet.display_items = [sinusoid]

    first_workbook_id = workbook.id
    first_worksheet_id = worksheet.id
    first_sinusoid_id = sinusoid.id
    spy.workbooks.push(workbook, path='test_workbook_push_and_refresh', refresh=False)

    # Since refresh=False, the IDs will not have changed from the generated IDs on the objects
    assert first_workbook_id == workbook.id
    assert first_worksheet_id == worksheet.id
    assert first_sinusoid_id == sinusoid.id

    # However, the ID that is actually used on the server is different from the ID in the object. (That's why refresh
    # defaults to True-- users can get confused if the IDs are not the same.)
    with pytest.raises(ApiException, match='The item with ID.*could not be found'):
        workbooks_api.get_workbook(id=workbook.id)

    # Now if we push with refresh=True, the IDs will be updated to reflect what the server used for IDs
    spy.workbooks.push(workbook, path='test_workbook_push_and_refresh', refresh=True)
    assert first_workbook_id != workbook.id
    assert first_worksheet_id != worksheet.id
    assert first_sinusoid_id != sinusoid.id

    search_df = spy.workbooks.search({'Path': 'test_workbook_push_and_refresh'})
    assert len(search_df) == 1

    second_workbook_id = workbook.id
    second_worksheet_id = worksheet.id
    second_sinusoid_id = sinusoid.id

    # Because we refreshed the in-memory objects with the correct IDs, we can change names around and it will update
    # the ones we already pushed
    workbook.name = 'My Second From-Scratch Workbook'
    worksheet.name = 'My Second From-Scratch Worksheet'
    sinusoid.name = 'My Second Sinusoid'
    spy.workbooks.push(workbook, path='test_workbook_push_and_refresh')
    assert second_workbook_id == workbook.id
    assert second_worksheet_id == worksheet.id
    assert second_sinusoid_id == sinusoid.id

    search_df = spy.workbooks.search({'Path': 'test_workbook_push_and_refresh'})
    assert len(search_df) == 1

    workbook_output = workbooks_api.get_workbook(id=workbook.id)  # type: WorkbookOutputV1
    assert workbook_output.name == 'My Second From-Scratch Workbook'

    worksheet_output = workbooks_api.get_worksheet(workbook_id=workbook.id,
                                                   worksheet_id=worksheet.id)  # type: WorksheetOutputV1
    assert worksheet_output.name == 'My Second From-Scratch Worksheet'

    search_results = items_api.search_items(filters=['My*Sinusoid'],
                                            scope=workbook.id)  # type: ItemSearchPreviewPaginatedListV1

    assert len(search_results.items) == 1
    assert search_results.items[0].id == sinusoid.id

    item_output = items_api.get_item_and_all_properties(id=sinusoid.id)  # type: ItemOutputV1
    assert item_output.name == 'My Second Sinusoid'

    # Now change it all back so that this test can run successfully twice
    workbook.name = 'My First From-Scratch Workbook'
    worksheet.name = 'My First From-Scratch Worksheet'
    sinusoid.name = 'My First Sinusoid'
    spy.workbooks.push(workbook, path='test_workbook_push_and_refresh')

    search_df = spy.workbooks.search({'Path': 'test_workbook_push_and_refresh'})
    assert len(search_df) == 1


@pytest.mark.system
def test_globals():
    workbooks = spy.workbooks.load(_get_full_path_of_export('Globals (3ACFCBA0-F390-414F-BD9D-4AF93AB631A1)'))
    workbook = workbooks[0]
    global_compressor_high = workbook.item_inventory['2EF5FA09-A221-475D-AF19-5FBDF717E9FE']

    spy.workbooks.push(workbooks, scope_globals_to_workbook=False)

    items_api = ItemsApi(_login.client)
    item_output = items_api.get_item_and_all_properties(id=global_compressor_high.id)  # type: ItemOutputV1
    assert not item_output.scoped_to


@pytest.mark.system
def test_scalar_edit():
    scalars_api = ScalarsApi(test_common.get_client())

    calculated_item_input = ScalarInputV1()
    calculated_item_input.name = 'A Scalar I Will Edit'
    calculated_item_input.formula = '42'
    calculated_item_output = scalars_api.create_calculated_scalar(
        body=calculated_item_input)  # type: CalculatedItemOutputV1

    workbook = spy.workbooks.Analysis('test_scalar_edit')
    worksheet = workbook.worksheet('The Only Worksheet')
    worksheet.display_items = spy.search({'ID': calculated_item_output.id})
    spy.workbooks.push(workbook)

    scalar = workbook.item_inventory[calculated_item_output.id]
    scalar['Formula'] = '43'
    spy.workbooks.push(workbook, scope_globals_to_workbook=False)

    scalar = Item.pull(calculated_item_output.id)
    assert scalar['Formula'] == '43'


@pytest.mark.system
def test_topic_document_archive_and_resurrect():
    topic = spy.workbooks.Topic('test_topic_document_archive_and_resurrect')
    topic.document('My Doc 1')
    spy.workbooks.push(topic)

    # Now clear the worksheets so that My Doc 1 gets archived
    topic.worksheets = list()
    topic.document('My Doc 2')
    spy.workbooks.push(topic)

    # Make sure we can push the topic with My Doc 1 again
    topic.document('My Doc 1')
    spy.workbooks.push(topic)


@pytest.mark.system
def test_push_workbooks_all_fail():
    workbook = Analysis({'Name': 'workbook_that_cant_be_pushed'})
    # We are just testing that the following line does not raise an exception
    push_df = spy.workbooks.push(workbook, errors='catalog')
    assert 'Error' in push_df.at[0, 'Result']
