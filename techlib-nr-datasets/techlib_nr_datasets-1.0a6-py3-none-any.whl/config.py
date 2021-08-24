# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CESNET.
#
# NR datasets repository is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Default configuration."""

from __future__ import absolute_import, print_function

from functools import partial

from elasticsearch_dsl.query import Bool, Q
from invenio_records_rest.facets import terms_filter
from invenio_records_rest.utils import allow_all, deny_all
from nr_common.links import nr_links_factory
from nr_common.search import community_search_factory
from nr_generic.config import FACETS, CURATOR_FACETS, CURATOR_FILTERS, FILTERS
from oarepo_communities.links import community_record_links_factory
from oarepo_multilingual import language_aware_text_term_facet, language_aware_text_terms_filter
from oarepo_records_draft import DRAFT_IMPORTANT_FILTERS
from oarepo_records_draft.rest import DRAFT_IMPORTANT_FACETS
from oarepo_taxonomies.serializers import taxonomy_enabled_search
from oarepo_ui.facets import translate_facets, term_facet, nested_facet, translate_facet
from oarepo_ui.filters import nested_filter

from oarepo_communities.constants import STATE_PUBLISHED, STATE_EDITING, STATE_APPROVED, STATE_PENDING_APPROVAL, \
    STATE_DELETED
from nr_datasets.constants import PUBLISHED_DATASET_PID_TYPE, PUBLISHED_DATASET_RECORD, \
    published_index_name, \
    DRAFT_DATASET_PID_TYPE, DRAFT_DATASET_RECORD, ALL_DATASET_PID_TYPE, ALL_DATASET_RECORD, \
    all_datasets_index_name
from nr_datasets.record import draft_index_name
from nr_datasets.search import DatasetRecordSearch

_ = lambda x: x

