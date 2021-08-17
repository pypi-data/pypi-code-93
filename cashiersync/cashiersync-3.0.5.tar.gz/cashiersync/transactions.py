'''
    Ledger Transactions
'''
from .ledger_exec import LedgerExecutor
from typing import List


class Transaction:
    ''' Transaction model '''
    def __init__(self):
        super().__init__()
        self.date = None
        self.payee = None
        self.account = None
        self.amount = None
        self.total = None


class LedgerTransactions:
    def __init__(self):
        super().__init__()

    def get_transactions(self, account, dateFrom, dateTo) -> List[str]:
        ''' Fetch historical transactions and return an array '''
        from cashiersync.json_helper import obj_to_dict

        ledger = LedgerExecutor(None)
        params = f'r "{account}" -b {dateFrom} -e {dateTo}'
        output = ledger.run(params)
        lines = ledger.split_lines(output)

        # Parse
        txs = []
        for line in lines:
            tx = self.__get_tx_from_line(line)
            dic = obj_to_dict(tx)
            txs.append(dic)

        return txs

    def __get_tx_from_line(self, line: str) -> Transaction:
        ''' parse ledger output line and create a Transaction object '''
        from cashiersync.ledger_output_parser import LedgerOutputParser

        parser = LedgerOutputParser()
        
        parts = line.split('  ')
        parts = parser.remove_blank_values_from_splits(parts)
        parts = parser.trim_all(parts)
        # date payee   account   amount  total
        date_payee = parts[0].split(' ')

        tx = Transaction()
        tx.date = date_payee[0]
        tx.payee = date_payee[1]
        tx.account = parts[1]
        tx.amount = parts[2]
        tx.total = parts[3]

        return tx

