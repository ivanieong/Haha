import pandas as pd
import numpy as np
import yfinance as yf
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#加back test 今年和過去
def countif(value, seq):
  return sum(1 for item in seq if (value <= item))

def remove_29Feb(s):
  mask = (s.index.year % 4 == 0) & ((s.index.year % 100 != 0) | (s.index.year % 400 == 0)) & (s.index.month == 2) & (s.index.day == 29)
  s = s.loc[~mask]
  return s

def gen_data(data, day_range):
  dayHigh = data['High'].reset_index(drop=True) 
  dayLow = data['Low'].reset_index(drop=True)
  dayClose = data['Close'].reset_index(drop=True)
  dayAdjClose = data['Adj Close'].reset_index(drop=True)
  rows, cols = (day_range, day_range)
  output = [[0 for i in range(cols)] for j in range(rows)]
  for i in range(day_range):
    for j in range(i + 1, day_range):
      if ( j > i ):
        period_highest = (((dayHigh[i:(j+1)].max() + dayAdjClose[i] - dayClose[i])/(dayLow[i] + dayAdjClose[i] - dayClose[i])) - 1) * 100
        output[i][j] = period_highest
  output = np.round_(output, decimals = 2)
  #print(output)
  return output

def get_raw_data(code):
  raw_data = pd.read_csv(code + '.csv', index_col='Date')
  raw_data.index = pd.to_datetime(raw_data.index)
  begin_year = raw_data.index.year.min()
  #========begin resample raw data========
  if (pd.to_datetime(str(begin_year) + '-01-01') not in raw_data.index):
    set_begin = pd.DataFrame({},index =[pd.to_datetime(str(begin_year) + '-01-01')])
    raw_data = pd.concat([set_begin, raw_data])
  raw_data = raw_data.resample('1D').bfill()
  ##========end resample raw data========
  raw_data = remove_29Feb(raw_data)
  raw_data = raw_data.fillna(method="ffill").fillna(method="bfill").reset_index()
  raw_data.rename(columns = {'index':'Date'}, inplace=True)
  raw_data[["Year"]] = raw_data["Date"].dt.year
  print(raw_data)
  return raw_data, begin_year

def get_high_low_of_every_year(raw_data, years, begin_month, begin_day, end_month, end_day):
  high_of_every_year = []
  for y in years:
    begin_date = pd.Timestamp(y,begin_month,begin_day)
    end_date = pd.Timestamp(y,end_month,end_day)
    request_data = raw_data.loc[(raw_data["Date"] >= begin_date) & (raw_data["Date"] <= end_date)]
    print('=========處理' + str(y) + '年中==========')
    #print(request_data)
    output = gen_data(request_data, len(request_data))
    high_of_every_year.append(output)
  return high_of_every_year, len(request_data)

#find 90% value
def get_final_output(prob, history_years, day_range):
  pos = np.floor((1 - prob) * len(history_years)).astype(int)
  final_output = []
  prob_output = []
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

#=========begin input value=========
begin_month = 5
end_month = 5
begin_day = 11
end_day = 25
prob = 0.9
code = '0670.HK'
##=========end input value=========

code = input("輸入股票代號(輸入格式如: 0700.HK/MSFT/1234.TW 等): ")
begin_month = int(input("輸入開始月份(1-12): "))
begin_day = int(input("輸入開始日期(1-31): "))
end_month = int(input("輸入結束月份(1-12): "))
end_day = int(input("輸入結束日期(1-31): "))
prob = int(input("輸入出現機率%(輸入格式如: 90, 80): ")) / 100

yf.download(code, period="max").to_csv(code + '.csv')
raw_data, begin_year = get_raw_data(code)
years = np.sort(raw_data.Year.unique())
#years = [2021]
if (len(years) > 1):
  history_years = np.delete(years, len(years) - 1)
else:
  history_years = years
#print(history_years, months, days)
high_of_every_year, day_range = get_high_low_of_every_year(raw_data, history_years, begin_month, begin_day, end_month, end_day)
final_output, prob_output, higest_pencentage = get_final_output(prob, history_years, day_range)
#print('=========歷史矩陣=========')
#print(final_output)
#print(prob_output) 
print(code + '過往' + str(len(years)) + '年' + str(prob*100) + '%機率出現最高升波幅:' + str(higest_pencentage) + '%')
result_begin_offset = np.where(final_output == np.amax(final_output))[0][0]
result_end_offset = np.where(final_output == np.amax(final_output))[1][0]
result_begin_date = pd.Timestamp(begin_year, begin_month, begin_day) + pd.Timedelta(days=result_begin_offset)
result_end_date = pd.Timestamp(begin_year, begin_month, begin_day) + pd.Timedelta(days=result_end_offset)
print('出現時段: ' + str(result_begin_date.month) + "-" + str(result_begin_date.day) + "最低位至" + str(result_end_date.month) + "-" + str(result_end_date.day))

final_output_df = pd.DataFrame(final_output)
final_output_df.to_excel(code + '_output.xlsx') # For backtest
input("任意鍵退出: ")