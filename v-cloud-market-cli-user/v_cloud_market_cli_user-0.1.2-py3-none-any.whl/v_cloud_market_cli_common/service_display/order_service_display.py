from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.measure import Measurement
from rich.panel import Panel
from rich import box

from market_place_cli.v_cloud_market_cli_common.service_display.display_common import utc_to_local


class OrderServiceDisplay:

    def __init__(self, console: Console):
        self.console = console

    def display_order_page(self, title: str, page_result: dict) -> int:
        self.console.clear()
        table = Table(show_header=True, header_style='magenta')
        if len(page_result["list"]) > 0:
            table.title = '[bold magenta]' + title + f' --- Address: {page_result["list"][0]["address"]}'
        else:
            table.title = '[bold magenta]' + title + ' --- Address: there is no pending orders'
        table.box = box.SIMPLE_HEAD
        table.add_column('Order ID', justify='center')
        table.add_column('Order Status', justify='center')
        table.add_column('Creation Time', justify='center')
        table.add_column('Service Type', justify='center')
        table.add_column('Recipient Address', justify='center')
        table.add_column('Duration (hour)', '[u]432,000,000', justify='right')
        table.add_column('Amount (VSYS)', '[u]412,000,000', justify='right')
        table.add_column('Amount Paid (VSYS)', '[u]412,000,000', justify='right')
        table.add_column('Service Enabled', justify='center')
        for row in self.form_order_rows(page_result['list']):
            table.add_row(*row)
        self.console.print(table, justify='center')
        return Measurement.get(self.console, table).maximum

    def display_order_info(self, order_info):
        timeStr = utc_to_local(datetime.utcfromtimestamp(int(order_info['createdAt']))).strftime('%Y-%m-%d %H:%M:%S')
        optionMsg = ''
        for k in order_info['serviceOptions']:
            optionMsg += ' ' * 21 + f'[bright_green]' + k + ':[/] ' + order_info['serviceOptions'][k] + '\n'

        msg = '[bold magenta]Address:[/] ' + ' ' * 12 + order_info['address'] + '\n' + \
              '[bold magenta]Order ID:[/] ' + ' ' * 11 + order_info['id'] + '\n' + \
              '[bold magenta]Service:[/] ' + ' ' * 12 + order_info['service'] + '\n' + \
              '[bold magenta]Service ID:[/] ' + ' ' * 9 + order_info['serviceID'] + '\n' + \
              '[bold magenta]Recipient:[/] ' + ' ' * 10 + order_info['recipient'] + '\n' + \
              '[bold magenta]Creation Time:[/] ' + ' ' * 6 + timeStr + '\n' + \
              '[bold magenta]Duration (hour):[/] ' + ' ' * 4 + str(order_info['duration']) + '\n' + \
              '[bold magenta]Amount (VSYS):[/] ' + ' ' * 6 + str(order_info['amount']) + '\n' + \
              '[bold magenta]Amount Paid (VSYS):[/] ' + ' ' + str(order_info['amountPaid']) + '\n' + \
              '[bold magenta]Status:[/] ' + ' ' * 13 + str(order_info['status']) + '\n' + \
              '[bold magenta]Service Enabled:[/]' + ' ' * 5 + str(order_info['serviceActivated']) + '\n' + \
              '[bold magenta]Service Options:[/] \n%s' % optionMsg
        self.console.print(Panel.fit(msg))
        self.console.input('Press ENTER to continue...')

    def form_order_rows(self, orderList: [dict]) -> [[str]]:
        rows = []
        for order in orderList:
            row = [order['id'], order['status']]
            time_dt = datetime.utcfromtimestamp(int(order['createdAt']))
            timeStr = utc_to_local(time_dt).strftime('%Y-%m-%d %H:%M:%S')
            row.extend([
                timeStr,
                order['service'],
                order['recipient'],
                str(order['duration']),
                str(order['amount']),
                str(order['amountPaid']),
                'true' if order['serviceActivated'] else 'false'
            ])
            rows.append(row)
        return rows
