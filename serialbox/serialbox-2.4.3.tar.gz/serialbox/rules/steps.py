# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

from quartet_capture.rules import Step, Rule
from quartet_capture.models import Task as DBTask

def execute_rule_inline(message: bytes, db_task: DBTask):
    '''
    Helper function that executes a rule inline and returns
    the context.  The celery task below essentially does the same thing
    without returning the rule context.
    When a message arrives, creates a record of the message and parses
    it using the appropriate parser.
    :param message_data: The data to be handled.
    '''
    try:
        # create an executable task from a database rule
        c_rule = Rule(db_task.rule, db_task)
        # execute the rule
        c_rule.execute(message)
        # return the context
        db_task.STATUS = "FINISHED"
        db_task.save()
    except:
        db_task.STATUS = "FAILED"
        db_task.save()
        raise
    return c_rule
