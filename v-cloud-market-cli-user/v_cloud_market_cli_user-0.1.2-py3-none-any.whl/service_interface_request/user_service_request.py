from rich.console import Console

class UserServiceRequest:

    def __init__(self, console: Console):
        self.console = console

    def get_user_service_id(self) -> str:
        msg = '[bright_green]Please enter order id for detail: '
        return self.console.input(msg)

    def get_api_func(self, apis) -> (bool, str):
        api_types = ['normal', 'secret']
        while True:
            is_secret = False
            self.console.print('Please Choose API Type: ')
            msg = '[purple]1[/] -- Normal API Request\n' + \
                '[purple]2[/] -- Secret API Request\n'
            self.console.print(msg)
            choice = self._get_int_num('[bright_green]Please choose a number: ')
            if choice < 1 or choice > 2:
                continue
            is_secret = choice == 2
            while True:
                keys = list(apis[api_types[choice-1]].keys())
                api_func_msg = ''
                for index in range(len(keys)):
                    api_func_msg += f'[purple]{index+1}[/]' + ' -- ' + keys[index] + '\n'
                self.console.print(api_func_msg)
                api_func_choice = self._get_int_num('[bright_green]Please choose an API function: ')
                while api_func_choice < 1 or api_func_choice > len(keys):
                    self.console.print('[bright_red]!! Invalid Index Number !!\n')
                    api_func_choice = self._get_int_num('[bright_green]Please choose an API function: ')
                return is_secret, keys[api_func_choice-1]

    def _get_int_num(self, msg):
        try:
            choice = int(self.console.input(msg))
            return choice
        except ValueError:
            self.console.print('[bright_red]The input you entered in invalid.')
            return 0
