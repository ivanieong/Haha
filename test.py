import pandas as pd
import numpy as np
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def gen_data(day_range):
  dayHigh = raw_data['High'].head(day_range)
  dayOpen = raw_data['Open'].head(day_range)
  output = []
  for i in range(day_range):
    tmp_array = []
    for j in range(day_range):
      if ( j >= i ):
        up = ((dayHigh[j]/dayOpen[i]) - 1) * 100
      else:
        up = 0
      tmp_array.insert(j, up)
      continue
    output.append(tmp_array)
  output = np.round_(output, decimals = 2)
  print(output)

raw_data = pd.read_csv('0700.csv', index_col='Date')
raw_data.index = pd.to_datetime(raw_data.index)
raw_data = raw_data.resample('1D').ffill().reset_index()
raw_data[["Day"]] = raw_data["Date"].dt.day
raw_data[["Month"]] = raw_data["Date"].dt.month
raw_data[["Year"]] = raw_data["Date"].dt.year
print(raw_data)
#raw_data = raw_data.dropna()
#df = raw_data.reset_index(drop=True)
#raw_data = raw_data.head(10)
print(raw_data.loc[(raw_data["Day"] == 17) & (raw_data["Month"] == 6)])

years = np.sort(raw_data.Year.unique())
months = np.sort(raw_data.Month.unique())
days = np.sort(raw_data.Day.unique())
print(years, months, days)
#gen_data(10)