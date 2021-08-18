from gravity_core.functions.capture_user_activity import capture_user_activity
from gravity_core.tests.sqlhell_test import shell
import gravity_core.wsettings as s



all_activities = [{'event': 'LOGIN'}, {'event': 'START'}, {'event':'EXIT'}]
for event in all_activities:
    capture_user_activity(shell, 1, event['event'], s.cm_events_table, s.cm_events_log_table)