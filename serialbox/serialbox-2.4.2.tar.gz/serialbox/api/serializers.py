'''
    Copyright 2018 SerialLab, CORP

    This file is part of SerialBox.

    SerialBox is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SerialBox is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with SerialBox.  If not, see <http://www.gnu.org/licenses/>.
'''
import importlib

import six
from django.apps import apps
from django.utils.translation import gettext as _
from rest_framework import serializers

from quartet_capture.models import Rule
from serialbox import models
from serialbox.api import errors


class RegionSerializer(serializers.ModelSerializer):
    '''
    Adds machine_name relation to the serialized Region for pools and also
    excludes the numeric primary key since it is meaningless for clients.
    '''
    pool = serializers.SlugRelatedField(slug_field='machine_name',
                                        queryset=models.Pool.objects.all())


class SequentialRegionSerializer(RegionSerializer):
    '''
    Specifies the model...excludes the id...
    '''

    class Meta(object):
        model = models.SequentialRegion
        exclude = ('id',)


class SequentialRegionHyperlinkedSerializer(SequentialRegionSerializer):
    '''
    Adds URL relation to the serialized Region for pools and also
    excludes the primary key since it is meaningless for clients.
    '''
    pool = serializers.HyperlinkedRelatedField(view_name='pool-detail',
                                               read_only=True,
                                               lookup_field='machine_name')


class PoolSerializerMeta(serializers.SerializerMetaclass):

    @classmethod
    def _inspect_installed_apps(cls, field_dict, attrs):
        '''
        Will go through each app and look for pool_slug_fields and
        pool_hyperlink_fields defined on each app instance.
        '''
        confs = apps.get_app_configs()
        # this gets the app_field_mapping from the current class
        # attributes.  This value is how the meta class knows what
        # to look for on any included apps modules to find new serializer
        # fields dynamically.
        attr = attrs.get('app_field_mapping', '')
        for conf in confs:
            if hasattr(conf, attr):
                fields = getattr(conf, attr)
                for key, value in fields.items():
                    try:
                        clsname = value
                        module_name, class_name = clsname.rsplit(".", 1)
                        somemodule = importlib.import_module(module_name)
                        field = getattr(somemodule, class_name)
                        field_dict[key] = field
                    except (ImportError, AttributeError):
                        raise errors.PoolSerializerFieldConfigurationError(
                            _('The app field mapping for application %s is '
                              'incorrect.  The value %s could not be translated '
                              'into a valid Field.  Check '
                              'the applications apps.py '
                              'module and make sure this value is correct.'
                              % (conf, clsname))
                        )

    @classmethod
    def _get_declared_fields(cls, bases, attrs):
        ret = super(PoolSerializerMeta, cls)._get_declared_fields(bases, attrs)
        cls._inspect_installed_apps(ret, attrs)
        return ret


class PoolDetailSerializer(six.with_metaclass(PoolSerializerMeta,
                                              serializers.ModelSerializer)):
    '''
    Returns a full, detailed sequential region
    '''
    app_field_mapping = 'pool_slug_fields'
    sequential_region_set = SequentialRegionSerializer(
        many=True,
        read_only=True
    )

    class Meta(object):
        model = models.Pool
        fields = '__all__'


class PoolSerializer(serializers.ModelSerializer):
    '''
    Adds URL relation to the serialized Region for pools and also
    excludes the primary key since it is meaningless for clients.
    '''
    app_field_mapping = 'pool_slug_fields'

    sequentialregion_set = serializers.SlugRelatedField(
        many=True,
        queryset=models.SequentialRegion.objects.all(),
        slug_field='machine_name',
        required=False
    )

    class Meta(object):
        model = models.Pool
        fields = '__all__'


class PoolModelSerializer(six.with_metaclass(PoolSerializerMeta,
                                        serializers.ModelSerializer)):
    '''
    Adds URL relation to the serialized Region for pools and also
    excludes the primary key since it is meaningless for clients.
    '''
    app_field_mapping = 'pool_slug_fields'

    sequentialregion_set = serializers.SlugRelatedField(
        many=True,
        queryset=models.SequentialRegion.objects.all(),
        slug_field='machine_name',
        required=False
    )

    class Meta(object):
        model = models.Pool
        fields = '__all__'

class PoolHyperlinkedSerializer(six.with_metaclass(PoolSerializerMeta,
                                                   PoolSerializer)):
    '''
    Adds URL relation to the serialized Region for pools and also
    excludes the primary key since it is meaningless for clients.
    '''
    app_field_mapping = 'pool_hyperlink_fields'
    sequentialregion_set = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='sequential-region-detail',
        lookup_field='machine_name',
    )

class ResponseRuleSerializer(serializers.ModelSerializer):
    '''
    Default serializer for the ResponseRule model.
    '''
    pool = serializers.PrimaryKeyRelatedField(queryset=models.Pool.objects.all())
    rule = serializers.PrimaryKeyRelatedField(queryset=Rule.objects.all())
    class Meta:
        model = models.ResponseRule
        fields = '__all__'


class ResponseSerializer(serializers.ModelSerializer):
    '''
    A response serializer for handling the return from a call to the Pool
    Request API.
    '''
    numbers = serializers.CharField(source='get_number_list')

    class Meta(object):
        model = models.Response
        read_only_fields = ['numbers']
        exclude = (
            'id',
            'created_date',
            'modified_date',
            'pool',
            'remote_host')
