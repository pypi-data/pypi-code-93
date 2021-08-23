from IPython.display import clear_output
import time

from lumipy.client import Client
from lumipy.common.string_utils import indent_str


def live_status_in_cell(client: Client, ex_id: str, period: int = 1):
    """Periodically report the status of a runnning Luminesce query in a jupyter cell

    Args:
        client (Client): web client that can query the cluster the request is running on
        ex_id (str): the execution ID of the request
        period (int, optional): period in seconds to check the running request. Defaults to every 1s.

    """
    check = client.get_status(ex_id)

    progress_lines = []

    def add_line_criterion(candidate):
        existing = [pl.split('>>')[-1] for pl in progress_lines]
        return candidate.split('>>')[-1] not in existing

    print("Query launched! 🚀")
    print(f"Monitoring progress of Execution ID: {ex_id}\n")
    while check['status'] == 'WaitingForActivation':
        time.sleep(period)
#        clear_output(wait=True)
#        print("Status:", check['status'])
        for line in check['progress'].split('\n'):
            if add_line_criterion(line):
                progress_lines.append(line)
                print(line)
                
        check = client.get_status(ex_id)
    for line in check['progress'].split('\n'):
        if add_line_criterion(line):
            progress_lines.append(line)
            print(line)

#    clear_output(wait=True)
    completion_status = check['status']
    if completion_status == 'RanToCompletion':
        print(f"\nQuery finished successfully! 🛰🪐\n    Execution ID: {ex_id}")
    else:
        info_str = f"Status: {completion_status}\nExecution ID: {ex_id}"
        print(f"\nQuery was unsuccessful... 💥\n{indent_str(info_str, n=4)}")