RECORDS_DRAFT_ENDPOINTS = {
    'datasets-community': {
        'draft': 'draft-datasets-community',
        'pid_type': PUBLISHED_DATASET_PID_TYPE,
        'pid_minter': 'nr_datasets',
        'pid_fetcher': 'nr_datasets',
        'default_endpoint_prefix': True,
        'max_result_window': 500000,
        'record_class': PUBLISHED_DATASET_RECORD,
        'search_index': published_index_name,
        'search_factory_imp': taxonomy_enabled_search(community_search_factory,
                                                      taxonomy_aggs=[],
                                                      fallback_language="cs"),

        'list_route': '/<community_id>/datasets/',
        'item_route': f'/<commpid({PUBLISHED_DATASET_PID_TYPE},model="datasets",record_class="'
                      f'{PUBLISHED_DATASET_RECORD}"):pid_value>',

        'publish_permission_factory_imp':
            'nr_common.permissions.publish_draft_object_permission_impl',
        'unpublish_permission_factory_imp':
            'nr_common.permissions.unpublish_draft_object_permission_impl',
        'edit_permission_factory_imp': 'nr_common.permissions.update_object_permission_impl',
        'list_permission_factory_imp': allow_all,
        'read_permission_factory_imp': allow_all,
        'create_permission_factory_imp': deny_all,
        'update_permission_factory_imp': deny_all,
        'delete_permission_factory_imp': deny_all,
        'default_media_type': 'application/json',
        'links_factory_imp': partial(community_record_links_factory,
                                     original_links_factory=nr_links_factory),
        'search_class': DatasetRecordSearch,
        # 'indexer_class': CommitingRecordIndexer,
        'files': dict(
            # Who can upload attachments to a draft dataset record
            put_file_factory=deny_all,
            # Who can download attachments from a draft dataset record
            get_file_factory=allow_all,
            # Who can delete attachments from a draft dataset record
            delete_file_factory=deny_all
        )

    },
    'draft-datasets-community': {
        'pid_type': DRAFT_DATASET_PID_TYPE,
        'record_class': DRAFT_DATASET_RECORD,

        'list_route': '/<community_id>/datasets/draft/',
        'item_route': f'/<commpid({DRAFT_DATASET_PID_TYPE},model="datasets/draft",record_cla'
                      f'ss="{DRAFT_DATASET_RECORD}"):pid_value>',
        'search_index': draft_index_name,
        'links_factory_imp': partial(community_record_links_factory,
                                     original_links_factory=nr_links_factory),
        'search_factory_imp': community_search_factory,
        'search_class': DatasetRecordSearch,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },
        'record_serializers': {
            'application/json': 'oarepo_validate:json_response',
        },

        'create_permission_factory_imp':
            'nr_common.permissions.create_draft_object_permission_impl',
        'update_permission_factory_imp':
            'nr_common.permissions.update_draft_object_permission_impl',
        'read_permission_factory_imp': 'nr_common.permissions.read_draft_object_permission_impl',
        'delete_permission_factory_imp':
            'nr_common.permissions.delete_draft_object_permission_impl',
        'list_permission_factory_imp': 'nr_common.permissions.list_draft_object_permission_impl',
        'record_loaders': {
            'application/json': 'oarepo_validate.json_files_loader',
            'application/json-patch+json': 'oarepo_validate.json_loader'
        },
        'files': dict(
            put_file_factory='nr_common.permissions.put_draft_file_permission_impl',
            get_file_factory='nr_common.permissions.get_draft_file_permission_impl',
            delete_file_factory='nr_common.permissions.delete_draft_file_permission_impl'
        )

    },
    'datasets': {
        'draft': 'draft-datasets',
        'pid_type': PUBLISHED_DATASET_PID_TYPE + '-datasets',
        'pid_minter': 'nr_datasets',
        'pid_fetcher': 'nr_datasets',
        'default_endpoint_prefix': True,
        'max_result_window': 500000,
        'record_class': ALL_DATASET_RECORD,
        'search_index': published_index_name,

        'list_route': '/datasets/',
        'item_route': f'/not-really-used',
        'publish_permission_factory_imp': deny_all,
        'unpublish_permission_factory_imp': deny_all,
        'edit_permission_factory_imp': deny_all,
        'list_permission_factory_imp': allow_all,
        'read_permission_factory_imp': allow_all,
        'create_permission_factory_imp': deny_all,
        'update_permission_factory_imp': deny_all,
        'delete_permission_factory_imp': deny_all,
        'default_media_type': 'application/json',
        'links_factory_imp': partial(community_record_links_factory,
                                     original_links_factory=nr_links_factory),
        'search_class': DatasetRecordSearch,
        # 'indexer_class': CommitingRecordIndexer,
        'files': dict(
            # Who can upload attachments to a draft dataset record
            put_file_factory=deny_all,
            # Who can download attachments from a draft dataset record
            get_file_factory=allow_all,
            # Who can delete attachments from a draft dataset record
            delete_file_factory=deny_all
        )
    },
    'draft-datasets': {
        'pid_type': DRAFT_DATASET_PID_TYPE + '-draft-datasets',
        'record_class': ALL_DATASET_RECORD,

        'list_route': '/datasets/draft/',
        'item_route': f'/not-really-used',
        'search_index': draft_index_name,
        'links_factory_imp': partial(community_record_links_factory,
                                     original_links_factory=nr_links_factory),
        'search_class': DatasetRecordSearch,
        'search_serializers': {
            'application/json': 'oarepo_validate:json_search',
        },
        'record_serializers': {
            'application/json': 'oarepo_validate:json_response',
        },

        'create_permission_factory_imp': deny_all,
        'update_permission_factory_imp': deny_all,
        'read_permission_factory_imp': 'nr_common.permissions.read_draft_object_permission_impl',
        'delete_permission_factory_imp': deny_all,
        'list_permission_factory_imp': 'nr_common.permissions.list_draft_object_permission_impl',
        'files': dict(
            put_file_factory=deny_all,
            get_file_factory='nr_common.permissions.get_draft_file_permission_impl',
            delete_file_factory=deny_all
        )
    }
}

