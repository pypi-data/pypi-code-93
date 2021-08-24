# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CESNET.
#
# NR datasets repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Record state transition handler functions."""
import traceback
from typing import List

from flask import make_response, jsonify
from flask_restful import abort
from invenio_db import db
from invenio_pidstore.models import PersistentIdentifier
from oarepo_records_draft import current_drafts
from oarepo_records_draft.exceptions import InvalidRecordException
from oarepo_records_draft.ext import PublishedDraftRecordPair

from nr_datasets.record import DraftDatasetRecord, PublishedDatasetRecord
from .constants import DRAFT_DATASET_PID_TYPE, PUBLISHED_DATASET_PID_TYPE


def handle_request_approval(sender, **kwargs):
    if isinstance(sender, DraftDatasetRecord):
        print('request draft dataset approval', sender)
        # TODO: send mail notification to community curators


def handle_request_changes(sender, **kwargs):
    if isinstance(sender, DraftDatasetRecord):
        print('requesting changes for draft dataset', sender)
        # TODO: send mail notification to record owner


def handle_approve(sender, force=False, **kwargs):
    if isinstance(sender, DraftDatasetRecord):
        print('approving draft dataset', sender)

        # TODO: update references in all referencing articles

        record_pid = PersistentIdentifier.query. \
            filter_by(pid_type=DRAFT_DATASET_PID_TYPE, object_uuid=sender.id).one()
        try:
            published = \
                current_drafts.publish(sender, record_pid, require_valid=not force)
            db.session.commit()

            return {
                'url': published[0].published_context.record.canonical_url,
                'pid_type': published[0].published_context.record_pid.pid_type,
                'pid': published[0].published_context.record_pid.pid_value,
            }
        except InvalidRecordException as e:
            traceback.print_exc()
            abort(make_response(jsonify({
                "status": "error",
                "message": e.message,
                "errors": e.errors
            }), 400))
        except:
            traceback.print_exc()
            raise


def handle_revert_approval(sender, force=False, **kwargs):
    if isinstance(sender, PublishedDatasetRecord):
        print('reverting dataset approval', sender)
        # TODO: update references in all referencing articles
        # TODO: send mail notification to interested people
        record_pid = PersistentIdentifier.query. \
            filter_by(pid_type=PUBLISHED_DATASET_PID_TYPE, object_uuid=sender.id).one()
        try:
            unpublished: List[PublishedDraftRecordPair] = \
                current_drafts.unpublish(sender, record_pid)
            db.session.commit()
            return {
                'url': unpublished[0].draft_context.record.canonical_url,
                'pid_type': unpublished[0].draft_context.record_pid.pid_type,
                'pid': unpublished[0].draft_context.record_pid.pid_value,
            }
        except:
            traceback.print_exc()
            raise


def handle_publish(sender, **kwargs):
    if isinstance(sender, PublishedDatasetRecord):
        print('making dataset public', sender)
        # TODO: send mail notification to interested people


def handle_unpublish(sender, **kwargs):
    if isinstance(sender, PublishedDatasetRecord):
        print('making dataset private', sender)
        # TODO: send mail notification to interested people


def handle_delete_draft(sender, **kwargs):
    if isinstance(sender, DraftDatasetRecord):
        print('deleting draft dataset', sender)
        sender.delete()
        record_pid = PersistentIdentifier.query. \
            filter_by(pid_type=DRAFT_DATASET_PID_TYPE, object_uuid=sender.id).one()
        record_pid.delete()
        db.session.commit()

        # TODO: fix indexer for record (seems to always contact localhost:9200)
        indexer = current_drafts.indexer_for_record(sender)
        indexer.delete(sender, refresh=True)

        return {
            'status': 'ok'
        }
