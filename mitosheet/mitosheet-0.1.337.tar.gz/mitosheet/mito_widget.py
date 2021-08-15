#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Mito.

"""
Main file containing the mito widget.
"""
from mitosheet.user.schemas import UJ_FEEDBACKS, UJ_MITOSHEET_LAST_FIFTY_USAGES
from mitosheet.user.db import get_user_field
from mitosheet.utils import get_new_id
from mitosheet.api import API
from mitosheet.mito_analytics import log, log_event_processed, log_recent_error
import pandas as pd

from ipywidgets import DOMWidget
import traitlets as t

from mitosheet._frontend import module_name, module_version
from mitosheet.errors import EditError, get_recent_traceback_as_list
from mitosheet.saved_analyses import (
    read_and_upgrade_analysis, 
    write_analysis,
    saved_analysis_names_json
)

from mitosheet.steps_manager import StepsManager

from mitosheet.user import is_local_deployment, should_upgrade_mitosheet
from mitosheet.data_in_mito import DataTypeInMito


class MitoWidget(DOMWidget):
    """
        The MitoWidget holds all of the backend state for the Mito extension, and syncs
        the state with the frontend widget. 
    """
    _model_name = t.Unicode('ExampleModel').tag(sync=True)
    _model_module = t.Unicode(module_name).tag(sync=True)
    _model_module_version = t.Unicode(module_version).tag(sync=True)
    _view_name = t.Unicode('ExampleView').tag(sync=True)
    _view_module = t.Unicode(module_name).tag(sync=True)
    _view_module_version = t.Unicode(module_version).tag(sync=True)

    is_local_deployment = t.Bool(True).tag(sync=True)
    analysis_name = t.Unicode('').tag(sync=True)
    curr_step_idx = t.Int(0).tag(sync=True)
    sheet_json = t.Unicode('').tag(sync=True)
    code_json = t.Unicode('').tag(sync=True)
    df_names_json = t.Unicode('').tag(sync=True)
    df_sources_json = t.Unicode('').tag(sync=True)
    df_shape_json = t.Unicode('').tag(sync=True)
    saved_analysis_names_json = t.Unicode('').tag(sync=True)
    column_spreadsheet_code_json = t.Unicode('').tag(sync=True)
    column_filters_json = t.Unicode('').tag(sync=True)
    column_type_json = t.Unicode('').tag(sync=True)
    has_rendered = t.Bool(True).tag(sync=True)
    user_email = t.Unicode('').tag(sync=True)
    step_summaries_list_json = t.Unicode('').tag(sync=True)
    should_upgrade_mitosheet = t.Bool(False).tag(sync=True)
    data_type_in_mito = t.Unicode('').tag(sync=True)
    received_tours = t.Unicode('').tag(sync=True)
    num_feedbacks = t.Int(0).tag(sync=True)
    num_usages = t.Int(0).tag(sync=True)

    def __init__(self, *args, **kwargs):
        """
        Takes a list of dataframes and strings that are paths to CSV files
        passed through *args.
        """
        # Call the DOMWidget constructor to set up the widget properly
        super(MitoWidget, self).__init__()

        # Set if this is a local deployment
        self.is_local_deployment = is_local_deployment()

        # Mark if it is time for the user to update
        self.should_upgrade_mitosheet = should_upgrade_mitosheet()
            
        # Set up the state container to hold private widget state
        self.steps_manager = StepsManager(args)
        
        # When the widget is first created, it has not been rendered on the frontend yet,
        # but after it is rendered once, this is set to False. This helps us detect 
        # when we are rendering for the first time vs. refreshing the sheet
        self.has_rendered = False

        # Set up starting shared state variables
        self.update_shared_state_variables()

        # Set up message handler
        self.on_msg(self.receive_message)

        # And the api
        self.api = API(self.steps_manager, self.send)

        # We also update the variables that mark how many times
        # the user has given feedback, as well as how many times
        # the user has used the tool
        self.num_feedbacks = len(get_user_field(UJ_FEEDBACKS))
        self.num_usages = len(get_user_field(UJ_MITOSHEET_LAST_FIFTY_USAGES))


    def update_shared_state_variables(self):
        """
        Helper function for updating all the variables that are shared
        between the backend and the frontend through trailets.
        """
        self.sheet_json = self.steps_manager.sheet_json
        self.curr_step_idx = self.steps_manager.curr_step_idx
        self.column_spreadsheet_code_json = self.steps_manager.column_spreadsheet_code_json
        self.code_json = self.steps_manager.code_json
        self.df_names_json = self.steps_manager.df_names_json
        self.df_sources_json = self.steps_manager.df_sources_json
        self.df_shape_json = self.steps_manager.df_shape_json
        self.analysis_name = self.steps_manager.analysis_name
        self.saved_analysis_names_json = saved_analysis_names_json()
        self.column_filters_json = self.steps_manager.column_filters_json
        self.column_type_json = self.steps_manager.column_type_json
        self.user_email = self.steps_manager.user_email
        self.step_summaries_list_json = self.steps_manager.step_summaries_list_json
        self.data_type_in_mito = str(self.steps_manager.data_type_in_mito)
        self.received_tours = self.steps_manager.received_tours


    def handle_edit_event(self, event):
        """
        Handles an edit_event. Per the spec, an edit_event
        updates both the sheet and the codeblock, and as such
        the sheet is re-evaluated and the code for the codeblock
        is re-transpiled.

        Useful for any event that changes the state of both the sheet
        and the codeblock!
        """
        # First, we send this new edit to the evaluator
        self.steps_manager.handle_edit_event(event)

        # We update the state variables 
        self.update_shared_state_variables()

        # Also, write the analysis to a file!
        write_analysis(self.steps_manager)

        # Tell the front-end to render the new sheet and new code with an empty
        # response. NOTE: in the future, we can actually send back some data
        # with the response (like an error), to get this response in-place!        
        self.send({
            'event': 'response',
            'id': event['id']
        })



    def handle_update_event(self, event):
        """
        This event is not the user editing the sheet, but rather information
        that has been collected from the frontend (after render) that is being
        passed back.

        For example:
        - Names of the dataframes
        - Name of an existing analysis
        """
        # If this is just a message to notify the backend that we have rendered, set and return
        if event['type'] == 'has_rendered_update':
            self.has_rendered = True
            return

        self.steps_manager.handle_update_event(event)

        # Update all state variables
        self.update_shared_state_variables()

        # Also, write the analysis to a file!
        write_analysis(self.steps_manager)

        # Tell the front-end to render the new sheet and new code with an empty
        # response. NOTE: in the future, we can actually send back some data
        # with the response (like an error), to get this response in-place!
        self.send({
            'event': 'response',
            'id': event['id']
        })

    def receive_message(self, widget, content, buffers=None):
        """
        Handles all incoming messages from the JS widget. There are two main
        types of events:

        1. edit_event: any event that updates the state of the sheet and the
        code block at once. Leads to reevaluation, and a re-transpile.

        2. update_event: any event that isn't caused by an edit, but instead
        other types of new data coming from the frontend (e.g. the df names 
        or some existing steps).

        3. A log_event is just an event that should get logged on the backend.
        """
        event = content

        try:
            if event['event'] == 'edit_event':
                self.handle_edit_event(event)
            elif event['event'] == 'update_event':
                self.handle_update_event(event)
            elif event['event'] == 'api_call':
                self.api.process_new_api_call(event)
                return 
            
            # NOTE: we don't need to case on log_event above because it always gets
            # passed to this function, and thus is logged. However, we do not log
            # api calls, as they are just noise.
            log_event_processed(event, self.steps_manager)
        except EditError as e:
            print(get_recent_traceback_as_list())
            print(e)
            
            # Log processing this event failed
            log_event_processed(event, self.steps_manager, failed=True, edit_error=e)

            # Report it to the user, and then return
            self.send({
                'event': 'edit_error',
                'id': event['id'],
                'type': e.type_,
                'header': e.header,
                'to_fix': e.to_fix
            })
        except:
            print(get_recent_traceback_as_list())
            # We log that processing failed, but have no edit error
            log_event_processed(event, self.steps_manager, failed=True)
            # Report it to the user, and then return
            self.send({
                'event': 'edit_error',
                'id': event['id'],
                'type': 'execution_error',
                'header': 'Execution Error',
                'to_fix': 'Sorry, there was an error during executing this code.'
            })

