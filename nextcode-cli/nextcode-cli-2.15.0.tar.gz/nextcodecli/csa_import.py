#!/usr/bin/env python

import os
import sys
import pprint
import nextcode
from nextcodecli.utils import abort
from click import echo, secho

WARN_MSG = "Mismatched %d columns in line %d, but %s in header"


class TsvDict(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def get_item(self, key, default):
        value = self.get(key, default)
        if value == '':
            value = default

        return value


def parse(file_name):
    with open(file_name, 'r') as f:
        lines = f.readlines()

    samples = {}

    if len(lines) == 0:
        return samples

    headerline = lines[0]

    # Get an array of all the column names in lowercase to avoid
    # case sensitivity issues
    colnames = headerline.rstrip("\n").lower().split("\t")
    for line_num, line in enumerate(lines[1:]):
        parts = line.rstrip("\n").split("\t")
        dct = TsvDict()
        if len(parts) != len(colnames):
            exit_msg = WARN_MSG % (len(parts), line_num + 2, len(colnames))
            raise ValueError(exit_msg)
        else:
            dct = TsvDict(zip(colnames, parts))
            if dct['#sampleid'] not in samples:
                sample = {
                    'subject_id': dct.get_item('subjectid', None),
                    'gender': dct.get_item('gender', None),
                    'product': dct.get_item('product', None),
                    'product_version': dct.get_item('productversion', None),
                    'study_id': dct.get_item('studyid', None),
                    'study_role': dct.get_item('studyrole', None),
                    'affected': dct.get_item('affected', None),
                    'sample_tags': dct.get_item('sampletags', None),
                    'files': [],
                }
                samples[dct['#sampleid']] = sample

            file = {
                'platform': dct.get_item('platform', None),
                'file_type': dct.get_item('filetype', None),
                'compression': dct.get_item('compression', None),
                'data_type': dct.get_item('datatype', None),
                'read_no': dct.get_item('readno', None),
                'part_no': dct.get_item('partno', None),
                'file_name': dct.get_item('filename', None),
                'path': dct.get_item('path', None),
                'md5': dct.get_item('md5', None),
                'file_tags': dct.get_item('filetags', {}),
            }

            samples[dct['#sampleid']]['files'].append(file)

    return samples


def is_remote(path):
    parts = path.split('://')
    return len(parts) > 1


def create_sample_data(
    sample, sample_id, subject_id, org_key, project_name, skip_processing_state=False
):
    sample_data = {
        'extid': sample_id,
        'sample_data_type': sample.get('product'),
        'sample_data_type_version': sample.get('product_version'),
        'initial_study': {
            'extid': sample.get('study_id'),
            'participant_kind': sample.get('study_role'),
            'affected': sample.get('affected'),
        },
        'subject': {
            'extid': subject_id,
            'gender': sample.get('gender'),
            'organization_key': org_key,
            'initial_project_key': project_name,
        },
        'tags': sample.get('sampletags', {}),
        'sample_data_files': [],
    }

    if not skip_processing_state:
        sample_data['processing_state'] = 'uploaded'
    return sample_data


def create_file_data(file):
    file_path = file['path']
    if is_remote(file_path):
        full_path = file_path
    else:
        full_path = os.path.abspath(os.path.expanduser(file_path))

    file_tags = file.get('file_tags', {})
    tags = dict(
        {
            'filetype': file['file_type'],
            'platform': file['platform'],
            'datatype': file['data_type'],
            'read_no': file['read_no'],
            'part_no': file['part_no'],
        },
        **file_tags,
    )

    file_data = {
        'file_name': file['file_name'],
        'full_path': full_path,
        'platform': file['platform'],
        'sample_type': file['data_type'],
        'file_type': file['file_type'],
        'read_no': file['read_no'],
        'part_no': file['part_no'],
        'md5': file['md5'],
        'tags': tags,
    }
    return file_data


def process_sample(session, params):
    sample = params.get('sample', None)
    org_key = params.get('org_key', None)
    sample_id = params.get('sample_id', None)
    subject_id = params.get('subject_id', None)
    project_name = params.get('project_name', None)
    skip_processing_state = params.get('skip_processing_state', False)
    sample_data = create_sample_data(
        sample, sample_id, subject_id, org_key, project_name, skip_processing_state
    )

    for file in sample.get('files'):
        file_data = create_file_data(file)
        sample_data['sample_data_files'].append(file_data)

    try:
        result = session.import_sample(sample_data)
        echo('%s imported successfully to %s' % (sample_id, project_name))
    except nextcode.exceptions.CSAError as ex:
        secho(f"Error occurred when importing sample '{sample_id}'", fg="red")
        abort(ex)
    return result
