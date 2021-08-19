"""
    An easy(ier) python implementation of the TeamDynamix Rest APIs
    By Chris Garrett cmgarOK@gmail.com

    ---
    NOTES FOR DEVELOPERS AND CONTRIBUTERS:
    Class methods to retrieve data should begin with get_.

    Class methods to update data should begin with update_.

    Class methods to find data should begin with search_.

    Methods that aren't required to pass in JSON should use 
    the self._get_data function to return information.

    Any method that is marked in the documentation from TDX to 
    be rate-limited should use the sleep() function for the 
    appropriate amount of time to prevent HTTP 429 errors.

    Please follow the docstring commenting for documentation
    of any functions that are added.
"""

__version__ = "2021.08.18"

import datetime as dt
import json
from requests.sessions import Session
from typing import Any, List
from time import sleep

class EzTDXException(Exception):
    """The base class for EzTDX-specific problems"""
    pass

class EzTDX():
    def __init__(self, beid: str, web_services_key: str, app_id: int, sandbox: bool = True) -> None:
        """ initialization """ 
        self.beid = beid
        self.web_services_key = web_services_key
        self.app_id = app_id
        self.bearer_token = None

        self.session = Session()
        self.credentials = {'BEID': self.beid, 'WebServicesKey': self.web_services_key}

        self.sandbox_base_url = 'https://api.teamdynamix.com/SBTDWebApi/api'
        self.prod_base_url = 'https://api.teamdynamix.com/TDWebApi/api'
        self.sandbox = sandbox

        if self.sandbox:
            self.BASE_URL = self.sandbox_base_url
        else:
            self.BASE_URL = self.prod_base_url

        try:
            response = self.session.post(f'{self.BASE_URL}/auth/loginadmin', data=self.credentials)

            if response.status_code == 200:
                self.session.headers['Authorization'] = f'Bearer {response.text}'
            else:
                raise ConnectionError
        except Exception as ex:
            self.log(f'Error in init: {ex}')

    def _get_data(self, api: str) -> Any:
        """GET Request
        - API string
        """
        try:
            response = self.session.get(f'{self.BASE_URL}{api}')
            if response.status_code == 200:
                return json.loads(response.text)
            elif response.status_code == 429:
                raise Exception(f"You've hit the rate limit for this API call {api}.")
            else:
                raise Exception(f'Error: get_data(): {response.status_code} : {api}')
        except Exception as ex:
            raise Exception(f'Exception in generic_get: {ex}')

    def add_people_to_group(self, group_id: int, guids: List[str], is_primary: str = 'false', is_notified: str = 'true', is_manager: str = 'false') -> str:
        """ Add list of guids to group """
        try:
            api = f'{self.BASE_URL}/groups/{group_id}/members?isPrimary={is_primary}&isNotified={is_notified}&isManager={is_manager}'

            response = self.session.post(api, data = guids, headers={'content-type' : 'application/json'})

            if response.status_code == 200:
                return response.text
            else:
                raise Exception(response.text)
        except Exception as ex:
            self.log(f'Error in add_people_to_group: {ex}')

    def add_time_entry(self, time_entry: dict) -> Any:
        """ Create a time entry 
            - time_entry: TeamDynamix.Api.Time.TimeEntry 
            https://api.teamdynamix.com/TDWebApi/Home/type/TeamDynamix.Api.Time.TimeEntry
        """
        try:
            api = f'{self.BASE_URL}/time'

            response = self.session.post(api, data = time_entry, headers={'content-type' : 'application/json'})

            if response.status_code == 200:
                return response.text
            else:
                raise Exception(response.text)
        except Exception as ex:
            self.log(f'Error in add_time_entry: {ex}')

    def get_group(self, group_id: int) -> dict:
        """Get Group by ID """
        try:
            return self._get_data(f'/groups/{group_id}')
        except Exception as ex:
            self.log(f'Error in get_group: {ex}')

    def get_group_members(self, group_id: int) -> List[dict]:
        """Get Group members by ID """
        try:
            return self._get_data(f'/groups/{group_id}/members')
        except Exception as ex:
            self.log(f'Error in get_group_members: {ex}')

    def get_location_by_id(self, location_id: int) -> dict:
        """Get Location by ID"""
        try:
            return self._get_data(f'/locations/{location_id}')
        except Exception as ex:
            self.log(f'Error in get_location_by_id: {ex}')

    def get_person(self, user_id: str) -> Any:
        """Get User by ID"""
        try:
            api = f'/people/{user_id}'
            return self._get_data(api)
        except Exception as ex:
            self.log(f'Error in get_person: {ex}')

    def get_people_groups(self, user_id: str) -> List[str]:
        """Return list of groups by person
        - User ID
        """
        try:
            api = f'/people/{user_id}/groups'
            return self._get_data(api)
        except Exception as ex:
            self.log(f'Error in get_people_groups: {ex}')

    def get_ticket_attribute(self, ticket_id: int, attribute_name: str) -> Any:
        """ Gets a ticket attribute from a ticket
            - ticket_id: int: The ID of the ticket
            - attribute_name: string: Attribute name to retrieve
        """
        try:
            ticket = self.get_ticket_by_id(ticket_id)

            for attribute in ticket['Attributes']:
                if attribute['Name'] == attribute_name:
                    return attribute['ValueText']
            return 'N/A'
        except Exception as ex:
            self.log(f'Error in get_ticket_attribute: {ex}')

    def get_ticket_by_id(self, ticket_id: str) -> dict:
        """ Gets a single ticket by it's id
            - ticket_id: The ID of the ticket
        """
        try:
            api = f'/{self.app_id}/tickets/{ticket_id}'
            return self._get_data(api)
        except Exception as ex:
            self.log(f'Error in get_ticket_by_id: {ex}')

    def get_ticket_config_items(self, ticket_id: int) -> List[str]:
        """ Gets a list of configuration items attached to a ticket
            - ticket_id: int: The ID of the ticket
        """
        try:
            # prevents breaking rate limiting
            sleep(1.125)

            return self._get_data(f'/{self.app_id}/tickets/{ticket_id}/assets')
        except Exception as ex:
            self.log(f'Error in get_ticket_config_items: {ex}')

    def get_ticket_description(self, ticket_id: str) -> str:
        """ Get ticket description from ID
            - ticket_id: Ticket ID
        """
        try:
            api = f'/{self.app_id}/tickets/{ticket_id}'

            # prevents breaking rate limiting
            sleep(1.125)

            ticket = self._get_data(api)
            return ticket['Description']
        except Exception as ex:
            self.log(f'Error in get_ticket_description: {ex}')

    def get_ticket_feed(self, ticket_id: str) -> List[str]:
        """ Get ticket feed from ID
            - ticket_id: Ticket ID
        """
        try:
            # prevents breaking rate limiting
            sleep(1.125)

            return self._get_data(f'/{self.app_id}/tickets/{ticket_id}/feed')
        except Exception as ex:
            self.log(f'Error in get_ticket_feed: {ex}')

    def get_ticket_status_id(self, txt_status: str) -> int:
        """ Return ticket status id from text name
            - txt_status: String status code
        """
        try:
            api = f'/{self.app_id}/tickets/statuses'

            ticket_statuses = self._get_data(api)

            for ticket_status in ticket_statuses:
                if ticket_status['Name'] == txt_status:
                    return int(ticket_status['ID'])
        except Exception as ex:
            self.log(f'Error in get_ticket_status: {ex}')

    def get_ticket_status_ids(self, ticket_statuses_text: List[str]) -> List[int]:
        """ Change list of ticket status text to list of status ids
            - ticket_status: List of text ticket statuses
        """

        try:
            api = f'/{self.app_id}/tickets/statuses'

            ticket_statuses = self._get_data(api)

            ticket_status_ids = []

            for ticket_status_text in ticket_statuses_text:
                for ticket_status in ticket_statuses:
                    if ticket_status['Name'] == ticket_status_text:
                        ticket_status_ids.append(ticket_status['ID'])

            return ticket_status_ids
        except Exception as ex:
            self.log(f'Error in get_ticket_status_ids: {ex}')

    def get_ticket_tasks(self, ticket_id: int, is_eligible_predecessor: str = '') -> List[dict]:
        """ Get ticket tasks
            - ticket_id: int: ID of the ticket you would like to retrieve tasks for
            - is_eligible_predecessor: str: If true, this will only retrieve ticket 
                tasks that can be assigned as a predecessor for other ticket tasks. A value of None will return all tasks. (default: blank)
        """
        try:
            api = f'/{self.app_id}/tickets/{ticket_id}/tasks?isEligiblePredecessor={is_eligible_predecessor}'

            # prevents breaking rate limiting
            sleep(1.125)

            return self._get_data(api)
        except Exception as ex:
            self.log(f'Error in get_ticket_tasks: {ex}')

    def get_ticket_task_feed(self, ticket_id: int, task_id: int) -> List[dict]:
        """ Gets the feed entries for the ticket task.
            - ticket_id: int: The ticket ID on which the ticket task exists.
            - task_id: int: The ticket task ID
        """
        try:
            api = f'/{self.app_id}/tickets/{ticket_id}/tasks/{task_id}/feed'

            # prevents breaking rate limiting
            sleep(1.125)

            return self._get_data(api)
        except Exception as ex:
            self.log(f'Error in get_time_types: {ex}')

    def get_time_entry(self, time_id: int) -> dict:
        """ Get a specific time entry by ID """
        try:
            sleep(1.125)
            return self._get_data(f'/time/{time_id}')
        except Exception as ex:
            self.log(f'Error in get_time_types: {ex}')

    def get_time_types(self) -> List[str]:
        """Get Time Types"""
        try:
            api = f'/time/types'

            # prevents breaking rate limiting
            sleep(1.125)

            return self._get_data(api)
        except Exception as ex:
            self.log(f'Error in get_time_types: {ex}')

    def get_time_type(self, time_type_id: int) -> str:
        """Get Time Type by ID"""
        try:
            api = f'/time/types/{time_type_id}'

            # prevents breaking rate limiting
            sleep(1.125)

            return self._get_data(api)
        except Exception as ex:
            self.log(f'Error in get_time_types: {ex}')

    def get_time_type_from_name(self, time_type_name: str) -> int:
        """ Gets the time type ID from the name """
        """Get Time Type by ID"""
        try:
            api = '/time/types'

            # prevents breaking rate limiting
            sleep(1.125)

            time_types =  self._get_data(api)

            for time_type in time_types:
                if time_type['Name'] == time_type_name:
                    return time_type['ID']
        except Exception as ex:
            self.log(f'Error in get_time_type_from_name: {ex}')

    def get_workspace_time_types(self, workspace_id: int) -> List[dict]:
        """ Gets time types associated with a workspace """
        try:
            sleep(1.125)
            return self._get_data(f'/time/types/component/workspace/{workspace_id}')
        except Exception as ex:
            self.log(f'Error in get_workspace_time_types: {ex}')


    def log(self, msg: str) -> None:
        """Log to file"""
        try:
            now = str(dt.datetime.now())

            print(f'{now} - {msg}')
        except Exception as ex:
            print(f'Error writing to log: {ex}')

    def search_people(self, search_by: str, max_results: int = 10) -> List[dict]:
        """Search people
        - Search terms
        - Max results: default 10, max 100
        """
        try:
            api = f'/people/lookup?searchText={search_by}&maxResults={max_results}'
            # prevents breaking rate limiting
            sleep(1)
            return self._get_data(api)
        except Exception as ex:
            self.log(f'Error in get_people: {ex}')

    def search_tickets(self, search_str: str, ticket_status: List[str] = ['New'], max_results: int = 5) -> List[str]:
        """ Searches for tickets 
            - search_str: Search Text to filter tickets on
            - ticket_status: List of ticket statuses to filter on (default: New tickets)
            - max_results: How many tickets to return (default: 5 tickets)
        """

        try:
            # convert list of text status types into their IDs
            ticket_status_ids = self.get_ticket_status_ids(ticket_status)

            data = {
                'MaxResults': max_results,
                'StatusIDs': ticket_status_ids,
                'SearchText': search_str
            }
            response = self.session.post(f'{self.BASE_URL}/{self.app_id}/tickets/search', data=data)

            if response.status_code == 200:
                tickets = json.loads(response.text)

                return tickets
        except Exception as ex:
            self.log(f'Error in search_tickets: {ex}')

    def search_tickets_custom(self, search_criteria: dict, ticket_status: List[str] = ['New'], max_results: int = 5) -> List[str]:
        """ Searches for tickets with more specific criteria
            - search_criteria: Dictionary: Search info to search with
            - ticket_status: List of ticket statuses to filter on (default: New tickets)
            - max_results: How many tickets to return (default: 5 tickets)
        """
        try:
            search_criteria['StatusIDs'] = self.get_ticket_status_ids(ticket_status)

            response = self.session.post(f'{self.BASE_URL}/{self.app_id}/tickets/search', data=search_criteria)

            if response.status_code == 200:
                return json.loads(response.text)
        except Exception as ex:
            self.log(f'Error in search_tickets_custom: {ex}')

    def search_time_entries(self, entry_date_from: str, entry_date_to: str, person_ids: List[str]=[], max_results: int=1000) -> List[str]:
        """Search for time entered
        - Entry Date From: 2021-06-02T00:00:00Z format
        - Entry Date To: 2021-06-02T00:00:00Z format
        - Person IDs: List of GUIDS (default: empty list)
        - Max Results: (default: 1000 entries)
        """
        
        try:
            data = {
                'EntryDateFrom': entry_date_from,
                'EntryDateTo': entry_date_to,
                'PersonUIDs': person_ids,
                'MaxResults': max_results
            }

            response = self.session.post(f'{self.BASE_URL}/time/search', data=data)

            if response.status_code == 200:
                return json.loads(response.text)
        except Exception as ex:
            self.log(f'Error in search_time: {ex}')

    def update_ticket(self, ticket_id: int, updates: str) -> dict:
        """ Update ticket
            - ticket_id: Ticket to be patched.
            - updates: JSON string in HTTP PATCH notation (http://jsonpatch.com/)

        """
        try:
            response = self.session.patch(f'{self.BASE_URL}/{self.app_id}/tickets/{ticket_id}', data=updates, headers={'content-type' : 'application/json'})

            if response.status_code == 200:
                return json.loads(response.text)
        except Exception as ex:
            self.log(f'Error in update_ticket: {ex}')

    def update_ticket_feed(self, ticket_id: int, comment: str, new_status: str = "None", notify_list: List[str]=[], is_private: bool = False) -> str:
        """ Update a ticket feed
            - ticket_id: ID of ticket to be updated
            - new_status: Change the status of the ticket (default: None for no change)
            - comment: Comment to add to the feed
            - is_private: Mark the comment as private
        """
        try:
            new_status_id = 0

            if new_status != 'None':
                new_status_id = self.get_ticket_status_id(new_status)

            data = {
                'NewStatusID': new_status_id,
                'Comments': comment,
                'Notify': notify_list,
                'IsPrivate': is_private
            }

            response = self.session.post(f'{self.BASE_URL}/{self.app_id}/tickets/{ticket_id}/feed', data=data)

            if response.status_code == 201:
                return f'Ticket {ticket_id} updated successfully!'
            else:
                return f'Ticket {ticket_id} could not be updated.'
        except Exception as ex:
            self.log(f'Error in update_ticket: {ex}')

    def update_ticket_task(self, ticket_id: int, task_id: int, percent_complete: int, title: str, estimated_minutes: int = 60) -> dict:
        """ Update ticket task
            - ticket_id: int: Ticket ID
            - task_id: int: Ticket task ID
            - percent_complete: int: 0 - 100
            - title: str: Title of the task
            - estimated_minutes: int: Estimated minutes of completion (default 60)
        """

        try:
            data = {
                'ID' : task_id,
                'TicketID' : ticket_id,
                'Title' : title,
                'EstimatedMinutes' : estimated_minutes,
                'PercentComplete' : percent_complete
            }

            response = self.session.put(f'{self.BASE_URL}/{self.app_id}/tickets/{ticket_id}/tasks/{task_id}', data=data)

            if response.status_code == 200:
                return json.loads(response.text)
        except Exception as ex:
            self.log(f'Error in update_ticket_task: {ex}')

    def update_ticket_task_feed(self, ticket_id: int, task_id: int, percent_complete: int, comments: str, notify: List[str] = [], is_private: bool = False) -> dict:
        """ Update ticket task feed
            - ticket_id: int: Ticket ID
            - task_id: int: Ticket task ID
            - percent_complete: int: 0 - 100
            - comments: str: Comments for the feed
            - notify: List[str]: list of emails to notify (default empty list)
            - is_private: boolean: is the feed entry private (default False)
        """

        try:
            data = {
                'PercentComplete' : percent_complete,
                'Comments' : comments,
                'Notify' : notify,
                'IsPrivate': is_private
            }

            response = self.session.post(f'{self.BASE_URL}/{self.app_id}/tickets/{ticket_id}/tasks/{task_id}/feed', data=data)

            if response.status_code == 201:
                return json.loads(response.text)
        except Exception as ex:
            self.log(f'Error in update_ticket_task_feed: {ex}')