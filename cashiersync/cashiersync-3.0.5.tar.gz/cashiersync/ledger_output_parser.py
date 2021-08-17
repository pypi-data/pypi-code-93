'''
The helper for Ledger output parsing
'''
from typing import List
from cashiersync.model import RegisterRow


class LedgerOutputParser:
    def __init__(self):
        super().__init__()
    
    def get_total_lines(self, output):
        '''
        Extract the total lines from the output, 
        unless there is only one account, in which case use the complete output
        '''
        result = []
        next_line_is_total = False
        total_line = None

        # Special cases
        # if len(output) == 0:
        #     return 0
        
        if len(output) == 1:
            # No income is an array with an empty string ['']
            if output[0] == '':
                total_line = "0"
            else:
                # One-line results don't have totals
                total_line = output[0]
            result.append(total_line)
        else:
            for i, item in enumerate(output):
                # get total
                if next_line_is_total:
                    total_line = output[i]
                    #self.logger.debug(f'total {total_line}')
                    result.append(total_line)
                else:
                    if '------' in output[i]:
                        next_line_is_total = True

        if total_line is None:
            raise ValueError(f'No total fetched in {output}')

        return result

    def remove_blank_values_from_splits(self, split_array: List):
        ''' Removes the empty valuse from a string split array.
        Used mostly when separating by double-space '  ', to clean up.
        '''
        # while '' in split_array:
        #     split_array.remove('')
        res = list(filter(lambda a: a != '', split_array))
        return res

    def trim_all(self, parts: List) -> List:
        ''' Trim all elemnts of a list '''
        return([x.strip() for x in parts])

    def clean_up_register_output(self, report: List[str]) -> List[str]:
        ''' 
        Clean-up the ledger register report.
        The report variable is a list of lines.
        '''
        # eliminate useless lines
        lines = []
        for line in report:
            if line == '':
                pass
            # Check the account line. If empty, skip. This is just the running total.
            elif line[50] == " ":
                # skip
                pass
            else:
                lines.append(line)

        return lines

    def get_rows_from_register(self, ledger_lines: List[str]) -> List[RegisterRow]:
        ''' Parse raw lines from the ledger register output and get RegisterRow. '''
        txs = []
        # remember the header row, which contains the medatada: date, symbol.
        prev_row = None

        for line in ledger_lines:
            tx = self.get_row_from_register_line(line, prev_row)

            if(tx.date):
                prev_row = tx

            txs.append(tx)

        return txs

    def get_row_from_register_line(self, line: str, header: RegisterRow) -> RegisterRow:
        ''' Parse one register line into a Transaction object '''
        from decimal import Decimal

        # header is the transaction with the date (and other metadata?)

        has_symbol = line[0:1] != ' '

        date_str = line[0:10].strip()
        payee_str = line[11:46].strip()
        account_str = line[46:85].strip()
        amount_str = line[85:107].strip()
            
        tx = RegisterRow()

        # Date
        if date_str == '':
            #date_str = None
            date_str = header.date
        tx.date = date_str

        # Payee
        if payee_str == '':
            # payee_str = None
            payee_str = header.payee
        tx.payee = payee_str

        # Symbol
        if has_symbol:
            parts = payee_str.split()
            symbol = parts[0]
            # We need to remove the exchange from ledger symbols, i.e. EUNY.DE
            if '.' in symbol:
                index = symbol.index('.')
                symbol = symbol[0:index]
            tx.symbol = symbol
        else:
            tx.symbol = header.symbol

        # Type
        account = account_str
        # Get just the first 3 characters.
        account = account[0: 2: 1]
        if account == "In":
            tx.type = "Dividend"
        if account == "Ex":
            tx.type = "Tax"

        # Account
        tx.account = account_str

        # Amount
        # Get from the end.
        parts = amount_str.split()
        if (len(parts) != 2):
            print(tx)
        assert len(parts) == 2

        amount_str = parts[0].replace(',', '')
        tx.amount = Decimal(amount_str)
        # Currency
        tx.currency = parts[1]

        return tx
