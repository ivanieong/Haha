import pandas as pd
import numpy as np
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def countif(value, seq):
    return sum(1 for item in seq if (value <= item))

def gen_data(data, day_range):
  dayHigh = data['High'].reset_index(drop=True) 
  dayLow = data['Low'].reset_index(drop=True)
  dayClose = data['Close'].reset_index(drop=True)
  dayAdjClose = data['Adj Close'].reset_index(drop=True)
  output = []
  for i in range(day_range):
    tmp_array = []
    for j in range(day_range):
      if ( j >= i ):
        period_highest = (((dayHigh[i:(j+1)].max() + dayAdjClose[i] - dayClose[i])/(dayLow[i] + dayAdjClose[i] - dayClose[i])) - 1) * 100
      else:
        period_highest = 0
      tmp_array.insert(j, period_highest)
      continue
    output.append(tmp_array)
  output = np.round_(output, decimals = 2)
  print(output)
  return output

def get_raw_data(code):
  raw_data = pd.read_csv(code + '.csv', index_col='Date')
  raw_data.index = pd.to_datetime(raw_data.index)
  begin_year = raw_data.index.year.min()
  set_begin = pd.DataFrame({},index =[pd.to_datetime(str(begin_year) + '-01-01')])
  raw_data = pd.concat([set_begin, raw_data])
  raw_data = raw_data.resample('1D').bfill().reset_index()
  raw_data = raw_data.fillna(method="ffill").fillna(method="bfill")
  raw_data.rename(columns = {'index':'Date'}, inplace=True)
  print(raw_data)
  #raw_data[["Day"]] = raw_data["Date"].dt.day
  #raw_data[["Month"]] = raw_data["Date"].dt.month
  raw_data[["Year"]] = raw_data["Date"].dt.year
  return raw_data, begin_year
#print(raw_data)

def get_high_low_of_every_year(raw_data, years, begin_month, begin_day, end_month, end_day):
  high_of_every_year = []
  for y in years:
    begin_date = pd.Timestamp(y,begin_month,begin_day)
    end_date = pd.Timestamp(y,end_month,end_day)
    request_data = raw_data.loc[(raw_data["Date"] >= begin_date) & (raw_data["Date"] <= end_date)]
    print('=========' + str(y) + '==========')
    #print(request_data)
    day_range = len(request_data)
    output = gen_data(request_data, len(request_data))
    high_of_every_year.append(output)
  return high_of_every_year

#find 90% value
def get_final_output(prob, history_years, day_range):
  pos = np.floor((1 - prob) * len(history_years)).astype(int)
  final_output = []
  prob_output = []
  #print("find pos in tmp:" + str(pos))
  for j in range(day_range):
    final_row = []
    prob_row = []
    for k in range(day_range):
      tmp = []
      for i in range(len(history_years)):
        tmp.append(high_of_every_year[i][j][k])
      tmp = np.sort(tmp)
      target = tmp[pos]
      final_row.insert(k, target)
      prob_row.insert(k, countif(target, tmp)/len(history_years))
    final_output.append(final_row)
    prob_output.append(prob_row)
  return (np.round_(final_output, decimals = 2)), (np.round_(prob_output, decimals = 2)), (np.amax(final_output))

#begin input value
begin_month = 7
end_month = 7
begin_day = 1
end_day = 31
prob = 0.9
code = '0700'
#end input value
raw_data, begin_year = get_raw_data(code)
day_range = (pd.Timestamp(begin_year,end_month,end_day) - pd.Timestamp(begin_year,begin_month,begin_day)).days + 1
years = np.sort(raw_data.Year.unique())
#years = [2019,2020,2021]
history_years = np.delete(years, len(years) - 1)
#months = np.sort(raw_data.Month.unique())
#days = np.sort(raw_data.Day.unique())
#print(history_years, months, days)
high_of_every_year = get_high_low_of_every_year(raw_data, history_years, begin_month, begin_day, end_month, end_day)
final_output, prob_output, higest_pencentage = get_final_output(prob, history_years, day_range)
print(final_output)
print(prob_output) 
print(str(higest_pencentage) + '%')
result_begin_offset = np.where(final_output == np.amax(final_output))[0][0]
result_end_offset = np.where(final_output == np.amax(final_output))[1][0]
result_begin_date = pd.Timestamp(begin_year, begin_month, begin_day) + pd.Timedelta(days=result_begin_offset)
result_end_date = pd.Timestamp(begin_year, begin_month, begin_day) + pd.Timedelta(days=result_end_offset)
print('Period: ' + str(result_begin_date.month) + "-" + str(result_begin_date.day) + " to " + str(result_end_date.month) + "-" + str(result_end_date.day))