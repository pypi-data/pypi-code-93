import datetime as dt
from .connect import Connection

class GoogleCalendar:
    """
    Google API Wrapper for Google Calender
    REMEMBER your 'client_secret.json' file in your PATH

    Parameters
    auth: googleapiclient.discovery.Resource object 
            created from the Connection class by default
            no need to mess with this
    cal_id: string id of calendar in Google Calendar 
            This is found in your calendar settings
    """
    def __init__(self, auth = Connection().cal(), cal_id:str = None):
        
        self.service = auth
        
        # pulls all calendars your authentication has access to
        # saves as self.cal_list
        self.cal_list = None 
        self.__all_calendars()

        # if not passed in as parameter, console will prompt for
        # calendar id to be inputed
        if cal_id is None:
            self.calId = self.set_calendar()
        else:
            self.calId = cal_id

    def __all_calendars(self) -> None:
        """
        sets the self.cal_list variable to all the calendars
        that this authentication of google has access to

        you can see these by calling self._print_ids()
        """
        self.cal_list = self.service.calendarList().list().execute()

    def _print_ids(self, data:dict = None) -> None:
        """
        prints the ids of a calendar event, or calendar list
        defaults to printing the calendar list

        used when setting up the default calendar
        """
        if data is None:
            data = self.cal_list
        for x in data["items"]:
            try:
                print("Name: {}, ID: {}".format(x["summary"], x["id"]))
            except ValueError:
                print("Error with {}".format(x))

    def set_calendar(self, hide_prompt = False, cal_id = None) -> None:
        """
        allows you to set a default (active) calendar
    
        will print a list of all calendars for your account
        then prompt you to enter the calendar id in console

        prompt can be silenced by calling this function with
        the hide_prompt parameter set to True

        """
        if hide_prompt:
            if cal_id is None:
                raise ValueError(
                        "Please pass in your calendar ID "\
                        "if silencing the console prompt. "\
                        "cal_id = \"your_cal_id\""
                                )
            self.calId = cal_id
        else:
            self._print_ids()
            self.calId = input("\nType ID of calendar: ")

    def find_event(self, name:str) -> dict:
        """
        search for an event by the event title (name)

        returns a event list dictionary object of all events found
        """
        return (
            self.service.events()
            .list(
                calendarId=self.calId, 
                q=name
                )
            .execute()
        )

    def get_event(self, event_id:str) -> dict:
        """
        query calendar for an event by the event id (event_id)

        returns a event dictionary object of the event id
        """
        return (
            self.service.events()
            .get(
                calendarId=self.calId, 
                eventId=event_id
                )
            .execute()
        )

    def all_events(
                    self, 
                    num_events:int = 100, 
                    min_date: dt.datetime = dt.date.today().strftime("%Y-%m-%dT%H:%M:%SZ")
                    ):
        """
        returns all events on a calendar

        defaults to only 100 events, but that can be changed
        up to 2500 using the num_events parameter

        min_date parameter is the date/time time which the search starts

        returns the dictionary with events in a list
        under the dictionary['items']
        """
        return (
            self.service.events()
            .list(
                calendarId = self.calId, 
                maxResults = num_events, 
                timeMin = min_date
                )
            .execute()
        )

    def update_event(
                    self, 
                    new_event:dict, 
                    send_update = "all"
                    ) -> dict:
        """
        updates an event on your calendar

        accepts the updated dictionary object (new_event)
        uses the 'id' field from new_event to update your calendar

        option to send updates to invites is default yes
        can be changed to 'none', or 'externalOnly'

        returns the updated event dictionary
        """
        return (
            self.service.events()
            .update(
                calendarId = self.calId,
                eventId = new_event["id"],
                body = new_event,
                sendUpdates = send_update,
            )
            .execute()
        )
