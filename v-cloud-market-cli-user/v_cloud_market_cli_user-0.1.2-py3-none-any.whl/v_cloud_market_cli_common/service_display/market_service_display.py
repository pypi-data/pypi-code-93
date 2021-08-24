from rich.console import Console
from rich.panel import Panel
from rich.measure import Measurement
from rich.table import Table
from rich import box


class MarketServiceDisplay:

    def __init__(self, console: Console):
        self.console = console

    def display_service_page(self, result: dict):
        self.console.clear()
        table = Table(show_header=True, header_style='bright_magenta')
        table.title = '[bold magenta]Service Type Information'
        table.box = box.ROUNDED
        table.add_column('Service ID')
        table.add_column('Service Provider')
        table.add_column('Service Name')
        table.add_column('Service Options', no_wrap=True, justify='full')
        table.add_column('Available Service API', no_wrap=True)
        table.add_column('Refundable')
        table.add_column('Duration To Price', no_wrap=True)
        table.add_column('Description')

        for row in self._form_service_type_rows(result['list']):
            table.add_row(*row)
        self.console.print(table, justify='center')
        return Measurement.get(self.console, table).maximum

    def display_category_page(self, result: dict):
        self.console.clear()
        table = Table(show_header=True, header_style='bright_magenta')
        table.title = '[bold magenta]Service Category Information'
        table.box = box.ROUNDED
        table.add_column('Service Category ID')
        table.add_column('Provider')
        table.add_column('Category Name')
        table.add_column('Service Type')
        table.add_column('Service Options')
        table.add_column('Description')

        for row in self._form_category_rows(result['list']):
            table.add_row(*row)
        self.console.print(table, justify='center')
        return Measurement.get(self.console, table).maximum

    def display_provider_page(self, result: dict):
        self.console.clear()
        table = Table(show_header=True, header_style='bright_magenta')
        table.title = '[bold magenta]Service Provider Information'
        table.box = box.ROUNDED
        table.add_column('Provider Name')
        table.add_column('Wallet Address')
        table.add_column('Provided Service Category Name')

        for row in self._form_provider_rows(result['list']):
            table.add_row(*row)
        self.console.print(table, justify='center')
        return Measurement.get(self.console, table).maximum

    def _form_provider_rows(self, providers):
        rows = []
        for provider in providers:
            row = [provider['name'], provider['walletAddress']]
            categories = ''
            for c in provider['category2ID'].keys():
                categories += c + '\n'
            row.append(categories)
            rows.append(row)
        return rows

    def _form_category_rows(self, categories):
        rows = []
        for category in categories:
            row = [category['categoryID'], category['provider'], category['name']]
            service_type = ''
            service_opts = ''

            if category['name2ID']:
                for sType in category['name2ID'].keys():
                    service_type += sType + '\n'

            if category['serviceOptions']:
                service_opts = self._form_service_options(category['serviceOptions'])
            row.extend([service_type, service_opts, category['description']])
            rows.append(row)
        return rows

    def _form_service_type_rows(self, service_types):
        rows = []
        for service_type in service_types:
            row = [service_type['id'], service_type['provider'], service_type['name'],
                   self._form_service_options(service_type['serviceOptions']),
                   self._form_service_api((service_type['serviceAPI'])),  str(service_type['refundable']),
                   self._form_duration_to_price(service_type['durationToPrice']), service_type['description']]
            rows.append(row)
        return rows

    def _form_service_options(self, serviceOptions) -> str:
        service_opts = ''
        if not serviceOptions or len(serviceOptions) == 0:
            return service_opts
        for opt_key in serviceOptions.keys():
            service_opts += '[bright_green]' + opt_key + ':[/]\n'
            for opt in serviceOptions[opt_key]:
                service_opts += ' ' * 4 + opt + '\n'
        return service_opts

    def _form_duration_to_price(self, duration_to_prices) -> str:
        result = ''
        for ps in duration_to_prices:
            tmp = ''
            tmp += '[bold bright_green]Price: ' + str(ps['price']) + '\n'
            tmp += '[bold bright_green]Charging Service Options: \n'
            for opt in ps['chargingOptions']:
                tmp += '\t[light_cyan1]' + opt + ': ' + ps['chargingOptions'][opt] + '\n'
            tmp += '[bold bright_green]Price Factor for Different Time Period:\n'
            for d in ps['duration']:
                tmp += '\t[light_cyan1]' + str(d) + ' hour: ' + str(ps['duration'][d]) + '\n'
            result += tmp + '\n'
            result += "=" * Measurement.get(self.console, result).maximum + '\n'
        return result

    def _form_service_api(self, service_apis):
        result = '[bold magenta]API Types\n'
        for api in service_apis:
            if isinstance(service_apis[api], dict):
                result += f'[bold bright_green]{api} API:\n'
                for key in service_apis[api]:
                    result += ' ' * 4 + f'[bold cyan1]{key}\n'
        return result

    def _form_name_to_id(self, name2ID):
        result = ''
        for k in name2ID:
            row = f'[bright_green]{k}[/]: {name2ID[k]}'
            result += row + '\n'
        return result

    def display_order_brief(self, info):
        msg = '[bold bright_magenta]Order ID[/]: ' + info['id'] + '\n' + \
              '[bold bright_magenta]Recipient[/]: ' + info['recipient'] + '\n' + \
              '[bold bright_magenta]Amount[/]: ' + str(info['amount'])
        self.console.print(Panel.fit(msg,
                                     title='[bold bright_green]! New Order Created !',
                                     title_align='center'),
                           justify='center')
        self.console.input('Press ENTER to continue...')

    def display_service_type(self, info):
        msg = '[bold bright_magenta]Service Type ID:[/] ' + info['id'] + '\n' + \
              '[bold bright_magenta]Service Name:[/] ' + info['name'] + '\n' + \
              '[bold bright_magenta]Service Category:[/] ' + info['category'] + '\n' + \
              '[bold bright_magenta]Provider:[/] ' + info['provider'] + '\n' + \
              '[bold bright_magenta]Refundable:[/] ' + str(info['refundable']) + '\n' + \
              '[bold bright_magenta]Service Options:[/] \n' + self._form_service_options(info['serviceOptions']) + '\n' + \
              '[bold bright_magenta]Duration To Price:[/] \n' + self._form_duration_to_price(info['durationToPrice'])
        self.console.print(Panel.fit(msg,
                                     title='[bold bright_green]Service Type Information',
                                     title_align='center'))
        self.console.input('Press ENTER to continue...')

    def display_service_category(self, info):
        msg = '[bold bright_magenta]Category ID:[/] ' + info['categoryID'] + '\n' + \
              '[bold bright_magenta]Category Name:[/] ' + info['name'] + '\n' + \
              '[bold bright_magenta]Provider:[/] ' + info['provider'] + '\n' + \
              '[bold bright_magenta]Description:[/] ' + info['description'] + '\n' + \
              '[bold bright_magenta]Service Options:[/]\n' + self._form_service_options(info['serviceOptions']) + '\n' + \
              '[bold bright_magenta]Service Type To ID:[/]\n' + self._form_name_to_id(info['name2ID'])
        self.console.print(Panel.fit(msg,
                                     title='[bold bright_green]Service Category Information',
                                     title_align='center'))
        self.console.input('Press ENTER to continue...')

    def display_provider(self, info):
        msg = '[bold bright_magenta]Name:[/] ' + info['name'] + '\n' + \
              '[bold bright_magenta]Wallet Address:[/] ' + info['walletAddress'] + '\n' + \
              '[bold bright_magenta]Service Category To ID:[/]\n' + self._form_name_to_id(info['category2ID'])
        self.console.print(Panel.fit(msg,
                                     title='[bold bright_green]Service Provider Information',
                                     title_align='center'))
        self.console.input('Press ENTER to continue...')
