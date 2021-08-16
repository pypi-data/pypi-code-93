#!/usr/bin/env python

import os
import copy
import time
from urllib.parse import urlparse
import requests
import logging

from nextcodecli.utils import get_logger
from nextcode.credentials import find_aws_credentials

logging.getLogger('botocore').setLevel(logging.WARNING)


def find_job(service, job_id):
    log = get_logger()
    job_info = None
    job_url = None
    session = service.session
    if str(job_id) == 'latest':
        print()
        if not service.current_user:
            log.error("No user in session")
            return None

        user_name = service.current_user['preferred_username']
        resp = session.get(
            session.url_from_endpoint('jobs'),
            json={
                'user_name': user_name,
                'field': ['job_id', 'links'],
                'status': 'ALL',
                'limit': 1,
            },
        )
        resp.raise_for_status()
        jobs = resp.json()['jobs']
        if len(jobs) > 0:
            job_info = jobs[0]
            job_url = job_info['links']['self']
            log.info("Found latest job for %s: %s", user_name, job_url)
        else:
            log.warning("Found no jobs for %s", user_name)
            return None

    else:
        job_id = int(job_id)
        job_endpoint = session.url_from_endpoint('jobs')
        log.debug('job_endpoint=%s, job_id=%s' % (job_endpoint, job_id))
        resp = session.get(job_endpoint, json={'job_id': job_id, 'field': ['job_id', 'links']})
        resp.raise_for_status()
        jobs = resp.json()['jobs']
        if not jobs:
            log.warning("Job '%s' not found" % job_id)
            return None
        job_info = jobs[0]
        job_url = job_info['links']['self']

    fields = []
    # Now get the actual resource
    try:
        resp = session.get(job_url, data={'field': [fields]})
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.error("Error getting job info from %s: %s", job_url, e)
        log.error("Just returning basic job info!")
        return job_info


def download_output_file(folder_name, url):
    log = get_logger()
    url_parts = urlparse(url)
    file_name = url_parts.path.split('/')[-1]
    log.info("Downloading '%s' to %s..." % (file_name, folder_name))
    path = os.path.expanduser(folder_name)
    try:
        os.makedirs(path)
    except Exception:
        pass
    local_filename = os.path.join(path, file_name)
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian
    return local_filename


def post_job(
    session,
    manifest,
    build_source=None,
    build_context=None,
    pipeline_definition=None,
    force_start=False,
    is_test=False,
):
    log = get_logger()

    # ! TODO: Check json
    pipeline_name = manifest['pipeline_name']

    url = session.url_from_endpoint('jobs')
    log.info("Running pipeline '%s' against endpoint '%s'...", pipeline_name, url)
    log.info("Samples: %s" % (", ".join([s['name'] for s in manifest['samples']])))

    # copy most things from the manifest to the post body
    skip_keys = ['samples']
    job_description = copy.deepcopy(manifest)
    for k in skip_keys:
        try:
            del job_description[k]
        except Exception:
            pass

    # if we do not have iam_keys in the job description, assume we have iam_profiles and pull
    # the keys from the user's aws credentials file
    if 'iam_keys' not in job_description:
        iam_keys = []
        for profile_name, profile in manifest['iam_profiles'].items():
            credentials = find_aws_credentials(profile)
            iam_key = {'profile': profile_name}
            iam_key.update(credentials)
            iam_keys.append(iam_key)
        job_description['iam_keys'] = iam_keys
    try:
        del job_description['iam_profiles']
    except KeyError:
        pass

    # allow user to upload etl-pipelines package (!! dev mode)
    if build_source:
        log.info("Using build source %s with context '%s'", build_source, build_context)
        job_description['build_source'] = build_source
        job_description['build_context'] = build_context

    # allow user to override the pipeline definition with local file (!! dev mode)
    if pipeline_definition is not None:
        job_description['pipeline_definition'] = pipeline_definition
    responses = []

    # now go through the samples and post a separate job for each one
    for sample in manifest['samples']:
        sample_name = sample['name']
        if 'input' in sample:
            input_files = sample.get('input')
        # backwards compatibility
        elif 'files' in sample:
            input_files = {'samples': sample['files']}
            log.warning(
                "Backwards compatibility for 'files' in manifest. Please fix your manifest file"
            )
        else:
            raise Exception("Manifest sample does not include necessary 'input' key")
        input_list = []
        for key_name, files in input_files.items():
            input_list.append({'key': key_name, 'files': files})
        this_job = copy.deepcopy(job_description)

        # allow override of all parameters for each sample
        for key in this_job.keys():
            if key in sample:
                val = sample[key]
                if isinstance(val, dict):
                    this_job[key].update(val)
                else:
                    this_job[key] = val

        this_job['sample_name'] = sample_name
        this_job['input'] = input_list
        if is_test:
            this_job['test'] = True

        log.info("Creating job for sample '%s'...", sample_name)
        resp = session.post(url, json=this_job)
        if resp.status_code == requests.codes.created:
            log.info("Success: Job %s has been created", resp.json()['job_id'])
        else:
            log.error("Failure: %s" % resp.text)
        if not is_test and force_start and resp.status_code == requests.codes.created:
            links = session.links(resp.json())
            job_url = links['self']
            instances_url = links['instances']
            log.info("Force job start...")
            instance_resp = session.post(instances_url, json={})
            if not instance_resp.status_code == requests.codes.created:
                log.error("Failed to launch instance: %s" % instance_resp.text)
            resp = session.get(job_url)
        responses.append(resp)
        # do not flood the server
        time.sleep(0.1)
    return responses
