import pandas as pd
import numpy as np
import datetime
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def countif(value, seq):
    return sum(1 for item in seq if (value <= item))

def gen_data(data, day_range):
  dayHigh = data['High'].reset_index(drop=True)
  dayOpen = data['Low'].reset_index(drop=True)
  output = []
  for i in range(day_range):
    tmp_array = []
    for j in range(day_range):
      if ( j >= i ):
        up = ((dayHigh[:(j+1)].max()/dayOpen[i]) - 1) * 100
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
set_begin = pd.DataFrame({},index =[pd.to_datetime('2004-01-01')])
raw_data = pd.concat([set_begin, raw_data])
#set_end = pd.DataFrame({},index =[pd.to_datetime('2020-12-31')])
#raw_data = pd.concat([set_end, raw_data])
print(raw_data)
raw_data = raw_data.resample('1D').bfill().reset_index()
raw_data = raw_data.fillna(method="ffill").fillna(method="bfill")
raw_data.rename(columns = {'index':'Date'}, inplace=True)
print(raw_data)
raw_data[["Day"]] = raw_data["Date"].dt.day
raw_data[["Month"]] = raw_data["Date"].dt.month
raw_data[["Year"]] = raw_data["Date"].dt.year
years = np.sort(raw_data.Year.unique())
years = np.delete(years, len(years) - 1)
months = np.sort(raw_data.Month.unique())
days = np.sort(raw_data.Day.unique())
print(years, months, days)
#print(raw_data)
#end get raw data

#begin input value
bm = 6
em = 6
bd = 11
ed = 15
prob = 0.9
#end input value
all_years_output = []
day_range = 0
#years = [2020, 2021]
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

#find 90% value
pos = np.floor((1 - prob) * len(years)).astype(int)
final_output = []
prob_output = []
print("find pos in tmp:" + str(pos))
for j in range(day_range):
  final_row = []
  prob_row = []
  for k in range(day_range):
    tmp = []
    for i in range(len(years)):
      tmp.append(all_years_output[i][j,k])
    tmp = np.sort(tmp)
    target = tmp[pos]
    final_row.insert(k, target)
    prob_row.insert(k, countif(target, tmp)/len(years))
  final_output.append(final_row)
  prob_output.append(prob_row)
print(np.round_(final_output, decimals = 2))
print(np.round_(prob_output, decimals = 2))