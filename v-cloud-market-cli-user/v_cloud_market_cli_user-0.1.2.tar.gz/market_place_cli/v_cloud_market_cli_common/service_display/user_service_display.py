from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.measure import Measurement

from market_place_cli.v_cloud_market_cli_common.service_display.display_common import utc_to_local


class UserServiceDisplay:

    def __init__(self, console: Console):
        self.console = console

    def show_user_service_page(self, title: str, infoList: [dict]):
        self.console.clear()
        table = Table(show_header=True)
        table.title = '[bold bright_magenta]' + title
        table.box = box.ROUNDED
        table.add_column('Order ID', justify='center')
        table.add_column('Service Type', justify='center')
        table.add_column('Creation Time', justify='center')
        table.add_column('Duration (HOUR)', justify='center')
        table.add_column('Expiration Time', justify='center')
        for col in table.columns:
            col.header_style = 'magenta'

        rows = self._form_user_service_rows(infoList)
        for row in rows:
            table.add_row(*row)
        self.console.print(table, justify='center')
        return Measurement.get(self.console, table).maximum

    def show_user_service_detail(self, info):
        table = Table(show_header=True)
        table.box = box.ROUNDED
        table.title = '[bold bright_magenta]' + info['id'] + '\nUser Service Details'
        table.add_column('Service Type', justify='center')
        table.add_column('Service Options', justify='left')
        for col in table.columns:
            col.header_style = 'magenta'

        row = [info['service'], self._form_service_options(info['serviceOptions'])]
        table.add_row(*row)
        self.console.print(table, justify='center')
        self.console.input('Press ENTER to continue...')

    def display_user_service(self, info, secret: str = ''):
        msg = '[bold magenta]ID:[/] ' + info['userServiceID'] + '\n' + \
              '[bold magenta]Service:[/] ' + info['service'] + '\n' + \
              '[bold magenta]Service ID:[/] ' + info['serviceID'] + '\n' + \
              '[bold magenta]Address:[/] ' + info['address'] + '\n' + \
              '[bold magenta]Status:[/] ' + info['status'] + '\n' + \
              '[bold magenta]Service Active Timestamp:[/] ' + self.to_local_time_str(info['serviceActiveTS']) + '\n'

        if info['status'] in ['ServiceRunning', 'ServiceDone', 'ServiceAbort']:
            time_str = self.to_local_time_str(info['serviceRunningTS'])
            msg += '[bold magenta]Service Running Timestamp:[/] ' + time_str + '\n'
        if info['status'] == 'ServiceDone':
            time_str = self.to_local_time_str(info['serviceDoneTS'])
            msg += '[bold magenta]Service Done Timestamp:[/] ' + time_str + '\n'
        if info['status'] == 'ServiceAbort':
            time_str = self.to_local_time_str(info['serviceAbortTS'])
            msg += '[bold magenta]Service Abort Timestamp:[/] ' + time_str + '\n'

        msg += '[bold magenta]Service Options:[/] \n' + self._form_service_options(info['serviceOptions'])

        if secret:
            msg += '[bold magenta]Secret Info:[/] \n' + secret + '\n'
        self.console.print(Panel.fit(msg))
        self.console.input('Press ENTER to continue...')

    def _form_user_service_rows(self, infoList: [dict]) -> [[str]]:
        rows = []
        for info in infoList:
            row = [info['id'], info['service']]
            cTime = self.to_local_time_str(info['serviceActivateTS'])
            if int(info['endAt']) == 0:
                eTime = 'xxxxxx'
            else:
                eTime = self.to_local_time_str(info['endAt'])
            row.extend([cTime, str(info['duration']), eTime])
            rows.append(row)
        return rows

    def _form_service_options(self, serviceOptions) -> str:
        service_opts = ''
        if not serviceOptions or len(serviceOptions) == 0:
            return service_opts
        for opt_key in serviceOptions.keys():
            service_opts += '[bright_green]' + opt_key + ':[/]\n'
            service_opts += ' ' * 4 + serviceOptions[opt_key] + '\n'
        return service_opts

    def to_local_time_str(self, ts: str):
        return utc_to_local(datetime.utcfromtimestamp(int(ts))).strftime('%Y-%m-%d %H:%M:%S')

