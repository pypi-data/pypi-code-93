from tala.model.device import DddDevice, DeviceAction, DeviceWHQuery


class DatetimeDevice(DddDevice):
    class BookFlight(DeviceAction):
        def perform(self, departure_time):
            return True

    class next_arrival_time(DeviceWHQuery):
        def perform(self):
            return ["2018-04-11T22:00:00.000Z"]

    class event_time(DeviceWHQuery):
        def perform(self):
            return ["2018-05-06T09:30:00.000Z"]

    class ShareEventTime(DeviceAction):
        def perform(self, event_time):
            def has_natural_language_form(date_time_expression):
                return date_time_expression == "05/06/2018 09:30 AM"
            return has_natural_language_form(event_time)
