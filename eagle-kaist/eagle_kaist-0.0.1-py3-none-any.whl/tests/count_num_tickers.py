import pandas as pd

data = pd.read_csv("./eagle_datastore/data_refs/amibroker_all_data_2.txt")
print(data)

print(len(pd.unique(data['<Ticker>'])))
