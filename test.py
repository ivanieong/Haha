import pandas as pd
import numpy as np
import datetime
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

raw_data = pd.read_csv('0700.csv', index_col = 'Date')
print(raw_data)
raw_data = raw_data.head(20)
new_index = pd.date_range(start='2004-06-01', end='2004-06-30')
raw_data.reindex(new_index)
print(raw_data)

#dd = pd.read_csv('0700.csv', parse_dates=['Date'])
raw_data[["day", "month", "year"]] = raw_data["Date"].str.split("/", expand = True)
#print(raw_data)
raw_data = raw_data.dropna()
df = raw_data.reset_index(drop=True)

(row, num_col) = df.shape

a = df['High'].head(20)
b = df['Open'].head(20)

output = []
for i in range(len(b)):
  tmp_array = []
  for j in range(len(a)):
    if ( j >= i ):
      up = ((a[j]/b[i]) - 1) * 100
    else:
      up = 0
    tmp_array.insert(j, up)
    continue
  output.append(tmp_array)
output = np.round_(output, decimals = 2)
print(len(output))