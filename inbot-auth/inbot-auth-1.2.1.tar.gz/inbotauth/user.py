import attr
from typing import Any, Dict, Optional
from flask import Flask
from marshmallow import ValidationError, validates_schema, pre_load
from marshmallow_annotations.ext.attrs import AttrsSchema

@attr.s(auto_attribs=True, kw_only=True)
class User:
    # ToDo (Verdan): Make user_id a required field.
    #  In case if there is only email, id could be email.
    #  All the transactions and communication will be handled by ID
    user_id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    domain: Optional[str] = None
    tenant_id: Optional[str] = None
    is_active: bool = True
    github_username: Optional[str] = None
    team_name: Optional[str] = None
    slack_id: Optional[str] = None
    employee_type: Optional[str] = None
    manager_fullname: Optional[str] = None
    manager_email: Optional[str] = None
    manager_id: Optional[str] = None
    role_name: Optional[str] = None
    authority: Optional[int] = 1
    profile_url: Optional[str] = None
    other_key_values: Optional[Dict[str, str]] = attr.ib(factory=dict)  # type: ignore
    # TODO: Add frequent_used, bookmarked, & owned resources


class UserSchema(AttrsSchema):
    class Meta:
        target = User
        register_as_scheme = True

    # noinspection PyMethodMayBeStatic
    def _str_no_value(self, s: Optional[str]) -> bool:
        # Returns True if the given string is None or empty
        if not s:
            return True
        if len(s.strip()) == 0:
            return True
        return False

    @pre_load
    def preprocess_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if self._str_no_value(data.get('user_id')):
            data['user_id'] = data.get('email')

        if self._str_no_value(data.get('profile_url')):
            data['profile_url'] = ''
            if data.get('GET_PROFILE_URL'):
                data['profile_url'] = data.get('GET_PROFILE_URL')(data['user_id'])  # type: ignore

        first_name = data.get('first_name')
        last_name = data.get('last_name')

        if self._str_no_value(data.get('full_name')) and first_name and last_name:
            data['full_name'] = f"{first_name} {last_name}"

        if self._str_no_value(data.get('display_name')):
            if self._str_no_value(data.get('full_name')):
                data['display_name'] = data.get('email')
            else:
                data['display_name'] = data.get('full_name')

        # microsoft login
        try:
            data['full_name'] = data['name']
            data['first_name'] = data.get('given_name') or data['name'].split()[0]
            data['last_name'] = data.get('family_name') or data['name'].split()[-1]
        except KeyError:
            pass

        return data

    @validates_schema
    def validate_user(self, data: Dict[str, Any]) -> None:
        if self._str_no_value(data.get('display_name')):
            raise ValidationError('"display_name", "full_name", or "email" must be provided')

        if self._str_no_value(data.get('user_id')):
            raise ValidationError('"user_id" or "email" must be provided')


def _str_no_value(s: Optional[str]) -> bool:
    # Returns True if the given string is None or empty
    if not s:
        return True
    if len(s.strip()) == 0:
        return True
    return False


def load_user(app: Flask, user_data: Dict) -> User:
    try:
        schema = UserSchema()
        # In order to call 'GET_PROFILE_URL' we make sure the user id exists
        if _str_no_value(user_data.get('user_id')):
            user_data['user_id'] = user_data.get('email')
        # Add profile_url from optional 'GET_PROFILE_URL' configuration method.
        # This methods currently exists for the case where the 'profile_url' is not included
        # in the user metadata.
        if _str_no_value(user_data.get('profile_url')) and app.config['GET_PROFILE_URL']:
            user_data['profile_url'] = app.config['GET_PROFILE_URL'](user_data['user_id'])
        data, errors = schema.load(user_data)
        return data
    except ValidationError as err:
        return err.messages


def dump_user(user: User) -> Dict:
    schema = UserSchema()
    try:
        data, errors = schema.dump(user)
        return data
    except ValidationError as err:
        return err.messages


def put_user(app, user_info):
    try:
        return dump_user(load_user(app, user_info))
    except Exception as e:
        print(e)
        return None
