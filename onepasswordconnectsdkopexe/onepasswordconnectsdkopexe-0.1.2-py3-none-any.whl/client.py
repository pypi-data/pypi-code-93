"""Python Client for connecting to 1Password Connect"""

import base64
import datetime
from getpass import getpass
import json
import logging
import os
import platform
import re
import subprocess
import sys
import uuid

from dateutil.parser import parse
import six

from onepasswordconnectsdkopexe.models import OPField as Field
from onepasswordconnectsdkopexe.models import OPItem as Item
from onepasswordconnectsdkopexe.models import OPVault as Vault
import onepasswordconnectsdkopexe.models


class Client:

    PRIMITIVE_TYPES = (float, bool, bytes, six.text_type) + six.integer_types
    NATIVE_TYPES_MAPPING = {
        "int": int,
#         "long": int if six.PY3 else long,  # type: ignore # noqa: F821
        "long": int,  # type: ignore # noqa: F821
        "float": float,
        "str": str,
        "bool": bool,
        "date": datetime.date,
        "datetime": datetime.datetime,
        "object": object,
    }

    
    
    OS_MAP = {
        'Linux':    {'name': 'linux',   'compyle': ['386', 'amd64', 'arm', 'arm64'],    'pkg_ext': 'zip'},
        'Darwin':   {'name': 'apple',   'compyle': 'universal',                         'pkg_ext': 'pkg'},
        'Windows':  {'name': 'windows', 'compyle': ['386', 'amd64'],                    'pkg_ext': 'zip'},
        'FreeBSD':  {'name': 'freebsd', 'compyle': ['386', 'amd64', 'arm', 'arm64'],    'pkg_ext': 'zip'},
        'OpenBSD':  {'name': 'openbsd', 'compyle': ['386', 'amd64', 'arm64'],           'pkg_ext': 'zip'}
    }

    """Python Client Class"""

    def __init__(self, url: str, email_address: str, secret_key: str, master_password: str, account: str, exe: str=None):
        """Initialize client"""
        if not exe:
            if getattr(sys, 'frozen', False):
                # we are running in a bundle
                BUNDLE_DIR = sys._MEIPASS
            else:
                # we are running in a normal Python environment
                BUNDLE_DIR = os.path.dirname(os.path.abspath(__file__))
            self.exe = os.path.join(BUNDLE_DIR, 'bin', ("op.exe" if platform.system() == 'Windows' else 'op'))
        else:
            self.exe = exe
        if not os.path.isfile(self.exe):
            raise RuntimeError('the file "{}" cannot be found'.format(self.exe))
        self.account = account
        self.url = url
        self.email_address = email_address
        self.secret_key = secret_key

        self.master_password = master_password

        self.token = self.create_token()
        self.global_flags = self._get_global_flags()

    def create_token(self):
        cmd = '"{exe}" signin "{url}" "{email_address}" "{secret_key}" --raw --shorthand="{account}"'.format(**self.__dict__)
        master_password = self.master_password if isinstance(self.master_password, bytes) else self.master_password.encode()
        rc, stdout, stderr = self._process_raise(cmd=cmd,stdin=master_password)
        self.token = stdout.strip()
        return self.token

    def get_item(self, item_id: str, vault_id: str):
        """Get a specific item by uuid
        Parameters:
        item_id (str): The id of the item to be fetched
        vault_id (str): The id of the vault in which to get the item from

        Returns:
        Item object: The found item
        """
        cmd = '"{exe}" get item "{item_id}" {global_flags} --vault "{vault_id}"'.format(**self.__dict__, item_id=item_id, vault_id=vault_id)
        rc, stdout, stderr = self._process_raise(cmd=cmd,tail_stdout=0)
        data = json.loads(stdout.strip())
        data = self.__organise_item(data)
        return self.__deserialize(data, "OPItem")

    def get_item_by_title(self, title: str, vault_id: str):
        """Get a specific item by title
        Parameters:
        title (str): The title of the item to be fetched
        vault_id (str): The id of the vault in which to get the item from

        Returns:
        Item object: A summary of the found item
        """


        cmd = '"{exe}" list items  {global_flags} --vault "{vault_id}"'.format(**self.__dict__, vault_id=vault_id)
        rc, stdout, stderr = self._process_raise(cmd=cmd,tail_stdout=0)
        items = json.loads(stdout.strip())
        items_fond = []
        for i, item in enumerate(items):
            item = self.__organise_item(item)
            if 'title' in  item and title == item['title']:
                items_fond.append(item)

        if len(items_fond) != 1:
            raise FailedToRetrieveItemException(
                f"Found {len(items_fond)} items in vault {vault_id} with \
                    title {title}"
            )

        return self.__deserialize(items_fond, "list[SummaryItem]")[0]

    def get_items(self, vault_id: str):
        """Returns a list of item summaries for the specified vault

        Args:
            vault_id (str): The id of the vault in which to get the items from

        Raises:
            FailedToRetrieveItemException: Thrown when a HTTP error is returned
            from the 1Password Connect API

        Returns:
            List[SummaryItem]: A list of summarized items
        """
        cmd = '"{exe}" list items  {global_flags} --vault "{vault_id}"'.format(**self.__dict__, vault_id=vault_id)
        rc, stdout, stderr = self._process_raise(cmd=cmd,tail_stdout=0)
        items = json.loads(stdout.strip())
        for i, item in enumerate(items):
            items[i]=self.__organise_item(item)

        return self.__deserialize(items, "list[SummaryItem]")

    def __organise_item(self, item):

        if 'overview' in item:
            item = {**item, **item['overview']}
            del item['overview']
        if 'details' in item:
            item = {**item, **item['details']}
            del item['details']
        if 'faveIndex' in item:
            item['faveIndex'] = True
        if 'trashed' in item:
            item['trashed'] = False if item['trashed'] else True
        if 'templateUuid' in item:
            item['templateUuid'] = list(Item.categories.keys())[list(Item.categories.values()).index(item['templateUuid'])] if item['templateUuid'] in list(Item.categories.values()) else 'CUSTOM'
        if 'vaultUuid' in item:
            item['vaultUuid'] = {'id': item['vaultUuid']}

        if 'URLs' in item and 'url' in item:
            for i, url in enumerate(item['URLs']):
                item['URLs'][i]['primary'] = True if url['u'] == item['url'] else False
        if 'fields' in item:
            type_field = {'T': 'STRING', 'P': 'CONCEALED'}
            for i, old_field in enumerate(item['fields']):
                field = {
                    "type": type_field[ old_field['type']],
                    "purpose": old_field['designation'].upper(),
                    "label": old_field['name'],
                    "value": old_field['value']
                }
                if 'id' in old_field:
                    field["id"] = old_field['id']
                item['fields'][i] = field
        else:
            item['fields'] = []
        if 'notesPlain' in item:
            field = {
                "id": "notesPlain",
                "type": "STRING",
                "purpose": "NOTES",
                "label": "notesPlain",
                "value": item['notesPlain']
            }
            item['fields'].append(field)
        if 'password' in item:
            field = {
                "id": "password",
                "type": "CONCEALED",
                "purpose": "PASSWORD",
                "label": "password",
                "value": item['password']
            }
            item['fields'].append(field)
        if 'sections' in item:
            for i, old_section in enumerate(item['sections']):
                section = {
                    'id': old_section['name'],
                    'label': old_section['title']
                }
                if 'fields' in old_section:
                    for old_field in old_section['fields']:
                        type = None
                        if old_field['n'].startswith('TOTP'):
                            type = 'OTP'
                        elif old_field['k'] in list(Field.types.values()):
                            type = list(Field.types.keys())[list(Field.types.values()).index(old_field['k'])]
                        else:
                            continue

                        field = {
                            'id' : old_field['n'],
                            'section':{'id': old_section['name']},
                            'type': type ,
                            'label': old_field['t'],
                            'value': old_field['v'] if old_field['k'] != 'address' else json.dumps(old_field['v']),
                        }
                        item['fields'].append(field)
                item['sections'][i] = section
        return item

    def delete_item(self, item_id: str, vault_id: str):
        """Deletes a specified item from a specified vault

        Args:
            item_id (str): The id of the item in which to delete the item from
            vault_id (str): The id of the vault in which to delete the item
            from

        Raises:
            FailedToRetrieveItemException: Thrown when a HTTP error is returned
            from the 1Password Connect API
        """
        cmd = '"{exe}" delete  item "{item_id}" {global_flags} --vault "{vault_id}"'.format(**self.__dict__, item_id=item_id, vault_id=vault_id)
        rc, stdout, stderr = self._process_raise(cmd=cmd,tail_stdout=0)
        return stdout

    def create_item(self, vault_id: str, item: Item):
        """Creates an item at the specified vault

        Args:
            vault_id (str): The id of the vault in which add the item to
            item (Item): The item to create

        Raises:
            FailedToRetrieveItemException: Thrown when a HTTP error is returned
            from the 1Password Connect API

        Returns:
            Item: The created item
        """

        serialized_body = self.sanitize_for_serialization(item)

        primary_url = ""
        if 'URLs' in serialized_body:
            for i, url in enumerate(serialized_body['URLs']):
                if 'primary' in url:
                    if url['primary'] and not primary_url:
                        primary_url = url['u']
                    del serialized_body['URLs'][i]['primary']

        if primary_url and len(serialized_body['URLs']):
            primary_url = serialized_body['URLs'][0]['u']

        if not( 'templateUuid' in serialized_body and serialized_body['templateUuid']):
            serialized_body['templateUuid'] = 'LOGIN'

        encoded_item = {}
        encoded_item['fields'] = []
        encoded_item['sections'] = {}