def sheet(
        *args, 
        saved_analysis_name=None
    ) -> MitoWidget:
    """
    Renders a Mito sheet. If no arguments are passed, renders an empty sheet. Otherwise, renders
    any dataframes that are passed. Errors if any given arguments are not dataframes or paths to
    CSV files that can be read in as dataframes.

    If running this function just prints text that looks like `MitoWidget(...`, then you need to 
    install the JupyterLab extension manager by running:

    jupyter labextension install @jupyter-widgets/jupyterlab-manager@2;

    Run this command in the terminal where you installed Mito. It should take 5-10 minutes to complete.

    Then, restart your JupyterLab instance, and refresh your browser. Mito should now render.

    NOTE: if you have any issues with installation, please book a demo at https://hubs.ly/H0FL1920
    """
    args = list(args)

    # We error if the saved analysis does not exist
    if saved_analysis_name is not None and read_and_upgrade_analysis(saved_analysis_name) is None:
        log(
            'mitosheet_sheet_call_failed', 
            {'error': f'There is no saved analysis with the name {saved_analysis_name}.'}
        )
        raise ValueError(f'There is no saved analysis with the name {saved_analysis_name}.')

    try:
        # We pass in the dataframes directly to the widget
        widget = MitoWidget(*args) 

        # Log they have personal data in the tool if they passed a dataframe
        # that is not tutorial data or sample data from import docs
        if widget.steps_manager.data_type_in_mito == DataTypeInMito.PERSONAL:
            log('used_personal_data') 

    except:
        log_recent_error('mitosheet_sheet_call_failed')
        raise

    # Then, we log that the call was successful, along with all of it's params
    log(
        'mitosheet_sheet_call',
        dict(
            **{
                'param_saved_analysis_name': saved_analysis_name
            },
            **{
                # NOTE: analysis name is the UUID that mito saves the analysis under
                'steps_manager_analysis_name': widget.steps_manager.analysis_name,
            },
            **{
                'param_num_args': len(args),
                'params_num_str_args': len([arg for arg in args if isinstance(arg, str)]),
                'params_num_df_args': len([arg for arg in args if isinstance(arg, pd.DataFrame)]),
                'params_df_index_type': [str(type(arg.index)) for arg in args if isinstance(arg, pd.DataFrame)],
            }
        )
    )
    
    # If an analysis is passed, we pass this to the widget
    if saved_analysis_name is not None:
        widget.receive_message(widget, {
            'event': 'update_event',
            'id': get_new_id(),
            'type': 'replay_analysis_update',
            'analysis_name': saved_analysis_name,
            'import_summaries': None,
            'clear_existing_analysis': False
        })

    return widget
