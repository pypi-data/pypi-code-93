'''
Security details calculation
'''
from .ledger_exec import LedgerExecutor


class SecurityDetails:
    '''
    The idea is to calculate the security details: 
    - average price (this will come with --average-lot-prices)
    - yield in the last 12 months
        - get the distributions "^income and :symbol$" in the last 12 months
        - divide by the current value
    '''
    def __init__(self, logger, symbol, currency):
        super().__init__()

        self.logger = logger
        self.symbol = symbol
        # The currency to use for all values
        self.currency = currency
    
    def calculate(self):
        '''
        The main method, which calculates everything.
        '''
        result = {}
        # result['message'] = ''
        # ledger = LedgerExecutor(self.logger)

        # lots
        # ledger_cmd = f'b ^Assets and :{self.symbol}$ --lots --no-total --depth 2'
        # lots = ledger.run(ledger_cmd)
        # result['lots'] = lots

        # average price
        # result['avg_price'] += 'N/A'

        # yield in the last 12 months
        result['yield'] = self.get_yield()

        # Gain/Loss
        result['g/l'] = self.get_gainloss()

        # income (demo)
        # income = self.get_income()
        # result['income'] = income

        return result

    def get_gainloss(self):
        ''' Get gain/loss from ledger '''
        ledger = LedgerExecutor(self.logger)
        # --collapse = -n
        # -G = gain/loss
        ledger_cmd = f'b ^Assets and :{self.symbol}$ -G -n -X {self.currency}'
        output = ledger.run(ledger_cmd)
        number = self.get_number_from_collapse_result(output)

        result = f"{number} {self.currency}"

        return result

    def get_yield(self):
        '''
        Calculate the yield in the last 12 months.
        This, of course is affected by the recent purchases, which affect the current value!
        '''
        from decimal import Decimal

        # get the income in the last 12 months
        income_str = self.get_income_balance()
        income = Decimal(income_str)
        #self.logger.debug(f'{self.symbol} gives `{income_str}` as income string')

        # turn into a positive number
        income = abs(income)

        # get the current value
        value_str = self.get_value_balance()
        value = Decimal(value_str)

        if value == 0:
            the_yield = 0
        else:
            the_yield = income * 100 / value

        result = f'{the_yield:.2f}%'
        return result

    def get_income(self):
        from datetime import date, timedelta

        yield_start_date = date.today() - timedelta(weeks=52)
        yield_from = yield_start_date.strftime("%Y-%m-%d")
        
        ledger = LedgerExecutor(self.logger)
        # the accound ends with the symbol name
        ledger_cmd = f'b ^Income and :{self.symbol}$ -b {yield_from} --flat --no-total'
        rows = ledger.run(ledger_cmd)
        rows = ledger.split_lines(rows)
        return rows

    def get_income_balance(self):
        ''' Gets the balance of income for the security '''
        from datetime import date, timedelta
        
        ledger = LedgerExecutor(self.logger)

        yield_start_date = date.today() - timedelta(weeks=52)
        yield_from = yield_start_date.strftime("%Y-%m-%d")
        
        # the accound ends with the symbol name
        # todo: use --collapse instead
        ledger_cmd = f'b ^Income and :{self.symbol}$ -b {yield_from} --flat -X {self.currency}'
        output = ledger.run(ledger_cmd)
        output = ledger.split_lines(output)
        #self.logger.debug(f'income lines for {self.symbol}: {output}')

        total = self.get_total_from_ledger_output(output)
        return total

    def get_value_balance(self):
        ''' Gets the current value of the security holdings in the given currency '''
        ledger = LedgerExecutor(self.logger)
        cmd = f"b ^Assets and :{self.symbol}$ -X {self.currency}"
        output = ledger.run(cmd)
        output = ledger.split_lines(output)
        value = self.get_total_from_ledger_output(output)
        return value

    def get_total_from_ledger_output(self, output):
        ''' Extract the total value from ledger output '''
        from cashiersync.ledger_output_parser import LedgerOutputParser

        parser = LedgerOutputParser()
        total_line = parser.get_total_lines(output)[0]
        #self.logger.debug(total_line)
        total_numeric = self.extract_total(total_line)
        return total_numeric

    def extract_total(self, total_line):
        ''' Gets the numeric value of the total from the ledger total line '''
        #self.logger.debug(total_line)
        
        # Extract the numeric value of the income total.
        total_parts = total_line.split(' ')
        total_numeric = total_parts[0]
        #self.logger.debug(f'total: {total_numeric}')
        # Remove thousand-separator
        total_numeric = total_numeric.replace(',', '') 

        # result = Decimal(total_numeric)
        result = total_numeric
        return result

    def get_number_from_collapse_result(self, ledger_output: str):
        ''' Parses a 1-line ledger result, when --collapse is used '''
        if not ledger_output:
            return 0

        # cleanup
        ledger_output = ledger_output.strip()
        # -1,139 EUR  Assets
        parts = ledger_output.split(' ')
        assert len(parts) == 4

        number = parts[0]
        number = number.replace(',', '') 

        return number
