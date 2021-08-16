from uuid import UUID

from datalogue.clients._http import _HttpClient, List, Union, HttpMethod, Optional
from datalogue.errors import DtlError
from datalogue.models.permission import (
    Permission,
    SharePermission,
    ObjectType,
    UnsharePermission,
)
from datalogue.models.scope_level import Scope
from datalogue.models.tag import Tag
from datalogue.dtl_utils import _parse_list


class _TagClient:
    """
    Client to interact with the Tags
    """

    def __init__(self, http_client: _HttpClient):
        self.http_client = http_client
        self.service_uri = "/scout"

    def create(self, tag: Tag) -> Union[DtlError, List[Tag]]:
        """
        Creates a tag
        :param tag: A Tag object to create
        :return: Returns created Tag object if successful, or DtlError if failed
        """
        payload = {"name": tag.name}
        res = self.http_client.make_authed_request(self.service_uri + "/tags", HttpMethod.POST, [payload])

        if isinstance(res, DtlError):
            return res

        return _parse_list(Tag._from_payload)(res)[0]

    def update(self, old_name: str, name: Optional[str]) -> Union[DtlError, Tag]:
        """
          Updates a tag

          :param id: id of the tag to be updated
          :param name: the updated name to be applied
          :return: Returns Tag object if successful, or DtlError if failed
        """
        payload = {}
        if name is not None:
            payload["name"] = name

        searched_tag_rsp = self.search(old_name)

        if isinstance(searched_tag_rsp, DtlError):
            return searched_tag_rsp

        res = self.http_client.make_authed_request(
            self.service_uri + f"/tags/{searched_tag_rsp.id}", HttpMethod.PUT, payload
        )

        if isinstance(res, DtlError):
            return res

        return Tag._from_payload(res)

    def get(self, name: str) -> Union[DtlError, Tag]:
        """
            Retrieve a tag locally by its id.

            :param name: the name of the tag to be retrieved locally
            :return: the tag if successful, or a DtlError if failed
        """
        searched_tag_rsp = self.search(name)

        if isinstance(searched_tag_rsp, DtlError):
            return searched_tag_rsp

        res = self.http_client.make_authed_request(self.service_uri + f"/tags/{searched_tag_rsp.id}", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return Tag._from_payload(res)

    def search(self, name: str) -> Union[DtlError, Tag]:
        """
            Search a tag locally by its name.

            :param name: the name of the tag to be searched locally
            :return: the tag if successful, or a DtlError if failed
        """
        res = self.http_client.make_authed_request(self.service_uri + f"/tags/{name}/search", HttpMethod.GET)

        if isinstance(res, DtlError):
            return res

        return Tag._from_payload(res)

    def delete(self, name: str) -> Union[DtlError, bool]:
        """
            Delete a tag.

            :param name: the name of the tag to be deleted
            :return: Returns True if successful, or DtlError if failed
        """
        searched_tag_rsp = self.search(name)

        if isinstance(searched_tag_rsp, DtlError):
            return True

        res = self.http_client.make_authed_request(self.service_uri + f"/tags/{searched_tag_rsp.id}", HttpMethod.DELETE)

        if isinstance(res, DtlError):
            return res

        return True

    def list(self, page: int = 1, item_per_page: int = 25) -> Union[DtlError, List[Tag]]:
        """
            List all tags.

            :param page: page to be retrieved
            :param item_per_page: number of items to be put in a page
            :return: Returns a List of all the available tags if successful, or DtlError if failed
        """
        res = self.http_client.make_authed_request(
            self.service_uri + f"/tags?page={page}&size={item_per_page}", HttpMethod.GET
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(Tag._from_payload)(res)

    def share(
        self, name: str, target_type: Scope, target_id: UUID, permission: Permission
    ) -> Union[SharePermission, DtlError]:
        """
            Share a tag.

            :param name: name of the tag to be shared
            :param target_type: Scope (`User`, `Group` or `Organization`) with whom you want to share the tag. It can be User, Group or Organization.
            :param target_id: id of the User, Group or Organization you want to share with (depending on the target_type param)
            :param permission: Permission (`Read`, `Write`, or `Share`) to be shared for a tag. It can be Read, Write or Share.
            :return: Returns a SharePermission for the specific tag if successful, or DtlError if failed
        """

        searched_tag_rsp = self.search(name)

        if isinstance(searched_tag_rsp, DtlError):
            return searched_tag_rsp

        url = f"/scout/tags/{searched_tag_rsp.id}/shares"
        params = {
            "targetType": str(target_type.value),
            "targetId": str(target_id),
            "permission": str(permission.value),
        }
        res = self.http_client.execute_authed_request(url, HttpMethod.POST, params=params)

        if isinstance(res, DtlError):
            return res
        elif res.status_code == 200:
            return SharePermission(object_type=ObjectType.Tag).from_payload(res.json())
        else:
            return DtlError(res.text)

    def unshare(
        self, name: str, target_type: Scope, target_id: UUID, permission: Permission
    ) -> Union[UnsharePermission, DtlError]:
        """
            Unshare a tag.

            :param name: name of the tag to be unshared
            :param target_type: Scope (`User`, `Group` or `Organization`) with whom you want to unshare the tag. It can be User, Group or Organization.
            :param target_id: id of the User, Group or Organization you want to unshare with (depending on the target_type param)
            :param permission: Permission (`Read`, `Write`, or `Share`) to be unshared for a tag. It can be Read, Write or Share.
            :return: Returns an UnsharePermission if successful, or DtlError if failed
        """

        searched_tag_rsp = self.search(name)

        if isinstance(searched_tag_rsp, DtlError):
            return searched_tag_rsp

        url = f"/scout/tags/{searched_tag_rsp.id}/shares"
        params = {
            "targetType": str(target_type.value),
            "targetId": str(target_id),
            "permission": str(permission.value),
        }

        res = self.http_client.execute_authed_request(url, HttpMethod.DELETE, params=params)

        if isinstance(res, DtlError):
            return res
        elif res.status_code == 200:
            return UnsharePermission(object_type=ObjectType.Tag).from_payload(res.json())
        else:
            return DtlError(res.text)

    def get_shares(self, name: str) -> Union[DtlError, List[SharePermission]]:
        """
            List sharings of a tag.

            :param name: name of the tag to get its shared list
            :return: Returns a List of user shares for the specific tag if successful, or DtlError if failed
        """
        searched_tag_rsp = self.search(name)

        if isinstance(searched_tag_rsp, DtlError):
            return searched_tag_rsp

        res = self.http_client.make_authed_request(
            self.service_uri + f"/tags/{searched_tag_rsp.id}/shares", HttpMethod.GET
        )

        if isinstance(res, DtlError):
            return res

        return _parse_list(SharePermission(object_type=ObjectType.Tag).from_payload)(res)
