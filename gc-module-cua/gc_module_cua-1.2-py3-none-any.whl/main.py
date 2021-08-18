from gc_module_cua import functions


class EventsCatcher:
    def __init__(self, sql_shell, events_table, events_log):
        self.sql_shell = sql_shell
        self.events_table = events_table
        self.events_log = events_log
        self.all_events = self.get_all_events()

    def get_all_events(self, *args, **kwargs):
        """ Получить список словарей, описывающих всех события в системе"""
        all_events = functions.get_all_events(self.sql_shell, self.events_table)
        return all_events

    def capture_user_activity(self, event, user, *args, **kwargs):
        """ Зафиксировать действие пользователя """
        response = functions.capture_user_activity(self.sql_shell, user, event, self.events_table, self.events_log)
        return response

    def try_capture_new_event(self, event, user=1, *args, **kwargs):
        """ Попытка зафиксировать новое событие """
        if functions.is_event_valid(self.all_events, event):
            return self.capture_user_activity(event, user)
        else:
            return {'status': 'failed', 'info': 'В базе нет данных о событии под названием {}'.format(event)}
