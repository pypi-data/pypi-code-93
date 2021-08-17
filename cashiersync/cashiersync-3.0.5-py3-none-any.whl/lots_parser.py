'''
Parse the output for lots and return the array of lots for a symbol
'''

class LotParser:
    def __init__(self, logger):
        super().__init__()

        self.logger = logger
    
    def get_lots(self, symbol):
        from .ledger_exec import LedgerExecutor
        from .ledger_output_parser import LedgerOutputParser

        assert isinstance(symbol, str)

        params = f"b ^Assets and invest and :{symbol}$ --lots --no-total --collapse"
    
        ledger = LedgerExecutor(self.logger)
        output = ledger.run(params)
        output = ledger.split_lines(output)

        #
        num_lines = len(output)
        if num_lines == 1 and output[0] == '':
            #print(f'*{output}*')
            print(f'No lots found for symbol {symbol}!')
            return None

        last_line = output[num_lines - 1]
        if "Assets" in last_line:
            #position = last_line.find("Assets")
            #last_line = last_line.substring(0, position)
            parts = last_line.split("Assets")
            last_line = parts[0].strip()
            output[num_lines - 1] = last_line

        return output

    def parse_lots(self, lots_string_array):
        ''' Parse the lot string array into the Lot objects '''
        from .model import Lot

        result = []

        for line in lots_string_array:
            parts = line.split(' ')
            lot = Lot()

            if len(parts) != 5:
                print(f'Faulty line: {parts}')
            assert len(parts) == 5

            lot.quantity = parts[0]
            lot.symbol = parts[1]

            price = parts[2]
            price = price[1:] # cut the {
            #price = price[0: len(price)]
            lot.price = price
            
            currency = parts[3]
            currency = currency[:len(currency)-1]
            lot.currency = currency
            
            date = parts[4]
            date = date[1:len(date)-1]
            lot.date = date

            result.append(lot)
        
        return result

