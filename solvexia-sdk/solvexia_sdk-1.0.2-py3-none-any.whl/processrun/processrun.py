import requests
import json
import sys
from solvexia_sdk import api

class processRuns:
    def __init__(self, process_run_id):
        self.process_run_id = process_run_id

    def get_process_run(self):
        response = api.api_get(f"processruns/{self.process_run_id}")
        api.status_code_check(response, f"Error getting the specified process run with process_run_id {self.process_run_id}")
        return response.json()
    
    def start_process_run(self):
        payload = {
            'request': 'ProcessRun_StartRq',
            'processRunId': self.process_run_id
        }
        response = api.api_post("requests", payload)
        api.status_code_check(response, f"Error starting process run with process_run_id {self.process_run_id}")
        return response.json()

    def cancel_process_run(self):
        payload = {
            'request': 'ProcessRun_CancelRq',
            'processRunId': self.process_run_id
        }
        response = api.api_post("requests", payload)
        api.status_code_check(response, f"Error cancelling process run with process_run_id {self.process_run_id}")
        return response.json()

    def get_process_run_status(self):
        response = api.api_get(f"processruns/{self.process_run_id}/runstatus")
        api.status_code_check(response, f"Error getting run status of a process run with process_run_id {self.process_run_id}")
        return response.json()

    def get_process_run_data_steps_list(self):
        response = api.api_get(f"processruns/{self.process_run_id}/steps")
        api.status_code_check(response, f"Error getting list of data steps of process run with process_run_id {self.process_run_id}")
        return response.json()
