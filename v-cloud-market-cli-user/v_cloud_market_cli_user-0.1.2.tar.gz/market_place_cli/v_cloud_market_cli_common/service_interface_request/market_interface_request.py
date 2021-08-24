import math
from rich.console import Console
from datetime import datetime

from market_place_cli.v_cloud_market_cli_common.service_display.display_common import utc_to_local


class MarketServiceRequest:

    def __init__(self, console: Console):
        self.console = console

    def get_category_name(self) -> str:
        msg = '[bright_green]Please enter category name: '
        return self.console.input(msg)

    def get_provider_name(self) -> str:
        msg = '[bright_green]Please enter provider name: '
        return self.console.input(msg)

    def get_service_id(self) -> str:
        msg = '[bright_green]Please enter service id: '
        return self.console.input(msg)

    def get_display_qr_code(self) -> bool:
        msg = '[bright_green]Show send payment QR code (default n) [Y/n]: '
        choice = self.console.input(msg)

        if choice.lower() not in ['y', 'n', '']:
            choice = 'n'
        if choice == '':
            choice = 'n'
        return choice.lower() == 'y'

    def user_choose_options(self, options) -> dict:
        result = {}
        for key in options:
            self.console.print(f'Choose service option for [bold magenta]{key}[/]:')
            choice_output = ''
            for index in range(len(options[key])):
                choice_output += f'[purple]{index + 1}[/]' + ' -- ' + options[key][index] + '\n'
            self.console.print(choice_output)
            choice = self._get_int_num('[bright_green]Please choose a number: ')
            while choice < 1 or choice > len(options[key]):
                choice = self._get_int_num('[bright_green]Please choose a number: ')
            result[key] = options[key][choice-1]
        return result

    def user_choose_duration(self, price_set):
        duration_result = {}
        self.console.print('\nPlease choose time duration ( HOUR ) on the left. '
                           'The right side is corresponding price factor.')
        self.console.print('[magenta]0: Enter A Custom Expiration Date in YYYY-MM-DD hh:mm:ss')
        for key in price_set['duration']:
            self.console.print('[magenta]' + str(key) + '[/] : ' + '[cyan]' + str(price_set['duration'][key]))
        self.console.print('\n')

        min_hour = self._get_min(price_set['duration'].keys())
        duration = self._get_int_num('[bright_green]Please enter the time duration number: ')
        if duration == 0:
            FMT = '%Y-%m-%d %H:%M:%S'
            date_str = self.console.input('[bright_green]Please enter expired date: ')
            time_delta = datetime.strptime(date_str, FMT) - datetime.now()
            total_time = math.ceil(time_delta.total_seconds() / 3600)
            if total_time <= 0:
                self.console.print('[bright_red]Invalid Expiration Date!!')
                return self.user_choose_duration(price_set)
            duration_result['time'] = total_time
            duration_result['expiredDate'] = utc_to_local(datetime.strptime(date_str, FMT)).strftime('%Y-%m-%d')
            return duration_result
        while duration < min_hour:
            self.console.print('[bright_red]The number you entered is not available.\n')
            duration = self._get_int_num('[bright_green]Please enter the time duration number: ')
        duration_result['time'] = duration
        return duration_result

    def _get_int_num(self, msg):
        try:
            choice = int(self.console.input(msg))
            return choice
        except ValueError:
            self.console.print('[bright_red]The input you entered is invalid.')
            return 0

    def _get_min(self, strList) -> int:
        result = []
        for a in strList:
            result.append(int(a))
        return min(result)
