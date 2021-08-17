from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from yaml import parse
from .ledger_exec import LedgerExecutor
import logging

logger = logging.getLogger("uvicorn.error")

app = FastAPI()

# CORS
# origins = [
#     'http://localhost:5000',
#     'http://0.0.0.0:5000'
# ]
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True,
    allow_methods=['*'], allow_headers=['*'])

@app.get("/")
async def hello():
    return "Hello World!"


@app.get('/hello')
async def hello_img():
    ''' Returns an image, can be used with <img> element to check online status. '''

    import io
    import base64

    # Base64 encoded pixel
    pixelEncoded = b'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    pixel = base64.b64decode(pixelEncoded)
    buf = io.BytesIO(pixel)
    
    response = StreamingResponse(buf, media_type='image/png')
    
    return response


@app.get("/accounts")
def accounts():
    params = "accounts"
    ledger = LedgerExecutor(logger)
    result = ledger.run(params)

    lines = result.split('\n')
    # clean-up blank lines
    clean_lines = [x for x in lines if x]
    output = clean_lines

    return output


@app.get("/balance")
def balance():
    params = "b --flat --no-total"
    ledger = LedgerExecutor(logger)
    result = ledger.run(params)

    return result


@app.get("/currentValues")
def currentValues(root: str, currency: str):
    '''
    Current values of accounts under the given root account and 
    in the requested currency.
    Used for Asset Allocation to get investment accounts balances.
    '''
    params = f"b ^{root} -X {currency} --flat --no-total"

    ledger = LedgerExecutor(logger)
    ledger_output = ledger.run(params)

    # Parse
    rows = ledger_output.split('\n')
    parsed = {}
    for row in rows:
        row = row.strip()
        # ignore empty rows
        if row == '':
            continue
        # split at the root account name
        index = row.index(root)
        balance = row[0:index]
        balance = balance.strip()
        account = row[index:]
        account = account.strip()
        
        parsed[account] = balance

    return parsed


@app.get("/lots")
def lots(symbol: str):
    from .lots_parser import LotParser

    parser = LotParser(logger)
    result = parser.get_lots(symbol)

    return result


@app.get('/payees')
def payees():
    ''' Send Payees as a simple list '''
    params = f"payees"
    ledger = LedgerExecutor(logger)
    result = ledger.run(params)
    return result


@app.post('/search')
async def search_tx(query: dict = Body(...)):
    ''' Search Transactions - Register '''
    from cashiersync.ledger_output_parser import LedgerOutputParser

    logger.debug(query)
    assert query is not None

    dateFrom = query['dateFrom']
    dateTo = query['dateTo']
    payee = query['payee']
    freeText = query['freeText']

    params = f'r '
    if dateFrom:
        params += f'-b {dateFrom} '
    if dateTo is not None:
        params += f'-e {dateTo} '
    if payee:
        params += f'@"{payee}" '
    if freeText:
        params += f'{freeText} '

    # Do we have any parameters?
    if params == f'r ':
        return {'message': 'No parameters sent!'}

    ledger = LedgerExecutor(logger)
    result = ledger.run(params)

    lines = result.split('\n')
    parser = LedgerOutputParser()
    lines = parser.clean_up_register_output(lines)

    txs = parser.get_rows_from_register(lines)

    return txs


@app.get('/securitydetails')
def security_details(symbol: str, currency: str):
    ''' Displays the security details (analysis) '''
    from .sec_details import SecurityDetails

    # symbol = request.args.get('symbol')
    # currency = request.args.get('currency')
    logger.debug(f'parameters: {symbol}, {currency}')

    x = SecurityDetails(logger, symbol, currency)
    result = x.calculate()

    return result


@app.get('/transactions')
def transactions(account: str, dateFrom: str, dateTo: str):
    ''' Fetch the transactions in account for the giver period '''
    from .transactions import LedgerTransactions

    # account = request.args.get('account')
    # dateFrom = request.args.get('dateFrom')
    # dateTo = request.args.get('dateTo')

    assert account is not None
    assert dateFrom is not None
    assert dateTo is not None

    tx = LedgerTransactions()
    txs = tx.get_transactions(account, dateFrom, dateTo)

    return txs


@app.post('/xact')
async def xact(query: dict = Body(...)):
    # query = request.get_json()
    logger.debug(f'query={query}')
    params = 'xact '

    if 'date' in query:
        date_param = query['date']
        params += date_param + ' '
    if 'payee' in query:
        params += f'@"{query["payee"]}" '
    if 'freeText' in query:
        free_text = query['freeText']
        params += free_text

    assert params != 'xact '

    ledger = LedgerExecutor(logger)
    try:
        result = ledger.run(params)
    except Exception as error:
        result = str(error)

    return result


@app.get('/about')
def about():
    ''' display some diagnostics '''
    import os
    cwd = os.getcwd()
    return f"cwd: {cwd}"

# Operations

# @app.get('/shutdown')
# def shutdown():
#     # app.do_teardown_appcontext()

#     func = request.environ.get('werkzeug.server.shutdown')
#     if func is None:
#         raise RuntimeError('Not running with the Werkzeug Server')
#     func()

###################################


def run_server():
    ''' Available to be called from outside, i.e. console scripts in setup. '''
    # Prod setup:
    # debug=False
    import uvicorn
    uvicorn.run("cashiersync.main:app", host="0.0.0.0", port=5000)
    # log_level='debug'
    # log_level="info"


##################################################################################
if __name__ == '__main__':
    run_server()
