# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


class _DictBased:
    """A base class to enable a class retrieving its properties from a dict."""

    def __init__(self, dct):
        self._dct = dct

    def _get(self, path, default=None):
        return self._dct.get(path, default)

    @property
    def dct(self):
        return self._dct


class ModuleEntity(_DictBased):
    """Module entity.

    Note: We need to get creation info from modulentity instead of directly from module dto.
    """

    @property
    def created_date(self):
        """The date the module was created."""
        return self._get('createdDate')

    @property
    def last_modified_date(self):
        """The date the module last modified."""
        return self._get('lastModifiedDate')


class CreationContext(_DictBased):
    """Creation context with user and time as well as modification time."""

    @property
    def created_date(self):
        """The date the module was created."""
        module_entity = self._get('moduleEntity')
        return ModuleEntity(module_entity).created_date

    @property
    def last_modified_date(self):
        """The date the module last modified."""
        module_entity = self._get('moduleEntity')
        return ModuleEntity(module_entity).last_modified_date

    @property
    def created_by(self):
        """The user/app name who created the module."""
        return self._get('registeredBy')


class ComponentVersion(_DictBased):
    """Component version.

    Note: This class and AssetVersion should be 2 different concepts.
    This class is just used to get version from module dto dict.
    """

    @property
    def version(self):
        return self._get('version')

    @property
    def version_id(self):
        return self._get('moduleVersionId')


class RegistrationContext(_DictBased):
    """Registration context which includes registration metadata from module dto dict."""
    SOURCE_NAMES = {
        1: 'Local files',
        2: 'Github repo',
        4: 'Azure DevOps artifacts',
    }
    UNKNOWN_SOURCE_NAME = 'Unknown'

    SCOPE_NAMES = {
        1: 'Global',
        2: 'Workspace',
        3: 'Anonymous',
    }
    UNKNOWN_SCOPE_NAME = 'Unknown'

    COMPONENT_STATUS_NAMES = {0: 'Active', 1: 'Deprecated', 2: 'Archived'}
    MODULE_STATUS_NAMES = {0: 'Active', 1: 'Deprecated', 2: 'Disabled'}
    UNKNOWN_STATUS_NAME = 'Unknown'

    @property
    def id(self):
        """The id of the component."""
        return self._get('moduleVersionId')

    @property
    def default_version(self):
        """The default version of the component."""
        return self._get('defaultVersion')

    @property
    def versions(self):
        """The list of history versions of the component."""
        versions = self._get('versions')
        return [ComponentVersion(v).version for v in versions] if versions else []

    @property
    def version_ids(self):
        """The list of history version Ids of the component."""
        versions = self._get('versions')
        return [ComponentVersion(v).version_id for v in versions] if versions else []

    @property
    def all_versions(self):
        """Return all versions of component and mark default version in them."""

        def iter_versions():
            for v in self.versions:
                yield v + ' (Default)' if v == self.default_version else v

        return ', '.join(iter_versions())

    @property
    def source(self):
        """The source of the component."""
        raw_value = self._get_int_raw_value(self._get('moduleSourceType'))
        return self.SOURCE_NAMES.get(raw_value, self.UNKNOWN_SOURCE_NAME)

    @property
    def shared_scope(self):
        """The scope of the component."""
        raw_value = self._get_int_raw_value(self._get('moduleScope'))
        return self.SCOPE_NAMES.get(raw_value, self.UNKNOWN_SCOPE_NAME)

    @property
    def status_code(self):
        """The status of the component."""
        code = self._get_int_raw_value(self._get('entityStatus'))
        # NOTE: we only return status from dto, because module/component has different status names
        return code

    @property
    def yaml_link(self):
        """The relative link of the component spec path in the snapshot."""
        return self._get('yamlLink')

    @staticmethod
    def _get_int_raw_value(value):
        """Return an int value if the value is string value '1', '2', '3',
        this is used because some keys are generated as a string instead of an int.
        """
        return None if value is None else int(value)