#         encoded_item['URLs'] = serialized_body['URLs']   # Not supported

        type_field = {'STRING': 'T', 'CONCEALED': 'P'}
        for field in serialized_body['fields']:
            if 'purpose' in field:
                if field['purpose'] == 'NOTES':
                    encoded_item['notesPlain'] = field['value']
                elif field['purpose'] == 'PASSWORD' and serialized_body['templateUuid'] == '005':
                    encoded_item['password'] = field['value']
                else:
                    encoded_field = {
                        'id': "",
                        'designation': field['purpose'].lower(),
                        'name': field['label'] ,
                        'type': type_field[field['type']],
                        'value': field['value']
                        }
                    encoded_item['fields'].append(encoded_field)
            elif 'section' in field:
                if not 'id' in field['section']:
                    continue
                encoded_field = {
                    "k": Field.types[field['type']] if field['type'] != 'OTP' else 'concealed',
                    "n": str(uuid.uuid4()) if field['type'] != 'OTP' else f'TOTP_{str(uuid.uuid4())}',
                    "t": field['label'],
                    "v": json.loads(field['value']) if field['type'] == 'ADDRESS' else int(field['value']) if field['type'] in ['DATE', 'MONTH_YEAR'] else field['value']
                    }
                if not field['section']['id'] in encoded_item['sections']:
                    encoded_item['sections'][field['section']['id']] = {'fields':[]}
                encoded_item['sections'][field['section']['id']]['fields'].append(encoded_field)

        for section in serialized_body['sections']:
            if section['id'] in encoded_item['sections']:
                encoded_item['sections'][section['id']]['title'] = section['label']
            else:
                encoded_item['sections'][section['id']] = {'title':section['label']}
            encoded_item['sections'][section['id']]['name']= f'Section_{str(uuid.uuid4())}'

        encoded_item['sections'] = list(encoded_item['sections'].values())

        cmd = '"{exe}" encode {global_flags}'.format(**self.__dict__)

        rc, stdout, stderr = self._process_raise(cmd=cmd,stdin=json.dumps(encoded_item).encode())
        encoded_item = stdout.strip()


        cmd = '"{exe}" create item "{category}" "{encoded_item}" {global_flags} --vault "{vault_id}"'.format(**self.__dict__, category=serialized_body['templateUuid'].lower(), encoded_item=encoded_item, vault_id=vault_id)
        if 'title' in serialized_body:
            cmd = f'{cmd} --title "{self._escape_quote(serialized_body["title"])}"'
        if primary_url:
            cmd = f'{cmd} --url "{self._escape_quote(primary_url)}"'

        if 'tags' in serialized_body and serialized_body['tags']:
            cmd = '{cmd} --tags "{tags}"'.format(cmd=cmd, tags=self._escape_quote(",".join(serialized_body['tags'])))

        rc, stdout, stderr = self._process_raise(cmd=cmd,tail_stdout=0)
        return self.deserialize(stdout.strip(), "OPItem")



    def update_item(self, item_id: str, vault_id: str, item: Item):
        """Update the specified item at the specified vault.

        Args:
            item_id (str): The id of the item in which to update
            vault_id (str): The id of the vault in which to update the item
            item (Item): The updated item

        Raises:
            FailedToRetrieveItemException: Thrown when a HTTP error is returned
            from the 1Password Connect API

        Returns:
            Item: The updated item
        """

        serialized_body = self.sanitize_for_serialization(item)

        primary_url = ""
        if 'URLs' in serialized_body:
            for i, url in enumerate(serialized_body['URLs']):
                if 'primary' in url:
                    if url['primary'] and not primary_url:
                        primary_url = url['u']
                    del serialized_body['URLs'][i]['primary']

        if primary_url and len(serialized_body['URLs']):
            primary_url = serialized_body['URLs'][0]['u']

        assignments = ' '
        if 'title' in serialized_body:
            assignments += 'title="{title}" '.format( title=self._escape_quote(serialized_body["title"]))
        if primary_url:
            assignments += 'url="{primary_url}" '.format( primary_url=self._escape_quote(primary_url))

        if 'tags' in serialized_body and serialized_body['tags']:
            assignments += 'tags="{tags}" '.format( tags=self._escape_quote(",".join(serialized_body['tags'])))

        for field in serialized_body['fields']:
            if 'purpose' in field:
                if field['purpose'] == 'NOTES':
                    assignments += 'notesPlain="{value}" '.format( value=self._escape_quote(field["value"]))
                else:
                    assignments += '{id}="{value}" '.format(id=field["label"], value=self._escape_quote(field["value"]))
            elif 'section' in field:
                if not 'id' in field['section']:
                    continue
                if not field['type'] in ['DATE', 'MONTH_YEAR', 'ADDRESS']:
                    assignments += '{id}="{value}" '.format(id=field["id"], value=self._escape_quote(field["value"]))
                else:
                    logging.debug(f'"{field["type"]}" fields aren\'t supported yet')


        cmd = '"{exe}" edit item "{item_id}" {assignments} {global_flags} --vault "{vault_id}"'.format(**self.__dict__, category=serialized_body['templateUuid'].lower(), item_id=item_id, assignments=assignments, vault_id=vault_id)
        rc, stdout, stderr = self._process_raise(cmd=cmd,tail_stdout=0)

        return self.get_item( item_id, vault_id)

    def get_vault(self, vault_id: str):
        """Returns the vault with the given vault_id

        Args:
            vault_id (str): The id of the vault in which to fetch

        Raises:
            FailedToRetrieveVaultException: Thrown when a HTTP error is
            returned from the 1Password Connect API

        Returns:
            Vault: The specified vault
        """

        cmd = '"{exe}" get vault "{vault_id}" {global_flags}'.format(**self.__dict__, vault_id=vault_id)
        rc, stdout, stderr = self._process_raise(cmd=cmd,tail_stdout=0)
        vault = json.loads(stdout.strip())
        vault = self.__organise_vault(vault)

        return self.__deserialize(vault, "OPVault")

    def get_vaults(self):
        """Returns all vaults for service account set in client

        Raises:
            FailedToRetrieveVaultException: Thrown when a HTTP error is
            returned from the 1Password Connect API

        Returns:
            List[Vault]: All vaults for the service account in use
        """

        cmd = '"{exe}" list vaults {global_flags}| "{exe}" get vault - {global_flags}'.format(**self.__dict__)
        rc, stdout, stderr = self._process_raise(cmd=cmd,tail_stdout=0)
        vaults = []
        for vault in stdout.splitlines() :
            vaults.append(self.__organise_vault(json.loads(vault.strip())))

        return self.__deserialize(vaults, "list[OPVault]")

    def __organise_vault(self, vault):
        if 'type' in vault:
            vault['type'] = list(Vault.types.keys())[list(Vault.types.values()).index(vault['type'])] if vault['type'] in list(Vault.types.values()) else None

        return vault

    def build_request(self, method: str, path: str, body=None):
        """Builds a http request
        Parameters:
        method (str): The rest method to be used
        path (str): The request path
        body (str): The request body

        Returns:
        Response object: The request response
        """
        url = f"{self.url}{path}"

        if body:
            serialized_body = json.dumps(self.sanitize_for_serialization(body))
            response = self.session.request(method, url, data=serialized_body)
        else:
            response = self.session.request(method, url)
        return response

    def deserialize(self, response, response_type):
        """Deserializes response into an object.

        :param response: RESTResponse object to be deserialized.
        :param response_type: class literal for
            deserialized object, or string of class name.

        :return: deserialized object.
        """
        # fetch data from response object
        try:
            data = json.loads(response)
        except ValueError:
            data = response

        return self.__deserialize(data, response_type)

    def sanitize_for_serialization(self, obj):
        """Builds a JSON POST object.

        If obj is None, return None.
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date convert to string
        in iso8601 format.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is OpenAPI model, return the properties dict.

        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if obj is None:
            return None
        elif isinstance(obj, self.PRIMITIVE_TYPES):
            return obj
        elif isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj) for sub_obj in obj]  # noqa: E501
        elif isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj) for sub_obj in obj)  # noqa: E501
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        if isinstance(obj, dict):
            obj_dict = obj
        else:
            # Convert model obj to dict except
            # attributes `openapi_types`, `attribute_map`
            # and attributes which value is not None.
            # Convert attribute name to json key in
            # model definition for request.
            obj_dict = {
                obj.attribute_map[attr]: getattr(obj, attr)
                for attr, _ in six.iteritems(obj.openapi_types)
                if getattr(obj, attr) is not None
            }

        return {
            key: self.sanitize_for_serialization(val)
            for key, val in six.iteritems(obj_dict)
        }

    def __deserialize(self, data, klass):
        """Deserializes dict, list, str into an object.

        :param data: dict, list or str.
        :param klass: class literal, or string of class name.

        :return: object.
        """
        if data is None:
            return None

        if type(klass) == str:
            if klass.startswith("list["):
                sub_kls = re.match(r"list\[(.*)\]", klass).group(1)
                return [self.__deserialize(sub_data, sub_kls) for sub_data in data]  # noqa: E501

            if klass.startswith("dict("):
                sub_kls = re.match(r"dict\(([^,]*), (.*)\)", klass).group(2)
                return {
                    k: self.__deserialize(v, sub_kls) for k, v in six.iteritems(data)  # noqa: E501
                }

            # convert str to class
            if klass in self.NATIVE_TYPES_MAPPING:
                klass = self.NATIVE_TYPES_MAPPING[klass]
            else:
                klass = getattr(onepasswordconnectsdkopexe.models, klass)

        if klass in self.PRIMITIVE_TYPES:
            return self.__deserialize_primitive(data, klass)
        elif klass == object:
            return self.__deserialize_object(data)
        elif klass == datetime.date:
            return self.__deserialize_date(data)
        elif klass == datetime.datetime:
            return self.__deserialize_datetime(data)
        else:
            return self.__deserialize_model(data, klass)

    def __deserialize_primitive(self, data, klass):
        """Deserializes string to primitive type.

        :param data: str.
        :param klass: class literal.

        :return: int, long, float, str, bool.
        """
        try:
            return klass(data)
        except UnicodeEncodeError:
            return six.text_type(data)
        except TypeError:
            return data

    def __deserialize_object(self, value):
        """Return an original value.

        :return: object.
        """
        return value

    def __deserialize_date(self, string):
        """Deserializes string to date.

        :param string: str.
        :return: date.
        """
        try:
            return parse(string).date()
        except ImportError:
            return string
        except ValueError:
            raise FailedToDeserializeException(
                f'Failed to parse `{0}`\
                 as date object".format(string)'
            )

    def __deserialize_datetime(self, string):
        """Deserializes string to datetime.

        The string should be in iso8601 datetime format.

        :param string: str.
        :return: datetime.
        """
        try:
            return parse(string)
        except ImportError:
            return string
        except ValueError:
            raise FailedToDeserializeException(
                f'Failed to parse `{0}`\
                 as date object".format(string)'
            )

    def __deserialize_model(self, data, klass):
        """Deserializes list or dict to model.

        :param data: dict, list.
        :param klass: class literal.
        :return: model object.
        """
        has_discriminator = False
        if (
            hasattr(klass, "get_real_child_model")
            and klass.discriminator_value_class_map
        ):
            has_discriminator = True

        if not klass.openapi_types and has_discriminator is False:
            return data

        kwargs = {}
        if (
            data is not None
            and klass.openapi_types is not None
            and isinstance(data, (list, dict))
        ):
            for attr, attr_type in six.iteritems(klass.openapi_types):
                if klass.attribute_map[attr] in data:
                    value = data[klass.attribute_map[attr]]
                    kwargs[attr] = self.__deserialize(value, attr_type)

        instance = klass(**kwargs)

        if has_discriminator:
            klass_name = instance.get_real_child_model(data)
            if klass_name:
                instance = self.__deserialize(data, klass_name)
        return instance

    def _get_global_flags(self):
        return '--account "{account}" --session "{token}"'.format(**self.__dict__)

    def _escape_quote(self,text):
        if sys.platform == 'win32':
            if text[-1:] == '\\':
                text += '\\'
            return text.replace('^','^^').replace('&', '^&').replace('|', '^|').replace('>', '^>').replace('<', '^<').replace('\\"', '\\\\"').replace('"','\\"')
        else:
            return text.replace("\\","\\\\").replace('"', '\\"')

    def _process(self,
                cmd: str,
                cwd: str=None,
                tail_stdout: int=None,
                show_cmd: bool=True,
                stdin: bytes = None,
                timeout: int=15):
        '''
        Execute a child program in a new process.
        :param logger: the variable to manage debugging logs
        :type logger: object logging
        :param cmd: order to be executed
        :type cmd: string
        :param cwd: Sets the current directory before the child is executed, defaults to None
        :type cwd: String, None, optional
        :param tail_stdout: set the number of last lines displays them in the logging object of the normal console output of the executed command (stdout). if the value is None all the stdout will be used, defaults to None
        :type tail_stdout: Int, None, optional
        :param show_cmd: allows not to display the executed command in the logs before it is launched, defaults to True
        :type show_cmd: Boolean, optional
        :return: Composed of 3 elements, the return code of the end of the execution of the command, the normal output (stdout) of the executed command and the error output (stderr) of the executed command.
        :rtype: Tuple(Int, String, String)
        '''

        if show_cmd:
            logging.debug('execute : {} - on : {}'.format(cmd, cwd))
        proc = subprocess.Popen(cmd,
                                cwd = cwd,
                                shell=True,
                                stdin = subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if(stdin) :
            stdin += b"\n"
        stdout,stderr = proc.communicate( input=stdin, timeout=timeout)
        proc.poll()
        returncode = proc.returncode
        logging.debug('return error code : {}'.format(returncode))
        stdout = stdout.decode('utf8').strip()
        stderr = stderr.decode('utf8').strip()
        if stdout:
            if tail_stdout is None:
                logging.debug('stdout = {}'.format(stdout))
            elif tail_stdout > 0:
                array_stdout = stdout.split("\n")
                p_stdout = "\n".join(array_stdout[tail_stdout*-1:])
                logging.debug('tail stdout = {}'.format(p_stdout))
        if not returncode == 0:
            logging.error('stderr = {}'.format(stderr))
        elif stderr:
            logging.debug('stderr = {}'.format(stderr))
        return returncode, stdout, stderr

    def _process_raise(self, cmd, cwd=None, tail_stdout=None, show_cmd=True, stdin = None, timeout=15):
        '''
        Execute a child program in a new process and return an error if it does not return 0 in returncode variable
        :param logger: the variable to manage debugging logs
        :type logger: object logging
        :param cmd: order to be executed
        :type cmd: string
        :param cwd: Sets the current directory before the child is executed, defaults to None
        :type cwd: String, None, optional
        :param tail_stdout: set the number of last lines displays them in the logging object of the normal console output of the executed command (stdout). if the value is None all the stdout will be used, defaults to None
        :type tail_stdout: Int, None, optional
        :param show_cmd: allows not to display the executed command in the logs before it is launched, defaults to True
        :type show_cmd: Boolean, optional
        :raises RuntimeError: is switched on if the return code of the executed command is different from 0
        :return: Composed of 3 elements, the return code of the end of the execution of the command, the normal output (stdout) of the executed command and the error output (stderr) of the executed command.
        :rtype: Tuple(Int, String, String)

        '''
        returncode, stdout, stderr = self._process(cmd,
                                             cwd=cwd,
                                             tail_stdout=tail_stdout,
                                             show_cmd=show_cmd,
                                             stdin =stdin,
                                             timeout = timeout)
        if not returncode == 0 :
            raise RuntimeError(stderr)

        return returncode, stdout, stderr


def new_client(url: str, account, email_address: str, secret_key: str, master_password: str ):
    return Client(url=url, account=account, email_address=email_address, secret_key= secret_key, master_password=master_password)

def new_client_interactif(url: str = None, account = None, email_address: str = None, secret_key: str = None, master_password: str = None ):
    while not url:
        url = input("Please input your url of your server: ")
    while not account:
        account = input("Please input your 1password account: ")
    while not email_address:
        email_address = input("Please input your email address used for 1Password account: ")

    while not secret_key:
        secret_key = getpass("Please input your 1Password secret key: ")

    while not master_password:
        master_password = getpass("Please input your 1Password master password: ").encode()
    return Client(url=url, account=account, email_address=email_address, secret_key= secret_key, master_password=master_password)

class OnePasswordConnectSDKError(RuntimeError):
    pass


class EnvironmentTokenNotSetException(OnePasswordConnectSDKError, TypeError):
    pass

class EnvironmentHostNotSetException(OnePasswordConnectSDKError, TypeError):
    pass

class FailedToRetrieveItemException(OnePasswordConnectSDKError):
    pass


class FailedToRetrieveVaultException(OnePasswordConnectSDKError):
    pass


class FailedToDeserializeException(OnePasswordConnectSDKError, TypeError):
    pass
