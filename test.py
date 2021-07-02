import pandas as pd
import numpy as np
import datetime
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def gen_data(data, day_range):
  dayHigh = data['High'].reset_index(drop=True)
  dayOpen = data['Open'].reset_index(drop=True)
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
  return output

#begin get raw data
raw_data = pd.read_csv('0700.csv', index_col='Date')
raw_data.index = pd.to_datetime(raw_data.index)
raw_data = raw_data.resample('1D').ffill().reset_index()
raw_data[["Day"]] = raw_data["Date"].dt.day
raw_data[["Month"]] = raw_data["Date"].dt.month
raw_data[["Year"]] = raw_data["Date"].dt.year
years = np.sort(raw_data.Year.unique())
months = np.sort(raw_data.Month.unique())
days = np.sort(raw_data.Day.unique())
print(years, months, days)
#print(raw_data)
#end get raw data

#begin input value
bm = 6
em = 6
bd = 16
ed = 20
#end input value
all_years_output = []
day_range = 0
#years = [2018, 2019, 2020, 2021]
for y in years:
  begin_date = pd.Timestamp(y,bm,bd)
  end_date = pd.Timestamp(y,em,ed)
  request_data = raw_data.loc[(raw_data["Date"] >= begin_date) & (raw_data["Date"] <= end_date)]
  print('=========' + str(y) + '==========')
  print(request_data)
  day_range = len(request_data)
  output = gen_data(request_data, len(request_data))
  all_years_output.append(output)
print(all_years_output)

for j in range(day_range):
  for k in range(day_range):
    tmp = []
    for i in range(len(years)):
      tmp.append(all_years_output[i][j,k])
    print(tmp)