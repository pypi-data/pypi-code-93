from typing import List

from seeq.sdk import *

from seeq.spy.workbooks._item import Item
from seeq.spy.workbooks._user import ItemWithOwnerAndAcl

from seeq.spy import _common
from seeq.spy import _login

SHARED = '__Shared__'
CORPORATE = '__Corporate__'
ALL = '__All__'
USERS = '__Users__'
MY_FOLDER = '__My_Folder__'

SYNTHETIC_FOLDERS = [SHARED, CORPORATE, ALL, USERS]


def massage_ancestors(item: Item):
    if not _login.corporate_folder:
        return

    if len(item.definition['Ancestors']) > 0 and item.definition['Ancestors'][0] == _login.corporate_folder.id:
        # Why replace the Corporate folder ID with the CORPORATE string token? The user doesn't want to have to
        # deal with the ID of the corporate folder, especially when importing/exporting workbooks from one server to
        # another.
        item.definition['Ancestors'][0] = CORPORATE


class Folder(ItemWithOwnerAndAcl):
    def _pull(self, item_id):
        folders_api = FoldersApi(_login.client)
        folder_output = folders_api.get_folder(folder_id=item_id)  # type: FolderOutputV1
        self._pull_owner_and_acl(folder_output.owner)
        self._pull_ancestors(folder_output.ancestors)
        self.provenance = Item.PULL

    def _pull_ancestors(self, ancestors: List[ItemPreviewV1]):
        super()._pull_ancestors(ancestors)
        massage_ancestors(self)

    def _find_by_name(self, folder_id):
        folders_api = FoldersApi(_login.client)

        if folder_id and folder_id != _common.PATH_ROOT:
            folders = folders_api.get_folders(filter='owner',
                                              folder_id=folder_id,
                                              limit=10000)  # type: FolderOutputListV1
        else:
            folders = folders_api.get_folders(filter='owner',
                                              limit=10000)  # type: FolderOutputListV1

        content_dict = {content.name.lower(): content for content in folders.content}
        if self.name.lower() in content_dict and content_dict[self.name.lower()].type == 'Folder':
            return content_dict[self.name.lower()]

        return None

    def push(self, parent_folder_id, datasource_maps, datasource_output, item_map, *, owner=None, label=None,
             access_control=None):
        items_api = ItemsApi(_login.client)
        folders_api = FoldersApi(_login.client)
        folder_item = self.find_me(label, datasource_output)

        if folder_item is None and self.provenance == Item.CONSTRUCTOR:
            folder_item = self._find_by_name(parent_folder_id)

        if not folder_item:
            folder_input = FolderInputV1()
            folder_input.name = self['Name']
            if 'Description' in self:
                folder_input.description = self['Description']
            folder_input.owner_id = self.decide_owner(datasource_maps, item_map, owner=owner)
            folder_input.parent_folder_id = parent_folder_id if parent_folder_id != _common.PATH_ROOT else None

            folder_output = folders_api.create_folder(body=folder_input)

            items_api.set_properties(id=folder_output.id, body=[
                ScalarPropertyV1(name='Datasource Class', value=datasource_output.datasource_class),
                ScalarPropertyV1(name='Datasource ID', value=datasource_output.datasource_id),
                ScalarPropertyV1(name='Data ID', value=self._construct_data_id(label))])
        else:
            folder_output = folders_api.get_folder(folder_id=folder_item.id)  # type: FolderOutputV1

            props = [ScalarPropertyV1(name='Name', value=self['Name'])]
            if 'Description' in self:
                props.append(ScalarPropertyV1(name='Description', value=self['Description']))

            # If the folder happens to be archived, un-archive it. If you're pushing a new copy it seems likely
            # you're intending to revive it.
            props.append(ScalarPropertyV1(name='Archived', value=False))

            items_api.set_properties(id=folder_output.id, body=props)

            owner_id = self.decide_owner(
                datasource_maps, item_map, owner=owner, current_owner_id=folder_output.owner.id)

            self._push_owner_and_location(folder_output, owner_id, parent_folder_id)

        item_map[self.id.upper()] = folder_output.id.upper()

        if access_control:
            self._push_acl(folder_output.id, datasource_maps, item_map, access_control)

        return folder_output
