import json

def check_sectors(input_file):
    with open(input_file) as fp:
        data = json.load(fp)
        print(data)
        print(len(data))
        return data

def load_tickers_list(input_file):
    """
    Load tickers list from file
    """
    tickers_list = []
    with open(input_file) as fp:
        for line in fp:
            ticker = line.strip()
            tickers_list.append(ticker)
    return tickers_list

vn30_tickers = load_tickers_list("./eagle/eagle_datastore/data_refs/vn30.txt")
all_tickers = load_tickers_list("./eagle/eagle_datastore/data_refs/tickers.txt")
etf_tickers = load_tickers_list("./eagle/eagle_datastore/data_refs/etf.txt")
data = check_sectors("./eagle/eagle_datastore/data_refs/sector_tickers.json")
data['vn30'] = vn30_tickers
data['all'] = all_tickers
data['etf'] = etf_tickers
# pprint(data)

with open("./eagle/eagle_datastore/data_refs/group_tickers.json", "w") as fp:
    json.dump(data, fp)

