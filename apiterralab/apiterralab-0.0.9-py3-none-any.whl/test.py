import pandas as pd
array = [0, 1, 2, 3, 4]
def Test(array):
  return pd.Series(array)

print(Test(array))
