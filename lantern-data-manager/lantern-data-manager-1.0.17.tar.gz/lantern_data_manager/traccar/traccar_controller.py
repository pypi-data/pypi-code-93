import os
import traceback
from lantern_data_manager.utils.traccar import get_server_credentials
from lantern_data_manager.utils.logger import logger
from lantern_data_manager.traccar.api_controller import RestAPIController
from lantern_data_manager.traccar.exceptions import *

class TraccarController:

    def __init__(self,traccar_url,credentials):
        """Constructor of class

        Args:
            url (string): url of traccar server
            credentials (dict): {
                "user" : user in traccar,
                "password" : password
            }
        """
        # base_url, http_user, http_password = get_server_credentials(server_id=server_id)
        if "user" not in credentials or "password" not in credentials:
            raise BadParamsException("Not user or password in credentials")
        self.api = RestAPIController(base_url=traccar_url, http_user=credentials["user"], http_password=credentials["password"] )

    def get_devices(self):
        """Returns a list of all devices

            Returns:
                list<dict>: all devices
        """
        uri = 'api/devices'
        return self.api.http_get(uri)
    
    def get_device(self, device_id):
        """Gets a device by its uniqueId

        Args:
            device_id (string): device to get
        Returns:
            list<dict>: data of device found
        """
        # pull device from traccar
        uri = 'api/devices'
        params = {'uniqueId':device_id}
        try:
            return self.api.http_get(uri,params)
        except Exception as e:
            # traceback.print_exc()
            if "NullPointerException" in str(e):
                raise ObjectNotFoundException(device_id)
            else:
                raise e;

    def create_device(self, uniqueId, name, data={}, user=None):
        """Creates a new device
        Args:
            uniqueId (string): new device's id
            name (string): new device's name
            data (dict): data to agregate to the new device
            user (string): user to link the device
            
        Raises:
            DuplicateEntryException: if uniqueId is already in use

        Returns:
            list<dict>: the new device
        """
        # data = self.formatJSON(data)
        uri = 'api/devices'
        data["uniqueId"] = uniqueId
        data["name"] = name
        try:
            device = self.api.http_post(uri,data)
            if user:
                # logger.debug("adding link with user_id: {} and device_id: {}".format(user_id, device["id"]))
                self.link_device_to_user(device_id=uniqueId, user_id=user)
            return device
        except Exception as e:
            if "Duplicate entry" in str(e):
                raise DuplicateEntryException(uniqueId)
            else:
                raise e

    def update_device(self,id, uniqueId,name, data):
        """Updates a device by its id

        Args:
            id (int): device's id given by traccar
            uniqueId (string): unique device's id, chosen
            name (string): device's name, can be the current name or a new one
            data (dict): data to insert into the device

        Returns:
            dict: device data updated
        """
        data["name"] = name
        data["id"] = id
        data["uniqueId"] = uniqueId
        uri = 'api/devices/{}'.format(id)
        try:
            return self.api.http_put(uri,data)
        except Exception as e:
            if "NullPointerException" in str(e):
                raise ObjectNotFoundException(id)
            
    def delete_device(self,id):
        """Deletes a device by its id

        Args:
            id (int): device's id givem by traccar

        Returns:
            bool: true when device is deleted
        """
        uri = 'api/devices/{}'.format(id)
        return self.api.http_delete(uri)

    def list(self):
        uri = 'api/devices'
        return self.api.http_get(uri)
    
    def link_device_to_user(self, device_id, user_id):
        uri = 'api/permissions'
        data = { "userId": user_id, "deviceId": device_id } ## order in this dict is important
        try:
            self.api.http_post(uri, data)
        except Exception as e:
            pass
        return True

    def query_devices(self,uri,action,data={},params={}):
        """Performs a query into the specified uri

        Args:
            uri (string): url to perform query
            action (string): action to perform, it must be "get"|"post"|"put"|"delete"
            data (dict, optional): body of request, it applies to post and put. Defaults to {}.
            params (dict, optional): params of request, it applies to get. Defaults to {}.

        Raises:
            BadRequestException: if action is not "get"|"post"|"put"|"delete"

        Returns:
            dict: response from url
        """
        if action not in ["get","post","put","delete"]:
            raise BadRequestException("action must be get,post, put or delete")
        if action == "get":
            response = self.api.http_get(uri,params)
        elif action == "post":
            response = self.api.http_post(uri,data)
        elif action == "put":
            response = self.api.http_put(uri,data)
        elif action == "delete":
            response = self.api.http_delete(uri)
        return response
        