RECORDS_REST_ENDPOINTS = {
    'all-datasets': dict(
        pid_type=ALL_DATASET_PID_TYPE,
        pid_minter='nr_all',
        pid_fetcher='nr_all',
        default_endpoint_prefix=True,
        record_class=ALL_DATASET_RECORD,
        search_class=DatasetRecordSearch,
        search_index=all_datasets_index_name,
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        list_route='/datasets/all/',
        links_factory_imp=partial(community_record_links_factory,
                                  original_links_factory=nr_links_factory),
        default_media_type='application/json',
        max_result_window=10000,
        # not used really
        item_route=f'/datasets/'
                   f'/not-used-but-must-be-present',
        list_permission_factory_imp='nr_common.permissions.list_all_object_permission_impl',
        create_permission_factory_imp=deny_all,
        delete_permission_factory_imp=deny_all,
        update_permission_factory_imp=deny_all,
        read_permission_factory_imp=deny_all,
        record_serializers={
            'application/json': 'oarepo_validate:json_response',
        },
        use_options_view=False
    ),
    'community-datasets': dict(
        pid_type=ALL_DATASET_PID_TYPE + '-community-all',
        pid_minter='nr_all',
        pid_fetcher='nr_all',
        default_endpoint_prefix=True,
        record_class=ALL_DATASET_RECORD,
        search_class=DatasetRecordSearch,
        search_index=all_datasets_index_name,
        search_factory_imp=community_search_factory,
        search_serializers={
            'application/json': 'oarepo_validate:json_search',
        },
        list_route='/<community_id>/datasets/all/',
        links_factory_imp=partial(community_record_links_factory,
                                  original_links_factory=nr_links_factory),
        default_media_type='application/json',
        max_result_window=10000,
        # not used really
        item_route=f'/dataset/'
                   f'/not-used-but-must-be-present',
        list_permission_factory_imp='nr_common.permissions.list_all_object_permission_impl',
        create_permission_factory_imp=deny_all,
        delete_permission_factory_imp=deny_all,
        update_permission_factory_imp=deny_all,
        read_permission_factory_imp=deny_all,
        record_serializers={
            'application/json': 'oarepo_validate:json_response',
        },
        use_options_view=False
    )
}


def state_terms_filter(field):
    def inner(values):
        if 'filling' in values:
            return Bool(should=[
                Q('terms', **{field: values}),
                Bool(
                    must_not=[
                        Q('exists', field='state')
                    ]
                )
            ], minimum_should_match=1)
        else:
            return Q('terms', **{field: values})

    return inner


DATASETS_FILTERS = {
    _('state'): state_terms_filter('state'),
    _('keywords'): terms_filter('keywords'),
    _('languages'): nested_filter('languages', language_aware_text_terms_filter('languages.title')),
    _('creators'): nested_filter('creators.person_or_org', terms_filter('creators.person_or_org.name')),
    _('affiliations'): nested_filter('creators.affiliations', terms_filter('creators.affiliations.name')),
    _('rights'): nested_filter('rights', language_aware_text_terms_filter('rights.title')),
}

DATASETS_FACETS = {
    'state': translate_facet(term_facet('state', missing=STATE_EDITING), possible_values=[
        _(STATE_EDITING),
        _(STATE_PENDING_APPROVAL),
        _(STATE_APPROVED),
        _(STATE_PUBLISHED),
        _(STATE_DELETED)
    ]),
    'languages': nested_facet('languages', language_aware_text_term_facet('languages.title')),
    'keywords': term_facet('keywords'),
    'creators': nested_facet('creators.person_or_org', term_facet('creators.person_or_org.name')),
    'affiliations': nested_facet('creators.affiliations', term_facet('creators.affiliations.name')),
    'rights': nested_facet('rights', language_aware_text_term_facet('rights.title')),
}

RECORDS_REST_FACETS = {
    draft_index_name: {
        "aggs": translate_facets(
            {**DATASETS_FACETS, **FACETS, **CURATOR_FACETS, **DRAFT_IMPORTANT_FACETS},
            label='{facet_key}',
            value='{value_key}'),
        "filters": {**DATASETS_FILTERS, **FILTERS, **CURATOR_FILTERS, **DRAFT_IMPORTANT_FILTERS}
    },
    all_datasets_index_name: {
        "aggs": translate_facets(
            {**DATASETS_FACETS, **FACETS, **CURATOR_FACETS, **DRAFT_IMPORTANT_FACETS},
            label='{facet_key}',
            value='{value_key}'),
        "filters": {**DATASETS_FILTERS, **FILTERS, **CURATOR_FILTERS, **DRAFT_IMPORTANT_FILTERS}
    },
}

RECORDS_REST_SORT_OPTIONS = {
    draft_index_name: {
        'alphabetical': {
            'title': 'alphabetical',
            'fields': [
                'title.cs.raw'
            ],
            'default_order': 'asc',
            'order': 1
        },
        'best_match': {
            'title': 'Best match',
            'fields': ['_score'],
            'default_order': 'desc',
            'order': 1,
        }
    }
}

RECORDS_REST_DEFAULT_SORT = {
    draft_index_name: {
        'query': 'best_match',
        'noquery': 'best_match'
    }
}
